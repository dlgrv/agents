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
- Generate multi-page patterns that tile to A4 for printing/scanning
- Any leatherworking project needing millimeter-precise layout

## Prerequisites

- Python 3.8+ with matplotlib, numpy, pypdf
- Install: `python3 -m pip install matplotlib numpy pypdf`

## Key Tools

- `references/macbook-sleeve-pattern.py` (ready-to-run script for MacBook sleeve pattern)
- `vision_analyze` for visual validation of generated PDFs
- `pypdf` for A4 size verification

## Workflow

1. **Define geometry:** Calculate outline points, hole positions, fold lines, and annotation text. Use constants for dimensions (e.g. `W, L = 37.5, 84` cm for MacBook sleeve).
2. **Set up matplotlib:** Configure figure size to A4 in cm (29.7 x 21.0), use `fig.add_axes()` to place drawing area with precise margins. Set `ax.set_aspect('equal')` for true proportions.
3. **Draw elements:** Use matplotlib primitives (lines, polygons, scatter for holes, text for labels) with explicit coordinates in cm.
4. **Add registration marks:** Draw crosshairs at 5cm intervals across the page for alignment during assembly.
5. **Tile large drawings:** For drawings larger than A4, calculate sub-page offsets and generate multiple pages with overlapping registration zones.
6. **Calibrate scale:** Verify 1:1 scale by checking that 1 cm in data = 39.37 px in output (fig.dpi should be 100). Use `ax.transData.transform()` to confirm pixel-to-cm ratio.
7. **Generate PDF:** Save as PDF with A4 page size, verify with pypdf that all pages are exactly 29.7 x 21.0 cm.
8. **Visually inspect:** Use `vision_analyze` to check for layout errors, overlapping text, or missing elements.

## Pitfalls

- **Scale drift:** Always verify pixel-to-cm ratio with `ax.transData.transform()`. Never assume DPI settings match physical output — measure.
- **Registration errors:** Crosshairs must align perfectly across pages. Test print-and-scanner alignment before cutting materials.
- **Text clipping:** Annotations near page edges may be cut off. Increase margins or reposition text inside safe zones.
- **Missing geometry:** When tiling, ensure all outline segments are drawn on their assigned pages. Use coordinate math to verify coverage.
- **PDF page size:** Verify with pypdf that output pages are exactly A4. Some viewers scale PDFs automatically, causing print misalignment.

## Example: MacBook Leather Sleeve Pattern

Use the ready-to-run script `references/macbook-sleeve-pattern.py` to generate a complete 13-page PDF pattern for MacBook Pro 16" leather sleeve with flap design. The script includes:

- 1:1 scale calibration (verified with pixel-to-cm transform)
- A4 tiling with registration marks for assembly
- Stitch hole guides (5mm spacing, 5mm from edge)
- Fold lines and panel annotations
- Visual validation instructions

Run: `python3 references/macbook-sleeve-pattern.py`

Output: 13 PDF pages (info + 12 pattern tiles) ready for printing and assembly.

## Verification

- Check all pages are exactly 29.7 x 21.0 cm using pypdf
- Verify 1 cm in drawing = 39.37 pixels in output
- Inspect PDF with vision_analyze for layout errors
- Test print alignment with registration marks

## Related Skills

- `pdf`: PDF manipulation and form generation
- `product-price-monitor`: Track material costs for leather projects
