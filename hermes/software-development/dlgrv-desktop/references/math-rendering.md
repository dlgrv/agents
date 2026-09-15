# Blog math rendering: MathML Core (Temml)

Setup and best practices for rendering mathematical formulas in blog articles.

## Why MathML, not KaTeX?

- **Typography integration:** MathML inherits the article's Georgia serif font (like Distill.pub),
  while KaTeX forces its own math fonts (KaTeX_Main/KaTeX_Mono) which look alien in serif articles.
- **Zero JavaScript:** MathML Core is natively supported by modern browsers (Chrome 109+, Safari 14+, Firefox),
  no client-side JS/CSS needed. KaTeX requires client-side rendering.
- **Server-side prerender:** Temml (from KaTeX author) converts LaTeX to MathML at build time,
  producing static HTML+MathML that works everywhere.
- **Best practice 2026:** "Native MathML — built into Chrome 109+, Safari 14+, Firefox. Zero JavaScript"
  (gauravtiwari.org, 2026).

## Setup

1. Install Temml: `npm install temml` (0 dependencies, Node.js module)
2. In `scripts/build-blog-pages.mjs`, add MathML rendering for `$...$` and `$$...$$` delimiters:
   ```js
   const { renderToString } = require('temml.cjs');
   // For inline math: `content.replace(/\$(.+?)\$/g, (match, expr) => renderToString(expr, { displayMode: false }));`
   // For display math: `content.replace(/\$\$(.+?)\$\$/g, (match, expr) => renderToString(expr, { displayMode: true }));
   ```
3. Use standard LaTeX syntax: `$z = wx + b$`, `$$P(t_i) = \frac{e^{l_i/T}}{\sum_j e^{l_j/T}}$$`
4. No additional CSS needed — MathML inherits font-family from parent (Georgia serif).

## Typography

- **Inline math:** `$z = wx + b$` renders as italic serif, same as article text.
- **Display math:** `$$...$$` renders as centered block with proper spacing.
- **Subscripts/superscripts:** Native MathML `<sub>`, `<sup>` support.
- **No fallback font:** Temml includes only optional Temml.woff2 for rare glyphs (√, Σ);
  most symbols render with the article's Georgia.

## Migration from inline code

Replace `` `formula` `` with `$formula$` in markdown. Remove `.tl_article code` styling for formulas;
keep it only for data tokens (`[кв]`, `Привет`).

## Verification

- Check rendered output: `grep -o '<math[^>]*>' public/blog/<slug>/index.html`
- Confirm no KaTeX classes or fonts: `grep -v 'katex' public/blog/<slug>/index.html`
- Check inheritance: `grep 'font-family' public/blog/<slug>/index.html` (should show Georgia, not KaTeX_*).

## Browser support

- Chrome 109+, Safari 14+, Firefox: full MathML Core support.
- Legacy browsers: MathML renders as plain LaTeX (no styling), still readable.

## Rendering pitfalls (NEW 2026-09)

- **Inline matrix rendering bug**: Chrome/Safari often render inline MathML matrices with incorrect vertical stretch — brackets appear only on the middle row, not the full height of the matrix. This is a browser limitation, not a MathML error.
- **Fix**: Always use display mode ($$...$$) for matrices with 3+ rows or multi-line equations. Never rely on inline $...$ for anything more than 1–2 row formulas.
- **Browser behavior**: Inline formulas render in the text flow and may be clipped by line-height; display formulas create their own block with proper vertical space and are not affected by parent line-height.
- **Test**: After rendering, inspect the MathML output — ensure <mo fence stretchy> brackets fully enclose the <mtable> in display mode, but not necessarily in inline mode.
