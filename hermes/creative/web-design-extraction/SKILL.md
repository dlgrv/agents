---
name: web-design-extraction
description: Reverse-engineer a live website's complete design system using browser tools — colors, typography, layout, effects, CSS architecture — without needing vision model support.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [design, css, web, extraction, reverse-engineering, browser, design-system]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, css, web, extraction, reverse-engineering, browser, design-system]
    related_skills: [popular-web-designs, claude-design, sketch, design-md]
---

# Web Design Extraction

Use this skill when the user asks to study, analyze, or copy a website's visual design — its color palette, typography, layout system, visual effects, and CSS architecture. This is the **extraction** step that precedes redesign work.

**Typical triggers:** "research this site's design", "analyze their styling", "copy this site's look", "what's their design system", "extract their CSS", "study their aidentity".

## Related skills

- **`popular-web-designs`** — 54 pre-extracted design systems. Check here first — the site may already be cataloged.
- **`claude-design`** — Use after extraction when building a new artifact from the extracted design.
- **`design-md`** — Use if the deliverable is a formal DESIGN.md token spec file.

## Core technique: browser_console JavaScript extraction

The reliable path is **not** screenshots + vision analysis. Many models don't support image inputs, and even when they do, vision descriptions miss exact CSS values. Instead, use `browser_console` with targeted JavaScript expressions to extract precise data from the live DOM.

### Pitfall: vision model limitations

`browser_vision` and `vision_analyze` fail with `400 - model does not support image inputs` on non-vision models. **Do not retry vision calls after this error** — switch immediately to the `browser_console` extraction workflow below. Screenshot files are still saved (at `~/.hermes/cache/screenshots/`) and can be shared with the user via `MEDIA:` paths, but you cannot analyze them yourself without vision support.

### 6-step extraction workflow

After `browser_navigate(url)`, run these `browser_console` expressions in parallel batches.

#### Step 1: CSS custom properties (design tokens)

```javascript
(function() {
  const root = document.documentElement;
  const cs = getComputedStyle(root);
  const vars = {};
  for (let i = 0; i < cs.length; i++) {
    const prop = cs[i];
    if (prop.startsWith('--')) {
      vars[prop] = cs.getPropertyValue(prop).trim();
    }
  }
  return JSON.stringify(vars, null, 2);
})()
```

Then collect scoped variables from the main container (sites often define component-level tokens):

```javascript
(function() {
  // Replace selector with the site's main container class
  const el = document.querySelector('.site-root, [class*="web"], main, #app');
  if (!el) return 'no container found';
  const cs = getComputedStyle(el);
  const vars = {};
  for (let i = 0; i < cs.length; i++) {
    const prop = cs[i];
    if (prop.startsWith('--')) {
      vars[prop] = cs.getPropertyValue(prop).trim();
    }
  }
  return JSON.stringify(vars, null, 2);
})()
```

#### Step 2: @font-face declarations (custom fonts)

```javascript
(function() {
  const fonts = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.cssText && rule.cssText.includes('@font-face')) {
          fonts.push(rule.cssText.substring(0, 300));
        }
      }
    } catch(e) {}
  }
  return JSON.stringify(fonts, null, 2);
})()
```

Also check font-family CSS class mappings (sites often define `--font-X` vars mapped to loaded fonts):

```javascript
(function() {
  const result = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.cssText && (rule.cssText.includes('font-family') || rule.cssText.includes('__className') || rule.cssText.includes('__variable'))) {
          result.push(rule.cssText.substring(0, 300));
        }
      }
    } catch(e) {}
  }
  return result.join('\n\n');
})()
```

#### Step 3: Colors and fonts in use (computed)

```javascript
(function() {
  const elements = document.querySelectorAll('*');
  const colors = new Set();
  const bgColors = new Set();
  const fonts = new Set();
  for (let i = 0; i < Math.min(elements.length, 200); i++) {
    const el = elements[i];
    const cs = getComputedStyle(el);
    if (cs.color && cs.color !== 'rgba(0, 0, 0, 0)') colors.add(cs.color);
    if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)') bgColors.add(cs.backgroundColor);
    if (cs.fontFamily) fonts.add(cs.fontFamily);
  }
  return JSON.stringify({
    textColors: [...colors].slice(0, 20),
    bgColors: [...bgColors].slice(0, 20),
    fonts: [...fonts].slice(0, 10)
  }, null, 2);
})()
```

#### Step 4: Computed styles of key elements

```javascript
(function() {
  const results = {};
  const selectors = {
    nav: 'nav',
    h1: 'h1',
    h2: 'h2',
    button: 'a[href*="download"], a[class*="btn"], button[class*="btn"]',
    card: 'article, [class*="card"]',
    footer: 'footer, [class*="footer"]'
  };
  for (const [name, sel] of Object.entries(selectors)) {
    const el = document.querySelector(sel);
    if (el) {
      const cs = getComputedStyle(el);
      results[name] = {
        background: cs.backgroundColor,
        color: cs.color,
        fontFamily: cs.fontFamily.substring(0, 60),
        fontSize: cs.fontSize,
        fontWeight: cs.fontWeight,
        lineHeight: cs.lineHeight,
        letterSpacing: cs.letterSpacing,
        textTransform: cs.textTransform,
        borderRadius: cs.borderRadius,
        padding: cs.padding,
        border: cs.border,
        backdropFilter: cs.backdropFilter,
        position: cs.position
      };
    }
  }
  return JSON.stringify(results, null, 2);
})()
```

#### Step 5: Class-specific CSS rules (full rule text)

```javascript
(function() {
  // Replace prefix with the site's class prefix (e.g., '.hw-', '.st-', '.nav-')
  const prefix = '.hw-'; // adjust per site
  const result = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.cssText && rule.cssText.includes(prefix)) {
          result.push(rule.cssText.substring(0, 500));
        }
      }
    } catch(e) {}
  }
  return result.join('\n\n');
})()
```

Also grab the main container's full rule:

```javascript
(function() {
  let fullCSS = '';
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        // Find the longest rule containing the main class
        if (rule.cssText && rule.cssText.startsWith('.main-class {') && rule.cssText.length > 500) {
          fullCSS = rule.cssText;
          break;
        }
      }
    } catch(e) {}
  }
  return fullCSS;
})()
```

#### Step 6: Images and assets

```javascript
(function() {
  const imgs = document.querySelectorAll('img');
  const result = [];
  for (const img of imgs) {
    const cs = getComputedStyle(img);
    result.push({
      src: img.src,
      alt: img.alt,
      width: cs.width,
      height: cs.height,
      objectFit: cs.objectFit
    });
  }
  return JSON.stringify(result, null, 2);
})()
```

Or use `browser_get_images` for a cleaner API.

### Step 7 (Astro / client-rendered islands): extract content from serialized `props`

Some modern sites (Astro v6+, many artist/portfolio "desktop OS" sites) render an **empty `<body>` shell** — the visible UI is built at runtime by a client island. The 6-step DOM extraction above returns almost nothing because there is no static DOM. All content lives in one place: the `props="..."` attribute of an `<astro-island>` (or similar web-component) element, serialized as **Astro's `[tag, value]` wire format**.

**Detection signal** — look for these in the raw HTML (fetch with `curl`, see fallback below):
- `<meta name="generator" content="Astro ...">`
- `<astro-island ... props="{...}" component-url=...>`
- A `<body>` that contains only an `h1` + `<astro-island></astro-island>` and nothing else.

**Decoding the wire format.** Every value is wrapped as `[tag, payload]`:
- `tag 0` → `payload` is a literal primitive **or** a plain object (already decoded JSON).
- `tag 1` → `payload` is an **array** of `[tag, payload]` elements (recurse).

The `props` attribute is HTML-escaped (`&quot;` for `"`, `&amp;` for `&`), so decode entities before `json.loads`:

```python
import re, json, html as H
raw = open('page.html', encoding='utf-8').read()
m = re.search(r'props="(\{.*?\})"', raw, re.S)
props = H.unescape(m.group(1)).replace('&quot;','"').replace('&amp;','&')
data = json.loads(props)

def walk(v):
    if isinstance(v, list):
        if len(v) == 2 and isinstance(v[0], int):
            return [walk(x) for x in v[1]] if v[0] == 1 else walk(v[1])
        return [walk(x) for x in v]
    if isinstance(v, dict):
        return {k: walk(x) for k, x in v.items()}
    return v

clean = walk(data)            # now plain nested dicts/lists
artists = clean['authors']    # real content, fully usable
```

This recovers 100% of the site's structured content (artist names, images, folder covers, links, backer lists) — enough to rebuild the page as a standalone artifact. The CSS is still fetched separately (see Step 1–5 via the linked stylesheet in `<head>`). Full worked script in `references/astro-island-props-extraction.md`.

### Fallback: `curl` when the browser tool is unavailable

If `browser_exec`/`browser_console` is blocked (e.g., Chrome's "Allow remote debugging?" popup that needs a manual click the user may not grant, or headless failure), **do not stall** — fall back to `curl` + local parsing. This is a *reliable* alternative, not a degraded one, and it works especially well for SSR/client-island HTML:

```bash
curl -sL --max-time 30 "https://site.example/" -o page.html
# 1) find linked stylesheets
grep -oE '<link[^>]*rel="stylesheet"[^>]*href="[^"]+"' page.html
# 2) pull the main CSS and grep tokens (colors, fonts, key classes)
curl -sL "https://site.example/_astro/main.abc.css" -o main.css
grep -oE '#[0-9a-fA-F]{3,8}\b' main.css | sort -u
grep -oE 'font-family:[^;]+;' main.css
# 3) find the props payload / content blocks and parse with the Python above
```

Then serve the built clone locally to verify: `python3 -m http.server 8911` (background), `curl -s http://localhost:8911/index.html | grep -o 'KnownArtistName'` to confirm content embedded, and `curl -s -o /dev/null -w "%{http_code}" <asset-url>` to confirm each CDN image returns 200. This verification path needs no browser at all. (Do NOT record "browser tools don't work" as a permanent rule — they work when the popup is granted; `curl` is just the fallback for when it isn't.)

### Step 8 (JS-bundle parsing): when styles live in the compiled bundle

Many modern sites (Astro + React/Preact islands, Next.js, Vite SPA) do **not** put all styles in the linked `.css` file. Component-scoped CSS, Tailwind-class mappings, and even **full CSS rule blocks as template strings** live inside the compiled **JS bundle**. Grepping the CSS alone then misses:
- exact class → font-family mappings (e.g. `.tg-article-title { font-family: 'Playfair Display' }`),
- gradient/box-shadow values for a specific component (e.g. a `.aqua-link` "Dive in" pill),
- asset URLs referenced only from JS (e.g. a `emoji-sphere.mp4` video),
- the literal text of buttons/labels.

**Detection:** after fetching the HTML, find the JS bundle(s) and grep them too — not just the CSS:

```bash
# 1) raw HTML
curl -sL --max-time 30 "https://site.example/" -o page.html
# 2) linked stylesheet(s)
grep -oE '<link[^>]*rel="stylesheet"[^>]*href="[^"]+"' page.html
# 3) script bundle(s) — Astro/Next/Vite often inline a hashed name
grep -oE '<script[^>]*src="[^"]+\.js"' page.html
#    or the module preload
grep -oE '/_astro/[a-zA-Z0-9_.-]+\.js' page.html
```

Then fetch the bundle and grep for the class/style you need:

```bash
curl -sL "https://site.example/_astro/main.abc.js" -o bundle.js
# find a component's full CSS rule (may be inside a template string)
grep -oE '\.aqua-link \{[^}]*\}' bundle.js
# find class → font-family mapping
grep -oE '[a-z-]+\{font-family:[^}]+\}' bundle.js | sort -u
# find asset URLs
grep -oE 'https://[^"'\'' ]+\.(mp4|woff2|png|webp)' bundle.js | sort -u
# find a specific component function and its surrounding JSX/CSS
python3 - <<'PY'
s=open('bundle.js',encoding='utf-8',errors='replace').read()
i=s.find('function ne(')            # the anchor from the site (button renderer, etc.)
print(s[i-20:i+800])
PY
```

**Why this matters for "copy this component 1:1":** to replica a specific button/panel exactly, you need the gradient stops, border-radius, box-shadow, and text style. If those only exist as a template string in the bundle (not in `main.css`), the CSS-file grep returns nothing and you'll approximate — and the user will notice. Always grep **both** the CSS and the JS bundle before concluding a value "isn't there".

**Note on class-name minification:** bundle class names may be stable (BEM/Tailwind) or hashed (`_astro_xxx`). If you find `.tg-article-title` in the bundle but your local build can't use that name, copy the *values* (font, size, weight) into your own class. If the name is stable, copy it verbatim (Workflow A).

Worked example (real site, real values recovered): `references/js-bundle-design-extraction.md`.

### Additional pages

If the site has a docs page or different design system on other routes, navigate there and repeat steps 1–4. Docs sites often use a completely different framework (Docusaurus, Mintlify) with their own token system — extract separately.

### Navigating sub-pages

Use `browser_snapshot` (full=true) to get the complete content tree. This reveals all section headings, text content, and structural elements — essential for understanding the content architecture you'll need to replicate.

### Benchmarking reference designs against an existing app UI

When the user's app UI was criticized ("different fonts", "bad typography", "dated", "tiny unreadable text") and they provide several pre-approved reference designs (e.g. v0.app template links) to pick a direction from, this is a benchmarking task, not single-site extraction:

1. **Audit the current app from code first** — theme/tokens file, grep usage patterns (`text-*` class frequency, `font-mono` usage count, `uppercase`), screenshot if available. Knowing what already exists (font files, wash/gradient tokens) is what makes the recommendation cheap to adopt.
2. **Extract each reference** — for v0.app templates `curl` the template page and download the official/og screenshots; screenshots + vision are enough for a style verdict. Verify each screenshot really shows the named template (showcase images of *other* templates leak into search results).
3. **Vision-analyze every reference AND the current app with the same question template** so the comparison is apples-to-apples. Downscale large shots first (see pitfall).
4. **Recommend fit, not taste** — a beautiful reference can be wrong for the domain (calendar-editorial grid ≠ finance dashboard); a neutral "matching-domain" template can re-import the exact complaint ("too plain").
5. **Prefer a hybrid mapped onto the user's EXISTING tokens** — one reference as the base system, named borrowings from the others. Strongest argument: "the target font pairing already ships in your codebase".
6. **Deliver**: comparison table, per-reference adopt/reject rationale, hybrid recipe, where-NOT-to-apply notes for effects, and offer a static HTML mockup before touching code (options-before-code users).

Worked example (4-way v0 template audit → hybrid recommendation): `references/design-reference-benchmarking.md`.

## Output: Design Analysis Report

Structure the extracted data as a report with these sections:

1. **Color palette** — table with role, color value, HEX
2. **Typography** — fonts (loaded + fallback), sizes, weights, letter-spacing, text-transform
3. **Layout** — grid/flex structure, spacing system, container widths, padding
4. **Visual effects** — noise, vignette, gradients, blend modes, shadows, borders, frames
5. **What's NOT there** — design constraints (no border-radius, no shadows, no gradients) — these negative observations are as important as positive ones
6. **Images** — all image URLs, sizes, formats
7. **Additional pages** — if docs/other pages use a different design system, document separately

## Applying extracted designs

Two workflows depending on user intent — **ask which one they want if unclear**.

### Workflow A: Direct clone (1:1 copy)

User says things like "1 в 1", "practically identical", "steal images/fonts/colors", "only difference is content".

**Download actual assets from the target site:**

1. **Fonts** — extract woff2 URLs from `@font-face` rules (Step 2 above), then download:
   ```python
   # Python via execute_code — batch download
   import urllib.request, os
   fonts = {"Sigurd.woff2": "https://site.com/_next/static/media/Sigurd.woff2", ...}
   for name, url in fonts.items():
       req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
       with urllib.request.urlopen(req, timeout=10) as resp:
           open(f"assets/fonts/{name}", "wb").write(resp.read())
   ```
   Then reference them in local `@font-face` declarations with the same `font-family` names the site uses.

2. **Images** — extract original paths from Next.js optimizer URLs (the `url=` query param contains the original path like `/img/desktop/hero-art.webp`). Download directly from `https://site.com/img/desktop/hero-art.webp`.

3. **Colors** — use the EXACT hex values, not substitutes. Copy CSS custom properties verbatim.

4. **Fonts** — use the downloaded fonts with the same `font-family` names (e.g., `displayFont`, `monoFont`) and the same `--font-sigurd`, `--font-mono` variable names.

5. **Layout** — copy the exact container-query scaling formula, grid structures, spacing tokens. Keep `width: 100dvw; margin-inline: calc(50% - 50dvw)` on the main container (NOT body) — it works fine with `container-type: inline-size`.

6. **Visual effects** — copy noise SVG data URI, blend modes, opacity values, frame border formula verbatim.

**Copy the exact CSS class structure** — if the site uses `.hermes-web`, `.hw-frame`, `.hw-noise`, `.hw-vignette`, `.hw-ghost`, `.hw-wordmark`, `.hw-mono`, keep those class names. This ensures the CSS rules transfer 1:1.

**The only thing that changes is informational content** — text, headings, links, schema data. Visual design is identical.

### Workflow B: Translation (inspired-by redesign)

User says things like "inspired by", "adapt the style", "use their layout but our colors".

1. **Map colors** — don't copy the exact palette; map roles (bg, fg, accent, surface) to the user's brand colors
2. **Map fonts** — proprietary fonts aren't available; find Google Fonts substitutes (see `popular-web-designs` font substitution reference)
3. **Port effects** — noise, vignette, frame borders are CSS-only and copy directly
4. **Port layout patterns** — grid structures, spacing systems, container-query scaling
5. **Write a plan** — use the `plan` skill to create an implementation plan before coding

### Redesign workflow (extract → plan → implement → QA)

1. **Extract** the target site's design system using the 6-step workflow above
2. **Determine workflow** — direct clone (A) or translation (B)? Ask the user if unclear.
3. **Plan** — write a markdown plan with: color/font mapping (B) or asset download list (A), layout diagram, file list, task breakdown. Get user approval before coding (especially for users who prefer planning first).
4. **Implement** — write CSS first (design tokens, base styles, effects, components, responsive), then HTML (semantic structure with all content), then JS (interactions). For Workflow A, download assets first.
5. **QA via browser_console** — not vision. See verification section below.

### Post-clone customization pitfall: accent color removal

After delivering a 1:1 clone, the user may ask to remove specific colors they don't like (e.g., "убери этот цвет" / "от него полностью избавимся"). The cleanest approach:

1. Find all references: `search_files` for the hex value and the CSS variable name
2. Change the CSS **variable definition** (e.g., `--color-hermes-accent: #edff45` → `#f5f5f5`) — this updates all 20+ usages in one line
3. Verify zero remaining instances: `grep -c 'edff45' style.css` → 0
4. Do NOT individually replace each usage — that's error-prone and tedious

**User preference signal:** when a user says "давай от него полностью избавимся" about a color, they want it gone **everywhere**, not just in one spot. Changing the variable definition is the only safe way.

### Post-clone customization: removing custom ::selection

Users may prefer standard browser selection over custom `::selection` styling. Simply remove the rule entirely — don't replace with another color. The browser default (typically blue bg, white text) is what they want.

### Post-clone customization: removing unwanted sections

When a user asks to remove a section (e.g., a video preview), remove both the HTML **and** any now-unused CSS classes. Don't leave empty `<section>` shells. Clean up completely.

### Post-clone customization: removing nav elements

After a 1:1 clone, the user may ask to remove specific nav elements (social icons, install buttons, extra links). Clean approach:

1. Remove the HTML elements (SVG icons, `<a>` tags, wrapping `<span>`s)
2. Adjust the nav grid: if a grid column had 2 items and now has 1, change `grid-template-columns: 1fr 1fr` → `grid-template-columns: 1fr` to avoid empty space
3. Keep the nav grid structure (`1fr auto 1fr`) intact — only adjust inner div grids

### Post-clone improvement audit

After the user is satisfied with the basic clone, proactively audit for issues they may not have noticed yet:

1. **Open the page in browser** and run a comprehensive `browser_console` audit:
   - Check ALL text elements for sub-10px font sizes: `fontSize < 10 && text.length > 3`
   - Check for low opacity text: `opacity < 0.5 && text.length > 10`
   - Check platform card image coverage (height vs card height)
   - Check section spacing and empty sections (1 item in a grid looks sparse)
   - Check footer position (Hermes uses fixed; relative may leave whitespace)

2. **Present findings as a numbered list** with specific values (e.g., "who-tag: 5.8px", "truth items: 1") and ask the user which to fix — don't assume all are problems

3. **Common fixes:**
   - Tags/labels using `calc(10 * var(--u))` → switch to `var(--hw-text-body)`
   - Sparse sections → add 2-3 more items with relevant content
   - Platform card images too short → add `min-height` to card + `opacity: 0.5` on images
   - Hero CTA column layout → change `flex-direction: column` to `row` with `flex-wrap: wrap`
   - Footer → add `min-height: 100dvh` for full-viewport portal section

### Post-clone customization: text readability on colored backgrounds

After delivering a 1:1 clone, the user may report that text is hard to read — "сливается с фоном", "мелкий тонкий шрифт". This happens because the source site's `--hw-text-eyebrow` token (`calc(18 * var(--u))` ≈ 10px on desktop) was designed for tiny labels, but when reused for body copy it's too small. Combined with `color-mix(in srgb, var(--hw-fg) 50-60%, transparent)` the text becomes nearly invisible on a saturated blue background.

**Fix approach (systematic, one variable at a time):**

1. **Search** for all `color-mix` opacity values and `font-size: var(--hw-text-eyebrow)` usages in body text classes:
   ```
   search_files pattern="color-mix.*var\(--hw-fg\)|font-size.*var\(--hw-text-eyebrow\)"
   ```

2. **Increase font size** — the best approach is `clamp()` with rem minimums, NOT switching to `var(--hw-text-body)`. Even `--hw-text-body` (`calc(21 * var(--u))` ≈ 12px) can be too small on standard viewports. Use this pattern for all body/label text:
   ```css
   /* Body text (paragraphs, descriptions) */
   font-size: clamp(0.8rem, calc(18 * var(--u)), 1rem);
   
   /* Labels, eyebrows, tags */
   font-size: clamp(0.75rem, calc(16 * var(--u)), 0.9rem);
   
   /* Small labels (stat labels, footer bottom) */
   font-size: clamp(0.7rem, calc(14 * var(--u)), 0.85rem);
   ```
   This guarantees a minimum readable size (12.8px / 12px / 11.2px) regardless of viewport, while still scaling up on larger screens. Replace ALL `font-size: var(--hw-text-eyebrow)` and `font-size: var(--hw-text-body)` usages with clamp patterns.

3. **Increase opacity** — raise `color-mix` from 50-60% to 90-95% for body text. Labels/eyebrows can stay at 75-85%. Never go below 65% for any readable text on a saturated background. Specific mappings that worked:
   - `.hw-section-desc`, `.hw-truth-text p`, `.hw-who-card p`, `.hw-process-item p`, `.hw-faq-item dd`, `.hw-cta-desc`, `.hw-footer-desc`: `color-mix(... 95%, transparent)`
   - `.hw-process-tag`, `.hw-cta-note`, `.hw-footer-bottom`: `color-mix(... 80-90%, transparent)`
   - `.hw-feature-article p` (on white bg): `color-mix(in srgb, var(--hw-bg) 90%, transparent)`
   - `.hw-feature-num`: `opacity: 0.75` (was 0.5)
   - `.hw-feature-label`: `opacity: 0.7` (was 0.4)
   - `.hw-platform-card .hw-mono`: `opacity: 0.85` (was 0.6)
   - `.hw-slogan-sub`: `rgba(0,0,0,0.75)` (was 0.55)

4. **Increase line-height** — from 1.5 to 1.6-1.7 for paragraph text.

5. **Verify via browser_console** — check computed `fontSize` (should be ~12px, not ~7-10px) and color opacity (should be 65-100%, not 50-60%):
   ```javascript
   (function() {
     const els = ['.stat-label', '.hw-section-desc', '.hw-truth-text p', '.hw-process-item p', '.hw-faq-item dd', '.hw-cta-desc'];
     return JSON.stringify(els.map(s => { const el = document.querySelector(s); return el ? {[s]: getComputedStyle(el).fontSize + ' / ' + getComputedStyle(el).color} : null; }), null, 2);
   })()
   ```

**Pitfall:** `calc(13 * var(--u))` also produces ~7.5px — even smaller than eyebrow. Never use arbitrary small multipliers for text. Stick to `clamp(0.7rem, calc(N * var(--u)), 0.85rem)` minimums — the rem floor guarantees readability regardless of viewport width.

### Post-clone customization: comprehensive readability audit

After applying readability fixes, verify with a comprehensive `browser_console` audit that checks ALL leaf text nodes (not just manual selectors):

```javascript
(function() {
  const all = document.querySelectorAll('p, h1, h2, h3, span, dt, dd, a, button, div');
  const issues = [];
  const seen = new Set();
  all.forEach(el => {
    if (el.children.length > 0) return; // leaf nodes only
    const text = el.textContent.trim();
    if (!text || text.length < 3) return;
    const cs = getComputedStyle(el);
    const fontSize = parseFloat(cs.fontSize);
    const opacity = parseFloat(cs.opacity);
    // Check for low alpha in color (rgba or color-mix)
    let alpha = 1;
    const color = cs.color;
    if (color.startsWith('rgba')) {
      const m = color.match(/rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*([\d.]+)\)/);
      if (m) alpha = parseFloat(m[1]);
    } else if (color.startsWith('color(')) {
      const m = color.match(/\/\s*([\d.]+)\)/);
      if (m) alpha = parseFloat(m[1]);
    }
    // Check parent opacity chain
    let parentOp = 1;
    let p = el.parentElement;
    while (p && parentOp === 1) {
      parentOp = parseFloat(getComputedStyle(p).opacity);
      if (parentOp < 1) break;
      p = p.parentElement;
    }
    const effAlpha = alpha * parentOp;
    // Flag: font < 12px OR effective alpha < 0.7
    if ((fontSize < 12 || effAlpha < 0.7) && fontSize > 0) {
      const key = text.substring(0, 30) + fontSize.toFixed(0);
      if (seen.has(key)) return;
      seen.add(key);
      issues.push({ text: text.substring(0, 40), fontSize: fontSize.toFixed(1)+'px', alpha: effAlpha.toFixed(2) });
    }
  });
  return JSON.stringify(issues, null, 2);
})()
```

This catches issues manual selector checks miss — especially `color-mix()` values that compute to low alpha but don't appear as `rgba` in the color string.

**Note:** `color-mix(in srgb, var(--hw-fg) 50%, transparent)` computes to `color(srgb 0.96 0.96 0.96 / 0.5)` — the alpha is in the `/ 0.5` part, NOT in an `rgba()` wrapper. The regex above handles both formats.

### Post-clone customization: removing sections to shorten the page

Users may want a shorter landing page. The clean approach:

1. **Remove the HTML section entirely** — don't leave empty `<section>` shells
2. **Remove nav links pointing to removed sections** — update the nav grid columns if needed
3. **CSS for removed sections can stay** — unused CSS is harmless and keeps the file reusable. Don't delete CSS classes unless asked.
4. **Verify section count** — `grep -o '<section' index.html | wc -l` should match `grep -o '</section>' index.html | wc -l`

### Post-clone customization: removing invisible decorative wordmarks

Hermes-style sites include giant decorative wordmarks (e.g., `<div class="hw-feature-wordmark">LowBid</div>`) with `font-size: 311px`, `color: var(--hw-paper)` (white on white), and `line-height: 0.8`. These are **invisible** but occupy massive vertical space (~318px), creating an empty white band after the feature grid.

**Detection:** Run `browser_console` to measure panel children:
```javascript
(function() {
  const panel = document.querySelector('.hw-feature-panel');
  if (!panel) return 'no panel';
  const children = [];
  panel.querySelectorAll(':scope > *').forEach(child => {
    const r = child.getBoundingClientRect();
    const cs = getComputedStyle(child);
    children.push({
      tag: child.tagName, class: child.className?.substring?.(0,30),
      text: child.textContent.trim().substring(0,20),
      height: Math.round(r.height),
      color: cs.color, fontSize: cs.fontSize
    });
  });
  return JSON.stringify(children, null, 2);
})()
```
If a child has `height > 200` and `color` matching the background (e.g., `rgb(255,255,255)` on `rgb(255,255,255)`), it's an invisible wordmark — remove it from HTML.

**Fix:** Delete the wordmark `<div>` from HTML. Also reduce the feature grid's `padding-bottom` (e.g., from `calc(120 * var(--u))` to `calc(60 * var(--u))`) since the wordmark's own padding is no longer needed. The CSS class can stay (harmless, reusable).

### Post-clone customization: reducing scroll animations

Users may find excessive `IntersectionObserver`-based reveal animations distracting. The default clone may have 15+ `.reveal` elements (every card, article, truth-item, process-item).

**Fix:** Remove `reveal` and `reveal-delay-*` classes from individual items (cards, articles, process steps, truth items). Keep `reveal` only on section header blocks (the `<div>` containing the section label + title + description) — 2-3 animations total is enough for visual rhythm without being annoying.

**Verify:** `grep -o 'class="[^"]*reveal[^"]*"' index.html | wc -l` should be ≤ 3, and `grep -c 'reveal-delay' index.html` should be 0.

### Pitfalls when porting Hermes-style designs

- **`width: 100dvw` + `margin-inline: calc(50% - 50dvw)` causes horizontal scroll** — Hermes uses this on body for centering, but it creates 2px overflow on some viewports. Fix: remove both properties; `overflow-x: hidden` on body + `overflow-x: clip` on html is sufficient.
- **Frame border too thick on smaller viewports** — `calc(2.5 * (0.5vw + 0.5vh))` = 23px on a 1280px viewport. Hermes gets away with it because their viewport is very large. For typical viewports, use `calc(1vw + 0.5vh)` (~15px) or a fixed `clamp(8px, 1.2vw, 16px)`.
- **`text-transform: uppercase` on body affects everything** — body copy becomes unreadable in uppercase. Apply uppercase only to headings, nav, labels, eyebrows. Use `text-transform: none` on body/description paragraphs.
- **Container-query scaling `--u` needs tuning per site** — Hermes uses `100cqw / 2360` (their max design width). For a different site, set the divisor to the site's max content width. The anchor (`0.58px`) prevents sizes from going below sub-pixel on very narrow screens.
- **Noise SVG `mix-blend-mode: color-burn` is very strong on dark backgrounds** — use `overlay` with `opacity: 0.15` instead of `color-burn` with `0.2` when the background is near-black. Test visually.

### Verifying a static HTML/CSS page via browser_console

After writing the files, open `file:///path/to/index.html` in the browser and run these checks:

**1. Key element computed styles** — verify fonts, colors, sizes are applied:
```javascript
(function() {
  const checks = {};
  const frame = document.querySelector('.frame');
  if (frame) checks.frameBorder = getComputedStyle(frame).borderWidth;
  const h1 = document.querySelector('h1');
  if (h1) checks.h1 = { font: getComputedStyle(h1).fontFamily.substring(0,40), weight: getComputedStyle(h1).fontWeight, transform: getComputedStyle(h1).textTransform };
  // ... check nav, cards, section titles, etc.
  return JSON.stringify(checks, null, 2);
})()
```

**2. Font loading verification:**
```javascript
document.fonts.check('300 60px "Playfair Display"')  // → true when loaded
document.fonts.status  // → "loaded"
```

**3. Horizontal scroll check:**
```javascript
document.documentElement.scrollWidth > document.documentElement.clientWidth  // → false = good
```

**4. Grid layout verification:**
```javascript
(function() {
  const grid = document.querySelector('.features-grid');
  return getComputedStyle(grid).gridTemplateColumns; // → "333.5px 333.5px 333.5px" = 3 cols
})()
```

**5. Section visibility (all sections have non-zero dimensions):**
```javascript
(function() {
  const sections = document.querySelectorAll('section, aside, footer');
  return [...sections].map(s => {
    const r = s.getBoundingClientRect();
    return { tag: s.tagName, id: s.id, visible: r.width > 0 && r.height > 0, w: Math.round(r.width), h: Math.round(r.height) };
  });
})()
```

### Ad-hoc structural verification script

For static HTML/CSS with no build system or test suite, create a temporary shell script that checks:
- File existence and sizes
- HTML structure: doctype, closing tags, presence of key sections, `<section>`/`<div>` tag balance
- CSS structure: `:root` vars, key class names, `{}` brace balance, media queries
- Broken local file references (grep `href="..."` and check file exists)

Save under `$TMPDIR/hermes-verify-*.sh`, run with `bash`, clean up after. This is ad-hoc verification, not a test suite — report it as such.

### Design-prototype acceptance audit (built Vite/React app, no vision)

When the deliverable is a built app served by `vite preview` (not a static file) and vision analysis is unavailable or timing out, verify the design claims with a headless browser + computed styles instead of eyeballing. `playwright-core` is usually already in the frontend's node_modules:

```js
// run from the frontend dir so require('playwright-core') resolves
const { chromium } = require('playwright-core');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto('http://localhost:<port>/<base>/', { waitUntil: 'networkidle' });
await page.screenshot({ path: '/tmp/preview.png' });   // hand to user via MEDIA:
const audit = await page.evaluate(() => {
  const out = {};
  const card = document.querySelector('[class*="card"]');
  out.backdrop = card ? getComputedStyle(card).backdropFilter : 'no card'; // glass really applied?
  out.fonts = ['Inter', 'PrimePilot'].map(f => [f, document.fonts.check(`16px "${f}"`) ]);
  const h = document.querySelector('h1, [class*="balance"]');
  out.headline = h ? { font: getComputedStyle(h).fontFamily.slice(0, 40), size: getComputedStyle(h).fontSize } : null;
  out.tiny = [];                                        // sub-10px leaf text
  document.querySelectorAll('p, span, div, a, button').forEach(el => {
    if (el.children.length) return;
    const t = el.textContent.trim(); if (t.length < 3) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 10) out.tiny.push({ t: t.slice(0, 30), fs });
  });
  out.hScroll = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  out.cards = document.querySelectorAll('[class*="card"]').length;
  return out;
});
console.log(JSON.stringify(audit));
await browser.close();
```

Maps directly onto the standard design-review complaints: "разные шрифты" → all `fonts` true + one family per role; "мелкие непонятные шрифты" → `tiny` empty; glass/эффекты → `backdropFilter` non-`none`; broken layout → `hScroll` false. For state checks (modal opens, tab switches), drive clicks then screenshot. After any fix: rebuild (`npm run build`), restart `vite preview`, re-run — a clean second pass is the acceptance evidence. Judge only from the JSON numbers; keep screenshots for the user.

## Reference files

- `references/hermes-agent-nousresearch-com.md` — Complete design breakdown of the Nous Research Hermes Agent site (landing + docs), including exact CSS values, container-query scaling formulas, noise SVG data URI, and Google Fonts substitutes for the proprietary Sigurd font.
- `references/hermes-to-lowbid-translation.md` — Concrete design-translation mapping (Hermes → LowBid SSP) for Workflow B (inspired-by redesign): color/font mapping tables, container-query tuning, visual effect ports with modification rationale, implementation pitfalls, and browser_console verification checklist.
- `references/hermes-1to1-clone-technique.md` — Full 1:1 clone technique (Workflow A): how to download actual woff2 fonts and webp images from the target site, copy exact CSS class names and variables, preserve font fallback metrics, and verify computed styles match the source. Includes multi-subdomain asset discovery (portal subdomains), video element technique (webm + poster fallback), rate-limiting workarounds (429 fix with Referer + backoff), invalid asset detection, and the asset download script pattern and file structure layout.
- `references/astro-island-props-extraction.md` — Decode Astro/SSR client-island sites whose content lives in a serialized `props="..."` JSON attribute (empty `<body>` shell). Full detection heuristics, the `[tag, value]` wire-format `walk()` decoder, the `curl`-based fetch workflow, and a verification recipe (local `http.server` + `curl` content/asset checks — no browser needed).
- `references/js-bundle-design-extraction.md` — When a reference site's styles live in the compiled JS bundle (not the linked CSS): how to find/grep the bundle, recover exact class→font mappings, component gradients/shadows, and asset URLs. Includes the real probablynothing.xyz Playfair Display + `.aqua-link` "Dive in" recovery.

## Pitfalls

- **Vision model unsupported** — don't retry `browser_vision` after a 400 error. Switch to `browser_console` extraction immediately.
- **`vision_analyze` timeouts on large screenshots** — full-res 3200×1826 PNGs can time out repeatedly while smaller copies of the same image succeed. Downscale first: `sips -Z 1600 in.png --out in-small.png` and analyze the small copy; keep the full-res file for the user. **If it still times out 3–4× in a row (also on a ~65KB JPEG), the upstream vision service is down — not your image.** Stop retrying: verify the design programmatically with the headless-browser acceptance audit (see "Design-prototype acceptance audit" below) and hand the screenshots to the user via `MEDIA:` paths for human eyeballing; say plainly that the visual 'stylish or dated' judgment is theirs to make.
- **CORS-restricted stylesheets** — `sheet.cssRules` throws for cross-origin stylesheets without `crossorigin` attribute. Wrap in try/catch and skip.
- **Tailwind utility classes** — sites using Tailwind have thousands of utility rules. Filter by custom class prefixes or `--` custom properties instead of trying to collect all rules.
- **Container queries** — sites using `container-type: inline-size` have all sizes as multiples of a base unit. Extract the base unit formula (e.g., `--u: max(calc(100cqw / 2360), 0.58px)`) — it's the key to the entire spacing system.
- **Variable fonts** — `@font-face` with `font-weight: 300 800` range indicates a variable font. Note the range, not just a single weight.
- **Next.js image optimization** — image URLs go through `/_next/image?url=...&w=...&q=...`. The original path is in the `url` query parameter.
- **User may say "copy" but mean "1:1 clone"** — if the user says "1 в 1", "practically identical", "steal images/fonts/colors", or "only difference is content", they want Workflow A (direct clone), NOT Workflow B (translation). Don't substitute fonts or map colors — download the actual assets. When unclear, ask before starting implementation.
- **`width: 100dvw` on body causes horizontal scroll** — put it on a wrapper div (like `.hermes-web`) with `container-type: inline-size` instead. Add `overflow-x: clip` on `html`.
- **Multi-subdomain asset discovery** — the main landing page may not have all assets. Check related subdomains (portal.*, docs.*) for additional videos, high-res images, and logos. See `references/hermes-1to1-clone-technique.md` § Multi-subdomain asset discovery.
- **Downloaded file is HTML, not the actual asset** — some URLs return 404/redirect pages that save as "valid" bytes but are actually HTML. Verify with `file <asset>` — if it says "HTML document text", delete it.
- **Rate limiting (429) on batch asset downloads** — add `Referer` header + retry with exponential backoff (3s, 6s, 9s delays). See reference file for the exact header pattern.
- **Video elements in cloned sites** — Hermes uses `<video autoplay muted loop>` for animated content. Use `<source>` + `<img>` poster fallback. For background video effects, `mix-blend-mode: exclusion; opacity: 0.3` matches the Hermes ghost video aesthetic.
- **Hero art positioning must match exactly** — when the user provides the exact `<img>` element from the source site (with inline styles like `top: calc(219*var(--u)); right: calc(135*var(--u)); width: calc(1128*var(--u)); mix-blend-mode: lighten`), copy those inline styles verbatim. Don't approximate with `top: 50%; transform: translateY(-50%); width: 45%` — the user will notice and correct it.
- **Removing nav elements after clone** — users often don't have Discord/GitHub/install buttons. Remove the HTML elements AND adjust inner grid columns (`1fr 1fr` → `1fr`) to avoid empty space. Keep the outer nav grid (`1fr auto 1fr`) intact.
- **Proactive improvement audit after clone** — after the user is satisfied with basic customization, run a comprehensive `browser_console` audit checking: sub-10px text, low opacity, sparse sections (1 item), platform card image coverage, footer position. Present findings as a numbered list and ask which to fix. Common fixes: `calc(10 * var(--u))` tags → `var(--hw-text-body)`, add 2-3 more items to sparse sections, platform card `min-height` + image `opacity: 0.5`, hero CTA `flex-direction: row` instead of `column`.
- **Accent color is optional, not mandatory** — the Hermes accent (`#edff45` lime) is part of their brand, but the user may want it removed entirely. Default to keeping it in a 1:1 clone, but if asked to remove it, change the CSS variable definition (`--color-hermes-accent`) rather than individual usages.
- **Text unreadable on colored backgrounds after clone** — the source site's `--hw-text-eyebrow` token (`calc(18 * var(--u))` ≈ 10px) was designed for tiny labels. When reused for body copy in the clone, text is too small. Even `--hw-text-body` (≈12px) can be insufficient. Combined with `color-mix` at 50-60% opacity on a saturated blue (`#0000f2`) background, text becomes nearly invisible. Fix: replace ALL `font-size: var(--hw-text-eyebrow)` and `var(--hw-text-body)` with `clamp(0.7rem, calc(N * var(--u)), 0.9rem)` patterns (rem floor guarantees readability), raise `color-mix` opacity to 90-95% for body text / 80% for labels, increase line-height to 1.6-1.7. See "Post-clone customization: text readability" section above for the systematic fix approach and the comprehensive audit script.
- **Removing sections to shorten the page** — users may want fewer sections. Remove the HTML entirely (no empty shells), remove nav links to removed sections, adjust nav grid columns. CSS for removed sections can stay (harmless, keeps file reusable). Verify `grep -c '<section'` equals `grep -c '</section>'`.
- **Invisible decorative wordmark creates empty whitespace** — Hermes clones may include a `.hw-feature-wordmark` element (311px font, white-on-white) that's invisible but occupies ~318px. After feature cards, this appears as an unexplained white band. Detect via `browser_console` measuring panel children — if a child has height > 200 and color = background, remove it from HTML. Also reduce grid `padding-bottom` since the wordmark's spacing is no longer needed.
- **Too many scroll-reveal animations** — a 1:1 clone inherits 15+ `.reveal` elements. Users find this excessive. Remove `reveal`/`reveal-delay-*` from individual items (cards, articles, steps); keep only on section headers (2-3 total). Verify: `grep -c 'reveal' index.html` ≤ 3, `grep -c 'reveal-delay' index.html` = 0.
- **Hero spacing needs reduction when clone has less content** — the source site's `padding-top: calc(442 * var(--u))` (~256px) and `min-height: calc(1360 * var(--u))` (~789px) are tuned for their hero with multiple CTA rows + stats + install command. A clone with simpler hero content (just eyebrow + H1 + one CTA) ends up with excessive whitespace above the text. Reduce `padding-top` to `calc(220 * var(--u))` (~128px) and `min-height` to `calc(900 * var(--u))` (~522px). Measure via `browser_console`: eyebrow `getBoundingClientRect().top` should be ~220-260px (not ~350px). The hero art `top: calc(219 * var(--u))` positioning may also need adjustment if it overlaps text after reducing padding.
- **`calc(N * var(--u))` with small N produces sub-pixel text** — `calc(13 * var(--u))` = 7.5px, `calc(10 * var(--u))` = 5.8px. Never use arbitrary small multipliers for readable text. Use `--hw-text-body` (21 * var(--u) ≈ 12px) as the minimum.
- **Nav structure breaks when patching inner grid divs** — when adjusting nav layout (e.g., moving links between columns), the `<nav>` tag can accidentally be replaced with a `<div>` while the closing `</nav>` remains. This produces invalid HTML and the page renders blank (no `.hermes-web`, no content at all). **Always verify the nav tag pair** after any nav structure patch: `grep '<nav>' index.html` and `grep '</nav>' index.html` must both match. If the page is suddenly blank after a nav patch, this is the first thing to check.
- **Hero art image distortion with container-query width** — `width: calc(1128 * var(--u)); height: auto` does NOT preserve aspect ratio for absolutely-positioned images in a container-query context. The rendered width may not match the natural aspect ratio, producing a stretched/squashed image (e.g., ratio 1.215 instead of 0.796). **Fix:** use `height: calc(N * var(--u)); width: auto` instead — the browser calculates width from the natural aspect ratio of the loaded image. Verify via `browser_console`: `const r = img.getBoundingClientRect(); (r.width / r.height).toFixed(3)` should match `(img.naturalWidth / img.naturalHeight).toFixed(3)`. Also adjust `top` when reducing hero padding — if `padding-top` goes from `442` to `220`, the art `top` should also decrease (e.g., `219` → `180`) to avoid the art floating too far below the text.
