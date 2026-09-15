# Drag & interaction recipes for macOS-desktop clones

Lessons from the dlgrv.com session (Vite + TS, vanilla FSD): three separate
drag-breakage bugs and their fixes. All code verified against Playwright e2e
running real mouse input.

## 1. The drag implementation that works everywhere

Embedded webviews (Hermes preview pane) fire spurious `pointercancel` or fail to
retarget `setPointerCapture` events — a capture-based drag dies on frame one while
working fine in regular Chromium. Use per-drag document listeners instead:

```ts
export function makeDraggable(handle: HTMLElement,
  { onStart, onMove, onEnd }: DragHandlers): () => void {
  let lastX = 0, lastY = 0, dragging = false;

  const move = (e: PointerEvent) => {
    if (!dragging) return;
    e.preventDefault();                       // no text selection during drag
    onMove(e.clientX - lastX, e.clientY - lastY);
    lastX = e.clientX; lastY = e.clientY;
  };
  const finish = () => {
    if (!dragging) return;
    dragging = false;
    document.removeEventListener('pointermove', move);
    document.removeEventListener('pointerup', finish);
    document.removeEventListener('pointercancel', cancel);
    onEnd?.();
  };
  const cancel = (e: PointerEvent) => {
    // webviews emit false pointercancel for mouse (system-gesture misdetection):
    if (e.pointerType === 'mouse' && dragging) return;
    finish();                                 // touch cancels honestly
  };
  const down = (e: PointerEvent) => {
    if (dragging) return;
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    // MUST come before preventDefault: pd on pointerdown suppresses the
    // subsequent `click`, which silently killed traffic-light buttons.
    if ((e.target as HTMLElement).closest('button')) return;
    e.preventDefault();
    dragging = true;
    lastX = e.clientX; lastY = e.clientY;
    document.addEventListener('pointermove', move, { passive: false });
    document.addEventListener('pointerup', finish);
    document.addEventListener('pointercancel', cancel);
    onStart?.();
  };

  handle.addEventListener('pointerdown', down);
  return () => { handle.removeEventListener('pointerdown', down); finish(); };
}
```

## 2. Position math: start + delta, never rect-chasing

```ts
// in the widget creating the window:
const pos = { x: 0, y: 0 };   // closure-local — see §3
makeDraggable(titlebar, {
  onStart: () => {
    const r = win.getBoundingClientRect();
    const p = win.offsetParent!.getBoundingClientRect();
    pos.x = r.left - p.left;  pos.y = r.top - p.top;
  },
  onMove: (dx, dy) => {
    const maxL = win.offsetParent!.clientWidth - 80;
    const maxT = win.offsetParent!.clientHeight - 40;
    win.style.left = `${clamp(pos.x + dx, 0, max(maxL, 0))}px`;
    win.style.top  = `${clamp(pos.y + dy, 0, max(maxT, 0))}px`;
  },
});
```

❌ Recomputing from `getBoundingClientRect()` on EVERY move makes the window
chase its own displaced rect → cumulative drift → "окно уезжает вниз".
✅ Freeze start pos in `onStart`; move is always `start + delta`.

## 3. State scoping

Module-level `let startX/startY` shared by all windows: a lost pointerup on
window A leaves stale coords that teleport window B on its next drag.
Every window gets its own `pos` inside its factory-function closure.

## 4. If you must use setPointerCapture

- wrap `setPointerCapture` in try/catch (throws if pointer already gone)
- guard release with `handle.hasPointerCapture(e.pointerId)` — releasing an
  unheld capture throws and skips your drag-end logic
- know that it may simply not deliver events in embedded webviews

## 5. Playwright e2e for drags

```ts
async function dragBy(page, sel, dx, dy) {
  const b = await page.locator(sel).boundingBox();
  await page.mouse.move(b.x + b.width/2, b.y + b.height/2);
  await page.mouse.down();
  for (let i = 1; i <= 8; i++) {          // real movement path, not one jump
    await page.mouse.move(b.x + b.width/2 + dx*i/8, b.y + b.height/2 + dy*i/8);
    await page.waitForTimeout(12);
  }
  await page.mouse.up();
}
```

Tests worth having:
1. **open + move**: click icon → window appears → dragBy(-150, +120) → x decreased,
   y increased, position unchanged 300ms after mouse-up ("no teleport back").
2. **repeat drags / recreated windows**: close window, reopen, drag twice in
   opposite directions — second drag must move RELATIVE to current position
   (catches shared-state bug §3).
3. **mid-drag pointercancel**: dispatch synthetic
   `new PointerEvent('pointercancel', { bubbles: true })` mid-drag, then assert
   further mouse moves do NOT move the window.

Flake notes:
- CDP input delivery is async; tail pointermove can land AFTER the synthetic
  cancel → wait ~150ms before reading positions, else ±6px flake.
- If windows open on page load, expect them in count assertions; scope locators
  (`page.locator('.mac-window').first()` then `.locator('.titlebar')`).

## 6. Emoji sphere without three.js

Fibonacci-sphere distribution + CSS translate3d, one rAF loop:

```ts
const N = count;                      // ~40
const golden = Math.PI * (3 - Math.sqrt(5));
for (let i = 0; i < N; i++) {
  const y = 1 - (i/(N-1))*2, r = Math.sqrt(1 - y*y), th = golden*i;
  el.dataset.x = String(Math.cos(th)*r);       // base coords on unit sphere
  el.dataset.y = String(y);
  el.dataset.z = String(Math.sin(th)*r);
}
// each frame: rotate around Y by angle, fixed X tilt (~0.35 rad):
// rx = x·cosA + z·sinA ; rz = -x·sinA + z·cosA
// ry = y·cosT - rz·sinT ; rz' = y·sinT + rz·cosT
// transform = translate3d(rx·R, ry·R, rz'·R)
// opacity = .45 + ((rz'+1)/2)*.55   ← depth cue
// zIndex  = round(rz'*100)
```

Scene CSS: fixed square, `perspective: 700px`; items absolutely centered with
negative margins, `will-change: transform, opacity`. Zero dependencies vs a
three.js bundle; 40 spans at 60fps is trivial.

## 7. probablynothing.xyz measured design tokens

Pulled from `_astro/*.css` + client bundle (`HelloWorld.*.js`) — reuse directly:

| Element | Values |
|---|---|
| body font | `Archivo, sans-serif` (Google Fonts, wght 100..900 variable) |
| icon label | Archivo 14px, weight 500, white, centered, `drop-shadow(0 1px 2px #0000001a) drop-shadow(0 1px 1px #0000000f)` |
| window title (titlebar h2) | Archivo 13px, weight 700, black, centered, truncate |
| big in-window title | Archivo 800, 52px/50px (36px/40px mobile) |
| accent-text | Archivo 15px, 600, letter-spacing .3px |
| description-text | Archivo 15px, 400, letter-spacing .3px |
| description-small | Archivo 12px, opacity .5, letter-spacing .24px |
| secondary fonts loaded | Inter Tight (variable), Golos Text, Instrument Serif, Playfair Display, Beth Ellen |
| traffic lights | grey `#E3E3E3` fill, `#C8C8C8` border, 11px circles until hover |
| window chrome | bg `#F6F6F6`, borders `#E5E5E5`/`#C2C2C2`, rounded-xl |
| default-open window | config flag `isOpen: true` in the island props |

Extraction path that worked: `curl -sL` the HTML → grep `/_astro/*.css` links +
the Google-Fonts `<link>` → grep font-family rules from the CSS → for Tailwind-
class styling living in the JS bundle, download the `component-url` chunk and
grep its `className:"..."` strings (labels were NOT in static HTML — client-only
React render).
