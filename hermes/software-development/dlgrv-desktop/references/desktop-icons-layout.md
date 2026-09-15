# Desktop icons & wallpaper layout (dlgrv)

Condensed recipes for the icon/wallpaper work done in this session. Reproduce
with modifications; do not hand-type the SVG/CSS each time.

## 1. Icon placement: left grid vs right-center column

Two containers in `src/pages/desktop/ui/Desktop.ts`:
- `.desktop__icons` — default, top-left (`top: calc(var(--menubar-h)+40px); left:40px`).
- `.desktop__icons.desktop__icons--right` — right edge, vertically centered.

App decides its container via `profile.ts` `AppInfo.side`:
```ts
// profile.ts
export interface AppInfo { /* ... */ side?: 'right'; }
{ id: 'photos', name: 'Photos', theme: 'mac', side: 'right', icon: '/icons/photos.png' },
{ id: 'folder', name: 'Blog',   theme: 'mac', side: 'right', icon: '/icons/folder.png' },
```
```ts
// Desktop.ts
const grid = createElement('div', 'desktop__icons');
const gridRight = createElement('div', 'desktop__icons desktop__icons--right');
for (const app of apps) {
  const icon = createAppIcon(app, 80, () => openWindow(app));
  (app.side === 'right' ? gridRight : grid).appendChild(icon);
}
el.append(grid, gridRight);
```
```css
/* app.css — z-index:3 is MANDATORY so icons sit above wallpaper filters */
.desktop__icons--right {
  top: 50%; left: auto; right: 40px;
  z-index: 3;
  transform: translateY(-50%);
  flex-direction: column; align-items: flex-end; max-width: none;
}
.desktop__icons { position: absolute; z-index: 3; /* ...left grid... */ }
```

## 2. Generate a PNG icon (`public/icons/make-icon.py`)

Pillow script (needs `pip install Pillow` — system python lacks PIL). Gradient + glyph → 128×128 PNG.
```bash
cd public/icons
python3 make-icon.py telegram.png "✈" "#2aabee" "#0a84ff"
python3 make-icon.py projects.png "{}" "#30d158" "#0a84ff"
python3 make-icon.py links.png "@" "#ff9f0a" "#ff453a"
```
NOTE: the script's rounded-rect mask is a **fallback, not a true squircle** (see squircle rule in SKILL.md). For macOS-style icons prefer copying the real Apple asset instead (next section).

## 3. Apple-style icon from `.icns` (true squircle)

Copy from Downloads, convert with `sips`, then resize to 128:
```bash
cp ~/Downloads/Photos_macOS_Golden_Gate_*.icns photos_raw.icns
cp ~/Downloads/Folder_Star_Alt_*.icns folder_raw.icns
sips -s format png photos_raw.icns --out photos_raw.png
sips -s format png folder_raw.icns --out folder_raw.png
sips -z 128 128 photos_raw.png --out photos.png
sips -z 128 128 folder_raw.png --out folder.png
rm -f *_raw.*
```
Apple's Photos/Folder PNGs are already squircle-shaped (transparent corners) — use as-is.

## 4. `ava.png` white-background gotcha

`ava.png` has a **solid white** background (not transparent). Do NOT use
`mix-blend-mode: multiply` (turns white bg black AND the black-clad figure
vanishes → black blob) or `filter: invert`. Render plain:
```css
.about-ava { mix-blend-mode: normal; filter: none; }
```
Centered, plain white square — the figure reads fine.

## 5. Wallpaper muting (galaxy) — blur → vignette → grain

In `src/app/app.css`, `.desktop__wallpaper`:
```css
.desktop__wallpaper canvas { filter: blur(2px); }                 /* 1. blur the galaxy */
.desktop__wallpaper::before {                                      /* 2. dim bright core */
  content:''; position:absolute; inset:0; pointer-events:none; z-index:1;
  background: radial-gradient(120% 120% at 50% 45%, rgba(0,0,0,.35), rgba(0,0,0,.55));
}
.desktop__wallpaper::after {                                       /* 3. film grain on top */
  content:''; position:absolute; inset:-20px; pointer-events:none; z-index:2;
  background-image: url("data:image/svg+xml,%3Csvg ... %3E%3CfeTurbulence type='fractalNoise' baseFrequency='2.4' numOctaves='2' stitchTiles='stitch'/%3E ... %3C/svg%3E");
  background-size: 140px 140px; filter: blur(0.3px);
  mix-blend-mode: overlay; opacity: .68;
}
```
Tuning: finer grain → higher `baseFrequency`; stronger grain → higher `opacity`.
Order matters: canvas-blur is the bottom layer, grain (`::after`, z-index 2) is on top.

**CRITICAL**: icon containers must have `z-index: 3` so they are NOT painted over by `::before`/`::after` (symptom: icons look noisy/dimmed = "under the filter").

## 6. Icon safe-area normalization (fix "one icon looks bigger")

PNG icons from different sources fill the 128×128 canvas by very different amounts
(measured content fill%): About 98, Language 100, Folder 73, Safari 67, Photos 67.
That makes Language/About *look* bigger than Safari/Photos even though every `<img>`
is rendered at the same 72–80px. The fix is **optical**, not geometric: bring all
icons to a single **safe-area** (content ≈ 75% of the canvas, centered).

`public/icons/normalize-icons.py` does this for any PNG (Pillow only, no numpy):
```bash
cd public/icons
python3 normalize-icons.py              # normalizes every *.png in the folder
python3 normalize-icons.py a.png b.png  # or just specific files
```
It tight-crops transparent edges (PIL `getbbox`), scales content to `SAFE_AREA=0.75`
of a 128×128 canvas by the longer side, and re-centers. After a pass, all icons
land at ~46–56% fill → identical optical weight.

**Keep new icons consistent**: `make-icon.py` already aims content at 75% (`pad =
int(size * 0.125)`). If you add an icon from a raw source (screenshot, downloaded
PNG), run `normalize-icons.py` on it so it matches the set. Do NOT hand-trim one
icon (e.g. only Language) — that leaves About still over-filled.

## 7. Favicon + tab title

`index.html`:
```html
<title>dlgrv.com</title>
<link rel="icon" href="/icons/w95_53.ico" />
```
`w95_53.ico` (a Win95-style .ico) was copied from `assets/win95-winxp_icons/` into
`public/icons/` and is served at `/icons/w95_53.ico`. The tab title is the literal
`dlgrv.com` (the floating brand string is also `'dlgrv.com'`, hardcoded in
`src/shared/ui/floating-brand.ts`). Earlier the favicon was `about.png`; the user
swapped it to the Win95 .ico for retro flavor.

## 8. About Me social-button colors (brand colors, white text)

In `content.ts` the link builder adds a per-network modifier class:
```ts
const a = createElement('a', `about-link twist about-link--${label}`);
// label is 'telegram' | 'github' | 'linkedin' (from profile.links keys)
```
CSS (`widgets.css`, inside `.window-content--about`):
```css
.about-link { color:#fff; border:2px solid currentColor; border-radius:20px; background:#1a1a1a; }
.about-link--telegram { color:#fff; border-color:#229ED9; }   /* TG blue */
.about-link--github   { color:#fff; border-color:#2ea043; background:#1a1a1a; } /* GREEN */
.about-link--linkedin { color:#fff; border-color:#0A66C2; }   /* LinkedIn blue */
```
Rule: **colored border (brand hue) + WHITE text** — colored text on the dark
window bg was unreadable (user caught it). GitHub is **green `#2ea043`**, NOT
grey/black (user said "github какой-то серый" then chose green). To recolor a
button, add/extend the `.about-link--<label>` rule — the class is derived from the
link label automatically.
