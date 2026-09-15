---
name: frontend-architecture
description: React/TypeScript dashboard architecture patterns — shared runtime components, color synchronization, chart extraction, filter composition, API contract shapes, and the Vitest/Playwright test pyramid for FSD monorepos. Use when building/refactoring React dashboard sections with charts, filters, and polling, setting up Vitest/Playwright testing for an FSD npm-workspaces frontend, or scaffolding standalone design-preview apps (frontend/previews/<hash>/ pattern).
license: MIT
---

# Frontend Architecture

Patterns for React/TypeScript dashboard codebases with runtime sections, charts, and polling.

## 1. Color Synchronization

**All chart colors live in `theme.ts`, never inline in components.**

Place color functions next to their peers:

```ts
// theme.ts — bid and playback colors together
export function bidStatusColor(status: string): string { ... }
export function playbackStatusColor(adType: string, kind: 'views' | 'error'): string { ... }
```

When a color appears in multiple places (e.g., error red in both Bid Runtime and Playback Runtime), use the same hex value everywhere. The source of truth is `theme.ts`.

## 2. Chart Components in `runtime/`

**Every chart component gets its own file under `components/runtime/`.**

Each chart is a standalone React component that imports:
- `LineChart` from `./LineChart` (the base chart renderer)
- Color functions from `../../styles/theme`
- Formatting/label utilities from `../../utils/...`

Chart components should NOT contain data-fetching logic or dashboard shell markup — they are pure presentational components that receive `timeline` data and render lines.

Example: `PlaybacksByStatusChart`, `AttemptsByStatusChart`.

## 3. Shared Filter Component

**Extract duplicated filter UI into a `<RuntimeFilters>` component with a `children` slot.**

Dashboard sections typically share:
- Period select (5m/15m/1h/.../custom)
- Custom datetime inputs (from/to) + live toggle
- Section-specific filter selects (ad_type, status)

The shared component renders the common shell and the section passes its specific selects via `children`:

```tsx
<RuntimeFilters range={...} onRangeChange={...} ...>
  <label>Тип рекламы
    <select ...>...</select>
  </label>
</RuntimeFilters>
```

The `onRangeChange` callback receives both the new range AND default customFrom/customTo values, so the parent doesn't need to compute them.

## 4. Shared Utilities

**Common helpers go in the most specific shared module.**

- `formatSeconds`, `formatPercent`, `toMinuteKey` → `utils/runtimeRange.ts` (alongside `buildMinuteKeys`, `resolveRangeBounds`)
- `POLL_INTERVAL_MS` → same file (single source of truth)
- Chart series labels/order → alongside type labels in the relevant utils (e.g., `PLAYBACK_CHART_SERIES_LABELS` in `adPlaybackStat.ts`)

## 5. API Contract: `counts_by_status`

**For mutually exclusive status lines, the API returns `counts_by_status: Record<string, number>`.**

When backend groups by multiple dimensions (e.g., `ad_type` + `status`), use composite keys: `"{ad_type}:{status}"`. This mirrors the simpler `counts_by_status` pattern from Bid Runtime where only one dimension exists.

```json
{
  "counts_by_status": {
    "linear_vast:finish": 42,
    "linear_vast:error": 3,
    "wrapper_vast:finish": 38
  }
}
```

On the frontend, split keys on `:` to recover ad_type and status for rendering.

## 6. Merged/Composite Lines

**When semantically related statuses should display as one line, merge on the frontend.**

e.g., `finish` + `interrupt` → "Views" (both count as shown ad). The backend keeps them separate; the chart component sums them:

```ts
kind === 'views'
  ? timeline.map(p => (p.counts[`${adType}:finish`] ?? 0) + (p.counts[`${adType}:interrupt`] ?? 0))
  : timeline.map(p => p.counts[`${adType}:error`] ?? 0)
```

## 7. Eliminating Section Duplication

**When two dashboard sections share the same boilerplate, extract in this order:**

1. Small utilities first (`formatSeconds`, `toMinuteKey`) — zero friction, high reuse
2. Shared UI components (`RuntimeFilters`) — eliminate ~80 lines of duplicated JSX per section
3. Chart components to `runtime/` — each chart becomes a standalone file
4. Generic hooks (`useRuntimeDashboard`) — LAST resort, only if the duplication is truly structural. Often the sections differ enough (API shape, filters, KPIs) that a generic hook adds more type gymnastics than it removes code.

## 8. Refactoring Workflow

1. Present the duplication analysis with line counts
2. Offer options via `clarify` — let the user choose scope
3. Create shared modules FIRST, then update consumers
4. Verify with `npx tsc --noEmit` after each step
5. Remove now-unused local code (helpers, types, components)

## 9. Campaign Detail Page: Tabs Layout (Runtime / Settings)

**When a detail page mixes runtime monitoring (watched constantly) with settings (configured once), use tabs to separate them. Runtime is the default tab; Settings is secondary.**

### Problem

Settings blocks (General, Bid, Shared settings, Bid settings, Playback settings) are configured once. Runtime charts (Bid Runtime, Playback Runtime) are monitored constantly. Stacking them in a single scroll forces the user to scroll past settings to reach runtime.

### Solution: Tab Bar

Two tabs below the entity header:
- **Runtime** (default) — `BidAttemptsSection` + `PlaybackRuntimeSection`, both expanded
- **Settings** — 5 `FormSection` blocks in `campaign-sections-grid` (2-col grid, read-only)

### Implementation

Tab bar styles (inline `CSSProperties`, matching `theme.ts` palette) — pill style, not underline:

```ts
const tabBarStyle: CSSProperties = {
  display: 'flex',
  gap: spacing.xs,
  marginBottom: spacing.sm,
}

function tabStyle(active: boolean): CSSProperties {
  return {
    padding: `${spacing.xs}px ${spacing.md}px`,
    border: 'none',
    borderRadius: radius.pill,
    background: active ? colors.text : 'transparent',
    color: active ? colors.surface : colors.textMuted,
    cursor: 'pointer',
    font: 'inherit',
    fontSize: fontSize.md,
    fontWeight: active ? weight.semibold : weight.regular,
    transition: `background ${transition}, color ${transition}`,
  }
}
```

**Pill tabs, not underline.** The original underline style (`borderBottom: 2px solid`) was replaced with pill-style tabs (`borderRadius: radius.pill`, filled background on active).

**Active tab uses `colors.text` (black) background + `colors.surface` (white) text.** This creates a high-contrast inverted pill — the user approved this in the pill-style iteration. (Note: an earlier underline-style iteration used `colors.hoverBg` for active — that was rejected as too subtle. The pill style with black fill was accepted.)

State + reset on entity switch:

```tsx
type CampaignTab = 'runtime' | 'settings'
const [activeTab, setActiveTab] = useState<CampaignTab>('runtime')

// Reset to Runtime when switching campaigns
function openCampaign(id: number) {
  // ...
  setActiveTab('runtime')
}
```

JSX structure:

```tsx
<div style={tabBarStyle} role="tablist">
  <button role="tab" aria-selected={activeTab === 'runtime'}
    style={tabStyle(activeTab === 'runtime')}
    onClick={() => setActiveTab('runtime')}>
    Runtime
  </button>
  <button role="tab" aria-selected={activeTab === 'settings'}
    style={tabStyle(activeTab === 'settings')}
    onClick={() => setActiveTab('settings')}>
    Settings
  </button>
</div>
{activeTab === 'runtime' ? (
  <div style={collapsibleSectionsStackStyle}>
    <BidAttemptsSection campaignId={selected.id} />
    <PlaybackRuntimeSection campaignId={selected.id} />
  </div>
) : (
  <div className="campaign-sections-grid">
    {/* General, Bid, Shared settings, Bid settings, Playback settings */}
  </div>
)}
```

```
┌───────────────────────────────────────────┐
│ Campaign Name    [▶ Запустить][⚙ Настройки][🗑] │
├───────────────────────────────────────────┤
│  [ Runtime ] [ Settings ]    ← pill tabs   │
├───────────────────────────────────────────┤
│  ▾ Bid Runtime          Автообновление: 5c  │  ← default tab
│    [filters][KPIs][charts]                  │
│  ▾ Playback Runtime    Автообновление: 5c  │
│    [filters][KPIs][charts]                  │
└───────────────────────────────────────────┘
```

### Rules

- **Runtime is the default tab.** Reset `activeTab` to `'runtime'` when switching campaigns or creating a new one.
- **⚙ Настройки button** switches to Settings tab AND enters edit mode: `setIsEditing(true); setActiveTab('settings')`.
- **Cancel edit** returns to view mode but stays on the current tab (doesn't force-switch to Runtime).
- **Runtime sections are VERTICALLY stacked** (Bid above Playback). Do NOT put them in a horizontal grid.
- **Settings tab uses the existing `campaign-sections-grid`** (2-col grid, collapses to 1-col at 1100px). No new CSS classes needed.
- **Editing mode renders above the tabs** — when `isEditing` is true, the edit form replaces the entire tab area (header + tabs + content).

### Sidebar: Always Visible, No Status Dot

The campaign list sidebar is always 300px wide with no collapse/expand button. The page uses a Flex layout (not Grid) to allow the main panel to grow with a `maxWidth` while keeping the sidebar adjacent to it — both centred as a group.

**No status dot next to campaign name.** The 8×8px coloured dot was removed per user request — "давай его уберем". List items show only the campaign name text.

```tsx
<div style={{ display: 'flex', gap: 16, alignItems: 'start', justifyContent: 'center' }}>
  <div style={{ flexShrink: 0, width: SIDEBAR_WIDTH }}>
    <section style={listSectionStyle}>
      {/* "+ Новая кампания" button + campaign list */}
    </section>
  </div>
  <section style={{ ...panelStyle, flex: '1 1 auto', maxWidth: 1400, minWidth: 0 }}>
    {/* tabs + content */}
  </section>
</div>
```

**Why `justifyContent: center` on the OUTER flex (not an inner wrapper):** Putting centring on the outer flex centres the sidebar+panel GROUP together. The sidebar stays glued to the panel's left edge. If you instead wrap only the panel in an inner `flex: 1 + justifyContent: center` div, the sidebar gets pushed to the viewport edge and the panel centres in the remaining space — they visually separate.

**Why Flex not Grid:** CSS Grid `1fr` caps the main panel at remaining-space-after-sidebar, so `maxWidth` never triggers and centring is impossible. Flex `flex: '1 1 auto'` + `maxWidth` lets the panel fill available space up to a cap. See the pitfall "CSS Grid `1fr` maxWidth illusion" in `core-coding-guidelines/references/frontend-pitfalls.md`.

**Why no inner flex wrapper:** The section is a direct child of the outer flex. `flex: '1 1 auto'` makes it grow to fill remaining space; `maxWidth: 1400` caps it on wide viewports; `minWidth: 0` prevents flex overflow. No wrapper needed — fewer DOM nodes, simpler mental model.

### Removing Collapsible Toggle Buttons

When blocks are always expanded (no collapse/expand needed), remove the toggle infrastructure entirely — not just the button. This includes:

1. **`CollapsibleSection` component** — remove `expanded`, `onExpandedChange`, `defaultExpanded` props, `useState`, and the toggle button. Keep `title`, `children`, `headerExtra`, `style` props.
2. **`FormSection` wrapper** — remove collapse props pass-through.
3. **Runtime sections** (`BidAttemptsSection`, `PlaybackRuntimeSection`) — remove `collapsible` prop, `expanded` state, conditional rendering. Always render via `CollapsibleSection`.
4. **Prefs types** (`BidRuntimePrefs`, `PlaybackRuntimePrefs`) — remove `expanded` field from type, `defaultXxxPrefs()`, and `mergeXxxPrefs()`.
5. **Orphan cleanup** — delete `useCampaignSectionsPrefs` hook, `CampaignDetailSection` type, `CampaignSectionsPrefs`, `getSectionExpanded`, `loadCampaignSectionsPrefs`, `saveCampaignSectionsPrefs`, `CAMPAIGN_DETAIL_SECTIONS`, `runtimeCollapsibleShellStyle`.

Use `sed` for batch removal of `{...sectionCollapseProps(...)}` spread props across 5+ call sites:
```bash
sed -i '' "s/ {...sectionCollapseProps(sectionsPrefs, '[^']*')}//g" src/pages/CampaignsPage.tsx
```

### Campaign Toolbar: Pill Buttons

The campaign actions toolbar (Запустить/Остановить/Настройки/Удалить) uses pill-style buttons, not a bordered toolbar container. The old bordered toolbar with grouped run-control buttons was replaced with standalone pill buttons:

```ts
// No toolbar container border/bg — just inline-flex with gap
const campaignToolbarStyle: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: spacing.xs,
  flexWrap: 'wrap',
}

// Run control: standalone pill buttons (no group border)
function runControlButtonStyle(kind: 'start' | 'stop', enabled: boolean): CSSProperties {
  return {
    borderRadius: radius.pill,
    background: enabled ? (isStart ? colors.success : colors.text) : colors.hoverBg,
    // ... no borderRight, no minWidth, no group border
  }
}

// Settings: pill with border
const toolbarUtilityButtonStyle: CSSProperties = {
  border: `1px solid ${colors.border}`,
  borderRadius: radius.pill,
  background: colors.surface,
}

// Delete: icon-only, danger color, transparent bg, pill shape
const toolbarDangerButtonStyle: CSSProperties = {
  ...toolbarUtilityButtonStyle,
  color: colors.danger,
  borderColor: 'transparent',
  background: 'transparent',
}
```

**Delete button is icon-only** — `<TrashIcon />` with `aria-label="Удалить кампанию"`, no visible text. Title attribute provides hover tooltip. The `data-run-control` CSS rules in `index.css` were removed (no longer needed without grouped border).

**Delete button uses transparent background and border** — `borderColor: 'transparent'`, `background: 'transparent'`. It's a bare danger-colored icon in pill shape. It does NOT have a visible red border (an earlier version added `borderColor: colors.danger` but the user preferred the cleaner transparent look).

**All toolbar buttons use `height: controlHeight` (34px).** This ensures the icon-only Delete button matches the height of text buttons (Запустить, Остановить, Настройки). Use `padding: \`0 ${spacing.sm}px\`` with `height: controlHeight` — NOT padding-based height which varies by content.

### Chart Grid: `minmax(360px, 1fr)` for Two Charts Per Row

Charts within each runtime section use `runtimeChartGridStyle` (`repeat(auto-fit, minmax(360px, 1fr))`). At 360px minimum, two charts fit side-by-side at ~736px container width. Gap between charts is `spacing.md` (16px) for breathing room. This value is set in `styles/runtimeDashboard.ts` and applies globally.

### Chart Line Rendering: `null` Means Zero, Not Gap

**When data contains `null` (no measurement for a minute bucket), the chart line drops to zero — it does NOT break.** Missing data is visually a flat baseline at 0, not a gap in the line.

This is implemented in `buildSmoothPath` (`utils/runtimeChartPath.ts`):

```ts
// null → 0, no gaps — continuous line
const coords: Point[] = points.map((value, index) => ({
  x: index * stepX,
  y: toY(value ?? 0),
}))
return buildRunPath(coords, stepX)
```

**Before (gap-based):** `null` split the data into separate "runs" (contiguous non-null segments), each rendered as an independent SVG path. The line visually disappeared at `null` points.

**After (zero-based):** All points are rendered as a single continuous path. `null` is replaced with `0` via `value ?? 0`. The line drops to the baseline and rises back when data resumes.

**Tooltip also shows `0`** for `null` values, not `—` (em-dash):
```tsx
const value = item.values[hoverIndex] ?? 0
const formatted = (item.formatValue ?? ((v: number) => v.toFixed(2)))(value)
```

This applies to all charts using `LineChart`: Win rate, Response time, Playback duration, Playback delay, AttemptsByStatus, PlaybacksByStatus. Chart components that build `values` arrays with `?? 0` (AttemptsByStatusChart, PlaybacksByStatusChart) are unaffected — only components passing `null` in `values` (Win rate timeline, Response time timeline, Playback duration/delay timelines) are affected by this rendering change.

**Do NOT use `hasData={false}` + `emptyMessage` to show a text placeholder.** When a chart has no measurements (all `null` values), it should still render a zero-line graph — not an `EmptyChartMessage` text block. The `ChartCard` component has a `hasData` prop that, when `false`, empties the `values` array and triggers `LineChart`'s `hasSourceData=false` path, rendering text instead of a graph. This creates visual inconsistency: some charts show zero-lines (Win rate, Playback duration), others show text ("Нет замеров…").

**Fix:** Remove `hasData` and `emptyMessage` props from the `ChartCard` call. Pass the series with `null` values directly — `LineChart` treats `null` as `0` and draws a flat baseline. The footer shows `formatValue(0)`. Remove the `hasResponseTimeData` useMemo if it becomes unused.

```tsx
// ❌ Text placeholder — inconsistent with other charts that show zero-lines
<ChartCard
  title="Время ответа bid по минутам"
  series={responseTimeTimeline}
  hasData={hasResponseTimeData}
  emptyMessage="Нет замеров времени ответа за выбранный период"
/>

// ✅ Zero-line graph — same behavior as Win rate, Playback duration, etc.
<ChartCard
  title="Время ответа bid по минутам"
  series={responseTimeTimeline}
  // hasData defaults to true, null values render as zero baseline
/>
```

**Rule:** All `LineChart`-based charts render a zero baseline when data is null/empty. No chart should show a text-only empty state. The only component that shows text for empty data is `CountBars` (ErrorBars, interrupt bars) — and the empty state renders at natural height (no `minHeight`), so the card shrinks when there's no data.

### CountBars Empty State: Natural Height (No `minHeight`)

**When `CountBars` (and its wrapper `ErrorBars`) has no rows (`rows.length === 0`), the empty message renders WITHOUT a `minHeight` wrapper. The card shrinks to fit just the `ChartTitle` + `EmptyChartMessage` text.** This is the user's explicit preference — blocks that have no data should be visually smaller, and grow when data arrives.

```tsx
// CountBars.tsx — correct: no minHeight, natural height
{!rows.length ? (
  <EmptyChartMessage>{emptyMessage}</EmptyChartMessage>
) : (
  // ... bars ...
)}
```

**Do NOT add `minHeight: 200` or any fixed-height wrapper.** An earlier version of this rule added `minHeight: 200` to match chart card heights — the user explicitly rejected this and asked to revert: "вернем как было — если ошибок или прерываний нет, то блок уменьшается в высоте". The visual height difference between empty and data-filled states is intentional and expected.

### Pitfalls

**"2 графика в ряд" means within a section, NOT sections side-by-side.** When the user says charts should be side-by-side, they mean two charts INSIDE one runtime section (e.g., "Bid attempts по статусам" next to "Win rate по минутам"), NOT two sections (Bid Runtime + Playback Runtime) side by side. Sections remain vertically stacked. The fix is through `runtimeChartGridStyle`'s `auto-fit` + the `minmax` value — not through restructuring the section containers.

**Vite white screen after file moves/structural changes.** `tsc` + `vite build` may pass but dev server shows blank. Fix: `pkill -f vite && npm run dev`. If the user reports white screen but your dev server renders fine, check if they're using a Docker-proxied port (e.g., 5173 via `lowbid_frontend` container) — restart the container with `docker compose restart frontend`. See `core-coding-guidelines/references/frontend-pitfalls.md` for full detection steps.

**Docker HMR does not pick up host file changes reliably.** When running Vite inside Docker with volume mounts (`./frontend:/app`), HMR sometimes fails to detect file changes made from the host machine. The dev server stays running but serves stale code. `docker compose restart frontend` forces a fresh Vite startup that reads the current files. This is especially common after batch `sed` operations or when many files change at once. If the user reports visual issues but your headless browser renders correctly, restart their Docker container before debugging further.

**Nested section duplication: `CollapsibleSection` wrapping content with its own shell.** When a runtime section (`BidAttemptsSection`, `PlaybackRuntimeSection`) renders content inside a `<div style={shellStyle}>` (border + padding + background + `<h4>` title + `refreshStatus`), and that content is then wrapped in `<CollapsibleSection title="Bid Runtime" headerExtra={refreshStatus}>`, the result is a box-within-a-box with duplicated title and status text. Fix: remove the inner `shellStyle` div and the duplicated `<h4>`/`refreshStatus` — keep only a plain `<div style={{ display: 'grid', gap: 14 }}>` for vertical spacing. The `CollapsibleSection` already provides border, title, and `headerExtra`. This pattern arises when a component originally had both a standalone mode (with its own shell) and a collapsible mode (wrapped in `CollapsibleSection`) — after removing the standalone mode, the inner shell becomes redundant.

**Stale browser snapshot after state updates.** After clicking a button that triggers React state changes (e.g., entering/exiting edit mode), `browser_snapshot` may return stale content that doesn't reflect the new state. To verify the actual DOM state, evaluate via `browser_console` with an expression like `document.querySelector('h3')?.textContent` instead of trusting the snapshot.

**CSS Grid `1fr` cannot exceed available space — use Flex for fixed-width panels with centring.** When converting a grid layout (`gridTemplateColumns: '300px 1fr'`) where the main panel needs a specific width wider than `1fr` allows, `maxWidth` on a grid child does NOT work — `1fr` always shrinks to fit the remaining space, so `maxWidth` never triggers. The grid child is capped at `1fr` width regardless of `maxWidth`.

**Symptom:** You set `maxWidth: 'calc(100vw - 68px)'` on the main panel, but `getBoundingClientRect().width` shows the panel at `1fr` width (e.g., 916px), not the expected wider value. Centring (`justifyContent: 'center'`) has no visible effect because the panel fills the entire `1fr` column.

**Root cause:** CSS Grid `1fr` = `available space after fixed tracks`. When sidebar is 300px and viewport is 1280px, `1fr` = `1280 - 300 - 16 - padding ≈ 916px`. No `maxWidth` on the child can exceed this — the grid track itself is the constraint.

**Fix:** Switch from Grid to Flex layout. Put `justifyContent: 'center'` on the OUTER flex to centre sidebar+panel as a group:

```tsx
// ❌ Does NOT work — 1fr caps the panel, maxWidth never triggers
<div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 16 }}>
  <div>{sidebar}</div>
  <div style={{ display: 'flex', justifyContent: 'center' }}>
    <section style={{ maxWidth: 'calc(100vw - 68px)' }}>...</section>
  </div>
</div>

// ❌ Also does NOT work — inner wrapper centres only the panel,
// sidebar gets pushed to viewport edge, visually separates from panel
<div style={{ display: 'flex', gap: 16, alignItems: 'start' }}>
  <div style={{ flexShrink: 0, width: SIDEBAR_WIDTH }}>{sidebar}</div>
  <div style={{ flex: 1, display: 'flex', justifyContent: 'center', minWidth: 0 }}>
    <section style={{ width: '100%', maxWidth: 1200 }}>...</section>
  </div>
</div>

// ✅ Works — justifyContent on outer flex centres sidebar+panel as a group
<div style={{ display: 'flex', gap: 16, alignItems: 'start', justifyContent: 'center' }}>
  <div style={{ flexShrink: 0, width: SIDEBAR_WIDTH }}>{sidebar}</div>
  <section style={{ ...panelStyle, flex: '1 1 auto', maxWidth: 1400, minWidth: 0 }}>
    {/* content */}
  </section>
</div>
```

**Key points:**
- `justifyContent: 'center'` on the OUTER flex — centres the sidebar+panel group together (sidebar stays adjacent to panel)
- Sidebar: `flexShrink: 0` + fixed `width` — prevents shrinking
- Main panel: `flex: '1 1 auto'` + `maxWidth` + `minWidth: 0` — grows to fill, caps on wide screens, prevents overflow
- Use a fixed `maxWidth` (e.g., `1400`) rather than `calc(100vw - Npx)` — viewport-relative calcs don't account for App-level padding
- No inner flex wrapper needed — section is a direct child of the outer flex

**App-level `maxWidth` interaction.** If the App container has `maxWidth: 1480` and you need the main panel wider than what's available after sidebar, removing App's `maxWidth` lets the flex layout use the full viewport. This affects ALL pages — confirm with the user before removing it.

## 10. Design Token System

**All visual constants (radius, spacing, shadow, colors, control heights) live as named tokens in `theme.ts`. Components import tokens, never hardcode values.**

### Token categories

```ts
// theme.ts
export const colors = {
  text: '#111111',
  textMuted: '#595959',  // was #666666 — bumped for WCAG 7:1 contrast
  surface: '#ffffff',
  border: '#e5e5e5',
  borderStrong: '#111111',
  pageBg: '#f7f7f5',
  hoverBg: '#f5f5f3',
  tableHeaderBg: '#f7f7f5',
  tableRowSelected: '#ebebe8',
  activeBg: '#eeeeee',
  danger: '#b91c1c',
  success: '#15803d',
  warning: '#ea580c',
  dangerBright: '#dc2626',
  info: '#2563eb',
  chartTrack: '#f3f3f3',
  tooltipBg: '#111111',
  tooltipText: '#ffffff',
} as const

export const radius = {
  sm: 10,    // ALL elements — inputs, buttons, selects, cards, sections, chart boxes, panels
  pill: 999, // tabs, run control buttons, settings button, delete button, legend buttons, mood badges
} as const
// radius.md (10) was removed — merged into sm.
// radius.sm was bumped from 8 to 10 for a more rounded, friendly feel across the entire UI.
export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
} as const

export const shadow = {
  tooltip: '0 2px 8px rgba(0, 0, 0, 0.12)',
} as const
// shadow.card was removed — cards use border-only (1px solid), no shadow.
// This is the minimalist approach: border-only is cleaner than border+shadow.

export const controlHeight = 34

export const fontSize = {
  xs: 12,   // captions, descriptions, axis labels, card titles, legend, tooltip
  md: 14,   // UI text: buttons, form labels, table, section titles, tabs, nav, h1
  lg: 22,   // page titles (h1, h2), metric card values
  xl: 28,   // hero card values
} as const

export const weight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const
```

**Semantic colors** (`danger`, `success`, `warning`, `dangerBright`, `info`) replace all hardcoded hex values in status color functions, error text, and chart gradients. `chartTrack` is the background of empty bar tracks. `tooltipBg`/`tooltipText` are for the LineChart hover tooltip.

**All hardcoded hex values are eliminated from `.tsx` files.** Verify with:
```bash
grep -rn '#[0-9a-f]\{6\}' src/ --include='*.tsx'  # should be 0
```

**`spacing.xxs: 4`** is used for tight gaps in filter field labels and datetime fields. **`spacing.lg: 24`** replaces the old `padding: '1.5rem'` in App.tsx (the only rem in the project, now converted to px).

### Font token mapping

| Token | px | Usage |
|---|---|---|
| `fontSize.xs` | 12 | descriptions, axis labels, card titles, legend, tooltip, filter field labels, estimate text |
| `fontSize.md` | 14 | buttons, form labels, table, filter selects, section titles, tabs, nav links, App h1, CollapsibleSection title, metric inline values |
| `fontSize.lg` | 22 | App h1 brand, page titles (h2), campaign detail name (h3), metric card values (MetricCard, Win/No bid/Error) | | 28 | hero card values (MoneyPowerGlory) |

**4 sizes, not 5.** `fontSize.sm (13)` was removed — the 1px difference between 12 and 13 was not visually distinguishable and created inconsistent usage. All former `sm` uses were reclassified: UI text (buttons, labels, table) → `md`, metadata (descriptions, estimates) → `xs`.

| Weight token | Numeric | Usage |
|---|---|---|
| `weight.regular` | 400 | body text, inactive tabs/nav |
| `weight.medium` | 500 | secondary/ghost buttons |
| `weight.semibold` | 600 | primary buttons, table headers, active tabs/nav, detail labels |
| `weight.bold` | 700 | section titles (CollapsibleSection, ChartTitle), metric values, App h1 |

**Minimum font size is 12px (`fontSize.xs`).** The old `fontSize: 10` on InfoTooltip was bumped to `fontSize.xs`. Never use sizes below 12px.

**`fontSize: 'inherit'` is prohibited.** CollapsibleSection previously used `fontSize: 'inherit'` on its `<h4>` — this caused the title to inherit the parent's font size, which was unpredictable. Always set an explicit token.

**Root `font-size: 16px` inheritance on `<p>` elements.** The `:root` CSS sets `font-size: 16px` (browser default for `system-ui`). When a `<p>` element has no explicit `fontSize` in its style, it inherits 16px — even if its CHILD elements (label, span) have `fontSize: fontSize.md` (14px) set explicitly. This creates a visual mismatch: section titles at 14px appear SMALLER than the detail rows beneath them at 16px.

**Symptom:** In the Settings tab, "General" (section title, 14px bold) looks the same size or smaller than "ID:", "Статус:", "Создана:" (detail rows, 16px inherited). The hierarchy is inverted.

**Root cause:** `detailLabelStyle` and `detailValueStyle` set `fontSize: fontSize.md` on the `<span>` and `<label>` children, but the wrapping `<p>` itself has no `fontSize` — it inherits 16px from `:root`. The `<p>`'s `line-height` also inherits `1.5` from `:root`, making each row ~24px tall (16 × 1.5), which feels too spacious.

**Fix:** Set `fontSize: fontSize.md` AND `lineHeight: 1.4` on the `<p>` itself, not just on its children:

```tsx
// ❌ Children have fontSize, but <p> inherits 16px from :root
<p style={{ marginBottom: spacing.xs }}>
  <FieldLabel style={{ ...detailLabelStyle, fontSize: fontSize.md }}>ID:</FieldLabel>
  <span style={{ ...detailValueStyle, fontSize: fontSize.md }}>1</span>
</p>
// Result: <p> is 16px, children are 14px, line-height is 1.5 → tall rows, inverted hierarchy

// ✅ <p> itself has fontSize + lineHeight — controls the box, not just children
<p style={{ margin: 0, marginBottom: spacing.xxs, fontSize: fontSize.md, lineHeight: 1.4 }}>
  <FieldLabel style={detailLabelStyle}>ID:</FieldLabel>
  <span style={detailValueStyle}>1</span>
</p>
// Result: <p> is 14px, lineHeight 1.4 → ~20px rows, section title (14px bold) > row text (14px regular)
```

**General rule:** When a container element (`<p>`, `<div>`) wraps text-bearing children, always set `fontSize` and `lineHeight` on the CONTAINER — not just on the children. The container's inherited values affect `line-height` calculations and visual row height, even when children override `font-size`.

**Visual hierarchy with same font size:** When section title and detail rows both use `fontSize.md` (14px), differentiation comes from font-weight:
- Section title: `weight.bold` (700)
- Detail label: `weight.regular` (400) + `mutedTextStyle` (grey color)
- Detail value: `weight.semibold` (600) + `colors.text` (dark)

This is sufficient — no separate font size needed for the title to stand out.

**4 font sizes only — no `fontSize.sm`.** The token system uses exactly 4 sizes: `xs (12)`, `md (14)`, `lg (22)`, `xl (28)`. The previous `sm (13)` was removed because 1px difference from `xs (12)` was not visually meaningful and caused inconsistent usage. When classifying text:
- **UI text** (buttons, form labels, table cells, section titles, nav, badges, metric inline values) → `fontSize.md`
- **Metadata** (descriptions, axis labels, card titles, legend, tooltip, filter labels, estimate text) → `fontSize.xs`

### Replacing hardcoded font values

When refactoring an existing codebase to use font tokens:

1. Add `fontSize` and `weight` tokens to `theme.ts`
2. Use `sed` for batch replacement of identical patterns:
```bash
# Replace common patterns in one pass
sed -i '' \
  -e 's/fontSize: 13/fontSize: fontSize.sm/g' \
  -e 's/fontSize: 14/fontSize: fontSize.md/g' \
  -e 's/fontWeight: 600/fontWeight: weight.semibold/g' \
  -e 's/fontWeight: 400/fontWeight: weight.regular/g' \
  src/pages/CampaignsPage.tsx
```
3. Handle inline JSX styles separately (e.g., `fontWeight: active ? 600 : 400` → `fontWeight: active ? weight.semibold : weight.regular`)
4. Add `fontSize`/`weight` to the import from `../styles/theme` in each modified file
5. **Verify zero hardcoded values remain:**
```bash
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]' src/ | wc -l
# Must output 0
```

### Button system: 3 levels, used everywhere

Instead of ad-hoc button styles per component, use `buttonStyle(level)`:

```ts
export type ButtonLevel = 'primary' | 'secondary' | 'ghost'

export function buttonStyle(level: ButtonLevel): CSSProperties { ... }
```

| Level | Style | When |
|---|---|---|
| Primary | Solid `#111` bg, white text | Main action (Save, Start, Submit) |
| Secondary | `#fff` bg, `1px solid #e5e5e5` | Secondary (Settings, Cancel, Reset, sidebar create) |
| Ghost | Transparent, text color | Tertiary (Edit, Delete in tables, tabs) |

**`SubmitButton` component** renders `buttonStyle('primary')` internally — no more CSS default `<button>` styling. All form submit buttons across the app get consistent height, radius, and transition.

**Table action buttons** (Edit, Delete, Cancel, Reset) in `BidEndpointsPage`, `BidRequestTemplatesPage`, `PlaybackEventConfigsPanel`, and `CampaignsPage` all use `buttonStyle('secondary')` or `buttonStyle('ghost')`. Delete buttons in tables add `color: colors.danger` override on top of `buttonStyle('ghost')`.

**Never use a bare `<button>` without a `buttonStyle()` call** — the CSS default `button` style in `index.css` is a fallback only, not the intended visual. Every interactive button should explicitly set its style via `buttonStyle()` or a dedicated style object that references the same tokens.

### Navigation: underline links, no header border

Nav links use `navLinkStyle` with `borderBottom` (2px solid for active, transparent for inactive) — an underline pattern for the top-level app navigation. The campaign detail tabs use pill style (`borderRadius: radius.pill`, filled `colors.text` on active) which is visually consistent with the pill buttons in the campaign toolbar.

**App header has NO `borderBottom`.** The full-width underline under the nav toolbar (Campaigns, Money Power Glory, Bid endpoints, Bid request templates) was removed per user request — "давай уберем". The header is just `display: flex` + `gap` + `marginBottom`, no border, no padding-bottom. Individual nav links still have their own per-link underline (active/inactive via `navLinkStyle`).

### Focus states

Single CSS rule in `index.css`, not per-component:

```css
:focus-visible {
  outline: 2px solid var(--color-text);
  outline-offset: 2px;
}
```

`outline-offset: 2px` (was 1px) gives the focus ring breathing room without overlapping the element's border.

### Sidebar: pill-style list items, no border

`listItemButtonStyle` uses `borderRadius: radius.pill`, `border: 'none'`, `background: active ? colors.tableRowSelected : 'transparent'`. No border at all — active state is conveyed by soft grey background only. Transition on `background` for smooth hover/active changes. **Horizontal padding is `spacing.sm` (12px), not `spacing.xs` (8px)** — pill-shaped buttons need more horizontal padding so text doesn't sit too close to the rounded edge. Use `padding: \`${spacing.xs}px ${spacing.sm}px\`` (8px vertical, 12px horizontal).

`sidebarCreateButtonStyle` reuses `buttonStyle('secondary')` with `width: '100%'` and `justifyContent: 'center'` — not a custom style with hardcoded `height: 32`. This ensures consistent height (`controlHeight`), radius, and transition with all other buttons in the project.

### `cardStyle` — shared base for all card-like containers

**A single `cardStyle` base in `theme.ts` provides `border + borderRadius + background + padding`. All card-like style objects extend it via `...cardStyle` — never re-declare these 4 properties.**

```ts
// theme.ts
export const cardStyle: CSSProperties = {
  border: `1px solid ${colors.border}`,
  borderRadius: radius.sm,
  background: colors.surface,
  padding: spacing.sm,
}
```

6 style objects extend `cardStyle`:

| Style | File | Extra properties |
|---|---|---|
| `runtimeCardStyle` | runtimeDashboard.ts | `minHeight: 64` |
| `runtimeChartBoxStyle` | runtimeDashboard.ts | `position, display, flexDirection, height, minWidth, boxSizing` |
| `runtimeSectionStyle` | runtimeDashboard.ts | `display: grid, gap` |
| `runtimeCustomRangePanelStyle` | runtimeDashboard.ts | `display: flex, flexWrap, gap, alignItems` |
| `panelStyle` | CampaignsPage.tsx | (none — just `...cardStyle`) |
| `sectionStyle` | CollapsibleSection.tsx | `margin: 0, overflow: 'visible'` |

**Before `cardStyle`**, each of these 6 objects independently declared `border`, `borderRadius`, `background`, and `padding` — ~24 lines of duplicated code. When `radius.sm` changed from 8→10, all 6 needed updating. Now: change `cardStyle` once.

**When to add `...cardStyle`:** Any new style object that renders a visible card/container with border + background. If it only needs layout (no border), don't use `cardStyle` — use a plain layout object (like `runtimeShellStyle: { display: 'grid', gap: spacing.md }`).

### Rules

- **All colors — including chart colors — use `colors.*` tokens.** Chart status color functions (`bidStatusColor`, `playbackStatusColor`, `campaignStatusColor`) reference `colors.success`, `colors.danger`, `colors.dangerBright`, `colors.warning`, `colors.info`. Chart gradients (e.g., `ErrorBars`) use `colors.danger` via template literal. No hardcoded hex in any `.tsx` file.
- **Reuse existing tokens — don't create new ones for every magic number.** The user's philosophy: "чем меньше у нас разных переменных — тем лучше". Before adding a new token, check if an existing one fits. For example, `controlHeight` (34) already exists — use it for any 34px height, don't create `sidebarButtonHeight`. Semantic widths (`maxWidth: 1400` for layout, `maxWidth: 980` for textarea, `width: 360` for form inputs) are NOT tokens — they're component-specific constraints that vary by context.
- **`runtimeDashboard.ts` imports tokens** — all `borderRadius`, `border`, `background`, `gap` values reference `radius`, `colors`, `spacing`, `shadow` from `theme.ts`.
- **`runtimeSelectStyle`** — extends `runtimeControlInputStyle` with custom padding. Shared style constant for `<select>` elements in runtime filter sections. Prevents triplicated inline `padding/borderRadius/border/background` styles.
  ```ts
  export const runtimeSelectStyle: CSSProperties = {
    ...runtimeControlInputStyle,
    padding: `${spacing.xs}px ${spacing.sm}px`,
  }
  ```
- **`runtimeShellStyle` simplified** — no border, no background, no border-radius, no padding. Just `display: grid, gap: spacing.md`. The shell is a layout container only; visual styling (border, bg) lives on the child `CollapsibleSection` cards. This prevents double-border when sections have their own border.
- **All card-style elements use `padding: spacing.sm` (12px).** This includes `runtimeCardStyle`, `runtimeChartBoxStyle`, `CollapsibleSection.sectionStyle`, and `panelStyle`. An earlier version had `runtimeCardStyle` and `runtimeChartBoxStyle` at `spacing.xs` (8px) — inconsistent with the other cards. The user noticed the chart/metric cards looked tighter than surrounding panels. Always use `spacing.sm` for card padding — never `spacing.xs`.
- **Metric card `minHeight` was reduced from 78 to 64px.** The user asked to "чуть уменьшим высоту карточек" — compact metric cards are preferred. If the user asks to adjust card height again, change `runtimeCardStyle.minHeight` only — it's the single source.
- **`formTextInputStyle`, `formNumberInputStyle`, `formRowStyle`** — shared form styles in `theme.ts`, imported by CampaignsPage, BidEndpointsPage, BidRequestTemplatesPage. Eliminates `FORM_TEXT_INPUT_STYLE` / `FORM_ROW_STYLE` duplication across 3 files.
- **Campaign header** — `campaignHeaderStyle` includes `borderBottom: 1px solid + paddingBottom: spacing.sm` to visually separate header (name + toolbar) from tabs/content below.
- **SVG colors** — LineChart uses `colors.surface` (was `#fbfbfb`) for chart background and `colors.textMuted` (was `#5f6368`) for hover line. No hardcoded hex in SVG attributes.
- **`index.css` hardcodes token values** (CSS can't import TS), but must match `theme.ts` exactly. Comment each section.
- **When adding a new component**, grep for hardcoded values:
```bash
grep -rn 'fontSize: [0-9]\|fontWeight: [0-9]\|borderRadius: [0-9]\|boxShadow: .0\|#[0-9a-f]\{6\}' src/ --include='*.tsx'
# All should output 0 lines
```
- **Error text colour** is `colors.danger` (`#b91c1c`) — errors should be visually distinct, not just bold.
- **`sed` cannot produce template literals inside single-quoted strings in `.ts` style files.** When replacing `margin: '6px 0 0 0'` with `margin: '${spacing.xs}px 0 0 0'` via sed, the result is a literal string `'${spacing.xs}px 0 0 0'` — single quotes prevent JS interpolation. The fix is to replace `margin: 'Npx ...'` with `marginTop: spacing.xs` (or appropriate direction) via `patch`, not sed. In `.ts` style files (`runtimeDashboard.ts`), `margin: '6px 0 0 0'` → `marginTop: spacing.xs`. In `.tsx` inline JSX styles, same approach — use `marginTop`/`marginBottom` tokens instead of string margins.

### Font consistency rules

**All metadata text in runtime sections uses `fontSize.xs` + `mutedTextStyle`.** This includes:
- Section descriptions ("Bid attempts кампании в реальном времени")
- `refreshStatus` ("Автообновление: 5 c · обновлено: 00:39:11")
- Filter field labels ("Период", "Статус", "Тип рекламы")

**`mutedTextStyle` alone does NOT set a font size.** It only sets `color: colors.textMuted`. Without an explicit `fontSize`, the element inherits the root font size (16px from `:root`), which is larger than the section description (12px). Always pair `mutedTextStyle` with `fontSize: fontSize.xs` for metadata:

```tsx
// ❌ refreshStatus inherits 16px from :root — visually larger than the description
const refreshStatus = <span style={mutedTextStyle}>Автообновление: 5 c</span>

// ✅ explicit fontSize.xs — matches description and other metadata
const refreshStatus = <span style={{ ...mutedTextStyle, fontSize: fontSize.xs }}>Автообновление: 5 c</span>
```

**Filter labels passed as `children` to `RuntimeFilters` must use `filterFieldStyle`**, not ad-hoc inline styles. The "Период" label inside `RuntimeFilters` already uses `filterFieldStyle` (`fontSize.xs`, `color: textMuted`, `display: grid`, `gap: 4`, `flex: '0 1 180px'`). When a section passes its own filter (e.g., "Статус" select) as children, it must use the same style object — not a different inline `fontSize.sm` with `display: flex`. This ensures visual consistency: same size, same color, same layout behavior.

```tsx
// ❌ Inline style — different size (13px vs 12px), different color, different layout
<RuntimeFilters ...>
  <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: fontSize.sm }}>
    Статус <select ...>...</select>
  </label>
</RuntimeFilters>

// ✅ filterFieldStyle — matches "Период" label exactly
import { runtimeFilterFieldStyle as filterFieldStyle } from '../styles/runtimeDashboard'
<RuntimeFilters ...>
  <label style={filterFieldStyle}>
    Статус <select ...>...</select>
  </label>
</RuntimeFilters>
```

### CSS variables in index.css — mirror theme.ts

**`index.css` defines CSS custom properties in `:root` that mirror `theme.ts` token values. All CSS rules use `var(--...)` instead of hardcoded hex/px.** This is the only place hex values appear in CSS — they are variable definitions, not hardcodes.

```css
:root {
  --color-text: #111111;
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

button {
  color: var(--color-text);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 6px var(--spacing-sm);
  transition: background var(--transition);
}
```

When adding a new token to `theme.ts`, add the corresponding `--var` in `:root` and use it throughout CSS. Keep values in sync manually (CSS can't import TS).

### Transition token — smooth interactions

**`transition = '0.15s ease'` in `theme.ts`, applied to all interactive elements.**

In `theme.ts`, add `transition` to `buttonStyle` (all 3 levels), `navLinkStyle`, `listItemButtonStyle`:
```ts
export const transition = '0.15s ease'

// buttonStyle primary
transition: `background ${transition}, color ${transition}`,

// navLinkStyle
transition: `color ${transition}, border-color ${transition}`,

// listItemButtonStyle
transition: `background ${transition}, border-color ${transition}`,
```

In `index.css`, CSS `button` uses `transition: background var(--transition)`.

### Heading hierarchy — token-based

| Tag | `fontSize` | `weight` | Usage |
|---|---|---|---|
| `h1` | `fontSize.lg` (22) | `weight.bold` (700) | App brand/title |
| `h2` | `fontSize.lg` (22) | `weight.bold` (700) | Page titles (MoneyPowerGlory, BidEndpoints, BidRequestTemplates) |
| `h3` | `fontSize.lg` (22) | `weight.bold` (700) | Campaign detail name (matches page h2 size) |
| `h3` | `fontSize.md` (14) | `weight.semibold` (600) | Section titles (Campaign create/edit, runtime section headers) |
| `h4` | `fontSize.md` (14) | `weight.bold` (700) | Card titles (CollapsibleSection) |

**Campaign detail name matches page title size.** The user requested: "размер названия кампании слишком мелкий, давай будет такой же как названия вкладок на других вкладках". The campaign name `<h3>` uses `fontSize.lg` (22px) + `weight.bold` — same as `<h2>` on Money Power Glory, Bid endpoints, Bid request templates pages.

### Pitfalls

**`maxHeight` magic numbers on scrollable lists.** `listSectionStyle` had `maxHeight: 560` — a magic number unrelated to viewport size. Remove it; `overflowY: 'auto'` + flex layout handles scrolling naturally. The list grows to fill available space without an arbitrary cap.

**App header `borderBottom` was removed entirely.** The header previously had `borderBottom: '1px solid #e5e5e5'` + `paddingBottom: spacing.sm` — a full-width underline under the nav toolbar. The user asked to remove it: "под тулбаром сверху есть подчеркивание на всю ширину страницы — давай уберем". Now the header has no border and no padding-bottom. Also remove `colors` from the App.tsx import if it becomes unused after removing the border.

### Design token rollout

See `references/design-token-rollout-checklist.md` for the step-by-step checklist used to migrate an entire React dashboard from hardcoded values to a complete design token system (colors, spacing, shadow, radius, fontSize, fontWeight, gap, lineHeight, select styles, CSS variables, transitions, heading hierarchy, pill-style tabs/toolbar, border-only cards, unified radius).

## 11. Vitest / Playwright test setup (FSD monorepo)

For an FSD npm-workspaces frontend (public/cabinet/admin + shared packages) the test pyramid is:

- **Unit (Vitest):** per-app `defineProject` workspace, aliases, colocated `*.test.ts` in `lib/`. See `references/vitest-monorepo-setup.md`.
- **E2E (Playwright):** per-app projects with `baseURL`, isolated via `context.clearCookies()` in a shared `helpers/base.ts` (outside `testDir`). The session's hardest lesson — clearing `localStorage`/`sessionStorage` on `about:blank`/`data:` URLs throws `SecurityError`; clear them only AFTER navigating to the app. Full working pattern + pitfalls: `references/vitest-monorepo-setup.md` → "Playwright E2E isolation".

## 12. Standalone preview apps (design prototypes)

When the user asks for a visual prototype/mock of a dashboard or ЛК section WITHOUT touching the main apps, use the standalone preview-app pattern: `frontend/previews/<hash>/` (own Vite+React package, `base: '/<hash>/'`), a row in `frontend/previews/REGISTRY.md`, nginx + CI + deploy.sh entries copied 1:1 from the sibling preview branch — and branch from that sibling branch in a worktree (it carries the infra), not main. Full pattern, infra file shapes, verification checklist (incl. the ru-RU NBSP-in-Intl test pitfall and the headless design audit): `references/standalone-preview-apps.md`.
