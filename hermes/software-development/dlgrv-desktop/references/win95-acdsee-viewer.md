# Windows 95 ACDSee-style photo album (`photos:<trip>`)

The Photos album window is a 1v1 recreation of **ACDSee** (the dominant 95-era image
viewer). It opens as a SEPARATE win95 window when you click a trip folder in the white
Finder-style root Photos window. This file is the authoritative layout spec — read it
before touching `mountAlbumWindow` in `src/features/open-window/content.ts` or the
`.win95-acdsee` CSS in `src/shared/config/win95.css`.

## Two modes

**Browser mode** (default, after open): tree + thumbnail grid.
**Viewer mode**: double-click a thumbnail → one large photo. Toolbar `◄ / ►` step,
`+ / −` zoom, `Up` returns to Browser.

## DOM structure (built by `mountAlbumWindow`)

```
.window-content--win95.win95-acdsee        ← root (flex column, h:100%)
  .acdsee__toolbar                         ← flex row of 3D buttons
    button.acdsee__btn "Up"                → showBrowser()
    button.acdsee__btn "Thumbs" (disabled) → showBrowser() (already there)
    button.acdsee__btn "◄" (prev)         → step(-1)
    button.acdsee__btn "►" (next)         → step(1)
    button.acdsee__btn "+" (zoomIn)       → zoom(+0.25)
    button.acdsee__btn "−" (zoomOut)      → zoom(-0.25)
    button.acdsee__btn "Slide" (disabled) → noop
  .acdsee__body                            ← flex row (fills remaining height)
    .acdsee__tree                          ← flex:0 0 130px, white, inset border
      .acdsee__tree-node "📁 photos"
      .acdsee__tree-node.acdsee__tree-node--active "📁 <tripTitle>"   (navy #000080)
    .acdsee__pane                          ← flex:1, overflow:auto
      Browser: .acdsee__grid (flex-wrap) of
        .acdsee__cell (.is-active when idx===i)
          img.acdsee__cell-img (90×70 cover, loading=lazy)
          .acdsee__cell-cap (filename, ellipsis)
        click → idx=i + markActive(); dblclick → showViewer(i)
      Viewer: .acdsee__pane--viewer (dark, centered) >
        .acdsee__stage > img.acdsee__view-img (object-fit:contain)
```

State vars inside the closure: `photos: PhotoMeta[]`, `idx`, `zoomLvl` (1=fit).
`step(d)` wraps modulo `photos.length`; if pane has `.acdsee__pane--viewer` it calls
`showViewer(idx)`, else just `markActive()`. `showViewer` rebuilds only the stage (does
NOT recreate the grid), so `markActive()` re-applies `.is-active` to the persisted grid
cells. `zoom(d)` clamps 0.25–4 and rescales `.acdsee__view-img` max-w/h (1 = 100%, else
`zoomLvl*100%`).

## CSS tokens (in `src/shared/config/win95.css`)

| token | value |
|---|---|
| body bg | `#c0c0c0` |
| font | `"MS Sans Serif", Tahoma, sans-serif`, 12px |
| toolbar btn | bg `#c0c0c0`, `border:2px outset #dfdfdf`, `:active:not(:disabled){border-style:inset}`, disabled `#808080` |
| tree | `flex:0 0 130px`, bg `#fff`, `border:2px inset #dfdfdf` |
| tree active node | bg `#000080`, color `#fff` |
| body (tree+pane row) | `display:flex; overflow:hidden; flex:1; min-height:0` |
| pane (browser) | bg `#808080`, `overflow:auto` |
| pane (viewer) | bg `#404040`, **flex column** `align-items:stretch; justify-content:flex-start; overflow:hidden` |
| stage (viewer) | `flex:1; min-height:0; padding:8px; display:flex; centered` |
| caption | `flex:0 0 auto`, bg `#808080`, `border-top:2px groove #c0c0c0`, white 12px centered; `-date` 10px `#d8d8d8` |
| cell | width 96px, bg `#c0c0c0`, `border:2px solid transparent`; `.is-active{border-color:#000080}` |
| cell-img | 90×70, `object-fit:cover` |
| cell-cap | 10px, ellipsis |
| view-img | `object-fit:contain`, white border, `box-shadow:1px 1px 0 #000` |

⚠️ The `.acdsee__tree` / `.acdsee__pane` MUST be wrapped in a flex-row `.acdsee__body`,
NOT absolutely positioned. An earlier attempt used `position:absolute` on the tree +
`margin-left` on the pane and the tree painted over the toolbar / broke layout. The
flex-row body is the working fix.

## Plan + e2e

- Plan file: `.hermes/plans/2026-08-27_021500-photos-win95-acdsee.md`
- e2e: `e2e/photos-acdsee.spec.ts` (asserts win95 class, tree active node «Гонконг»,
  9 cells, dblclick→viewer, ► steps, Up→grid with nth(1) is-active; plus
  "vertical photo fits", "arrow keys navigate", "date always shown, comment only when
  present", and "trip folders behave like macOS Finder" — the latter opens the album
  via `.photos-folder().dblclick()`, see the Finder note in
  `references/content-apps-photos-blog-wishlist.md`).
- **When the root Photos folder behavior changes, update EVERY spec that opens an
  album.** When single-click-open became dblclick-open (Finder behavior, 2026-08),
  4 specs silently timed out because they still did `.photos-folder().click()` — the
  album window simply never appeared. Grep e2e for `.photos-folder` and switch all
  open-actions to `dblclick()`.

## Notes / decisions

- User picked ACDSee over the macOS dark style and over Paint (Paint is an editor, not
  a viewer). "Самое популярное решение" → ACDSee.
- `Thumbs` and `Slide` are **disabled placeholders** (like the originals were inactive
  in Browser mode). Wire up a real slide-show later if wanted — not in scope.
- Trip title in the tree is hardcoded-mapped (`hongkong→Гонконг`, `murmansk→Мурманск`)
  because `renderWindowContent` only knows the trip `id`, not its display name.
  If you add trips, extend the map OR fetch `/photos/manifest.json` for the title.
- Comments: currently only the **filename** shows under each thumbnail (ACDSee-style).
  If the user later wants the `comment` field shown there too, append it to
  `.acdsee__cell-cap` (the manifest already carries `comment`).
- Vision scored the rendered Browser at 10/10 similarity to ACDSee 95/98.

## Caption under the photo (comments/dates) — added 2026-08

**Final behavior (user-requested "поровну" — every photo gets the same info strip):**
`showViewer` renders `.acdsee__caption` under the photo whenever `ph.comment || ph.date`
(so the strip is CONSTANT for all photos, like a statusbar), in this order:
1. `.acdsee__caption-text` — the comment, only if `ph.comment` is non-empty.
2. `.acdsee__caption-date` — the EXIF date, only if `ph.date` is non-empty (present for all real photos).

No comment → date-only strip; no date → comment-only strip; neither → no strip at all
(never an empty bar). Comment ABOVE date is the user-approved order (he liked the first
working version where the note sat above the small grey date line).

**Flex layout requirement:** `.acdsee__pane--viewer` must be
`flex-direction: column; align-items: stretch; justify-content: flex-start; overflow: hidden`,
`.acdsee__stage` gets `flex:1; min-height:0` (NOT `height:100%` — that broke with a
caption sibling), and `.acdsee__caption` is `flex: 0 0 auto` with
`border-top: 2px groove #c0c0c0; background:#808080; color:#fff; text-align:center`
(`-date` line: 10px `#d8d8d8`). Photo fits the remaining space via the existing
fit-to-container chain; caption is always visible with NO scrolling.

**Known tradeoff the user accepted:** strip height varies (2 lines with a comment,
1 with date-only). If the user asks for fixed height to stop the jumping, add a
`min-height` reserving two lines.

**Manifests carry examples:** a few photos in `public/photos/{hongkong,murmansk}/manifest.json`
have filled `comment` strings (user writes these himself — treat any user-supplied
comment text as verbatim/sacred like all his copy). e2e:
"date always shown, comment only when present" (nav with ArrowRight/ArrowLeft, asserts
`.acdsee__caption-text`/`-date` counts flip 1/0 → 0/1 → 1/1).

## Pitfall: vertical photos don't fit (max-height:100% circular dependency)

**Symptom:** in Viewer, horizontal photos fit the window but **vertical photos overflow
and trigger pane scroll** instead of shrinking to fit. (Discovered 2026-08.)

**Root cause:** `img { max-height: 100% }` resolves against its containing block. The
`img` lived inside `.acdsee__stage`, which was `display:block` with **no height** — so
its height = content height (the image itself) → circular: img capped at 100% of stage,
stage grows to img, img ends at natural height, overflows `.acdsee__pane` (`overflow:auto`)
→ scroll instead of fit. Horizontal photos "worked" only because their width hit
`max-width:100%` (stage width = pane width).

**Fix (best-practice fit-to-container):** make `.acdsee__stage` itself height-limited and
a flex centerer, so `img.max-height:100%` resolves against the real limiter (`.pane`,
which is bounded by the window through the `min-height:0` flex chain body→pane):

```css
.acdsee__stage {
  height: 100%;
  width: 100%;
  box-sizing: border-box;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.acdsee__view-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;   /* keeps aspect ratio, never stretches */
  background: #fff;
  border: 2px solid #fff;
  box-shadow: 1px 1px 0 #000;
}
```

Also: **do NOT set inline `maxWidth/maxHeight` from JS when `zoomLvl===1`** — let CSS own
the fit. In `mountAlbumWindow`, only apply inline `maxWidth = zoomLvl*100%` /
`maxHeight='none'` when `zoomLvl !== 1` (zoom is relative to the *natural* size, like
ACDSee: Best Fit inlines, 100% = natural, + enlarges from natural). When zoom returns to
1, clear the inline styles (`im.style.maxWidth = ''; im.style.maxHeight = ''`) so CSS
re-takes control. e2e: `e2e/photos-acdsee.spec.ts` "vertical photo fits in viewer without
scroll" asserts `imgBox.height ≤ paneBox.height`.

## Keyboard arrow navigation (added 2026-08)

**Requirement:** arrow keys ←/→ switch photos while the album window is open.

**Implementation (in `mountAlbumWindow`):** a `document`-level `keydown` listener that:

```ts
const onKey = (e: KeyboardEvent) => {
  if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
  // only when THIS album window is the focused one
  const active = document.querySelector<HTMLElement>(
    '.mac-window.is-focused[data-window-id^="photos:"]',
  );
  if (!active || !active.contains(root)) return;
  e.preventDefault();
  step(e.key === 'ArrowRight' ? 1 : -1);
};
document.addEventListener('keydown', onKey);
root.addEventListener('DOMNodeRemovedFromDocument', () =>
  document.removeEventListener('keydown', onKey));
```

Why `document` + focused-window check (NOT attaching to the window element or `root`):
the `.mac-window` has **no `tabindex`** and is never programmatically `.focus()`-ed, so a
`keydown` listener on the window/`root` would only fire if focus happened to be inside an
interactive child. The `document` listener fires whenever focus is anywhere on the page
(except the browser URL bar), and the `is-focused` guard ensures only the active album
reacts — so arrows never steal input from other windows. `DOMNodeRemovedFromDocument`
cleans the listener when the window is closed (no leak). `step()` already does modulo
wrap-around, so `←` from photo 0 → last photo.

e2e "arrow keys navigate photos when album active" presses ArrowRight/ArrowLeft and
asserts the `.acdsee__view-img` `src` changes (in Viewer mode there are no `.acdsee__cell`
nodes, so test by `src`, not by `.is-active` on cells).
