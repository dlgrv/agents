# About Me window — melonking × emojiwave restyle (Win98 chrome)

The About Me app (`id:'about'`, `theme:'win95'` in `src/entities/profile/model/profile.ts`)
keeps its **Win98 window chrome** but its *content* is a "personal homepage" in the
melonking.net / emojiwave.xyz / neocities Y2K style. Reference sites studied live:

- **melonking.net/melon?z=/me** — content loads in `<iframe src="/me">`. Decorative
  classes: `wiggle-hover`, `tilt`, `twist` (rotate), `breaker_melon`, `rocket`
  (clouds at sides). Body `background:#000; color:#ff0; font:Times New Roman serif`.
  Window frame: `border:3px double #0000a6; border-radius:15px; box-shadow:10px 10px
  60px <blue>`. Tons of animated gifs (rockets, melons, hearts) — `image-rendering:
  pixelated`.
- **emojiwave.xyz** — editorial typography: huge headings (80px, weight 800, Archivo/
  Inter), lots of whitespace, white-on-black, no borders. This is the "type as hero"
  inspiration for the big "Hi, I'm dlgrv!" title.

## Our implementation

- Content branch in `src/features/open-window/content.ts` (`id === 'about'`) builds:
  `.about-hero` (two rocket gifs from `https://melonking.net/images/graphics-rocket-
  736050.gif` flanking an `<h1 class="about-title">`), `<img class="about-ava" src="/ava.png">`
  (ava.png copied to `public/ava.png`, 2048x2048), intro `<p>`, `section()` helper
  (yellow `<h3>` + `<p>` + `melon3.gif` divider), `.about-links` (telegram/github pills
  with `.twist` hover-rotate), `.about-counter` (green pixel-font "You are visitor #NNNNNN").
- Styles in `src/widgets/widgets.css` under `.window-content--about`:
  `background:#0a0a0a; color:#ffe600; font-family:Archivo,Inter,sans-serif;` title
  `clamp(30px,5vw,52px); font-weight:800; text-shadow:2px 2px 0 #0000a6;` avatar
  `width:220px; height:220px; object-fit:contain; margin:0 auto 18px; mix-blend-mode:normal; filter:none`
  (NO border, NO blend — ava.png has a white bg, a border/blend looks broken; see SKILL.md ava.png rule);
  counter `font-family:'Geist Pixel Square',monospace; color:#00ff9c`.

## Social buttons (telegram / github / linkedin) — per-brand color, WHITE text

The user wanted the three pills colored like each network, NOT yellow. Final, verified
styling (in `src/widgets/widgets.css` under `.window-content--about`):

- `.about-links` = `position:absolute; top:140px; right:24px; flex-direction:column; align-items:flex-end`.
  This puts the buttons on the RIGHT, BELOW the "Hi, I'm dlgrv!" title (top:140px so they
  don't ride over the title), aligned with the top of the centered avatar.
- Two rows built in `content.ts`: `row1` = telegram + github, `row2` = linkedin (single, right-aligned).
  Each `<a>` gets class `about-link twist about-link--<label>` where label ∈ {telegram,github,linkedin}.
- Base `.about-link`: `border:2px solid currentColor; border-radius:20px; background:#1a1a1a; color:#ffe600`.
- Per-brand overrides (border color = brand; TEXT MUST BE WHITE for readability — colored text
  on the dark bg was rejected as unreadable):
  - `.about-link--telegram { color:#fff; border-color:#229ED9; }`  (Telegram blue)
  - `.about-link--github   { color:#fff; border-color:#2ea043; background:#1a1a1a; }`  (GitHub GREEN — user rejected grey/black, explicitly chose green)
  - `.about-link--linkedin { color:#fff; border-color:#0A66C2; }`  (LinkedIn blue)
- Do NOT make the button text the brand color — white only. Do NOT make github grey/black
  (user said "github какой-то серый" then "давай будет зеленый").

## Photos & Blog apps (empty macOS windows)

Added to `apps` in `profile.ts`:
- `{ id:'photos', name:'Photos', theme:'mac', side:'right', icon:'/icons/photos.png' }`
- `{ id:'folder', name:'Blog', theme:'mac', side:'right', icon:'/icons/folder.png' }`

Icons come from real Apple `.icns` in `~/Downloads`, converted with:
`cp ~/Downloads/<x>.icns . && sips -s format png <x>.icns --out <x>.png && sips -z 128 128 <x>.png --out <x>.png && rm <x>.icns`.
`photos.png` is already a true squircle (Apple Photos flower) — leave as-is. `folder.png` is a
macOS folder with a star.
They render as EMPTY macOS windows: `content.ts` has `else if (id === 'photos' || id === 'folder')`
→ a centered `.mac-window__placeholder` ("Здесь будут фотографии." / "Здесь будет мой блог и статьи.").
`side:'right'` puts them in the right-center vertical column (see SKILL.md desktop layout).

## Don't regress

To confirm the melonking content + scroll, write a throwaway Playwright spec that:
1. opens the app via `page.locator('.app-icon').filter({hasText:'About Me'}).click({force:true})`
2. `page.evaluate` reads `document.querySelector('.window-content--about')` ->
   `{scrollH, clientH, overflowY, hasCounter}` (expect `scrollH>clientH`, `overflowY:'auto'`)
3. scroll to bottom (`el.scrollTop = el.scrollHeight`) then screenshot + read `.about-counter` textContent.
Then DELETE the spec. This is the standard e2e diagnostic pattern (see e2e-diagnostic-pattern.md).

## Don't regress

- Keep `theme:'win95'` on the about app — converting it to 'mac' broke the type and the
  user wanted Win98. (The `AppInfo.theme` type only allows `'win95'`.)
- Keep the win95.css flex-column body fix or the content clips (see SKILL.md Pitfalls).
