# Hermes → LowBid: 1:1 Direct Clone Technique

Session log from 2025-07-12. User requested a near-identical clone of hermes-agent.nousresearch.com — "1 в 1, разница только в информационной начинке" (1:1, difference only in content).

**Critical workflow correction:** The first attempt produced a Workflow B "translation" (dark bg, Google Fonts substitutes, renamed CSS classes). User corrected: "мы должны сделать наш landing очень похожим... возможно, даже украсть изображения, шрифты, цвета... быть практически 1 в 1, разница только в информационной начинке." This triggered a full rewrite to Workflow A (exact colors, downloaded fonts, original class names, exact positioning). **Lesson: when a user says "copy" or "похожим", default to Workflow A (1:1 clone) unless they explicitly say "inspired by" or ask to adapt colors/fonts.**

## What "1:1 clone" means in practice

| Aspect | Translation (Workflow B) | Direct clone (Workflow A) |
|---|---|---|
| Colors | Map to user's brand palette | Use exact hex values from target |
| Fonts | Google Fonts substitutes | Download actual woff2 files from target |
| Images | Omit or use placeholders | Download actual webp/images from target |
| CSS classes | Rename to user's namespace | Keep original class names (`.hermes-web`, `.hw-*`) |
| CSS variables | Rename (`--bg`, `--accent`) | Keep original (`--hw-bg`, `--hw-accent`, `--u`) |
| Container-query formula | Tune for user's content width | Copy verbatim |
| Noise/vignette/effects | Adjust for user's bg color | Copy exact values |
| Content | User's content | User's content (the ONLY thing that changes) |

## Asset download technique

### Fonts (woff2)

1. Extract `@font-face` src URLs via browser_console Step 2
2. URLs may contain query params (`?dpl=...`) — strip them or keep, both work
3. Download via `execute_code` with `urllib.request`:
   ```python
   fonts = {
       "Sigurd.woff2": "https://hermes-agent.nousresearch.com/_next/static/media/Sigurd_Variable-s.p.092~ec~icx8ri.woff2",
       "CourierPrime.woff2": "https://hermes-agent.nousresearch.com/_next/static/media/CourierPrime_Regular-s.p.0357340c9cxif.woff2",
       "RulesVariable.woff2": "https://hermes-agent.nousresearch.com/_next/static/media/RulesVariable-s.p.06y..a1h6bjwb.woff2",
   }
   ```
4. Save under `assets/fonts/`, reference in local `@font-face` with same `font-family` names

### Images (webp)

1. Use `browser_get_images` to list all `<img>` src URLs
2. Next.js sites wrap URLs in `/_next/image?url=/img/desktop/foo.webp&w=3840&q=75` — extract the `url=` param to get the original path
3. Download directly: `https://hermes-agent.nousresearch.com/img/desktop/hero-art.webp`
4. Save under `assets/img/`, update `src` attributes in HTML

### Full CSS rule extraction

```javascript
// Get ALL CSS rules matching the site's class prefix
(function() {
  const result = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.cssText && (
          rule.cssText.includes('.hermes-web') ||
          rule.cssText.includes('.hw-') ||
          rule.cssText.includes('@font-face')
        )) {
          result.push(rule.cssText);
        }
      }
    } catch(e) {}
  }
  return result.join('\n\n');
})()
```

### DOM structure extraction

```javascript
// Get the full element tree with classes (truncated for readability)
(function() {
  function getStructure(el, depth=0) {
    const tag = el.tagName?.toLowerCase() || '';
    const cls = typeof el.className === 'string' ? el.className.substring(0, 40) : '';
    const text = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3 ? el.textContent.trim().substring(0, 30) : '';
    const indent = '  '.repeat(depth);
    let result = `${indent}<${tag}${cls ? ' class="' + cls + '"' : ''}${text ? ' text="' + text + '"' : ''}>`;
    if (depth < 3) [...el.children].forEach(c => result += '\n' + getStructure(c, depth + 1));
    return result;
  }
  const hw = document.querySelector('.hermes-web');
  return hw ? [...hw.children].map(c => getStructure(c, 0)).join('\n') : 'not found';
})()
```

## Key CSS rules to copy verbatim

These are the exact values that make the Hermes design distinctive:

```css
/* Root container — the heart of the scaling system */
.hermes-web {
  --u: max(calc(100cqw / 2360), var(--u-anchor));
  --hw-bg: #0000f2;
  --hw-fg: #f5f5f5;
  --hw-accent: #edff45;
  --hw-paper: #fff;
  --hw-frame: calc(2.5 * calc(0.5vw + 0.5vh));
  --hw-gutter: calc(210 * var(--u));
  --hw-gap: calc(30 * var(--u));
  --hw-text-eyebrow: calc(18 * var(--u));
  --hw-text-body: calc(21 * var(--u));
  --hw-text-h3: calc(72 * var(--u));
  container-type: inline-size;
  text-transform: uppercase;
  font-family: var(--font-sigurd), "Times New Roman", serif;
}

/* Frame border */
.hw-frame {
  border: var(--hw-frame) solid var(--hw-bg);
  position: fixed; inset: 0;
  z-index: 100; pointer-events: none;
}

/* Noise overlay */
.hw-noise::after {
  background-image: url("data:image/svg+xml,...");  /* SVG turbulence data URI */
  mix-blend-mode: color-burn;
  opacity: 0.2;
  background-size: 12.8rem 12.8rem;
}

/* Vignette */
.hw-vignette::before {
  background: radial-gradient(120% 90% at 50% 42%, transparent 50%, var(--hw-bg) 100%);
  opacity: 0.2;
}

/* Ghost wordmark */
.hw-ghost {
  mix-blend-mode: exclusion;
  color: var(--hw-accent);
  opacity: 0.2;
  font-weight: 300;
}

/* Feature panel — inverts the color scheme */
.hw-feature-panel {
  background: var(--hw-paper);  /* white */
  color: var(--hw-bg);          /* blue text on white */
}

/* Nav grid */
nav { display: grid; grid-template-columns: 1fr auto 1fr; }

/* Scrollbars */
::-webkit-scrollbar { width: 0.25rem; }
```

## Pitfalls specific to 1:1 cloning

1. **`width: 100dvw` + `margin-inline: calc(50% - 50dvw)` on body** — causes 2px horizontal scroll on some viewports. In the 1:1 clone, put these on the `.hermes-web` container div (NOT `body`), and add `overflow-x: clip` on `html`. This matches how Hermes actually does it.

2. **Frame border thickness** — `calc(2.5 * (0.5vw + 0.5vh))` = 23px on 1280×633. Hermes hides it on mobile (`max-md:hidden`). Keep the exact formula for desktop authenticity; hide on mobile.

3. **`text-transform: uppercase` affects ALL text** — Hermes intentionally uppercases everything including body copy. This is part of their aesthetic. In a 1:1 clone, keep it uppercase on the main container, but apply `text-transform: none` selectively to long paragraph text if readability becomes an issue.

4. **Font fallback metrics** — Hermes defines fallback fonts with `ascent-override`, `descent-override`, `size-adjust` to minimize layout shift. Copy these exact values:
   ```css
   @font-face {
     font-family: "displayFont Fallback";
     src: local("Times New Roman");
     ascent-override: 94.17%; descent-override: 24.28%;
     line-gap-override: 0%; size-adjust: 95.57%;
   }
   ```

5. **Feature panel color inversion** — the white panel with blue text is a dramatic design moment. Make sure `background: var(--hw-paper)` and `color: var(--hw-bg)` are applied to the panel container, and all child elements inherit the blue text color.

## Verification for 1:1 clone

After implementation, verify via browser_console that computed values match the target:

```javascript
(function() {
  const hw = document.querySelector('.hermes-web');
  const cs = getComputedStyle(hw);
  return JSON.stringify({
    background: cs.backgroundColor,  // → "rgb(0, 0, 242)"
    color: cs.color,                  // → "rgb(245, 245, 245)"
    fontFamily: cs.fontFamily,        // → starts with "displayFont"
    textTransform: cs.textTransform,  // → "uppercase"
    containerType: cs.containerType,  // → "inline-size"
    fontsLoaded: {
      sigurd: document.fonts.check('300 60px "displayFont"'),  // → true
      mono: document.fonts.check('400 14px "monoFont"'),       // → true
    }
  }, null, 2);
})()
```

## Multi-subdomain asset discovery

When cloning a site 1:1, the main landing page may not have all assets. **Check related subdomains** — the same organization often hosts additional assets (videos, high-res images, logos) on a portal or docs subdomain.

Technique:
1. Navigate to related pages (e.g., `portal.nousresearch.com/manage-subscription`)
2. Run `browser_get_images` + the DOM extraction JS to find all `<img>`, `<video>`, and background-image URLs
3. Look for assets in `/assets/hermes-landing/` or similar paths — these are often the **original unoptimized** versions (no Next.js image optimizer wrapper)
4. Download any NEW assets not already captured from the main site

### Pitfall: downloaded file is actually HTML (404/redirect)

Some asset URLs return a 404 page or redirect HTML instead of the actual binary. The download "succeeds" (HTTP 200 or saved bytes) but the file is invalid.

**Detection:** Run `file <asset>` in terminal — if it says "HTML document text" instead of "PNG image" / "WebP" / "Video", the URL was invalid. Delete it.

**Prevention:** Check `Content-Type` header in the download script, or verify with `file` command after batch download.

### Pitfall: "higher-res" images on portal may be identical

Portal subdomains sometimes serve the same webp images without Next.js optimization, making them appear "higher resolution." Check file sizes — if the portal version is the same byte count as the landing version, they're identical and the hires copy is redundant. Delete duplicates.

### Rate limiting (429) on asset downloads

When downloading many assets from the same host in quick succession, the server may return `429 Too Many Requests`.

**Fix:** Add `Referer` header matching the source page + retry with exponential backoff:
```python
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Referer": "https://portal.nousresearch.com/manage-subscription",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
})
# Retry 3 times with 3s, 6s, 9s delays
```

## Video elements in cloned sites

Hermes uses `<video>` elements for animated content (portal figure orb, footer girl). When cloning:

1. Download `.webm` files alongside images
2. Use `<video autoplay muted loop playsinline>` with a `<source>` + `<img>` fallback poster:
   ```html
   <video autoplay muted loop playsinline style="object-fit: cover;">
     <source src="assets/img/portal-figure-orb.webm" type="video/webm">
     <img src="assets/img/portal-figure.webp" alt="..." style="object-fit: cover;">
   </video>
   ```
3. For footer/background video effects, use `mix-blend-mode: exclusion; opacity: 0.3;` to match Hermes' ghost video aesthetic
4. Verify video loaded via `browser_console`: `video.readyState` → 4, `video.videoWidth` > 0

## Post-clone fixes (session 2)

### Invisible decorative wordmark → empty white band

**Symptom:** After the feature grid, a tall white strip (~318px) appears with no content.

**Root cause:** The `.hw-feature-wordmark` element ("LowBid", 311px font-size, `color: var(--hw-paper)` = white-on-white) is invisible but occupies 318px including padding.

**Detection:**
```javascript
(function() {
  const panel = document.querySelector('.hw-feature-panel');
  panel.querySelectorAll(':scope > *').forEach(c => {
    const r = c.getBoundingClientRect();
    const cs = getComputedStyle(c);
    console.log(c.className?.substring?.(0,30), Math.round(r.height), cs.color, cs.fontSize);
  });
})();
```
A child with height > 200 and color matching background = invisible wordmark.

**Fix:** Remove the wordmark `<div>` from HTML. Reduce feature grid `padding-bottom` from `calc(120 * var(--u))` to `calc(60 * var(--u))` since the wordmark's spacing is gone. Result: panel height drops from 1287px to 934px.

### Hero art exact positioning

When the user provides the exact `<img>` element from the source site, copy inline styles verbatim:
```html
<img class="hw-hero-art" src="assets/img/hero-art.webp" alt="" aria-hidden="true"
  style="position: absolute; top: calc(219 * var(--u)); right: calc(135 * var(--u));
  z-index: 2; width: calc(1128 * var(--u)); max-width: none;
  mix-blend-mode: lighten; pointer-events: none; user-select: none; height: auto;">
```
Don't approximate with `top: 50%; width: 45%` — the user will notice and correct it.

Also add `@media (max-width: 767px) { .hw-hero-art { display: none; } }` in CSS — Hermes hides hero art on mobile (`max-md:hidden`).

### Reducing scroll animations

User feedback: "давай при скролле будет меньше анимаций"

**Before:** 15 `.reveal` elements (every card, article, truth-item, process-item had `reveal` + `reveal-delay-*`).

**After:** 2 `.reveal` elements — only section header blocks ("No Bullshit Policy" heading, "How It Works" heading). All individual items appear immediately.

**Fix:** Remove `reveal` and `reveal-delay-*` classes from `<article>`, `.hw-truth-item`, `.hw-process-item` elements. Keep `reveal` only on the `<div>` wrapping section label + title + description.

**Verify:** `grep -o 'class="[^"]*reveal[^"]*"' index.html | wc -l` → 2, `grep -c 'reveal-delay' index.html` → 0.

## File structure for 1:1 clone

```
landing_v2/
├── index.html              (~23KB — HTML with all content, JSON-LD schema)
├── style.css               (~31KB — exact Hermes CSS adapted)
├── assets/
│   ├── fonts/
│   │   ├── Sigurd.woff2           (318KB — displayFont)
│   │   ├── CourierPrime.woff2      (27KB — monoFont)
│   │   └── RulesVariable.woff2    (398KB — rulesFont)
│   └── img/
│       ├── hero-art.webp
│       ├── platform-art-mac.webp
│       ├── platform-art-windows.webp
│       ├── platform-art-linux.webp
│       ├── badge.webp
│       ├── feature-connect.webp
│       ├── feature-memory.webp
│       ├── feature-automation.webp
│       ├── feature-tasks.webp
│       ├── feature-browse.webp
│       ├── feature-sandbox.webp
│       ├── nous.webp (or nous-hand.png from portal subdomain)
│       ├── portal-figure.webp      (video poster — from portal subdomain)
│       └── portal-figure-orb.webm  (animated video — from portal subdomain)
├── favicon.svg
├── og-image.svg
├── robots.txt
├── sitemap.xml
└── llms.txt
```
