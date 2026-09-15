# Copying exact styles/sprites from a reference site

Recipe verified against probablynothing.xyz, dustinbrett.com (daedalOS),
emojiwave.xyz, and the Chrome dino game.

## Finding the real source of a visual
1. `curl -sL <site> -o /tmp/site.html` and grep for: linked CSS, `/_next/static/...`
   chunks, `.webm/.mp4` (video backgrounds), `canvas` (WebGL), sprite sheets.
2. SSR HTML may be nearly empty (client-rendered). The JS bundles contain the truth:
   grep bundles for font-family declarations, color literals, sprite coordinate
   tables (`TREX: { x: 1678, y: 2 }`), and asset URLs.
3. Open-source clones are goldmines: daedalOS wallpapers are real components on
   GitHub (`components/system/Desktop/Wallpapers/Galaxy/*` — WebGL galaxy, copy +
   rewrite imports); the Chrome dino game lives at wayou/t-rex-runner with exact
   sprite-sheet coordinates in `index.js`.

## Fonts
- Extract `font-family` from their CSS (grep the linked stylesheet), then either
  hotlink Google Fonts or self-host: download the TTF/WOFF2 from
  `fonts.gstatic.com` (the URL is in the Google Fonts CSS response), put in
  `public/fonts/`, declare `@font-face` locally. Self-hosting is mandatory when the
  user's network blocks Google Fonts — verify with a Playwright test that aborts
  `fonts.googleapis.com|fonts.gstatic.com` routes and asserts `document.fonts.check(...)`.

## Sprite sheets (pixel games)
- Get BOTH the 1x and 2x sheets. The 2x sheet's frame layout may NOT be exactly
  2× the 1x layout (frames can be packed tighter with no gaps) — do not guess.
- Measure frame boundaries programmatically: convert PNG→BMP via `sips`, decode
  BMP with `struct` (bottom-up rows, BGRA), and profile per-column opacity to find
  frame edges. ASCII-render the column profile to "see" the sprite without vision.
- Prefer the **1x sheet drawn at 2× scale** with `imageSmoothingEnabled = false`:
  the 1x layout matches the original source coordinates exactly (44px grid), while
  the 2x sheet packs frames differently.
- Take frame offsets/dimensions from the game's own source (`Trex.animFrames`,
  `Obstacle.types`, `spriteDefinition.LDPI/HDPI`), not from eyeballing.
- Verify visually: Playwright screenshot of the canvas + vision model, plus
  `container.dataset.state` assertions for game-flow tests.

## Animated backgrounds
- Identify the mechanism first: `<video>` loop (probablynothing), WebGL canvas
  (daedalOS Galaxy), CSS gradients, or pre-rendered MP4. Copying a WebGL component
  from an open-source repo is legitimate and cheap: download the module files,
  rewrite import paths to your alias structure, prune unused config types, mount
  after the element is in the DOM (canvas needs real `offsetWidth`; guard persist/
  init with `isConnected`/`offsetParent` checks and `requestAnimationFrame`).
- Always keep a static fallback (solid color) for no-WebGL environments.
- Decorative overlays (darkening, pixel grid, film grain) belong in a CSS
  `::after` layer above the canvas — never modify the render code. User may reject
  the styling; keep it as an easily-revertible layer.

## macOS chrome measurements (verified)
- Titlebar 28px, radius 10px, lights 12px ⌀ / 8px gap / ~13px left pad, title
  13px semibold `rgba(0,0,0,.85)` centered; unfocused title `rgba(0,0,0,.4)`;
  cursor stays `default` during titlebar drag; resize handle invisible (hotspot only).
- Win95: blue gradient titlebar `#000080→#1084d0`, title left white bold 11px Tahoma,
  buttons right, body `#C0C0C0`, radius 0, bevel borders. Inactive Win95 title is
  translucent white — raise selector specificity
  (`.mac-window.mac-window--win95:not(.is-focused)`) or the macOS unfocused rule
  (loaded later) wins.

## probablynothing.xyz specifics (verified from bundle)
- Icon labels: `text-sm font-medium text-white` + soft double drop-shadow
  `drop-shadow(0 1px 2px rgba(0,0,0,.1)) drop-shadow(0 1px 1px rgba(0,0,0,.06))`.
- Window title: `text-center text-black font-bold` 13px.
- "Dive in" button (aqua-link): pill `border-radius:70px`, height 44px, padding
  0 24px, `linear-gradient(0deg,#F5F5F5 -15.69%,#B5B5B5 127.45%)`,
  shadow `0 4px 8px rgba(62,62,62,.19)`, top highlight span (white→transparent,
  inset 1px/12px), bottom glow span (`#EDF8FF` blur 8.5px), text 16px/500 `#2A2A2A`.
- Article title font: `.tg-article-title` = **Playfair Display** (not Instrument Serif).
- Their "emoji sphere" is a pre-rendered MP4 (`emoji-sphere.mp4`) + dark overlay +
  large serif title — reproduce with CSS 3D (Fibonacci sphere points + per-item
  random tilt + radial dark overlay + centered Playfair Display title).
