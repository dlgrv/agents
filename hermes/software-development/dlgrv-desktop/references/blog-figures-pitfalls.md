# Blog figures rendering pitfalls

Common issues encountered during figure generation for dlgrv.com blog articles, with fixes.

## Text collisions in matplotlib

**Problem:** Multiple annotations stacked vertically near a panel's bottom (e.g., caption + sub-caption) overlap and become unreadable.

**Fix:** Adjust y-coordinates to spread them apart. Use:
```python
note(ax, line, (0.5, -0.13), fs=13.5)  # main caption
note(ax, sub, (0.5, -0.26), color=MUTED, fs=13.5, style="italic")  # sub-caption
```

**Verification:** Run vision_analyze on the rendered PNG to confirm no text is obscured.

## Centered layout

**Problem:** Figures appear left-aligned or have uneven margins, breaking the user's "centered" requirement.

**Fix:**
- For matplotlib: use `figsize` and bbox padding to naturally center content, then set explicit `width`/`height` on the saved PNG.
- For hand SVGs: set explicit `width` and `height` attributes on the root `<svg>` element and use CSS centering in the article.

**Verification:** Measure DOM offsets (left/right gaps equal) — never rely on visual alignment.

## Max width: 760px

**Problem:** Previously, figures rendered at full width (up to 1221px), making them too large and inconsistent.

**Fix:**
- Set a max width of 760px for all figures in CSS.
- Increase sub-annotation font size from 12.5 to 13.5 to maintain readability at the reduced size.

## PNG fallback for SVG

**Problem:** SVG images can fail lazy-loading or be distorted by CSS filters, making diagrams invisible or broken.

**Fix:** Generate both SVG and PNG versions of matplotlib figures. Use PNG in the markdown to ensure consistent rendering.

## Grayscale palette enforcement

**Problem:** Accidental color leaks in figures (e.g., blue accents, green highlights).

**Fix:** Use only grayscale colors: INK #111, MUTED #666, WARM #555, FAINT #e3e3e3, ACCENT #111. No exceptions.

## MathML rendering

**Problem:** Unicode superscripts (σ, ¹⁰) cause "Glyph missing" warnings in matplotlib; mixing unicode and mathtext breaks consistency.

**Fix:** Use mathtext for all scientific notation: `"10$^{-3}$"` instead of `10⁻³`.

## No layout shift

**Problem:** Images without explicit dimensions cause the page to reflow when they load.

**Fix:** Always set explicit `width` and `height` attributes on every SVG/PNG root element to reserve space before load.

## Annotation placement

**Problem:** Text placed directly on curves becomes unreadable; leader lines crossing whitespace cause clutter.

**Fix:** Place annotations in empty quadrants with leader lines only when necessary. For computed values (e.g., "пик ≈ 0.39"), add a white background rect if it overlaps data.
