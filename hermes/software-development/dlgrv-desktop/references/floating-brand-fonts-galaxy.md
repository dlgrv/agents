# Floating brand, fonts, galaxy polish (dlgrv)

## Floating brand (the "dlgrv" title, inteko-style)

There is **NO topbar / menu-bar** — the user removed it and explicitly corrected its
re-addition. The `dlgrv` title lives as a *floating* element "in the air":

- `src/shared/ui/floating-brand.ts` — `createFloatingBrand()` renders
  `<span class="floating-brand"><span class="floating-brand__nick">…</span><span class="floating-brand__caret"></span></span>`.
- Typing animation mirrors inteko exactly: start `setTimeout(tick, 250)`, then
  `nick.textContent = tag.slice(0, ++step)` every **110ms**; after the word is
  complete, `setTimeout(() => caret.classList.add('is-done'), 650)` fades the caret.
- Appended in `src/app/index.ts` as a sibling of desktop/window-layer/reset (NOT a bar).
- Position via modifier class (set in `app/index.ts`):
  - `floating-brand--bl` — bottom-left *(current default)*
  - `floating-brand--tc` — top-center
  - `floating-brand--br` — bottom-right, left of the Reset button (`right: 180px`)
- `pointer-events: none` so it never blocks clicks on the desktop/windows.

## Fonts (local, no Google Fonts dependency)

`src/app/styles/fonts.css` registers local `@font-face` (served from `public/fonts/`,
works offline / in webviews):

- `Geist Pixel Square` → `public/fonts/geist-pixel/GeistPixel-Square.woff2`
  — the REAL pixel font inteko uses for its title (their CSS var `--font-pixel`).
- `Geist Mono` → `public/fonts/geist-mono/*.woff2` — fallback (Vercel OFL).
- `Playfair Display` → `public/fonts/PlayfairDisplay-Bold.ttf` (pre-existing).

Stack on the brand: `'Geist Pixel Square', 'Geist Mono', 'Inter Tight', system-ui`.

### How we found the real inteko font (reusable technique — see website-clone skill)
inteko is a built SvelteKit/Vite site. The HTML `h1` uses
`font-family: var(--font-pixel), "Geist Mono", monospace;` but the variable value
is only in the bundled CSS, not the HTML. Grep the bundle CSS for
`--font-pixel:` → `"Geist Pixel Square"`, then the matching
`@font-face{font-family:Geist Pixel Square;src:url(../../../fonts/GeistPixel-Square.woff2)}`,
resolve the relative URL against the origin, and `curl` it from `/fonts/…`.

## Galaxy wallpaper (mono + film grain)

- **Monochrome toggle**: `src/shared/ui/galaxy/generate.ts` has
  `const GALAXY_MONOCHROME = true;` near `createColorGrade`. When true, after
  computing luminance it returns `[gray, gray, gray]` (with `*1.12` brightness lift
  to compensate for lost color energy). Set `false` to restore color.
- **Grain overlay**: `.desktop__wallpaper::after` in `src/app/app.css`:
  SVG `feTurbulence` (fractalNoise, `baseFrequency:1.6`, `numOctaves:2`) as a
  data-URI background, `filter: blur(0.6px)` for diffusion, `mix-blend-mode: overlay`,
  `opacity:.34`. To strengthen: raise `opacity` and `baseFrequency`; lower `background-size`.
  `inset:-20px` + `pointer-events:none` so the blur doesn't reveal edges or block clicks.
- Galaxy is paused on `visibilitychange` (renderer `setVisible(false)` cancels rAF);
  no CPU waste when the tab is hidden.
