# Playwright testing for desktop-OS-style sites

Hard-won failure modes from a macOS/Win95 windowed site. All patterns verified
against real runs (Playwright + Vite dev server).

## Overlay interception (the #1 icon-click killer)
`page.click('.app-icon')` fails with "element intercepts pointer events" when an
auto-opened window covers the icons. Diagnose with:
```ts
const hit = await page.evaluate(() => {
  const r = el.getBoundingClientRect();
  const t = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
  return t?.className ?? 'null';
});
```
Fixes: position windows so they don't cover the icon strip (open below it), or
click a guaranteed-free icon, or `{ force: true }` (bypasses actionability checks —
works because handlers are plain `click` listeners).

## Windows count assumptions break silently
When auto-open behavior changes (window opens on load vs only on click), every test
asserting `toHaveCount(N)` breaks. Prefer asserting on the specific window:
```ts
await expect(page.locator('.mac-window[data-window-id="lang"]')).toHaveCount(1);
```

## Ids with spaces break attribute selectors
`data-window-id="change lang"` cannot be selected with `[data-window-id="change lang"]`
reliably across engines/quote styles. Use machine ids (`lang`) for data attributes;
keep human names in `title`/labels only.

## Cascade positioning = flaky geometry
Windows open at `f(openCount)` offsets. If a test measures `boundingBox()` right
after opening, the cascade may not have settled. Add `await page.waitForTimeout(250)`
after opening before measuring, and compare before/after rather than to constants.

## Weak drag assertions hide real bugs
"expect(after.x).toBeLessThan(before.x)" passes even when the drag is broken
(window moved 12px of 144px requested). Assert the window lands ≈ where the mouse
ended:
```ts
await page.mouse.move(endX, endY, { steps: 8 });
await page.mouse.up();
const after = await win.boundingBox();
expect(after.x).toBeCloseTo(endX - grabOffsetX, 0);
```
Also assert no snap-back: re-measure after `waitForTimeout(300)` and compare.

## pointercancel simulation
Dispatch `new PointerEvent('pointercancel', { bubbles: true })` on the titlebar
mid-drag; then allow tail `pointermove` events to drain (`waitForTimeout(150)`)
before asserting the window stopped moving. Tail moves after cancel are normal.

## `not.toHaveClass(/re/)` fails on empty class
`expect(locator).not.toHaveClass(/is-dragging/)` throws when `class=""`. Use:
```ts
expect(await titlebar.evaluate(el => el.classList.contains('is-dragging'))).toBe(false);
```

## Cursor assertions
Read computed style, not class names, when the user cares about the visible cursor:
`getComputedStyle(titlebar).cursor` — and remember macOS does not change the cursor
during titlebar drag (stays `default`).

## Dev server dies between runs
`ERR_CONNECTION_REFUSED` on every test = Vite background process exited. Restart it
(`npx vite --port 4923 --strictPort` in background), health-check with curl, then run
tests. Don't debug app code when the failure is `goto: CONNECTION_REFUSED`.

## localStorage-persisted UI (windows/positions/scores)
- Persist on gesture end (`onEnd` of drag/resize), on focus (z-index), and on open.
  Guard persist with `if (!el.isConnected || !el.offsetParent) return` — the factory
  runs before the element is in the DOM and `offsetParent` is null.
- Restore on startup from a versioned key (`dlgrv.windows.v1`), sorted by z.
- "Closed" must persist as `open:false`, else closed windows resurrect on reload.
- Reset = clear storage + `location.reload()`; keep unrelated prefs (language) intact.
- Tolerances: restored position vs pre-reload position can differ by tail pointer
  events; assert `toBeCloseTo(before.x, -2)` (~50px) not exact equality.

## Canvas games in windows
- Game loop must die with the window: keep a `WeakMap<container, game>` registry and
  destroy the previous instance before creating a new one; `destroy()` cancels RAF and
  removes window-level key listeners.
- Canvas CSS `width/height:100%` distorts a fixed-internal-resolution canvas. Set
  canvas pixel size from `container.clientWidth` (clamped) and set explicit CSS px
  size; `ctx.imageSmoothingEnabled = false` for pixel-perfect sprites.
- Expose game state as `container.dataset.state = 'idle'|'running'|'over'` — tests
  assert on this instead of pixels.
