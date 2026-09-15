# FSD audit + Vitest for dlgrv

This repo is FSD (`app → pages → widgets → features → entities → shared`). A layer may
only import layers to its RIGHT (more abstract → less abstract). `widgets` must NOT import
`features`. This reference records the one real violation we found and how we fixed it,
plus the Vitest setup added this session.

## The FSD violation (found via import scan)

`src/widgets/window-manager/index.ts` imported:
- `renderWindowContent, onLanguageChange` from `@/features/open-window/content`
- `controlWindow` from `@/features/window-controls` (via `Window.ts`)

That breaks FSD. Symptom-check script (run from `src`): scan every `.ts` for `from '@/<layer>'`
and flag `widgets→features`, `shared→(non-shared)`, `entities→(app|pages|widgets|features)`.

## The fix: dependency injection from `app`

`widgets/window-manager` exposes a `WindowManagerDeps` interface and takes it as a param
instead of importing features directly.

```ts
// src/widgets/window-manager/index.ts
export interface WindowManagerDeps {
  renderContent: (id: string) => HTMLElement;
  control: (id: string, action: 'close' | 'minimize' | 'maximize') => void;
}

// openWindow accepts optional deps; if omitted, uses the module-level activeDeps
// (set earlier by restoreWindows/openDefaultLayout). This lets Desktop.ts keep
// calling openWindow(app) on icon click without threading deps through pages→desktop.
export function openWindow(app: AppInfo, deps?: WindowManagerDeps): void {
  if (deps) activeDeps = deps;
  const dep = activeDeps;
  if (!dep) return;
  // ...use dep.renderContent(app.id) and dep.control(app.id, a)
}

export function restoreWindows(deps: WindowManagerDeps): void {
  activeDeps = deps;
  const saved = getOpenStates();
  if (saved.length === 0) { openDefaultLayout(deps); return; }
  // ...createWindow with renderContent/control from deps
}

export function openDefaultLayout(deps: WindowManagerDeps): void { /* same pattern */ }
```

`app/index.ts` composes the deps and passes them:
```ts
import { renderWindowContent } from '@/features/open-window/content';
import { profile } from '@/entities/profile';
const windowManagerDeps: WindowManagerDeps = {
  renderContent: (id) => renderWindowContent(id, profile),
  control: windowControls, // the (id, action) => void fn registered via registerWindowControls
};
restoreWindows(windowManagerDeps);
```
`windowControls` is the `registerWindowControls((id, action) => {...})` callback, pulled
into a named `const` so it can be reused as `deps.control`.

For language-change updates, `window-manager` now uses `onLangChange` from
`@/entities/lang/model/lang` (entities layer — allowed) instead of `onLanguageChange`
(defined in `features/open-window/content`). The `activeDeps` module var holds the
render fn so the `onLangChange` subscription can call `refreshWindow(app.id, activeDeps.renderContent)`.

## Window.ts persist (no offsetParent guard)

`persist()` was the source of the "drag one window → others vanish" bug. The old code did
`if (!win.isConnected || !win.offsetParent) return;` inside `createWindow` — but `persist()`
runs BEFORE the window is appended to the DOM, so it early-returned and default windows were
never saved. Fix: extract position from `win.style` (already set at construction) into a pure
function `computeWindowState(id, win.style, size)` in `src/widgets/window-manager/ui/state.ts`,
and `persist` calls `saveWindowState(computeWindowState(...))`. No DOM read, no guard.

## Vitest setup (added this session)

Previously only Playwright e2e existed. To cover pure logic (persistence, FSD) add Vitest:

`vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
import { resolve } from 'node:path';
export default defineConfig({
  resolve: { alias: { '@': resolve(import.meta.dirname, 'src') } },
  test: { environment: 'jsdom', include: ['src/**/*.spec.ts'], globals: true },
});
```
Install: `npm install -D jsdom @types/node`. Add `"node"` to `types` in `tsconfig.json`
(`"types": ["vite/client", "node"]`) so `node:fs`/`node:path`/`process` resolve in specs.
Run: `npx vitest run`.

Specs added:
- `src/entities/window-state/model/__tests__/window-state.spec.ts` — save/get/clear, `open:false`
  excluded from `getOpenStates`, z-sort.
- `src/widgets/window-manager/ui/__tests__/window-persist.spec.ts` — `computeWindowState`.
- `src/widgets/window-manager/__tests__/restore.spec.ts` — regression: after default open of all
  3 + dragging ONE, reload still returns all 3 (the exact bug from the session).
- `src/__tests__/fsd-layers.spec.ts` — guards the FSD invariant (widgets≠features, shared/entities
  don't import upward). Re-run this after any refactor.

## e2e must assume the AUTO-OPENED default layout

`restoreWindows` opens About/Safari/Lang on load when `localStorage` is empty. Old e2e
written for an "empty desktop, click icon to open" model break in three ways:

1. Clicking an icon whose window is ALREADY open only re-focuses it → `expect(count).toHaveCount(1)` fails (actual 3).
2. Clicking an icon OVERLAPPED by an auto-opened window (e.g. `lang`/`About` icons under the wide left `about` window) hits the window, not the icon.
3. "expected 0 windows after close" is wrong — Safari/Lang remain.

Working pattern used this session:
- For default apps, select the live window directly: `.mac-window[data-window-id="lang"]` and drag/close it. No icon click needed.
- For "after close + reload" assert the *closed* id is absent but the *other* defaults remain (count = 2, not 0).
- To open a fresh window by click, use an app NOT in `DEFAULT_LAYOUT` (`photos`/`folder`) or close the overlapping default first.
- `expect(await locator.count()).toBeGreaterThanOrEqual(1)` — note `count()` returns a Promise; must `await` it (a bare `await expect(locator.count())...` throws "received Promise").

Re-audit every e2e spec whenever `DEFAULT_LAYOUT` or the `profile.ts` app list changes.
