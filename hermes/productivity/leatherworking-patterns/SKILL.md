---
name: leatherworking-patterns
description: Generate leather patterns with A4 tiling and 1:1 scale.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [leather, pattern, pdf, technical-drawing, sewing, craft]
    category: productivity
    related_skills: [pdf]
---

# Leatherworking Patterns Skill

Generate precise PDF patterns for leather goods (sleeves, wallets, bags, cases) with A4 tiling, 1:1 scale calibration, and automated crosshair registration marks for assembly. Supports complex geometries with fold lines, hole guides for stitching, and dimension annotations.

## When to Use

- Create sleeve/case patterns for laptops, tablets, or electronics
- Design wallet, passport cover, or bag patterns
- Generate multi-page patterns that tile to A4, A3, or A2 for printing/scanning
- Any leatherworking project needing millimeter-precise layout
- **Special case:** Simple two-panel 'pocket' designs (like MacBook sleeve with no flap, just two panels sewn on three sides)

## Prerequisites

- Python 3.8+ with matplotlib, numpy, pypdf
- Install: `python3 -m pip install matplotlib numpy pypdf`

## Key Tools

- `references/macbook-sleeve-pattern.py` (ready-to-run script for MacBook sleeve pattern)
- `vision_analyze` for visual validation of generated PDFs
- `pypdf` for A4 size verification

## Workflow

1. **Define geometry:** Calculate outline points, hole positions, and annotation text. Use constants for dimensions (e.g. `W, L = 37.5, 26.5` cm for simple pocket sleeve). For pocket designs with no flap, define two separate panels (front and back) with identical dimensions.
2. **Set up matplotlib:** Configure figure size to target page size (A4, A3, or A2) in cm (e.g. A4: 29.7 x 21.0, A2: 42.0 x 59.4), use `fig.add_axes()` to place drawing area with precise margins. Set `ax.set_aspect('equal')` for true proportions.
3. **Draw elements:** Use matplotlib primitives (lines, polygons, scatter for holes, text for labels) with explicit coordinates in cm. For pocket designs, draw both panels on the same page if they fit (A2: both panels side-by-side; A3: one panel per page).
4. **Add hole guides:** Plot stitching holes as dots with 5mm spacing from edges. For pocket designs, mark holes on all three sewn sides (top, bottom, and one side panel edge). Leave the open side (entry) without holes.
5. **Add reference lines:** Draw straight lines at 10cm intervals across the page for manual scale verification (critical when printing on large formats).
6. **Tile large drawings:** For drawings larger than the target page size, calculate sub-page offsets and generate multiple pages with overlapping registration zones.
7. **Calibrate scale:** Verify 1:1 scale by checking that 1 cm in data = 39.37 px in output (fig.dpi should be 100). Use `ax.transData.transform()` to confirm pixel-to-cm ratio.
8. **Generate PDF:** Save as PDF with correct page size, verify with pypdf that all pages are exactly the target dimensions (A4: 29.7 x 21.0, A3: 42.0 x 29.7, A2: 42.0 x 59.4 cm).
9. **Visually inspect:** Use `vision_analyze` to check for layout errors, overlapping text, or missing elements.

## Pitfalls

- **Scale drift:** Always verify pixel-to-cm ratio with `ax.transData.transform()`. Never assume DPI settings match physical output — measure.
- **Page size mismatch:** When printing on non-A4 formats (A3, A2), verify PDF page size matches target dimensions exactly. Some viewers auto-scale PDFs, causing misalignment.
- **Text clipping:** Annotations near page edges may be cut off. Increase margins or reposition text inside safe zones.
- **Geometry offset:** When drawing multiple panels (like front/back), ensure each panel is positioned at correct coordinates relative to page boundaries. Use coordinate math to verify coverage.
- **Missing registration:** For multi-page patterns, include registration marks or reference reference lines at page edges to help align printed pages during assembly.
- **Hole misalignment:** For pocket designs with two panels, ensure hole positions match exactly when panels are stacked. Use the same coordinate system for both panels.
- **Asymmetric hole numbering:** When holes are numbered along the seam path from a single endpoint, the last interval is often missing a hole at the endpoint. This causes misalignment when panels are sewn 'meat to meat' because the hole sets are offset by one interval. **Fix:** Place holes at both endpoints of the seam path and ensure the total hole count is even (so panels can be paired 1:1 when one is flipped). Always verify that hole count per panel is odd (so there's a center hole) and that the total path length equals (holes-1) × spacing.
- **Finger notch depth:** User may prefer shallow notches for easier insertion. Always clarify notch depth: 6 mm (shallow, wide opening) vs. 10 mm (deep, semi-circle). Use constants `NOTCH_DEPTH` and `NOTCH_OPENING` for clarity, and update the visual annotation to show actual depth. **Pitfall:** Shallow notches with 6mm depth require a larger opening (24mm) to maintain usability, while deep notches use 20mm opening. Always calculate notch radius as ρ = (opening²/4 + depth²)/(2×depth) to ensure the arc geometry matches the intended depth.
- **Seam path direction:** When generating arc segments for notches or curves, ensure the arc direction matches the contour flow. Downward-arching notches should be drawn from bottom to top (through the deepest point), not top to bottom, to avoid jagged geometry in the PDF output.
- **Corner radius matching:** For realistic design, match the corner radius of the leather pattern to the actual object's corners (e.g. MacBook Pro 16" uses ~15mm radius). Use a single radius constant for both panel corners and finger notch to maintain design consistency and user preference for unified aesthetics. **Pitfall:** Apple doesn't publish corner radii in specifications; research from third-party templates and physical measurements shows newer square-body laptops use ~15mm radius, while older models use 11-12mm. Always verify against actual device if possible.

## Example: MacBook Leather Sleeve Pattern

Use the ready-to-run script `references/pocket-sleeve-pattern.py` to generate a complete two-panel pattern for MacBook Pro 16" leather sleeve with user-configurable notch depth. The script includes:

- 1:1 scale calibration (verified with pixel-to-cm transform)
- A4/A3/A2 tiling with registration marks for assembly
- Stitch hole guides (5mm spacing, 4mm from edge)
- Symmetric hole alignment for 'meat to meat' sewing
- Configurable shallow (6mm) or deep (10mm) finger notch
- Visual validation instructions

Run: `python3 references/pocket-sleeve-pattern.py`

Output: PDF patterns for A2 (both panels), A3 (one panel per page), or A4 (single panel) ready for printing and assembly.

For asymmetric pocket designs with simple geometry, use `references/simple-pocket-pattern.py`.

## Verification

- Check all pages are exactly 29.7 x 21.0 cm using pypdf
- Verify 1 cm in drawing = 39.37 pixels in output
- Inspect PDF with vision_analyze for layout errors
- Test print alignment with registration marks

## Related Skills

- `pdf`: PDF manipulation and form generation
- `product-price-monitor`: Track material costs for leather projects
