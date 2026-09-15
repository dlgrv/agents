# Cloning original features 1:1 into dlgrv

User demand: copy the REAL source (Chromium dino, daedalOS galaxy) verbatim. Never
re-implement game/visual art from scratch — self-written versions produce "битые текстуры"
(corrupted/broken sprites) and he catches them.

## Pattern A — full standalone page → embed via <iframe>

Best when the original is a complete HTML page (the chrome://dino case).

**Source:** `https://github.com/Richi2PL/chome-dino` — `index.html` is the entire
`chrome://dino` game (234 KB, sprite sheets inlined as base64 in
`<img id="offline-resources-1x/2x">`, plus the `Runner` engine in `<script>` tags).

**Extraction that worked:**
1. `curl` the raw `index.html`.
2. It is bundled: script#2 = `function Runner(...)` (116 KB, original Chromium code,
   `Copyright The Chromium Authors`); script#3 = `Runner.spriteDefinitionByType`
   (exact LDPI frame coords: `CACTUS_LARGE:{x:332,y:2}`, `HORIZON:{x:2,y:54}`, etc.);
   script#0/#1/#4–#6 = Chrome error-page i18n/runtime we DON'T need.
3. Build a minimal `public/dino/chrome-dino.html`:
   - `<body class="offline">` + `<div id="offline-resources">` containing the two
     `<img id="offline-resources-1x/2x">` (base64 sprites, copied verbatim).
   - A `loadTimeData` polyfill (`getString/getValue/valueExists/overrideValues`) — Runner
     calls `loadTimeData.getValue(...)` for a11y strings.
   - `window.HIDDEN_CLASS = 'hidden'` + a `.hidden { display:none }` rule.
   - Optional DOM stubs Runner expects: `.icon-offline`, `#audio-resources`.
   - Order: `script#2` THEN `script#3` (s3 sets `Runner.spriteDefinitionByType`,
     which must exist before `new Runner` runs).
   - Bootstrap `<script>`: create `.interstitial-wrapper`, then `new Runner('.interstitial-wrapper')`.
4. In the Safari window (`src/features/open-window/content.ts`), render a
   `<iframe class="safari-frame" src="/dino/chrome-dino.html">` filling `.safari-view`.
   Toolbar `‹ ⟳ dlgrv://dino`; `⟳` does `iframe.contentWindow.location.reload()`.

**Gotchas that cost debugging:**
- `new Runner` throws `spriteDefinitionByType['original'] is undefined` if s3 runs
  BEFORE s2 (Runner must exist first). Order s2 → s3 → bootstrap.
- `loadTimeData is not defined` → add the polyfill BEFORE script#2.
- `HIDDEN_CLASS is not defined` / `reading 'content'` / `reading 'getElementById'` on
  reload → add `HIDDEN_CLASS` global + `.icon-offline` + `#audio-resources` stubs.
- Playwright: a canvas *inside* an iframe is addressed via
  `page.frameLocator('iframe.safari-frame').locator('canvas')`, NOT `win.locator('canvas')`.
  `win.locator('iframe').locator('canvas')` exists but `toBeVisible` is flaky — use `frameLocator`.

**Do NOT** recreate the engine in TS (deleted `src/shared/game/dino.ts`). Keep the
originals as static files; the project stays lean and pixel-perfect.

## Pattern B — component/module → copy + alias-rewrite

Best for daedalOS galaxy wallpaper (a multi-file WebGL module).
- Copy the source dir into `src/shared/ui/galaxy/`.
- Rewrite imports from the original path (`components/system/Desktop/Wallpapers/Galaxy/`)
  to local relative/alias paths.
- Drop unused type deps; supply a tiny local `types.ts`.
- Mount AFTER `root.append(...)` — before that the container has 0×0 and the canvas
  silently fails. This bug cost a debugging session.
- Keep particle density at ~40% of original (user taste); no PIXEL_SCALE (user reverted
  the pixelated look — wants clean bright galaxy). WebGL-less fallback = solid `#000`.
