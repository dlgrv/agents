---
name: macbook-sleeve-pattern
category: leatherworking-patterns
description: Generate custom MacBook sleeve patterns with precise fit.
version: 1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [leatherworking, pattern, macbook, sleeve]
    related_skills: [leatherworking-patterns]
---

## When to Use

Use when generating custom leather/fabric sleeve patterns for MacBook Pro laptops, with precise fit, vector output, and 1:1 scale verification.

## Procedure

1. **Gather dimensions**
   - Measure or lookup exact MacBook model dimensions (width × height × thickness)
   - Default: MacBook Pro 16" M5 = 35.57 × 24.81 × 1.68 cm
   - Add 0.12 cm per side for leather thickness (if using thick leather/fabric)

2. **Calculate panel dimensions**
   - Width: MacBook width + 2 × (leather thickness + seam allowance)
   - Height: MacBook height + wrap-around for thickness + clearance
   - Formula for wrap-around: π × thickness ÷ 4 (quarter-circle lower edge)
   - Clearance: 0.8-1.0 cm for comfort, adjust based on user preference

3. **Pattern generation script**
   - Use Python with matplotlib for vector output
   - Set scale: 39.37 px/cm = 100% 1:1 for A3 (1190.6×841.9 pt)
   - Draw panel with rounded corners (R = MacBook corner radius, typically 1.5 cm)
   - Add finger notch at top center if needed (depth 6 mm, width 24 mm, R15 mm arc)
   - Generate seam path: G-shape (sides + bottom, top open for top-loading)
   - Punch holes: 5 mm spacing, both ends included

4. **Output and verification**
   - Save as PDF (vector, 100% scale)
   - Generate preview PNG
   - Verify:
     - PDF page size matches A3 (1190.6×841.9 pt)
     - Scale = 39.37 px/cm
     - No punch holes on top edge (for top-loading sleeves)
     - Seam holes count matches calculation (typically 180 for standard size)

## Pitfalls

- **Thickness wrap-around**: Do not use raw MacBook height. Account for quarter-circle wrap-around of lower edge (+π×thickness/4) or sleeve will be too tight.
- **Top-loading orientation**: When user specifies top entry with wide side first, ensure panel orientation is correct (width = wide side, height = depth). Common mistake: rotating panels but keeping entry through narrow side.
- **Punch hole placement**: For top-loading sleeves, omit holes on top edge. Only include seam holes on sides and bottom. Verify with PDF vector inspection — small circles at y>27.0 cm indicate unwanted top holes.
- **Scale drift**: Always set matplotlib figure size to A3 dimensions (42.0×29.7 cm / 2.54 = 16.54×11.69 inches) and confirm final PDF scale with pymupdf or pixel measurement.
- **A3 layout**: When fitting large panels, verify entire panel fits on A3 before generating. Split panels across multiple sheets if needed, but align precisely with cross-marks for glue lines.

## User Preferences (from session)

- Top-loading entry with wide side first (not narrow side)
- Single universal panel for both front and back (cut ×2)
- No flap/clasp
- Top edge: free cut (no stitching holes), optionally finished with edge paint
- Finger notch at top center for easy removal
- Clear dimension labels and 10 cm scale reference on pattern
