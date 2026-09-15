# Hermes Agent (hermes-agent.nousresearch.com) — Design Breakdown

Extracted 2025-07-12 using the browser_console extraction workflow. This is a complete design analysis of the Nous Research Hermes Agent website.

## Two design systems on one domain

| | Landing (`/`) | Docs (`/docs`) |
|---|---|---|
| Framework | Next.js + Tailwind | Docusaurus |
| Style | Art-directed, editorial, brutalist | Functional dark docs |
| Theme | Electric blue dominant | Dark grey + gold accent |

## Landing page — full breakdown

### Color palette

| Role | HEX | CSS variable |
|---|---|---|
| Background (electric blue) | `#0000f2` | `--color-hermes`, `--hw-bg` |
| Text (off-white) | `#f5f5f5` | `--color-hermes-fg`, `--hw-fg` |
| Accent (electric lime) | `#edff45` | `--color-hermes-accent`, `--hw-accent` |
| Paper (dropdowns) | `#fff` | `--color-hermes-paper`, `--hw-paper` |
| Dropdown text | `#0000f2` | (same as bg) |
| Dropdown hover | `#eceaf5` | `--hermes-grey-100` |
| Selection | lime bg, blue text | `::selection` |

3 colors create the entire palette. No gradients in the main background.

### Typography

**3 custom variable fonts** (loaded as woff2 via Next.js):

| Font | CSS var | Role | Weight range |
|---|---|---|---|
| Sigurd (displayFont) | `--font-sigurd` | Headlines, nav, body | 300–800 |
| CourierPrime (monoFont) | `--font-mono` | Monospace, terminal | 400 |
| RulesVariable (rulesFont) | `--font-rules` | Decorative | 100–900 |

**Key sizes** (desktop, all scale via container queries):

| Element | Size | Weight | Letter-spacing |
|---|---|---|---|
| H1 (hero) | ~76px | 300 (light) | 0.03em |
| H2 (sections) | `72 * --u` (~42px) | — | — |
| Nav links | ~12.8px | 800 (extrabold) | 0.03em |
| Nav wordmark | ~23.2px | 800 | 0.03em |
| Eyebrow labels | `18 * --u` (~10px) | — | — |
| Body text | `21 * --u` (~12px) | — | — |
| Footer wordmark | 24.3cqi | 300 | 0.03em |

**All text is UPPERCASE** — `text-transform: uppercase` on `.hermes-web` root.

**Font weight contrast is extreme**: light (300) on massive headlines vs. extrabold (800) on tiny nav links.

### Container-query scaling system

```css
.hermes-web {
  container-type: inline-size;
  --u-anchor: 0.58px;
  --u: max(calc(100cqw / 2360), var(--u-anchor));
}
```

All sizes are multiples of `--u`:

| Token | Formula | Desktop value |
|---|---|---|
| `--hw-gutter` | `210 * --u` | ~121px |
| `--hw-gap` | `30 * --u` | ~17px |
| `--hw-edge` | `93 * --u` | ~54px |
| `--hw-frame` | `2.5 * (0.5vw + 0.5vh)` | viewport-relative |
| `--hw-text-eyebrow` | `18 * --u` | ~10px |
| `--hw-text-body` | `21 * --u` | ~12px |
| `--hw-text-h3` | `72 * --u` | ~42px |
| `--hw-wordmark-size` | `24.3cqi` | container-relative |

Mobile breakpoint (`max-width: 767px`):
```css
--u: min(calc(100cqw / 760), 0.58px);
--hw-gutter: calc(48 * --u);
```

### Layout

**Nav**: `position: absolute; display: grid; grid-template-columns: 1fr auto 1fr; padding: calc(50 * --u) var(--hw-gutter); z-index: 20;`

**Hero**: `display: flex; flex-direction: column; min-height: calc(1360 * --u); overflow-x: clip;` with `align-items: flex-start` on desktop.

**Scroll container**: `padding: var(--hw-frame) var(--hw-frame) 0; margin-bottom: var(--hw-footer-h); pointer-events: none;` — children re-enable `pointer-events: auto`.

### Visual effects

| Effect | Implementation |
|---|---|
| **Frame border** | `position: fixed; inset: 0; border: var(--hw-frame) solid var(--hw-bg); z-index: 100; pointer-events: none;` |
| **Noise texture** | SVG `feTurbulence` (fractalNoise, baseFrequency 0.72, numOctaves 4, stitchTiles) as data URI background. `mix-blend-mode: color-burn; opacity: 0.2; background-size: 12.8rem 12.8rem;` |
| **Vignette** | `radial-gradient(120% 90% at 50% 42%, transparent 50%, var(--hw-bg) 100%); opacity: 0.2;` |
| **Ghost text** | Wordmark with `mix-blend-mode: exclusion; color: var(--hw-accent); opacity: 0.2;` |
| **Arc hover** | Animated border stroke on hover: `animation: 2.23s linear infinite hw-arc-stroke;` |
| **Parallax** | `transform: translate3d(0, var(--py), 0); will-change: transform;` |
| **Scrollbars** | `width: 0.25rem; scrollbar-color: transparent transparent;` — visible on hover at 20% opacity |
| **Selection** | `background: var(--hw-accent); color: var(--hw-bg);` |

**Noise SVG data URI** (reusable):
```
data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.72' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E
```

### What's NOT there (design constraints)

- ❌ No `border-radius` anywhere (everything is 0px)
- ❌ No box-shadows on cards/buttons
- ❌ No gradients in background
- ❌ No card backgrounds or borders (features are pure text)
- ❌ No icons in navigation (text + logo only)
- ❌ No `backdrop-filter` on nav (it's `position: absolute`, not `fixed`)

### Hero art positioning (exact values)

The hero illustration (`hero-art.webp`, 1129×1418px) is positioned with exact container-query units:

```html
<img class="hw-hero-art" style="
  position: absolute;
  top: calc(219 * var(--u));
  right: calc(135 * var(--u));
  z-index: 2;
  width: calc(1128 * var(--u));
  max-width: none;
  mix-blend-mode: lighten;
  pointer-events: none;
  user-select: none;
" aria-hidden="true">
```

Key details:
- `mix-blend-mode: lighten` — the blue background shows through the artwork's dark areas, creating a luminous effect
- `max-width: none` — overrides default img constraints so it can overflow
- Hidden on mobile: `max-md:hidden` (display: none at < 768px)
- `sizes="48vw"` — responsive image hint
- `fetchpriority="high"` — eager loading for above-the-fold art

### Images

All `.webp` via Next.js Image optimizer (`/_next/image?url=...&w=3840&q=75`):
- `hero-art.webp` — hero illustration (1129×1418, positioned top-right with `mix-blend-mode: lighten`)
- `platform-art-{mac,windows,linux}.webp` — platform cards
- `badge.webp` — Hermes logo
- `feature-{connect,memory,automation,tasks,browse,sandbox}.webp` — 6 feature illustrations
- `nous.webp` — Nous Research logo

### Dropdown component

```css
.hw-dropdown {
  --hermes-primary: #0000f2;
  --hermes-white: #f5f5f5;
  --hermes-grey-100: #eceaf5;
  --hermes-dropdown-bg: var(--hermes-white);  /* inverted: white bg */
  --hermes-dropdown-fg: var(--hermes-primary); /* blue text on white */
  --hermes-dropdown-hover: var(--hermes-grey-100);
  --hermes-outline-inset: 2px 0 0 0 var(--hermes-line), -2px 0 0 0 var(--hermes-line), ...;
}
```

Dropdowns invert the color scheme: white background, blue text.

## Docs page — separate design system (Docusaurus)

| Parameter | Value |
|---|---|
| Background | `#1b1b1d` |
| Nav background | `rgba(7,7,13,0.933)` + `backdrop-filter: blur(12px)` |
| Nav border | `1px solid rgba(255, 215, 0, 0.08)` |
| Text | `#e8e4dc` |
| Accent | `gold` (`#ffd700`) |
| Link hover | `#ffbf00` |
| Cards/panels | `#242526` |
| Font (body) | **Inter** + `-apple-system, system-ui, Segoe UI, sans-serif` |
| Font (mono) | **JetBrains Mono**, Fira Code, Cascadia Code |
| H1 | 2rem / weight 600 |
| H2 | 1.5rem |
| H3 | 1.25rem |
| Sidebar | 300px, collapsible |
| Search | `⌘K` shortcut |
| Border radius | `0.4rem` (standard Docusaurus) |
| Scrollbar | 7px, `#686868` thumb |

## Google Fonts substitutes for Sigurd

Sigurd is a custom Nous Research variable font — not publicly available. Closest free alternatives:

| Font | Google Fonts URL | Character match |
|---|---|---|
| **Playfair Display** | `family=Playfair+Display:wght@300..900` | High-contrast serif, elegant at large sizes, variable weight |
| Bodoni Moda | `family=Bodoni+Moda:opsz,wght@6..96,400..900` | Didone style, dramatic thin/thick contrast |
| Cormorant Garamond | `family=Cormorant:ital,wght@0,300..700` | More calligraphic, lighter feel |
| DM Serif Display | `family=DM+Serif+Display` | Similar high-contrast but static weight only |

**Recommended:** Playfair Display — it's variable (300–900 like Sigurd), has the serif display character, and is widely available.
