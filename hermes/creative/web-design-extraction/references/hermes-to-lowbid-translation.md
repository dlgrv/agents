# Hermes → LowBid Design Translation

Concrete mapping from the Hermes Agent (hermes-agent.nousresearch.com) design system to the LowBid SSP landing page. Created 2025-07-12 during a live redesign session.

## Color palette mapping

| Hermes role | Hermes HEX | LowBid role | LowBid HEX | Notes |
|---|---|---|---|---|
| Background (electric blue) | `#0000f2` | Background (near-black) | `#0d0d0b` | Keep LowBid's dark brand |
| Text (off-white) | `#f5f5f5` | Text (warm off-white) | `#e8e6df` | LowBid's warmer tone |
| Accent (electric lime) | `#edff45` | Accent (acid yellow) | `#d4f000` | LowBid's signature yellow |
| Paper (dropdowns) | `#fff` | Dropdown/inverted bg | `#e8e6df` | |
| — | — | Alarm (CTA) | `#ff3535` | Kept from LowBid v1, Hermes has no equivalent |

## Typography mapping

| Hermes font | CSS var | LowBid substitute | Google Fonts URL | Notes |
|---|---|---|---|---|
| Sigurd (displayFont) | `--font-sigurd` | **Playfair Display** | `family=Playfair+Display:ital,wght@0,300..900;1,300..400` | High-contrast serif, variable weight 300-900. Light (300) for massive headlines. |
| CourierPrime (monoFont) | `--font-mono` | **Space Mono** | `family=Space+Mono:ital,wght@0,400;0,700;1,400` | Already in LowBid v1, kept as-is |
| RulesVariable (rulesFont) | `--font-rules` | — (skipped) | — | Decorative font not needed for LowBid |
| — | — | **DM Sans** | `family=DM+Sans:ital,wght@0,300..600;1,400` | Body text, kept from LowBid v1 |

## Container-query scaling tuning

Hermes uses `--u: max(calc(100cqw / 2360), 0.58px)` where 2360 is their max design width.

For LowBid (standard 1280px max content width), the same pattern works but with a different divisor:
```css
--u: max(calc(100cqw / 2360), 0.58px);  /* kept same — scales proportionally */
```

The `--u-anchor` of `0.58px` prevents sub-pixel sizes on narrow screens. Don't remove it.

Mobile breakpoint formula:
```css
@media (max-width: 767px) {
  :root {
    --u: min(calc(100cqw / 760), var(--u-anchor));
    --gutter: calc(48 * var(--u));  /* tighter gutters on mobile */
  }
}
```

## Visual effects: direct ports

These effects copied from Hermes with minimal modification:

| Effect | Hermes value | LowBid value | Change reason |
|---|---|---|---|
| Frame border | `2.5 * (0.5vw + 0.5vh)` → ~23px on 1280px | `1vw + 0.5vh` → ~15px | Too thick on typical viewports |
| Noise blend mode | `color-burn` | `overlay` | `color-burn` too strong on near-black bg |
| Noise opacity | 0.2 | 0.15 | Subtler on dark |
| Vignette opacity | 0.2 | 0.3 | Stronger vignette for darker bg |
| Ghost wordmark blend | `exclusion` | `exclusion` | Direct copy |
| Ghost wordmark opacity | 0.2 | 0.08 | More subtle |
| `::selection` | accent bg, blue text | accent bg, dark text | Direct copy pattern |

## Visual effects: NOT ported

| Hermes effect | Why skipped |
|---|---|
| Arc hover animation | Complex keyframe animation, not essential for landing page |
| Parallax scrolling | Requires JS scroll handlers, adds complexity |
| Video hero | LowBid has no hero video |
| Footer wordmark (100dvh) | LowBid footer is simpler |

## Body-level fixes (pitfalls hit during implementation)

1. **Removed `width: 100dvw; margin-inline: calc(50% - 50dvw)`** from body — caused 2px horizontal scroll. `overflow-x: hidden` on body + `overflow-x: clip` on html is sufficient.

2. **Added `text-transform: none`** on body paragraphs, section descriptions, and card text — `uppercase` on body made paragraphs unreadable. Uppercase is applied only to: headings, nav links, eyebrows, labels, button text.

3. **Frame border sizing** — `calc(2.5 * (0.5vw + 0.5vh))` = 23px on a 1280×633 viewport. Reduced to `calc(1vw + 0.5vh)` = ~15px. For even smaller screens, consider `clamp(8px, 1.2vw, 16px)`.

## Result file structure

```
landing_v2/
├── index.html     (~20KB — full markup with JSON-LD schema)
├── style.css      (~24KB — design system: tokens, base, effects, components, responsive)
├── favicon.svg    (copied from v1)
├── og-image.svg   (copied from v1)
├── robots.txt     (copied from v1)
├── sitemap.xml    (copied from v1)
└── llms.txt       (copied from v1)
```

## Verification checklist (browser_console based)

1. Frame border width: `getComputedStyle(document.querySelector('.frame')).borderWidth` → ~15px
2. Font loaded: `document.fonts.check('300 60px "Playfair Display"')` → true
3. No horizontal scroll: `document.documentElement.scrollWidth <= document.documentElement.clientWidth`
4. Grid columns: `getComputedStyle(document.querySelector('.features-grid')).gridTemplateColumns` → 3 equal columns
5. Section visibility: all sections have `width > 0 && height > 0`
6. CSS brace balance: `{}` count matches
7. HTML tag balance: `<section>` / `</section>` and `<div>` / `</div>` counts match
