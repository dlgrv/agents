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
- Use `references/bifold-wallet-audit.py` for automated validation of U-seam wallets with slot pockets

## Wallet Patterns (bifold)
- Wallet with card/bill pockets: seam must be U-shaped (bottom+sides), TOP OPEN. A closed perimeter seam seals the wallet shut — nothing can be inserted. The wallet v1 had exactly this bug.
- EVERY piece carries its own hole marks matching its position on the body; LEFT and RIGHT halves need MIRRORED hole sets (mirror x -> piece_width - x, not body_width - x). One shared mark = wrong-side holes.
- Keep ALL text (titles, dims) ≥5 mm from sheet edges: printers clip 3-5 mm. Cutting geometry can sit closer.
- Cards fit a bill-height bifold ONLY horizontally (card 85.6 long side along pocket width); vertical (88.6 with leather) exceeds 79 mm closed height. State card orientation in instructions explicitly.
- Instruction/schema drawings: never fill polygons (fc="none" everywhere) — fills kill label contrast and waste toner.
- Bill divider wall doesn't work: folded bill half-height ≈ 78.5 mm > any interior pocket half. Use two bill compartments (behind each card stack) instead.
- Closed seam path (perimeter loop): punch n = round(L/pitch) holes, NO +1 endpoint (a closed loop has no endpoints). Verify seam length against formula: 2*(W-4*SEAM) + 2*(H-4*SEAM) + 2*pi*SEAM for a rounded rect (arcs cut 2*SEAM per side, not 1*SEAM).- **U-shaped seams (bottom+sides, top open):** punch n = round(L/pitch) + 1 holes (open path with endpoints). Verify length against formula: 2*(H-4*SEAM) + (W-4*SEAM) + pi*SEAM (two quarter-arcs = half-circle, not full circle). Always test path segment-by-segment: if the last segment is a straight line to the start point, you accidentally closed a U-path into a loop.
- **Center seam placement:** For multi-panel wallets with a central divider, center seam offset from fold must balance usable card space and stitch hole grid alignment. If card width is W and grid step is S, usable space = W - 2*offset - 2*margin. The offset must avoid coinciding with grid nodes (minimum 2mm gap for grid step S=5mm) while ensuring usable space ≥ card width + 0.2cm tolerance. **Pitfall:** Reducing offset to increase usable space may cause the center seam to align with horizontal stitch holes, creating a single shared hole that splits between adjacent panels — this causes stitching misalignment. Always verify center offset against both horizontal (bottom seam grid) and vertical (side seam grid) grids simultaneously.
- Polylines must be continuous: after building any outline/seam path, assert max segment length <= longest straight edge; a big max segment means an arc was drawn from the wrong center/angles (classic: top-right rounded corner is 0-90 deg, NOT 270-360; zigs appear when reusing bottom-corner angles).- **Arc center placement:** arcs must be drawn around a center point offset by radius from the path, not centered on the path itself. If arc points start at (x,y) and the center is also at (x,y), the arc degenerates into a diagonal line. For a corner at (x,y) with radius r, the center is at (x±r, y±r) depending on the quadrant.
- Stacked-piece wallets (liner + 3 stepped card pockets on each half): punch ALL layers through one body markup — pieces don't need mirrored hole sets, they share the template. Bill sleeve separation: two compartments (one per half) via liner 'mouth' cutouts; a vertical divider cannot fit a bill folded once (78.5mm > half width).- **Slot pockets for cards:** design pockets with horizontal slits (card enters through slit, top edge protrudes). For cascade stacking, ensure slit y-coordinates don't overlap between adjacent pockets when stacked with offset (e.g. pocket bottom at y=0.15/1.15/2.15; slit at y=0.45–0.85 in each — no overlap).
- Page layout: place pieces bottom-up on a fixed grid WITHOUT height compensation offsets; verify no piece top exceeds page height. When pixel-verifying renders, mask annotation text/arrows precisely or expect +/-2 component miscounts.- **Multi-page patterns on one sheet:** for items like bifolds with many components, use a single A3 sheet (42×29.7 cm) not split A4 pages. Position all pieces with ≥3mm margins from edges (printers clip 3–5mm). Use pixel-level checks (numpy array of render) to confirm all content lies within safe zones.
- **Thread consumption calculation:** For stitching, thread length ≈ 3.5 × total seam length (accounting for knots, backstitching, and waste). Include a note on pattern PDF with estimated thread usage and assembly time. **Pitfall:** Underestimating thread length leads to mid-project stops; overestimation wastes material. Use actual stitch pitch (not just edge distance) to compute total holes and multiply by pitch × 3.5 for realistic estimate.

## Fold/Cut Patterns (No-Sew Wallets)

For wallets made from a single piece of leather with no stitching (fold/cut designs):

- **Tandy Stitchless Minimalist Wallet**: Classic fold/cut pattern from Tandy Leather. One piece, 3-4 oz vegetable tanned cowhide, folded along 3 main creases + 2 diagonal gouge lines, secured with one snap button. PDF pattern available at https://leathercraftlibrary.storage.googleapis.com/Archives/PDFs/Minimal-Wallet-Pattern.pdf. Validate with `pypdf` and `vision_analyze` to confirm fold lines and snap button holes.
- **Sailrite Wrap Wallet**: Similar fold/cut design but uses rivets instead of snaps. Pattern available at https://www.sailrite.com/leather-wallet-pattern. Requires rivet installation tools.
- **Origami-style wallets**: Complex multi-fold designs that create pockets through folding alone. These often require precise scoring/fold lines and may use decorative stitching only for aesthetics, not function.

**Key differences from sewn patterns:**
- No seam holes — fold lines and snap/rivet holes only
- Gouge lines (score lines on the back) for clean folding
- Single piece layout with fold indicators
- Button/rivet placement critical for functionality

**Validation workflow for fold/cut patterns:**
1. Download PDF pattern
2. Convert to PNG with `pymupdf` for visual inspection
3. Use `vision_analyze` to identify:
   - Fold lines (dashed or dotted lines)
   - Button/rivet hole positions
   - Single-piece contour (no separate panels)
   - Gouge lines (diagonal scoring lines on back)
4. Verify dimensions match expected wallet size

**Common pitfalls:**
- Misinterpreting fold lines as sewing lines
- Missing gouge line indicators (critical for clean folds)
- Incorrect button hole placement (causes misalignment when folded)
- Assuming all "minimalist wallet" patterns are no-sew (many use hidden stitching)

## Multi-Tier Wallet Patterns

For wallets with multiple tiers (e.g., 3-tier card holder with stepped pockets):

- **Tier height stacking:** Design tiers with increasing heights (e.g., 2.65, 3.65, 4.65 cm) to create cascading pockets. Ensure each tier's height allows cards to protrude by 0.3-0.5 cm for easy removal.
- **Shared hole alignment:** All tiers use the same x-coordinate grid for holes, but different y-coordinates based on their tier offset. Never reuse the same hole coordinates across tiers — each tier must have its own hole set.
- **Fold hole positioning:** Include holes through all tiers at the fold line for stitching through the entire stack. These holes must align precisely across all tiers to prevent misalignment during assembly.
- **Tier separation:** Leave 0.1-0.2 cm gaps between tiers in the pattern to account for leather thickness when stacked. Do not draw tiers touching each other.
- **Pocket usability:** Verify that the top edge of each tier extends above the tier below it by at least 0.3 cm to allow card insertion. Measure from the bottom of each tier to confirm proper stacking.

## Independent Auditing Workflow

When debugging complex wallet patterns, use independent validation to avoid blind spots:

1. **Run automated test suites:** Execute comprehensive test scripts (e.g., `wallet-test-suite.py`) that validate geometry, hole alignment, seam lengths, and print margins.
2. **Delegate independent audit:** Spawn a subagent with no prior knowledge of the pattern to perform a fresh audit. Provide only the pattern generation code and test suite, not your assumptions or fixes.
3. **Address critical failures first:** Fix any CRITICAL issues (e.g., card not fitting in pocket, physical impossibilities) before proceeding to MAJOR/MINOR issues.
4. **Iterative validation:** After each fix, regenerate the pattern and re-run tests. Continue until all tests pass.
5. **Manual verification:** Use PDF inspection tools (pypdf, pymupdf) to verify that all elements are within page boundaries and that hole coordinates match expected positions.

## Common Pitfalls in Multi-Tier Designs

- **Center column collision:** When adding a center seam divider, ensure it doesn't align with existing stitch holes. Minimum gap of 2mm required for grid step 5mm. If alignment occurs, adjust the center offset or increase pocket width.
- **Page boundary violations:** Increasing pocket width to improve usability can cause elements to extend beyond page boundaries. Always verify that PX0 + 2*POC_W + margin ≤ page width after any dimension changes.
- **Test suite drift:** When modifying pattern parameters, update all test thresholds to match the new geometry. Test expectations must reflect the actual pattern dimensions.
- **Coordinate system mismatch:** Ensure that drawing coordinates match test coordinate systems. When using variables like PX0 and PR_X in drawing code, use the same variables in tests to avoid mismatches.
- **Hole count validation:** For multi-panel designs, verify that left and right panels have matching hole counts when mirrored. Use set operations to ensure no duplicate holes at panel boundaries.
- **Text positioning:** After layout changes, verify that all text annotations remain within printable areas (≥3mm from page edges). Printers often clip content near edges.
- **Seam direction clarity:** Document whether seams are U-shaped (open top) or closed perimeter. Include this information in pattern instructions to prevent assembly errors.

## Related Skills

- `pdf`: PDF manipulation and form generation
- `product-price-monitor`: Track material costs for leather projects

## AirTag Donut Pattern

For specialized circular AirTag holders, see the complete workflow guide at `references/airtag-donut-workflow.md`. This covers:

- Circular geometry with grip calculations (15.4% perimeter compression)
- 24-hole stitch grid with 5.11 mm pitch
- Automated test suite (23/23 tests)
- Vector and pixel validation for PDF accuracy
- Assembly instructions for wallet and laptop sleeve integration
- Common pitfalls and troubleshooting guide
- Integration patterns for different use cases

The pattern uses skin tension grip (no glue/velcro) and is designed as a single piece that attaches to existing leather goods.

## Automated Validation Scripts

- `references/bifold-wallet-audit.py`: Comprehensive geometry and print margin validation for wallet patterns
- `references/wallet-test-suite.py`: Full test suite for wallet pattern generation (coverage: 70+ tests including hole alignment, seam length, pocket usability, scale accuracy)
- `references/multi-tier-wallet-audit.py`: Automated audit for complex multi-tier wallet patterns with center seams and independent validation
- `references/multi-tier-debugging-workflow.md`: Systematic debugging workflow for resolving critical issues in complex wallet patterns
- `references/test-airtag-donut.py`: Complete test suite for AirTag donut patterns (23 tests covering parameters, hole grid, PDF accuracy, and assembly)
- `references/airtag-donut-workflow.md`: Complete workflow for AirTag donut pattern generation with troubleshooting guide
