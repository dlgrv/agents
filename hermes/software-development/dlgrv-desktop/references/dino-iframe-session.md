# Dino-in-Safari session notes (wayou/t-rex-runner + iframe keyboard relay)

Session 2026-08-25 findings that belong in clone-originals.md once writable:

## Final working state
- `public/dino/` = verbatim wayou/t-rex-runner gh-pages tree (index.html/index.js/index.css
  + assets/default_{100,200}_percent/*-offline-sprite.png), embedded by Safari via
  `<iframe class="safari-frame" src="/dino/index.html">`.
- Dead ends: self-written TS engine (broken sprites); Richi2PL/chome-dino script
  reassembly (rendered raw sprite sheet, reload crashes). Both abandoned.

## [dlgrv] patches (why each exists)
- Trex constructor BEFORE this.init(): `this.xPos = Trex.config.START_X_POS;`
  → Trex.init() draws immediately; pinning after `new Trex()` leaves the idle canvas
  on the x=0 frame (proved by getImageData scan: idle x=2 vs run x=52).
- Runner.init(): `this.setArcadeMode()` after tRex creation → arcade-mode class +
  scale transform exist from frame one. NOT in the Runner constructor (containerEl null)
  and NOT inside adjustDimensions() (runs before containerEl exists either).
- playIntro gutted to `playingIntro=false; startGame();` (no intro animation).
- drawStartText(): pixel glyphs "PRESS SPACE TO START" (#535353, 5×7 @2×) while idle.
  No original font exists — sprite sheet only has G,A,M,E,O,V,R,H,I; removed Open Sans
  #messageBox overlay from index.html.
- index.css `.offline .runner-container{width:600px}` (was 44px clipped canvas).

## Keyboard relay (Space without clicking iframe)
- Parent content.ts relays Space/↑/↓ via iframe.postMessage while
  `document.activeElement !== iframe`; iframe feeds Runner.handleEvent.
- TRAP: fake event needs `target: document`. Game gates on
  `e.target != this.detailsButton` where detailsButton=null; `undefined != null` is
  false in JS → silent ignore. Two debug rounds lost here.

## Verification patterns
- Pixel measurement beats vision: vision flip-flopped calling a healthy game broken.
  Use ctx.getImageData dark-pixel scans in a y-band above ground.
- Playwright: frameLocator for locators; real Frame via page.frames().find(url match)
  for evaluate(); Runner.instance_ readable from the frame.
- Scripted str.replace on vendored index.js once emitted `new Trex(new Trex(...))`
  (syntax kill). After patches: grep markers + headless pageerror check.
