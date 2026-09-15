# Content apps: Photos / Blog / Wishlist (2026-08 session)

Manifest-driven content windows in `src/features/open-window/content.ts`. Vite cannot
list `/public` at runtime, so JSON manifests are the source of truth for every app.

## Photos — Finder-style (root window + dynamic album windows)

**User's explicit design (2026-08-27):** «это будет просто белое окно macos внутри
которого будут папки … при нажатии на папку открывается новое окно для этого альбома».
Do NOT revert to the single-window trips→album→detail state machine or to a dark root.

1. **Root Photos window** (`id: 'photos'`) — WHITE mac window, behaves 1:1 like a
   macOS Finder icon view (user: «чтобы было 1в1 как на macos»). Content =
   `.photos-folders` (flex-wrap grid) of `.photos-folder` buttons: folder icon
   (`/icons/folder-common.png` — Apple `Folder_Common` icns converted), trip name.
   **NO photo count under the name** (Finder doesn't show one) and **NO hover/active
   background** (`cursor: default`, not pointer). **Single click = SELECT**: adds
   `.is-selected` (blue pill `#0a60ff` + white text on the `.photos-folder__name`
   label only — the icon never gets a background), moves selection when another
   folder is clicked, clears when clicking empty window space. **Double click
   (`dblclick`) = OPEN the album window.** Do NOT restore hover backgrounds,
   a `meta` count line, or single-click-open — the user explicitly wanted
   Finder behavior.
2. **Album window** (`id: 'photos:<trip>'`, e.g. `photos:hongkong`) — a SEPARATE
   **Windows 95 ACDSee-style** window, opened on folder click via
   `openWindowById('photos:<trip>', tripTitle)`. The window is created with
   `theme: 'win95'` (see dynamic-window pattern) so it gets the win95 chrome +
   `.window-content--win95` body. The user explicitly chose **ACDSee** (the most
   popular 95-era photo viewer) over the macOS dark style — do NOT revert to a dark
   macOS Photos album. See `references/win95-acdsee-viewer.md` for the full layout,
   CSS tokens, and the Browser→Viewer state machine. Title = trip name.

   **ACDSee layout (1v1 with the 95-era ACDSee Browser):** toolbar (`Up`, `Thumbs`
   disabled, `◄`, `►`, `+`, `−`, `Slide` disabled) + left **folder tree**
   (`photos/` → `<trip>` highlighted navy) + right **thumbnail grid** (cell =
   90×70 cover img + filename caption below). Double-click a thumbnail → **Viewer**
   mode: single large photo centered on dark `#404040` stage, `◄/►` step through,
   `+ / −` zoom (1 = fit, 0.25–4), `Up` returns to the grid. Selected thumbnail
   gets `.is-active` (navy border) in both modes.

### Dynamic-window pattern (FSD-clean, reusable)

`features` may not import `widgets` (FSD). To spawn arbitrary-id windows from
`features/open-window/content.ts`:

- `src/features/window-controls/index.ts` — registry mirroring `registerWindowControls`:
  `registerWindowOpener(fn)` / `openWindowById(windowId, title)`. `features` calls the
  latter; the module-level `opener` is set by app.
- `src/app/index.ts` — registers the implementation: ids starting `photos:` →
  `openDynamicWindow(windowId, title, 720, 560, 'win95')` (**note the 5th `theme`
  arg — it is what makes the album a win95 window, not dark mac**).
- `src/widgets/window-manager/index.ts` — `openDynamicWindow(id, title, w, h, theme)`
  (5th param `theme: 'mac' | 'win95' = 'mac'`) like `openWindow` but for ids outside
  `apps[]`; re-clicking an open id focuses the window instead of duplicating (same
  `existing` check + synthetic `pointerdown`).
- `renderWindowContent` routes `id.startsWith('photos:')` →
  `mountAlbumWindow(body, id.slice('photos:'.length))` BEFORE any other branch.
  `mountAlbumWindow` adds `window-content--win95 win95-acdsee` classes to the root and
  builds the ACDSee tree+grid+viewer.

Gotcha: album windows persist their geometry via `persist()` like normal windows, and
`windowControls.close` in app/index.ts works for dynamic ids unchanged (it queries by
`data-window-id`). But `restoreWindows` skips them on reload (only `apps[]` ids are
restored — `findApp` misses `photos:*`). Accepted tradeoff for now; do not "fix" by
adding trips to `apps[]` (they'd get desktop icons).

### Per-trip manifest `/photos/<trip>/manifest.json`
```json
[{ "src": "/photos/hongkong/XXX.jpeg", "comment": "", "date": "2026-03-11 15:14" }]
```
- `comment` — optional; empty → not rendered, no reserved space (explicit user requirement).
- `date` — extracted from EXIF at manifest-generation time (see EXIF regex below).
- Main `/photos/manifest.json`: `{ id, title, year, thumb, count }`; thumb = first photo.
- To add a trip: `mkdir public/photos/<id>/`, drop JPEGs, generate the per-trip manifest
  (EXIF script), add an entry to the main manifest. UI picks it up with no code change.
- Album fetches are cached in `photosCache` per window mount.

### Palettes
**Root (white/Finder):** window content `#fff`, folder icon 64px, name 12px `#111`
with `padding:1px 6px; border-radius:5px` (so the selection pill fits it), selection
`.is-selected .photos-folder__name { background:#0a60ff; color:#fff }` (label only,
icon untouched), NO hover/active bg, `cursor: default`, folder button width 92px,
grid gap `18px 26px`, padding 22px.
**Album (Windows 95 ACDSee):** lives in `src/shared/config/win95.css` under
`.window-content--win95.win95-acdsee`. Body bg `#c0c0c0`, MS Sans Serif 12px. Toolbar
buttons = 3D outset `#c0c0c0` (`border:2px outset #dfdfdf`), disabled greyed.
Tree = white `#fff` with `border:2px inset`, active node navy `#000080` white text.
Pane bg `#808080` (browser) / `#404040` (viewer). Thumbnail cell 96px wide, img
90×70 cover, caption 10px filename. Viewer img `object-fit:contain` white border.
Full token list + the Browser/Viewer DOM structure: `references/win95-acdsee-viewer.md`.

### EXIF dates from macOS `file` output
`file` prints `datetime=YYYY:MM:DD HH:MM` (= sign). Working extractor:
```python
m = re.search(r'datetime[=:](\d{4}:\d{2}:\d{2}) (\d{2}:\d{2})', out)
date = m.group(1).replace(':', '-') + ' ' + m.group(2)
```
Blank dates = regex mismatch (check the `[=:]`), not missing EXIF.

## Blog (`folder` id)

- `public/blog/index.json`: `[{ slug, title, date, readingTime, excerpt, cover }]`
- Articles: `public/blog/<slug>/index.md`; inline images `![](/blog/<slug>/x.jpg)` work
  (public/ is web-root). Rendered by a tiny regex markdown→HTML in `openBlogPost(slug)`
  (h1-h3, bold, code, lists, paragraphs) — `marked` deferred until needed.
- Window content class `window-content--blog`.

### Publishing a new article (standalone page, verified 2026-09-09)

1. Write `public/blog/<slug>/index.md` (title `#`, sections `##`, ~9 min reads OK).
2. Add an entry to `public/blog/index.json` (`slug, title, date YYYY-MM-DD,
   readingTime, excerpt`).
3. `npm run build:pages` — regenerates BOTH `public/blog/<slug>/index.html` and the
   list page `public/blog/index.html` (the list is NOT hand-edited; it stays a
   placeholder until the first article exists).
4. Add `<url><loc>https://dlgrv.com/blog/<slug>/</loc><lastmod>…</lastmod></url>` to
   `public/sitemap.xml` (a vitest gate asserts the slug is present).
5. Update `public/blog.md` — the markdown twin of the blog index, with a link to the
   new post.
6. Verify: `npx vitest run src/__tests__/agent-readable.spec.ts` is the CONTENT gate
   (sitemap contains the slug, generated article HTML ≥500 chars, blog.md twin in
   sync) — 19 checks as of 2026-09. Plus `npx vitest run` (full) and
   `npx biome check public/blog/` for the rest.

**Renderer dialect (cost a full rewrite in 2026-09):** the standalone-page markdown→HTML
converter (like the blog-window `openBlogPost` one) supports ONLY h1-h3, `**bold**`,
inline `` `code` ``, `-`/`1.` lists, paragraphs. GitHub ``` fences and `>` quotes are
NOT supported: a fenced code block lands in the HTML as literal backtick/`<code>` soup,
a `>` quote renders the `>` raw. Write formulas/code lines as standalone inline-code
paragraphs (`` `z = w·x + b` — что делает ``) and quotes as plain paragraphs. After
build, sanity-check the generated HTML for artifacts (stray `` `` ``, `<p></code>`,
unbalanced `<code>` pairs) before reporting done.

## Wishlist (`wishlist` id)

## Wishlist (`wishlist` id)

- `public/wishlist/manifest.json`: `[{ id, title, image, caption?, price? }]`
- Cards = image + caption below (explicit user shape: «изображение и подпись у изображения»).
- Icon: Apple `Folder_Light_Pink_Saves` `.icns` from ~/Downloads →
  `sips -s format png x.icns --out x.png && sips -z 128 128 x.png --out wishlist.png`,
  then `python3 normalize-icons.py wishlist.png`. Verified optical widths match the rest
  of the set (94–96px content bbox on all icons — 1-2px variance is fine).

## Placeholder images

Never `write_file` an image (writes ASCII). 1×1 transparent GIF via python binary mode:
```python
import base64
open(p,'wb').write(base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'))
```

## e2e (verified flow)

Hide auto-opened windows first, then click icons by `img.app-icon__img[alt="Photos"]`:
```ts
await page.locator('.mac-window').evaluateAll(els => els.forEach(e => (e as HTMLElement).style.display='none'));
```
Finder flow spec: 2 folders in the white root → **double-click** first folder (single
click only selects — Finder behavior; every spec that opens an album must use
`.photos-folder().dblclick()`, single `.click()` leaves the album unopened and 4 specs
timed out on exactly this) → assert NEW window
`.mac-window[data-window-id="photos:hongkong"]` exists (count 1) and
`toHaveClass(/mac-window--win95/)`, 9 `.acdsee__cell` thumbnails, tree node
`.acdsee__tree-node--active` text «Гонконг» → `.acdsee__cell` dblclick →
`.acdsee__pane--viewer` + `.acdsee__view-img` appear → `►` steps, `Up` returns to
`.acdsee__grid` with nth(1) `.is-active` → re-click folder → still exactly 1 album
window (focus, not duplicate). Finder-selection spec: hover → folder bg stays
`rgba(0,0,0,0)`; single click → `.is-selected` + name pill `rgb(10, 96, 255)`;
clicking the 2nd folder moves the selection; dblclick opens. Playwright `console.log`
output is not greppable from the test runner output — use
`expect(...).toEqual(...)` assertions or write values into the error context instead.
Note: Playwright `expect(locator).not.toHaveText('')` is INVALID syntax (`.not` applies
to matchers, not as `.not()` call) — use `not.toHaveText('')`.
