# macOS-desktop "interactive OS" clone pattern

A sub-genre of site clone (see probablynothing.xyz): the page is a fake macOS
desktop — icon grid (artists/files), draggable windows with macOS chrome, a
dock or ticker, NOT logo. Faithful replicas need the *interactions*, not just
looks. Patterns that worked, ready to copy-modify.

## Visual chrome
- **Traffic-light controls** on the LEFT of the title bar (red/yellow/green),
  not grey outlines. Hover reveals the glyph inside each (× / – / +).
  ```css
  .tl{width:13px;height:13px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:700}
  .tl.close{background:#ff5f57}.tl.min{background:#febc2e}.tl.max{background:#28c843}
  .tl span{opacity:0}.titlebar:hover .tl span{opacity:1}
  ```
- **Title font**: `-apple-system,BlinkMacSystemFont,"Inter Tight",sans-serif`,
  weight 600 — macOS uses the system font, not a webfont.
- **Resize handle**: `position:absolute;right:0;bottom:0;width:18px;height:18px;
  cursor:nwse-resize;background:linear-gradient(135deg,transparent 50%,rgba(255,255,255,.45) 50%)`.
- **Icon selection**: macOS blue `#0a84ff` ring on the icon + blue label
  background. Deselect on empty-desktop mousedown.

## Behaviours (JS)
- **Open-from-icon animation**: append window, then `transform:translate(dx,dy)
  scale(.06);opacity:0` computed from the clicked icon's center, force reflow,
  transition to `none`/`opacity:1` over ~0.28s cubic-bezier(.2,.8,.2,1).
- **Minimize** -> `display:none` + a chip in a `#minbar` (bottom-left); chip
  click restores with a quick scale-in. Store `w._chip` to remove on close.
- **Zoom/maximize** -> toggle a `.maximized` class (full-viewport with margins);
  stash original geometry in `w._geo` to restore.
- **Draggable** via titlebar mousedown->mousemove; **resizable** via the handle
  updating width/height (min 300x220).
- **Stop event propagation** on the traffic-light buttons (mousedown +
  click) so they don't trigger drag/titlebar handlers.

## Background
- Real sites use a `<video>` (e.g. `emoji-sphere.mp4`) with `poster=bg.png`
  fallback, z-index behind content.
- **Animated film grain**: a fixed full-screen `feTurbulence` SVG layer,
  `mix-blend-mode:overlay`, opacity ~.10, `animation:grain` that translates it
  in 3 steps (~1.1s) — sells the lo-fi look better than static noise.

## Pixel font for headlines
- `Press Start 2P` breaks on Cyrillic. Add `Pixelify Sans` as fallback
  (`font-family:"Press Start 2P","Pixelify Sans",monospace`) so Russian text
  renders instead of tofu boxes.

## Real-collage over random
- Don't scatter emojis at `Math.random()` — place them on a fixed coordinate
  list and overlay a few text phrases (e.g. "beautiful people", "internet",
  "новая волна") to echo the source. Looks intentional, not noisy.
