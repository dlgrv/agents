# Throwaway e2e diagnostic spec pattern

When a behavior "doesn't work" in the dlgrv site, do not reason from code alone.
Write a temporary Playwright spec that prints real browser state, run it, read the
numbers, fix, delete the spec.

## Template

```ts
// e2e/zz-diag.spec.ts  (zz- prefix sorts last; delete after use)
import { test } from '@playwright/test';

test('diag', async ({ page }) => {
  page.on('pageerror', (e) => console.log('EXC:', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.log('ERR:', m.text()); });

  await page.goto('/');
  await page.waitForTimeout(500);

  console.log('windows:', await page.locator('.mac-window').count());
  console.log('ids:', await page.$$eval('.mac-window',
    (els) => els.map((e) => e.getAttribute('data-window-id'))));

  const el = page.locator('.app-icon', { hasText: 'Safari' });
  console.log('bbox:', JSON.stringify(await el.boundingBox()));

  // what actually receives the pointer at the element center?
  console.log('hit:', await el.evaluate((e) => {
    const r = e.getBoundingClientRect();
    const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return t ? t.className : 'null';
  }));

  // computed style probe
  console.log('cursor:', await page.locator('.mac-window__titlebar')
    .first().evaluate((e) => getComputedStyle(e).cursor));

  // localStorage state (window persistence)
  console.log('stored:', await page.evaluate(() => localStorage.getItem('dlgrv.windows.v1')));

  // canvas mounted?
  console.log('canvas:', await page.locator('#wallpaper canvas').count());
});
```

Run: `npx playwright test e2e/zz-diag.spec.ts` — grep the console lines, then
`rm -f e2e/zz-diag.spec.ts`.

## Problems this pattern actually solved in dlgrv

| Symptom | Diagnostic reading | Root cause |
|---|---|---|
| Window "returns to start" while dragging | during-drag position barely moved from start | `pos.x` fixed at drag-start but `dx` incremental → must accumulate `pos.x += dx` each frame |
| Click on desktop icon times out | `elementFromPoint` hit `emoji-sphere` from the windows layer | auto-opened window covered the icons |
| Window never opens on icon click | `PAGE_EXCEPTION: Cannot read properties of null (reading 'getBoundingClientRect')` | `persist()` ran before the element was in the DOM (`offsetParent === null`) |
| Old wallpaper still showing | `#wallpaper canvas` count = 0, desktop bg = static png | galaxy mounted before DOM append → 0×0 canvas; move mount after `root.append` |
| Torn dino sprite | stored x vs boundingBox mismatch; column profile of sprite sheet | wrong frame step (92px real vs 88 assumed) |
| Test fails with empty class | `Received string: ""` | `not.toHaveClass(/re/)` quirk → use `classList.contains` |

## Rules

- Always register `pageerror` + console error listeners first — silent page exceptions
  are the most common cause of "nothing happens".
- Prefer `data-state` / dataset attributes over pixel assertions for game state.
- Use `{ force: true }` for icon clicks in tests to skip pointer-intercept flakiness,
  but only after confirming via `elementFromPoint` what is intercepting.
- Delete the diagnostic spec before finishing — it pollutes the suite otherwise.
