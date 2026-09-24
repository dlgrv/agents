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

## Subagent dispatch discipline (figure/visual tasks)

- **A subagent given qualitative-only instructions stalls.** Dispatches framed as "analyze and fix the overlap" produced transcripts of geometric deliberation with ZERO commits — twice in a row, different tasks. The dispatch context must contain: exact file paths, the element to move (line/selector), old→new coordinates, and the verification command. If you cannot supply those numbers yet, compute them yourself first — or do the edit yourself instead of delegating.
- **Verify a delegated background task's claims with git, not the summary.** After a subagent reports "committed and pushed", run `git status --short` + `git log --oneline -N` in the target worktree before telling the user anything shipped — a stalled child's self-report says "done" with an empty worktree.
- **A stalled/duplicate-dispatch cleanup:** before re-dispatching a failed task, confirm the first attempt left nothing behind (`git status --short` empty, no stray branches/commits) so the retry starts from a clean base.

## Cosmetic edits to existing SVGs (no generator)

Some merged figures have NO generator script in repo history — do not burn time searching for one. Hand-edit the SVG XML directly with patch:

- **Compute geometry arithmetically, not by eye.** A label is `<g id="text_N" transform="translate(x y)">`; its width ≈ the last tspan's x offset. Markers are `<use x= y=>` plus half the symbol size from `<defs>` (~±5 units). Write out the text's bbox and the nearest markers/line as numbers BEFORE choosing a shift; shift only the group's `translate`, never tspans.
- **Leader lines** from a floating annotation to its data point: add a `<line>` with stroke #666 and the same stroke-width as the file's tick marks.
- **Regenerate the PNG twin with sharp** (already a repo dependency): `node -e "require('sharp')('f.svg',{density:D}).png().toFile('f.png')"` — pick D so PNG pixel size matches the original PNG-to-viewBox ratio.
- **Delegating to a subagent requires ready-made numbers.** An abstract task like «подвинь текст, чтобы не перекрывалось» sends the model into endless geometric deliberation — zero commits, verified twice. Either compute the exact from→to coordinates and offsets yourself and hand them over, or skip delegation and edit it yourself.
- **Branch topology for figure fixes:** cosmetic fixes to already-merged figures go on a fresh branch off main in their own worktree; new figures for articles living on a feature branch go into that same feature branch's worktree. Never mix the two in one branch.
- **Worktree for figure work needs the full toolchain** — `npm ci` (sharp etc.), then `node scripts/build-blog-pages.mjs` + `npm run check` before pushing.
