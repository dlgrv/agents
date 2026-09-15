# Frontend Tooling Pitfalls

## Vite HMR breaks on structural refactoring

**Symptom:** White screen in browser after file moves, new file creation, or import path changes. `npx vite build` and `npx tsc --noEmit` pass, but browser shows blank page with 0 elements.

**Root cause:** Vite's HMR (Hot Module Replacement) can't track module graph changes when files are created, moved, or when import structures shift significantly. The dev server continues running and reports "connected" but React fails to render silently — console errors appear as empty-message exceptions.

**Fix:** Kill and restart the dev server:
```bash
pkill -f vite && npx vite --host 0.0.0.0
```

**Detection:** After any refactoring that involves file creation/moves, always do a browser navigation check, not just TypeScript + build verification.

## Vite white screen from stale Docker container dev server

**Symptom:** White screen on the port the user normally opens (e.g., `localhost:5173`), but `tsc` and `vite build` pass, and a fresh dev server on a different port (e.g., `5174`) renders fine. `browser_console` shows an empty-message JS exception. Your local `pkill -f vite` doesn't help because the Vite process is inside a Docker container.

**Root cause:** A Docker container (e.g., `lowbid_frontend`) runs a Vite dev server with a bind-mounted source directory. When you edit 10+ files at once (rewriting `theme.ts`, deleting a hook file, changing exports), the container's Vite HMR module graph breaks silently — same mechanism as the host-level HMR pitfall above, but `pkill -f vite` on the host does NOT kill the container's Vite process.

**Detection:**
```bash
# Check if the port is served by Docker, not a host process
lsof -iTCP:5173 -sTCP:LISTEN -P | grep -v COMMAND
# If "OrbStack" or "docker-proxy" appears, it's a container
docker ps | grep frontend
```

**Fix:** Restart the Docker container, not the host process:
```bash
docker restart lowbid_frontend
```

**Key lesson:** When the user reports "white screen" but your local dev server renders fine, check which port they're actually using — it may be a Docker-proxied port with a stale Vite instance that needs `docker restart`, not `pkill`.

## Docker white screen after code changes — check volume mounts first

**Symptom:** User runs `docker compose up -d` after you've changed 10+ frontend files. White screen on the Docker-served port (e.g., 5173).

**Step 1 — Check if `docker-compose.override.yml` mounts volumes:**

```bash
cat docker-compose.override.yml | grep -A2 'frontend:'
# If you see `volumes: - ./frontend:/app`, code IS synced live
```

**If volumes ARE mounted** (common in dev override files): the container's filesystem mirrors your local source. The code is NOT stale — the white screen is browser-side (cache, service worker, stale HMR in the user's browser tab). Verify by checking the page yourself:

```bash
curl -s http://localhost:5173/ | head -5   # If HTML is served, server is fine
# Or: browser_navigate to the Docker port — if it renders, it's the user's browser
```

Fix: tell the user to hard-refresh (`Cmd+Shift+R`) or clear site data in DevTools. Do NOT tell them to rebuild the image — that's not the problem.

**If volumes are NOT mounted** (no override, or production-like setup): the Dockerfile's `COPY . .` copies source at build time. `docker compose up -d` WITHOUT `--build` reuses the old image with old code. Fix:

```bash
docker compose up -d --build frontend
```

**Key distinction:**
- Volumes mounted + white screen → browser cache / HMR (tell user to hard-refresh)
- No volumes + white screen after code changes → stale image (`--build`)
- HMR broke mid-session (no code changes) → `docker restart lowbid_frontend`

**Lesson learned:** In this project, `docker-compose.override.yml` mounts `./frontend:/app` with a separate `frontend_node_modules` volume. Code changes are live-synced. When the user reported white screen after token migration, the assumption was stale image — but the code was actually current. The real issue was the user's browser cache. Always check `docker-compose.override.yml` for volume mounts before assuming stale image.

## patch silent-failure recovery

When `patch(mode='replace')` reports a convincing diff and success but the file on disk is unchanged, fall back to:
1. `sed -i '' '/pattern/d' file` — for line removal
2. Rewrite the enclosing function with `write_file` using verified complete content
3. `git checkout -- file` + re-apply patches — as last resort

Do NOT retry the same `patch` call repeatedly — it wastes turns.

## `write_file` on style files: safe for full rewrites, deadly for partial edits

`write_file` overwrites the ENTIRE file. For `runtimeDashboard.ts` (170 lines of pure style constants), a full `write_file` is safe and efficient — you're replacing every line intentionally. But for a 1200-line component file like `CampaignsPage.tsx`, never use `write_file` unless you have the verified complete content.

**When `write_file` is appropriate for style files:**
- The file is small (<200 lines) and contains only constants/exports
- You're replacing ALL content intentionally (e.g., replacing every hardcoded value with tokens)
- You've read the full file without pagination in the current session

**When to use `patch(mode='replace')` instead:**
- Any file over 200 lines
- When only a few functions/sections need changing
- When the file was read with `offset`/`limit` (partial view) — you don't have the full content

**Recovery:** If `write_file` truncates a file, immediately `git checkout -- <file>` and re-apply with `patch`.

## `sed` batch replacement for design token migration

When migrating from hardcoded values to design tokens across many files, `sed` is dramatically faster than `patch` for mechanical replacements:

```bash
# Replace font size hardcodes across a single file
sed -i '' \
  -e 's/fontSize: 13/fontSize: fontSize.sm/g' \
  -e 's/fontSize: 14/fontSize: fontSize.md/g' \
  -e 's/fontWeight: 600/fontWeight: weight.semibold/g' \
  -e 's/fontWeight: 400/fontWeight: weight.regular/g' \
  src/pages/CampaignsPage.tsx
```

**Important:** `sed` only replaces exact string matches. Inline JSX like `fontWeight: active ? 600 : 400` won't match `fontWeight: 600` — handle these with `patch` after the `sed` pass.

After any `sed` batch:
1. Run `npx tsc --noEmit` — catches orphaned imports/types
2. `grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]' src/` — verify zero hardcodes remain
3. Add the new token imports (`fontSize`, `weight`) to each modified file's import from `../styles/theme`

## Batch JSX prop removal with `sed`

When you need to remove the same prop pattern from 5+ call sites in one file (e.g., removing `{...sectionCollapseProps(sectionsPrefs, 'X')}` from 8 `<FormSection>` elements), `patch(mode='replace')` requires one call per unique surrounding context. `sed` does it in one shot:

```bash
sed -i '' "s/ {...sectionCollapseProps(sectionsPrefs, '[^']*')}//g" src/pages/CampaignsPage.tsx
```

Key points:
- macOS `sed` requires `-i ''` (empty backup suffix), Linux `sed` uses just `-i`
- Use `[^']*` inside the quoted section name to match any string
- The `g` flag replaces all occurrences on each line
- Always follow with `npx tsc --noEmit` to catch any orphaned imports/types the removal created

Use this when `patch` would need 3+ near-identical replacements in the same file. For 1-2 replacements, `patch` is clearer.

## `vite build` rejected by terminal tool as "long-lived"

**Symptom:** `npx vite build` in foreground `terminal()` is rejected with: "This foreground command appears to start a long-lived server/watch process."

**Root cause:** The terminal tool's heuristic detects `vite` in the command and assumes it's a dev server (which never exits). `vite build` does exit, but the heuristic can't distinguish `build` from `dev`.

**Fix:** Run `vite build` with `background=true` + `notify_on_complete=true`, then `process(action='wait')`:
```bash
# In terminal(background=true, notify_on_complete=true):
npx vite build 2>&1 | tail -5
# Then process(action='wait') to get the result
```

`npx tsc --noEmit` runs fine in foreground — only `vite build` triggers the heuristic.

## `npx tsc --noEmit` + `npx vite build` combined in one command

Don't chain `tsc && vite build` in a single foreground `terminal()` call — `vite build` triggers the long-lived heuristic even when chained after `tsc`. Run them as separate calls:
1. `npx tsc --noEmit` (foreground, fast)
2. `npx vite build` (background + notify_on_complete, then wait)

## Stale browser snapshot after React state updates

**Symptom:** After clicking a button that triggers React state changes (e.g., entering/exiting edit mode via `setIsEditing`), `browser_snapshot` returns stale content that doesn't reflect the new state. The accessibility tree shows the old UI even though the DOM has updated.

**Root cause:** `browser_snapshot` can cache or race with React's re-render cycle. The snapshot is taken before React commits the state update.

**Fix:** Don't trust `browser_snapshot` for verifying state-dependent UI changes. Instead, evaluate the DOM directly via `browser_console`:
```js
document.querySelector('h3')?.textContent  // "Редактирование кампании" vs "USSP test campaign"
```

Or check structural indicators:
```js
JSON.stringify({
  h3: document.querySelector('h3')?.textContent,
  hasForm: !!document.querySelector('form'),
  tabs: [...document.querySelectorAll('[role=tab]')].map(t => t.getAttribute('aria-selected'))
})
```

## CSS Grid `1fr` maxWidth illusion

**Symptom:** You set `maxWidth: 'calc(100vw - 68px)'` on a grid child in a `gridTemplateColumns: '300px 1fr'` layout, but the child never reaches that width — it stays at `1fr` (e.g., 916px on a 1280px viewport). `justifyContent: 'center'` has no visible effect.

**Root cause:** `1fr` = remaining space after fixed tracks. The grid track itself is the constraint — no `maxWidth` on the child can exceed the track width. On a 1280px viewport with a 300px sidebar + 16px gap + 48px App padding, `1fr` = ~916px. Setting `maxWidth: 1212px` does nothing because the track is only 916px.

**Fix:** Switch from Grid to Flex for the outer layout. Put `justifyContent: 'center'` on the OUTER flex to centre sidebar+panel as a group:

```tsx
// ❌ Grid — 1fr caps the panel, maxWidth never triggers
<div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 16 }}>
  <div>{sidebar}</div>
  <div style={{ display: 'flex', justifyContent: 'center' }}>
    <section style={{ maxWidth: 'calc(100vw - 68px)' }}>...</section>
  </div>
</div>

// ✅ Flex — justifyContent on outer flex centres sidebar+panel as a group
<div style={{ display: 'flex', gap: 16, alignItems: 'start', justifyContent: 'center' }}>
  <div style={{ flexShrink: 0, width: 300 }}>{sidebar}</div>
  <section style={{ flex: '1 1 auto', maxWidth: 1400, minWidth: 0 }}>
    {/* content */}
  </section>
</div>
```

Use a fixed `maxWidth` (e.g., `1400`) instead of `calc(100vw - Npx)` — viewport-relative calcs don't account for App-level padding and are hard to reason about.

## `justifyContent: center` placement: outer vs inner flex

**Symptom:** You want a fixed-width sidebar adjacent to a main panel, with the whole group centred. You put `justifyContent: 'center'` on an inner flex wrapper around just the panel. Result: sidebar is pushed to the viewport edge, panel centres in the remaining space — they visually separate.

**Root cause:** `justifyContent: 'center'` on the inner wrapper only centres the panel within `flex: 1` (remaining space after sidebar). The sidebar sits at the left edge of the outer flex, separated from the panel by whatever space `flex: 1` didn't consume.

**Fix:** Put `justifyContent: 'center'` on the OUTER flex. This centres the sidebar+panel GROUP together. The sidebar stays glued to the panel's left edge. No inner wrapper needed — the section is a direct child of the outer flex.

```tsx
// ❌ Inner wrapper — sidebar pushed to edge, panel centres alone
<div style={{ display: 'flex', gap: 16, alignItems: 'start' }}>
  <div style={{ flexShrink: 0, width: 300 }}>{sidebar}</div>
  <div style={{ flex: 1, display: 'flex', justifyContent: 'center', minWidth: 0 }}>
    <section style={{ width: '100%', maxWidth: 1200 }}>...</section>
  </div>
</div>

// ✅ Outer justifyContent — group centred together, sidebar adjacent to panel
<div style={{ display: 'flex', gap: 16, alignItems: 'start', justifyContent: 'center' }}>
  <div style={{ flexShrink: 0, width: 300 }}>{sidebar}</div>
  <section style={{ flex: '1 1 auto', maxWidth: 1400, minWidth: 0 }}>...</section>
</div>
```

**Verify with `browser_console`:** Check that `sidebar.right + gap === panel.left` and that both have equal margins from viewport edges:
```js
const sb = document.querySelector('sidebar-selector').getBoundingClientRect();
const panel = document.querySelector('panel-selector').getBoundingClientRect();
// sb.right + 16 === panel.left  → sidebar adjacent to panel
// sb.left === viewport - panel.right  → group centred
```

## Design token systemization — full audit workflow

When a frontend has scattered hardcoded values (fontSize, fontWeight, colors, borderRadius, boxShadow, spacing), systemize them in one pass:

### Step 1: Audit
```bash
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]' src/ --include='*.tsx'
grep -rn 'borderRadius: [0-9]' src/ --include='*.tsx'
grep -rn "boxShadow: '0" src/ --include='*.tsx'
grep -rn '#[0-9a-f]\{6\}' src/ --include='*.tsx'  # hex colors
```

### Step 2: Define tokens in theme.ts
Add all token groups at once:
```ts
export const fontSize = { xs: 12, sm: 13, md: 14, lg: 22, xl: 28 } as const
export const weight = { regular: 400, medium: 500, semibold: 600, bold: 700 } as const
export const colors = { danger: '#b91c1c', success: '#15803d', warning: '#ea580c', ... } as const
export const shadow = { card: '...', tooltip: '...' } as const
export const spacing = { xxs: 4, xs: 8, sm: 12, md: 16, lg: 24 } as const
```

### Step 3: Mass-replace with sed, then patch stragglers
Use `sed` for exact-match replacements (e.g., `fontSize: 13` → `fontSize: fontSize.sm`). Handle ternary expressions and inline JSX with `patch` (sed won't match `fontWeight: active ? 600 : 400`).

### Step 4: Verify zero hardcodes remain
```bash
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]\|borderRadius: [0-9]\|boxShadow: .0\|#[0-9a-f]\{6\}' src/ --include='*.tsx'
# Should output 0 lines
```

### Pitfall: `fontSize: 'inherit'` and `fontSize: '1.25rem'`
These are NOT matched by `fontSize: [0-9]` grep. Search for `fontSize: '` separately. Replace `'inherit'` with an explicit token (e.g., `fontSize.md`) — inheriting from parent is fragile when the parent changes.

### Pitfall: Orphaned exports after token migration
When replacing hardcoded values with tokens in style files, check which exports are still imported by other files before deleting them. `runtimeShellStyle` looked orphaned after one component stopped importing it, but another page still used it. Always `grep` for import usage across the entire `src/` before removing an export.

### Pitfall: Duplicated inline styles → shared style constant
When the same inline style appears 3+ times (e.g., `padding: '6px 10px', borderRadius: 8, border: ..., background: ...` on every `<select>`), extract it to a named constant in the style file (e.g., `runtimeSelectStyle`). This is part of the token migration — don't leave duplicated inline styles after centralizing tokens.

## `sed` targeting only `*.tsx` misses `*.ts` style files

**Symptom:** After a `sed` batch replacing `gap: 8` → `spacing.xs` across `*.tsx` files, `npx tsc --noEmit` passes but hardcoded values remain in `styles/runtimeDashboard.ts` (a `.ts` file). The verification grep catches them, but only if it searches `*.ts` too.

**Root cause:** `find . -name '*.tsx' -exec sed ...` only processes `.tsx` files. Style files like `runtimeDashboard.ts` and `theme.ts` are `.ts` — they're skipped by the `find` filter.

**Fix:** Run `sed` separately on `.ts` style files, or use a broader `find`:
```bash
# Process both .tsx and .ts
find . -name '*.tsx' -o -name '*.ts' | xargs sed -i '' \
  -e 's/gap: 8,/gap: spacing.xs,/g' \
  ...
```

Or run `sed` directly on the style file:
```bash
sed -i '' -e 's/gap: 4,/gap: spacing.xxs/g' styles/runtimeDashboard.ts
```

**Detection:** Always include `--include='*.ts'` in verification greps:
```bash
grep -rn 'gap: [1-9]' src/ --include='*.tsx' --include='*.ts'
```

## `sed` replacing string margins with template literals: broken interpolation

**Symptom:** After `sed -i '' "s/margin: '6px 0 0 0'/margin: '${spacing.xs}px 0 0 0'/g"`, the file contains `margin: '${spacing.xs}px 0 0 0'` — but this is a **single-quoted string**, so `${spacing.xs}` is literal text, not interpolation. TypeScript compiles it as a plain string. The element gets `margin: "${spacing.xs}px 0 0 0"` literally.

**Root cause:** `sed` can't produce backtick-quoted template literals — it operates on flat text and the replacement string `'${spacing.xs}px 0 0 0'` stays inside the original single quotes. Template literals require backticks, which sed can't safely emit inside `s///` expressions.

**Fix:** Don't use `sed` to inject `${...}` interpolation into existing string literals. Instead, replace `margin: '...'` with `marginTop`/`marginBottom` using direct token values (no string interpolation needed):

```bash
# ❌ BROKEN — sed produces literal '${spacing.xs}' inside single quotes
sed -i '' "s/margin: '6px 0 0 0'/margin: '${spacing.xs}px 0 0 0'/g" file.tsx

# ✅ Use patch to replace with marginTop: spacing.xs (no string needed)
patch(mode='replace', old_string="margin: '6px 0 0 0'", new_string="marginTop: spacing.xs")
```

Or use a Python script that reads the file, does the replacement with proper context awareness (backticks vs single quotes), and writes back.

**Detection:** After any `sed` that injects `${...}` patterns:
```bash
grep -rn "margin: '\${spacing" src/  # Should be 0 — if not, sed broke it
grep -rn "\${spacing" src/ --include='*.tsx' | grep "'"  # Single-quoted template vars
```

**General rule:** `sed` is safe for replacing literal-with-literal (e.g., `fontSize: 13` → `fontSize: fontSize.md`). It is NOT safe for replacing literal-with-interpolation (e.g., `margin: '6px'` → `margin: \`${spacing.xs}px\``). For the latter, use `patch` or a Python script.

## Python script for multiline import patching: deduplication pitfall

**Symptom:** After running a Python script to add `spacing` to multiline `import { ... } from '../styles/theme'` blocks, `npx tsc --noEmit` fails with `TS1003: Identifier expected` — the script appended `, spacing }` to the end line, but `spacing` was already present on a line above, creating a duplicate.

**Root cause:** The Python script searches for the line containing `from '../styles/theme'` and appends `, spacing }` to it. But in multiline imports, the last line is `} from '../styles/theme'` — the script's `.replace("} from '../styles/theme'", ", spacing } from '../styles/theme'")` creates `spacing, \n, spacing }` when `spacing` was already added on a separate line by the same script in a previous iteration.

**Fix:** After running the Python import-patching script, always:
1. Run `npx tsc --noEmit` to catch duplicates immediately
2. If duplicates found, `patch(mode='replace')` the specific lines to remove the duplicate
3. Verify with `grep -c 'spacing' file.tsx` — should match exactly once in imports

**Better approach:** Use `sed` for single-line imports and `patch` for multiline imports. The Python script approach is fragile because it doesn't parse the import block structure — it just does string replacement on the last line.

## Chart null-value rendering: zero baseline, not gaps

**Symptom:** Line charts show gaps (broken lines) or em-dashes (`—`) in tooltips/footers when data contains `null` values (e.g., no bid attempts in a given minute). User expects "no data = zero", not "no data = invisible".

**Root cause:** `buildSmoothPath` in `runtimeChartPath.ts` split `null` values into separate SVG path runs (gaps). `ChartCard` footer and `LineChart` tooltip rendered `null` as `'—'`. When ALL values were `null`, `buildSmoothPath` returned an empty string — no line at all.

**Fix (3 changes):**
1. `buildSmoothPath`: remove the `if (!numeric.length) return ''` early return. Treat `null` as `0` via `value ?? 0`. Build a single continuous path — no run/gap splitting.
2. `LineChart` tooltip: `item.values[hoverIndex] ?? 0` instead of `?? null` + `=== null ? '—' : ...`.
3. `ChartCard` footer: `formatValue(current ?? 0)` instead of `current === null ? '—' : formatValue(current)`.

**JSDoc:** Update the `LineChartSeries.values` comment from "drawn as a gap" to "treated as zero — the line drops to zero, not a gap".

**Verification:** `grep -q 'if (!numeric.length) return' src/utils/runtimeChartPath.ts` → should NOT match. `grep -q 'value ?? 0' src/utils/runtimeChartPath.ts` → should match. `grep -q "=== null ? '—'" src/components/runtime/ChartCard.tsx` → should NOT match.

## Root font-size inheritance: `<p>` containers inherit 16px from `:root`

**Symptom:** In a Settings tab, section titles ("General", 14px bold) look the same size or SMALLER than the detail rows beneath them ("ID:", "Статус:", 16px). The visual hierarchy is inverted — the title should dominate.

**Root cause:** `:root` CSS sets `font-size: 16px` and `line-height: 1.5` (browser default for `system-ui`). A `<p>` element with no explicit `fontSize` inherits 16px. Even if its CHILD elements (`<span>`, `<label>`) have `fontSize: fontSize.md` (14px) set via inline styles, the `<p>` itself is still 16px — and `line-height: 1.5` makes each row ~24px tall (16 × 1.5), which feels too spacious.

The child `fontSize` overrides only the child's text rendering. The parent `<p>`'s `font-size` still controls the `line-height` calculation (unless `line-height` is also overridden on the `<p>`), and the parent's inherited `font-size` affects any text directly in the `<p>` that isn't wrapped in a child with its own `fontSize`.

**Fix:** Set `fontSize` AND `lineHeight` on the container element, not just on its children:

```tsx
// ❌ <p> inherits 16px/1.5 from :root — children have 14px but row is 24px tall
<p style={{ marginBottom: spacing.xs }}>
  <span style={{ fontSize: fontSize.md, fontWeight: weight.regular }}>ID:</span>
  <span style={{ fontSize: fontSize.md, fontWeight: weight.semibold }}>1</span>
</p>

// ✅ <p> explicitly sets fontSize + lineHeight — row is 14px, ~20px tall
<p style={{ margin: 0, marginBottom: spacing.xxs, fontSize: fontSize.md, lineHeight: 1.4 }}>
  <span style={detailLabelStyle}>ID:</span>
  <span style={detailValueStyle}>1</span>
</p>
```

**General rule:** When a container (`<p>`, `<div>`, `<section>`) wraps text-bearing children, always set `fontSize` and `lineHeight` on the CONTAINER itself. Child `fontSize` overrides do NOT affect the container's `line-height` calculation. The container's inherited values control row height and any text not wrapped in a child element.

**Detection:** Use `browser_console` to check computed styles:
```js
(() => {
  const p = document.querySelector('section p');
  const cs = getComputedStyle(p);
  return JSON.stringify({ fontSize: cs.fontSize, lineHeight: cs.lineHeight });
})()
// If fontSize is "16px" — the <p> is inheriting from :root, not using a token
```
