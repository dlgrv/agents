# Design Token Rollout Checklist

Step-by-step checklist for migrating a React dashboard from hardcoded values
to a complete design token system. Used on the LowBid v2 frontend (system-ui,
inline CSSProperties, no CSS framework).

## Audit phase — find all hardcoded values

```bash
# Font sizes and weights
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]' src/ --include='*.tsx' --include='*.ts'

# Border radius
grep -rn 'borderRadius: [0-9]' src/ --include='*.tsx'

# Hardcoded hex colors
grep -rn "#[0-9a-f]\{6\}" src/ --include='*.tsx'

# Box shadow strings
grep -rn "boxShadow: '0" src/ --include='*.tsx'

# Gap magic numbers (exclude gap: 0 which is intentional)
grep -rn 'gap: [1-9]' src/ --include='*.tsx'

# Line height values
grep -rn 'lineHeight:' src/ --include='*.tsx'

# Padding string literals (hardest to tokenize — evaluate case by case)
grep -rn "padding: '" src/ --include='*.tsx'
```

## Step 1: theme.ts — add/extend token groups

### Colors — add semantic tokens

```ts
export const colors = {
  // ... existing structural colors ...
  textMuted: '#595959',  // was #666666 — bumped for WCAG 7:1 contrast
  surface: '#ffffff',
  success: '#15803d',
  warning: '#ea580c',
  dangerBright: '#dc2626',
  info: '#2563eb',
  chartTrack: '#f3f3f3',
  tooltipBg: '#111111',
  tooltipText: '#ffffff',
} as const
```

Replace hardcoded hex in status color functions:
- `campaignStatusColor`: `'#15803d'` → `colors.success`, `'#b91c1c'` → `colors.danger`
- `bidStatusColor`: `'#15803d'` → `colors.success`, `'#dc2626'` → `colors.dangerBright`
- `playbackStatusColor`: `'#2563eb'` → `colors.info`, `'#ea580c'` → `colors.warning`, etc.
- `errorTextStyle`: `'#b91c1c'` → `colors.danger`
- `usspColors.revenue` → `colors.success`, `usspColors.impressions` → `colors.info`

### Spacing — extend with xxs and lg

```ts
export const spacing = {
  xxs: 4,   // tight gaps in filter labels, datetime fields
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,   // App container padding (replaces '1.5rem')
} as const
```

### Shadow — tooltip only

```ts
export const shadow = {
  tooltip: '0 2px 8px rgba(0, 0, 0, 0.12)',
} as const
```

**`shadow.card` was removed.** Cards use border-only (`1px solid`) — no shadow. This is the minimalist approach: border-only is cleaner than border+shadow. Remove all `boxShadow: shadow.card` references from `CollapsibleSection`, `panelStyle`, `listItemButtonStyle`, and `runtimeCardStyle`.

### Font tokens (if not already present)

See SKILL.md §10 for the full `fontSize` and `weight` token definitions.

**4 sizes only — no `fontSize.sm`.** The system uses `xs (12)`, `md (14)`, `lg (22)`, `xl (28)`. Former `sm (13)` was removed: UI text → `md`, metadata → `xs`.

## Step 2: runtimeDashboard.ts — propagate tokens

- All `gap: 4` → `spacing.xxs`
- All `gap: 8/10` → `spacing.xs`
- All `gap: 12/14` → `spacing.sm`
- Add `runtimeSelectStyle` constant for triplicated select inline styles:
```ts
export const runtimeSelectStyle: CSSProperties = {
  ...runtimeControlInputStyle,
  padding: `${spacing.xs}px ${spacing.sm}px`,
}
```
- Remove orphan exports (e.g., `runtimeCollapsibleShellStyle` if no longer imported)
- **`runtimeSelectStyle` must be declared AFTER `runtimeControlInputStyle`** in the file — it extends it via `...runtimeControlInputStyle`. TypeScript errors `TS2448: Block-scoped variable used before its declaration` if the order is wrong.

## Step 3: Batch replace gap magic numbers in .tsx files

```bash
# Run from src/ directory
find . -name '*.tsx' -exec sed -i '' \
  -e 's/gap: 4,/gap: spacing.xxs,/g' \
  -e 's/gap: 5,/gap: spacing.xxs,/g' \
  -e 's/gap: 6,/gap: spacing.xs,/g' \
  -e 's/gap: 7,/gap: spacing.xs,/g' \
  -e 's/gap: 8,/gap: spacing.xs,/g' \
  -e 's/gap: 10,/gap: spacing.xs,/g' \
  -e 's/gap: 12,/gap: spacing.sm,/g' \
  -e 's/gap: 14,/gap: spacing.sm,/g' \
  -e 's/gap: 16,/gap: spacing.md,/g' \
  {} +
```

**Note:** `sed` on macOS does NOT match inline JSX `gap: 8` inside `style={{ ... }}`
in all cases — manual `patch` may be needed for inline styles that sed misses.
After running sed, grep again to find stragglers:
```bash
grep -rn 'gap: [1-9]' src/ --include='*.tsx'
```

**Add `spacing` to imports** in every file that now uses `spacing.*`:
- Files with single-line `import { colors, ... } from '../styles/theme'` — add `spacing` to the braces
- Files with multi-line imports — add `spacing,` on its own line before the closing `}`
- Files that had no theme import at all (e.g., FieldLabel) — add a new import line

## Step 4: Replace borderRadius hardcodes in .tsx files

| Hardcode | Token | Where |
|---|---|---|
| `borderRadius: 8` | `radius.sm` | InfoTooltip, LineChart, PlaybackEventConfigsPanel, MoneyPowerGloryPage |
| `borderRadius: 10` | `radius.sm` | PlaybackEventConfigsPanel section (was `radius.md`, now unified to `sm`) |
| `borderRadius: 6` | `radius.sm` | CountBars bars |
| `borderRadius: 999` | `radius.pill` | LegendButton, ErrorRateMoodBadge |

**`radius.md` (10) was removed.** All former `radius.md` uses are now `radius.sm` (10). The 2px difference was not visually distinguishable. `radius.sm` was bumped from 8 to 10 for a more rounded, friendly feel across the entire UI. Add `radius` to imports in each modified file.

## Step 5: Replace hardcoded colors in .tsx files

| Hardcode | Token | Where |
|---|---|---|
| `'#b91c1c'` | `colors.danger` | CampaignsPage (toolbarDangerButtonStyle) |
| `'#c62828'` | `colors.danger` | PlaybackEventConfigsPanel error text |
| `'#15803d'` | `colors.success` | CampaignsPage (runControlButtonStyle start bg) |
| `'#111111'` | `colors.tooltipBg` | LineChart tooltip background |
| `'#ffffff'` | `colors.tooltipText` or `colors.surface` | LineChart tooltip text, CampaignsPage button text |
| `'#f3f3f3'` | `colors.chartTrack` | CountBars bar track background |

Use `sed` for batch replacement where the pattern is unambiguous:
```bash
sed -i '' \
  -e "s/color: '#b91c1c'/color: colors.danger/g" \
  -e "s/color: '#c62828'/color: colors.danger/g" \
  -e "s/background: '#111111'/background: colors.tooltipBg/g" \
  -e "s/color: '#ffffff'/color: colors.tooltipText/g" \
  file.tsx
```

**Warning:** `colors` is a variable name that shadows the local `colors` const
inside `playbackStatusColor`. When refactoring that function, rename the local
`const colors: Record<string, string>` to `const map` to avoid shadowing.

## Step 6: Replace boxShadow hardcodes

| Hardcode | Token | Where |
|---|---|---|
| `'0 2px 8px rgba(0, 0, 0, 0.08)'` | `shadow.tooltip` | InfoTooltip |
| `'0 2px 8px rgba(0, 0, 0, 0.2)'` | `shadow.tooltip` | LineChart tooltip |

Add `shadow` to imports in each modified file.

## Step 7: Unify lineHeight

Standard values: `1` (icon-only elements like InfoTooltip circle) and `1.4` (all body text, tooltips, badges).

```bash
sed -i '' "s/lineHeight: 1.35/lineHeight: 1.4/g" file.tsx
```

## Step 8: Replace select inline styles with runtimeSelectStyle

Three files had identical inline select styles (`padding: '6px 10px', borderRadius: 8, border: ..., background: ...`):

```tsx
// Before (×3 across BidAttemptsSection, PlaybackRuntimeSection)
<select style={{ padding: '6px 10px', borderRadius: 8, border: `1px solid ${colors.border}`, background: colors.surface }}>

// After
import { runtimeSelectStyle as selectStyle } from '../styles/runtimeDashboard'
<select style={selectStyle}>
```

## Step 9: App.tsx — replace rem with px token

```tsx
// Before
<div style={{ margin: '0 auto', padding: '1.5rem' }}>

// After
import { spacing } from './styles/theme'
<div style={{ margin: '0 auto', padding: spacing.lg }}>
```

This eliminates the only `rem` unit in the project — everything else is `px`.

## Step 10: Rename stale identifiers

When refactoring removes a concept (e.g., collapsibility), rename stale identifiers:
- `collapsibleSectionsStackStyle` → `sectionsStackStyle`
- Remove orphan files: `useCampaignSectionsPrefs.ts`
- Remove orphan exports from `campaignDashboardPrefs.ts`: `CAMPAIGN_DETAIL_SECTIONS`, `CampaignDetailSection`, `CampaignSectionsPrefs`, `getSectionExpanded`, `loadCampaignSectionsPrefs`, `saveCampaignSectionsPrefs`

```bash
sed -i '' 's/collapsibleSectionsStackStyle/sectionsStackStyle/g' src/pages/CampaignsPage.tsx
```

## Step 11: Replace margin magic numbers with spacing tokens

After gap migration, replace hardcoded `margin`/`marginTop`/`marginBottom` values:

```bash
# In .tsx files — use sed for exact numeric matches
find . -name '*.tsx' -exec sed -i '' \
  -e "s/marginTop: 6/marginTop: spacing.xs/g" \
  -e "s/marginTop: 10/marginTop: spacing.xs/g" \
  -e "s/marginTop: 12/marginTop: spacing.sm/g" \
  -e "s/marginTop: 16/marginTop: spacing.md/g" \
  -e "s/marginBottom: 8/marginBottom: spacing.xs/g" \
  -e "s/marginBottom: 16/marginBottom: spacing.md/g" \
  {} +
```

**DO NOT use `sed` to replace string margins like `margin: '6px 0 0 0'` with `${spacing.xs}px`** — sed cannot produce backtick-quoted template literals inside existing single-quoted strings. The result is literal `${spacing.xs}` text, not interpolation. Instead, replace `margin: 'Npx ...'` with `marginTop: spacing.xs` (or appropriate direction) via `patch` or a Python script:

```bash
# ❌ BROKEN — sed produces literal '${spacing.xs}' inside single quotes
sed -i '' "s/margin: '6px 0 0 0'/margin: '${spacing.xs}px 0 0 0'/g"

# ✅ Use patch — replace margin string with marginTop token
patch(mode='replace', old="margin: '6px 0 0 0'", new="marginTop: spacing.xs")
```

In `.ts` style files (runtimeDashboard.ts), same rule: replace `margin: '6px 0 0 0'` with `marginTop: spacing.xs`.

**Also replace:**
- `minHeight: 420` (magic number) — remove entirely; flex determines height
- `height: 34` → `controlHeight` in runtimeDashboard.ts and page components
- `letterSpacing: '-0.02em'` → `'-0.01em'` (unify to one value)

**Table padding compactness:** When a table (`PlaybackEventConfigsPanel`) shares a tab with compact `DetailRow` elements (~20px tall), table cells with `padding: '8px 10px'` + inherited `line-height: 1.5` produce 38px rows — nearly double the height. Fix:
- `tableStyle`: add `lineHeight: 1.4` (matches DetailRow)
- `thStyle`: `padding: '${spacing.xs}px ${spacing.sm}px'` (8px 12px — header slightly taller for visual distinction)
- `tdStyle`: `padding: '${spacing.xxs}px ${spacing.sm}px'` (4px 12px — compact data rows, ~29px height)
- `inputStyle`: `padding: '${spacing.xxs}px ${spacing.xs}px'` (4px 8px — tokens instead of hardcoded)

## Step 12: Reduce font sizes from 5 to 4

If the token system still has `fontSize.sm (13)`, remove it:
1. Delete `sm: 13` from the `fontSize` object in `theme.ts`
2. Replace all `fontSize.sm` → `fontSize.md` (UI text: buttons, labels, table, badges) or `fontSize.xs` (metadata: descriptions, estimates)
3. Replace in `theme.ts` `buttonStyle` (3 occurrences — all → `fontSize.md`)
4. Verify: `grep -rn 'fontSize\\.sm' src/` — must be 0

## Step 13: Fix root font-size inheritance on detail rows

**Problem:** `<p>` elements wrapping detail rows (label + value) inherit `font-size: 16px` and `line-height: 1.5` from `:root`, even when child elements (`<span>`, `<label>`) have explicit `fontSize: fontSize.md` (14px). This makes rows appear larger than section titles and too tall.

**Fix:** Set `fontSize` AND `lineHeight` on the container `<p>` itself:

```tsx
// ❌ <p> inherits 16px/1.5 from :root — children override font-size but row is still tall
<p style={{ marginBottom: spacing.xs }}>
  <span style={{ fontSize: fontSize.md }}>label</span>
  <span style={{ fontSize: fontSize.md }}>value</span>
</p>

// ✅ <p> explicitly sets fontSize + lineHeight — row is 14px, ~20px tall
<p style={{ margin: 0, marginBottom: spacing.xxs, fontSize: fontSize.md, lineHeight: 1.4 }}>
  <span style={detailLabelStyle}>label</span>
  <span style={detailValueStyle}>value</span>
</p>
```

Also tighten `marginBottom` from `spacing.xs` (8px) to `spacing.xxs` (4px) for compact rows.

**This applies to any container wrapping text children** — always set `fontSize` + `lineHeight` on the container, not just on the children.

## Step 14: Chart empty states — zero-line, not text placeholder

**Problem:** `ChartCard` with `hasData={false}` renders an `EmptyChartMessage` text block instead of a graph. This is inconsistent with other charts that render zero-line baselines for null data.

**Fix:** Remove `hasData` and `emptyMessage` from `ChartCard` calls. The series with `null` values renders as a flat zero line:

```tsx
// ❌ Text placeholder
<ChartCard title="..." series={timeline} hasData={hasData} emptyMessage="Нет данных" />

// ✅ Zero-line graph — hasData defaults to true
<ChartCard title="..." series={timeline} />
```

Remove now-unused `hasResponseTimeData` useMemo. Also replace any hardcoded `color="#hex"` with `color={colors.token}`.

## Step 15: CountBars empty state — natural height (NO minHeight)

**The user's explicit preference:** blocks with no data should shrink in height. Do NOT add `minHeight: 200` or any fixed-height wrapper. The empty message renders naturally:

```tsx
{!rows.length ? (
  <EmptyChartMessage>{emptyMessage}</EmptyChartMessage>
) : ( /* bars */ )}
```

The visual height difference between empty (~32px) and data-filled (~250px) is intentional. An earlier version added `minHeight: 200` — the user explicitly rejected it: "вернем как было — если ошибок или прерываний нет, то блок уменьшается в высоте".

## Step 16: Table padding compactness

When a table (`PlaybackEventConfigsPanel`) shares a tab with compact `DetailRow` elements (~20px tall), table cells with `padding: '8px 10px'` + inherited `line-height: 1.5` produce 38px rows — nearly double the height. Fix:
- `tableStyle`: add `lineHeight: 1.4` (matches DetailRow)
- `thStyle`: `padding: '${spacing.xs}px ${spacing.sm}px'` (8px 12px — header slightly taller for visual distinction)
- `tdStyle`: `padding: '${spacing.xxs}px ${spacing.sm}px'` (4px 12px — compact data rows, ~29px height)
- `inputStyle`: `padding: '${spacing.xxs}px ${spacing.xs}px'` (4px 8px — tokens instead of hardcoded)

## Step 17: CSS variables in index.css — mirror theme.ts

Replace all hardcoded hex/px in `index.css` with CSS custom properties defined in `:root`. The `:root` block is the ONLY place hex values appear in CSS — they are variable definitions, not hardcodes.

```css
:root {
  --color-text: #111111;
  --color-text-muted: #595959;
  --color-surface: #ffffff;
  --color-border: #e5e5e5;
  --color-page-bg: #f7f7f5;
  --color-hover-bg: #f5f5f3;
  --radius-sm: 10px;
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --control-height: 34px;
  --transition: 0.15s ease;
}
```

All CSS rules then use `var(--...)`:
```css
button {
  color: var(--color-text);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 6px var(--spacing-sm);
  transition: background var(--transition);
}
```

Keep CSS variable values in sync with `theme.ts` manually. When adding a new token to `theme.ts`, add the matching `--var` in `:root`.

## Step 18: Transition token — smooth interactions

Add `transition` token to `theme.ts`:
```ts
export const transition = '0.15s ease'
```

Apply to interactive elements in `theme.ts`:
- `buttonStyle` (all 3 levels): `transition: \`background ${transition}, color ${transition}\``
- `navLinkStyle`: `transition: \`color ${transition}, border-color ${transition}\``
- `listItemButtonStyle`: `transition: \`background ${transition}, border-color ${transition}\``

In `index.css`, CSS `button` uses `transition: background var(--transition)`.

## Step 19: Heading hierarchy tokens

Ensure all `<h1>`–`<h4>` elements have explicit `fontSize` and `fontWeight` tokens. Browser defaults (1.5em, 1.17em) break the token hierarchy.

| Tag | fontSize | fontWeight | Where |
|---|---|---|---|
| h1 | `fontSize.lg` (22) | `weight.bold` (700) | App brand |
| h2 | `fontSize.lg` (22) | `weight.bold` (700) | Page titles, campaign detail name |
| h3 | `fontSize.md` (14) | `weight.semibold` (600) | Section titles (create/edit) |
| h4 | `fontSize.md` (14) | `weight.bold` (700) | Card titles (CollapsibleSection) |

Files to check: `App.tsx` (h1), `MoneyPowerGloryPage.tsx` + `BidEndpointsPage.tsx` + `BidRequestTemplatesPage.tsx` (h2), `CampaignsPage.tsx` (h3).

## Step 20: Remove remaining magic numbers

- `maxHeight: 560` in `listSectionStyle` — remove; `overflowY: 'auto'` + flex handles scrolling
- `paddingBottom: 12` in App header → `paddingBottom: spacing.sm`
- `borderBottom: '1px solid #e5e5e5'` in App header → `` `1px solid ${colors.border}` ``

## Step 21: Pill-style tabs and toolbar buttons

**Tabs (Runtime/Settings) use pill style, not underline.** Active tab = `colors.text` (black) + `colors.surface` (white text) + `weight.semibold`. Inactive = transparent + `colors.textMuted` + `weight.regular`. Both have `borderRadius: radius.pill` and `transition` for smooth state changes. The black-filled active pill was approved by the user — it creates high contrast and clear visual selection.

**Campaign toolbar buttons are pill-shaped, standalone (no grouped container).** No toolbar border/bg wrapper — just `display: inline-flex, gap: spacing.xs`. Run control buttons are standalone pills with `borderRadius: radius.pill`. Settings button has `1px solid border`. Delete button is icon-only with `borderColor: colors.danger`.

**Toolbar buttons use `height: controlHeight` (34px).** All toolbar buttons (Запустить, Остановить, Настройки, Удалить) set `height: controlHeight` + `padding: \`0 ${spacing.sm}px\``. This ensures the icon-only Delete button matches the height of text buttons. Use `height: controlHeight`, NOT padding-based height which varies by content (icon vs text).

**Delete button: icon-only, no text, transparent bg.** `<TrashIcon />` with `aria-label="Удалить кампанию"`, `title` for hover tooltip. No "Удалить" text. Uses `borderColor: 'transparent'` + `background: 'transparent'` + `color: colors.danger` — a bare danger-colored icon in pill shape.

**Remove `data-run-control` CSS rules** from `index.css` — no longer needed without grouped border.

## Step 22: Border-only cards (no shadow)

**Remove `shadow.card` from all card-style elements.** Cards use `1px solid border` only — no `boxShadow`. This is the minimalist approach: border-only is cleaner than border+shadow.

Remove from: `CollapsibleSection.sectionStyle`, `CampaignsPage.panelStyle`, `listItemButtonStyle`, `runtimeCardStyle`, `runtimeChartBoxStyle`.

Keep `shadow.tooltip` — tooltips still need shadow for depth perception.

After removing `shadow.card`, the `shadow` object in `theme.ts` has only `tooltip`. Remove `shadow` from imports in files that no longer use it.

## Step 23: Unify radius to single value

**`radius.md` (10) is removed. All former `radius.md` uses become `radius.sm`.** Then bump `radius.sm` from 8 to 10 for a more rounded, friendly feel.

```ts
export const radius = {
  sm: 10,    // ALL elements
  pill: 999, // tabs, buttons, badges
} as const
```

Update `--radius-sm` in `index.css` `:root` to match (10px).

## Step 24: Campaign detail name — match page title size

The campaign detail name (`<h3>` in CampaignsPage) uses `fontSize.lg` (22px) + `weight.bold` — same as `<h2>` page titles on other pages. The user requested: "размер названия кампании слишком мелкий, давай будет такой же как названия вкладок на других вкладках".

## Step 25: Sidebar list padding — horizontal spacing.sm

`listItemButtonStyle` padding: `spacing.xs` (8px all sides) → `${spacing.xs}px ${spacing.sm}px` (8px vertical, 12px horizontal). Pill-shaped buttons need more horizontal padding so text doesn't sit too close to the rounded edge. The user noticed: "название кампании слишком близко к краю из-за этого не очень симпатично".

## Step 26: Card padding uniformity — all cards use spacing.sm

`runtimeCardStyle` and `runtimeChartBoxStyle` had `padding: spacing.xs` (8px), while `panelStyle` and `CollapsibleSection` used `spacing.sm` (12px). This made metric/chart cards look tighter than surrounding panels. Change both to `padding: spacing.sm` (12px) for visual consistency across all card-style elements.

## Step 27: Unify all buttons via buttonStyle()

Replace all bare `<button>` elements with explicit `buttonStyle()` calls:

| Button | Style | Files |
|---|---|---|
| Submit (Save/Add/Сохранить) | `buttonStyle('primary')` | SubmitButton.tsx (renders internally) |
| Cancel/Отмена/Reset | `buttonStyle('secondary')` | CampaignsPage, BidEndpoints, BidRequestTemplates |
| Edit (table) | `buttonStyle('ghost')` | BidEndpoints, BidRequestTemplates |
| Delete (table) | `{ ...buttonStyle('ghost'), color: colors.danger }` | BidEndpoints, BidRequestTemplates |
| Reset defaults | `buttonStyle('secondary')` | PlaybackEventConfigsPanel |

`SubmitButton` component renders `buttonStyle('primary')` internally — no caller needs to set style. `sidebarCreateButtonStyle` reuses `buttonStyle('secondary')` with `width: '100%'` instead of a custom style with hardcoded `height: 32`.

## Step 28: cardStyle — shared base for all card-like containers

Add `cardStyle` to `theme.ts`:

```ts
export const cardStyle: CSSProperties = {
  border: `1px solid ${colors.border}`,
  borderRadius: radius.sm,
  background: colors.surface,
  padding: spacing.sm,
}
```

Replace 6 independently-declared card style objects with `...cardStyle` extensions:

| Style | File | Before | After |
|---|---|---|---|
| `runtimeCardStyle` | runtimeDashboard.ts | 4 lines (border+radius+bg+padding) + minHeight | `...cardStyle` + `minHeight: 64` |
| `runtimeChartBoxStyle` | runtimeDashboard.ts | 4 lines + 5 layout props | `...cardStyle` + 5 layout props |
| `runtimeSectionStyle` | runtimeDashboard.ts | 4 lines + display+gap | `...cardStyle` + `display+gap` |
| `runtimeCustomRangePanelStyle` | runtimeDashboard.ts | 4 lines + flex layout | `...cardStyle` + flex layout |
| `panelStyle` | CampaignsPage.tsx | 4 lines | `...cardStyle` |
| `sectionStyle` | CollapsibleSection.tsx | 4 lines + margin+overflow | `...cardStyle` + `margin+overflow` |

After this, `CollapsibleSection.tsx` no longer needs `colors` or `radius` in its import (they come via `cardStyle`). `runtimeDashboard.ts` imports `cardStyle` from `theme.ts`.

**Before `cardStyle`**, each of these 6 objects independently declared `border`, `borderRadius`, `background`, and `padding` — ~24 lines of duplicated code. When `radius.sm` changed from 8→10, all 6 needed updating. Now: change `cardStyle` once.

**When to use `...cardStyle`:** Any style object that renders a visible card/container with border + background. If it only needs layout (no border), use a plain layout object (like `runtimeShellStyle: { display: 'grid', gap: spacing.md }`).

## Step 29: Remove app header border

The full-width `borderBottom` under the nav toolbar was removed per user request — "под тулбаром сверху есть подчеркивание на всю ширину страницы — давай уберем". Remove `borderBottom` and `paddingBottom` from the App header style. Remove `colors` from App.tsx imports if it becomes unused.

## Verify

```bash
# TypeScript
npx tsc --noEmit && echo "TSC_OK"

# Build
npx vite build

# Zero hardcoded font values
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]' src/ --include='*.tsx' --include='*.ts' | wc -l
# Must be 0

# Zero hardcoded gap (except gap: 0)
grep -rn 'gap: [1-9]' src/ --include='*.tsx' | wc -l
# Must be 0

# Zero hardcoded borderRadius in .tsx
grep -rn 'borderRadius: [0-9]' src/ --include='*.tsx' | wc -l
# Must be 0

# Zero hardcoded hex colors in .tsx
grep -rn '#[0-9a-f]\{6\}' src/ --include='*.tsx' | wc -l
# Must be 0

# Zero hardcoded boxShadow strings in .tsx
grep -rn "boxShadow: '0" src/ --include='*.tsx' | wc -l
# Must be 0

# No lineHeight 1.35
grep -rn 'lineHeight: 1.35' src/ | wc -l
# Must be 0

# CSS variables used in index.css (not hardcoded hex in rules)
grep -c 'var(--' src/index.css
# Must be > 0

# transition token exported from theme.ts
grep -q "export const transition" src/styles/theme.ts && echo "OK"
# Must print OK

# All h2/h3 have explicit fontSize
grep -rn '<h2' src/ --include='*.tsx' | grep -v 'fontSize' | wc -l
grep -rn '<h3' src/ --include='*.tsx' | grep -v 'fontSize' | wc -l
# Both must be 0
```

Note: `index.css` will still have hardcoded values (CSS cannot import TS tokens).
This is expected — CSS values must manually match `theme.ts` exactly.

## What NOT to change

- Chart-internal SVG attributes (stroke widths, fill colors in SVG elements — but DO replace hardcoded hex like `#fbfbfb` and `#5f6368` with `colors.*` tokens)
- `index.css` `:root` variable definitions (these ARE the hex values — CSS can't import TS, so `:root` is the source of truth for CSS)
- CSS rules in `index.css` that use `var(--...)` references (these are correct — not hardcodes)
- `gap: 0` (intentional — tab bar with no gap between tabs)
- `lineHeight: 1` (icon-only elements like InfoTooltip circle)
- Semantic width/height values: `width: 360` (form inputs), `width: 120` (number inputs), `width: 12-18` (icon/dot sizes), `maxWidth: 1400/980/280` (layout/textarea/tooltip constraints), `minWidth: 56, maxWidth: 72` (table inputs). These are component-specific, not design tokens — don't try to force them into the spacing system.
