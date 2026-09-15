# Original Minecraft assets — extraction recipe & repo inventory

The dlgrv.com site embeds real Minecraft game assets (never re-drawn). They live in
`public/minecraft/`. This file documents WHERE they came from and HOW to extract more,
so future sessions don't guess at fan-mirrors (the user's standing rule: clone 1:1 from
the real source — see SKILL.md «Clone features/games 1:1»).

## Official source (always this, no fan sites)

```python
import json, urllib.request, zipfile
manifest = json.load(urllib.request.urlopen(
    'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'))
ver = next(v for v in manifest['versions'] if v['id'] == '1.12.2')
vj = json.load(urllib.request.urlopen(ver['url']))
urllib.request.urlretrieve(vj['downloads']['client']['url'], '/tmp/mc-client-1.12.2.jar')
z = zipfile.ZipFile('/tmp/mc-client-1.12.2.jar')
```

This is the exact jar the Mojang launcher downloads — original textures/fonts/sounds.
- **Textures & fonts** are inside the jar under `assets/minecraft/textures/…`.
- **Sounds** are NOT in the jar: the version JSON has `assetIndex.url` → download that
  index JSON → it maps `sounds/...` names to object hashes → fetch each from
  `https://resources.download.minecraft.net/<hash[:2]>/<hash>`. (Legacy jars ≤1.7 do
  contain `assets/…ogg` directly.)

## Texture layout across versions (important)

- **1.12.x**: toast frames are one atlas `assets/minecraft/textures/gui/toasts.png`
  (256×256, transparent). Measured layout — four 160×32 toasts stacked on the left:
  y=0 tutorial (dark), **y=32 system (light)**, **y=64 ADVANCEMENT (the classic dark-blue
  toast with yellow «!»)**, y=96 system duplicate; icons grid on the right.
  Crop with PIL: `img.crop((0, 64, 160, 32+64))`. Center field color ≈ `#082C4C`,
  light-blue bevel frame, yellow `!` ≈ `#FFFF55`.
- **1.21+ (and 26.x)**: each toast is its own sprite
  `assets/minecraft/textures/gui/sprites/toast/<name>.png` (160×32), e.g.
  `advancement.png` (thin grey rounded outline), `recipe.png`, `system.png`,
  `tutorial.png`. No `.mcmeta` on them. The yellow-«!» variant no longer exists — only
  in 1.12.2's atlas.
- **Item icons**: `assets/minecraft/textures/item/*.png` (~800 files in the modern jar).
- **Bitmap font**: `assets/minecraft/textures/font/ascii.png` + `default.json`
  (glyph page mapping + metrics), `nonlatin_european.png` (**contains Cyrillic** —
  RU text renders in real Mojangles), `accented.png`, `space.json` (space widths).

## Inventory already extracted → `public/minecraft/` (236 KB, 2026-09)

- `toast/advancement-classic.png` — 1.12.2 dark-blue toast (crop of `toasts.png` at
  (0,64,160,32)); `toast/advancement|recipe|system.png` — modern 1.21-era sprites.
- `font/ascii.png`, `default.json`, `nonlatin_european.png`, `accented.png`, `space.json`.
- `sounds/in.ogg`, `out.ogg`, `challenge_complete.ogg`, `levelup.ogg` (toast slide in/out,
  challenge fanfare, levelup).
- `items/diamond|emerald|golden_apple|nether_star|totem_of_undying|experience_bottle.png`
  (16×16, for the toast's left icon slot).

Render at integer scale (160×32 ×3 = 480×96) with `image-rendering: pixelated`.

## Built feature (2026-09): Minecraft-style achievement toast

The planned toast is IMPLEMENTED (branch `feat/achievement-toast`; check `git log` for
merge state). FSD-clean architecture:

- `src/shared/lib/mcfont/` — bitmap-font renderer. `glyph-map.ts` parses `default.json`
  (+ `nonlatin_european.png` for Cyrillic); `atlas.ts` slices font pages into per-glyph
  bitmaps; `render-text.ts` draws to canvas with vanilla metrics incl. `space.json`
  advances. Lives in `shared/lib`, NOT `entities/` — Steiger flagged
  `insignificant-slice` (single referencing feature) and the move silenced it.
- `src/features/achievement-toast/` — `render-toast.ts` (DOM block: advancement.png
  plate ×3 = 480×96, left icon slot, 3 text lines), `toast-layer.ts` (single-slot
  queue: slide-in → 5 s → slide-out 0.5 s → remove → next), `tint.ts` (glyph
  compositing). Wiring: `entities/celebrate` unlock →
  `CustomEvent('dlgrv:achievement', { detail: { id } })` on `window` → layer. App glue
  in `app/index.ts`; styles `src/app/styles/achievement-toast.css`.
- Copy for the celebrate achievements in BOTH dicts: line 1 «Достижение
  получено!»/`Achievement Get!` (yellow), line 2 title (white), line 3 description
  (grey). `photos_all` icon = `filled_map.png` (Краевед → карта).
- e2e trigger pattern:
  `window.dispatchEvent(new CustomEvent('dlgrv:achievement', { detail: { id: 'photos_all' } }))`
  + `test.use({ reducedMotion: 'reduce' })` so the slide animation doesn't race the
  screenshot.

### Vanilla-fidelity gotchas (each cost a fix in the 1:1 audit)

- **Space width is NOT a glyph in `ascii.png`** — the space cell is empty; its 4 px
  advance comes from `space.json`. The renderer must load space advances separately
  or words fuse (`AchievementGet!`). Regression: `mcfont/__tests__/space.spec.ts`.
- **Text colors follow the PLATE.** Modern `advancement.png` is dark `#212121` with a
  grey `#555` frame → title `#FFFF55`, name white, description `#AAAAAA`. The v1 plan
  guessed light-plate (dark-text) colors — wrong; only the pixel audit caught it.
- **Tint glyphs via `source-in` composite** (how MC tints sprites itself), never CSS
  filters (they poison the alpha edges).
- **Line spacing is 8 px**, not 4 — three lines fuse at 4.
- **Integer scale + `image-rendering: pixelated`** for plate (160×32 ×3) and icon
  (16→48). If a vision model calls the icon "blurry", verify computed style + integer
  scale FIRST — the report can be a JPEG artifact of the screenshot, not a real defect.
- Item-icon traps: `crafting_table`/`piston` in the jar are BLOCK textures (use
  `crafting_table_front`/`piston_top`); `chicken.png` is raw; `clock.png` is an
  animation sheet — take a frame (`clock_16` = noon).
- Verification ritual for «1:1 как в minecraft»: (1) pixel-audit the source PNG
  (fill/frame/alpha colors via PIL), (2) live Playwright screenshot, (3) vision
  compare vs vanilla. Unit tests were green while 3 real divergences remained.
