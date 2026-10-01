# MacBook Sleeve with Flap Pattern Design Guidelines

## Overview

MacBook sleeve with flap (klapan) designs combine the structural integrity of single-piece construction with the convenience of a secure closure system. These patterns feature a flap that folds over the device opening, secured by snap buttons, providing both protection and easy access.

## Design Principles

### Single-Piece Construction with Flap
- Use a single piece of leather with a fold line for structural back
- Flap extends from the main panel and folds over the device opening
- Flap height typically 8-10 cm for secure coverage
- Bottom fold line creates the back panel
- Entry opening at the top edge with straight 90° corners for clean device insertion

### Flap Geometry
- **Flap base**: Positioned at y = 2 × PH (where PH is panel height)
- **Flap height**: 8-9 cm for secure device coverage
- **Flap width**: Matches panel width (PW) for full coverage
- **Flap overlap**: 7.5-9.0 cm when closed, ensuring device security
- **Button placement**: 2.5 cm from flap free edge for optimal closure

### Button and Socket System
- **Button on flap**: Centered horizontally, 2.5 cm from flap free edge
- **Socket on front panel**: Centered horizontally, aligned with button when closed
- **Alignment**: Button distance from flap edge equals socket distance from entry edge
- **Button type**: Size 16 or 18 snap buttons for secure closure

### Hole Alignment for Flap Designs
- **Left and right sides**: Mirror holes across fold line for proper alignment when folded
- **Flap edge**: Holes along flap free edge for sewing flap to main panel
- **Entry edge**: No holes on entry edge (clean insertion)
- **Hole spacing**: 5 mm between holes, 4 mm from edges
- **Total holes**: Even number for proper pairing when panels are sewn

## Pattern Generation

### Dimensions Calculation
```python
# MacBook Pro 16" + UAG dimensions
LAP_W, LAP_H, LAP_T = 35.57, 24.81, 1.68     # Laptop dimensions
UAG_H, UAG_W, UAG_T = 0.40, 0.40, 0.82      # UAG case dimensions

# Derived dimensions
HW = LAP_H + UAG_H                           # 25.21 (narrow side with case)
WW = LAP_W + UAG_W                           # 35.97 (long side with case)
TT = LAP_T + UAG_T                           # 2.50 (total thickness)

# Pattern parameters
SEAM_W = 0.4                                  # Seam allowance
HOLE_SPACING = 0.5                           # Stitch hole spacing
FLAP_H = 9.0                                 # Flap height
INT_SLACK_W = 1.6                            # Interior slack width
INT_SLACK_D = 0.9                            # Interior slack depth

# Calculated dimensions
PW = HW + TT + INT_SLACK_W + SEAM_W         # 30.41 (width for narrow entry)
PH = WW + INT_SLACK_D + SEAM_W              # 37.97 (depth for narrow entry)
TOTAL_H = 2 * PH + FLAP_H                    # 84.94 (total height)
FLAP_BASE = 2 * PH                            # 75.94 (flap base position)

# Button and socket placement
BTN_X = PW / 2                               # Center of flap
BTN_Y = TOTAL_H - 2.5                        # 2.5 cm from flap edge
MATE_X = BTN_X                              # Center of front panel
MATE_Y = 5.5                                 # 5.5 cm above entry edge
```

### Hole Generation for Flap Designs
```python
holes = []

# Left side holes (mirrored across fold line)
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((SEAM_W, y))
    holes.append((SEAM_W, TOTAL_H - y))

# Right side holes (mirrored)
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((PW - SEAM_W, y))
    holes.append((PW - SEAM_W, TOTAL_H - y))

# Flap edge holes
for x in range(SEAM_W, PW - SEAM_W, HOLE_SPACING):
    holes.append((x, TOTAL_H - SEAM_W))
```

### Entry Orientation Variants

#### Narrow Side Entry (24.81 cm)
- Pattern width: device_width + case_width + thickness + slack = 30.41 cm
- Pattern depth: device_length + case_length + slack = 37.97 cm
- Entry through the 24.81 cm side (width dimension)
- Suitable for compact designs and easier insertion

#### Wide Side Entry (35.97 cm)
- Pattern width: device_length + case_length + thickness + slack = 38.77 cm
- Pattern depth: device_width + case_width + slack = 29.91 cm
- Entry through the 35.97 cm side (length dimension)
- More convenient for frequent access to device

## Print Layout

### Page Size Considerations
- **Single-panel designs**: Use A2 format (42.0 × 59.4 cm) for most flap designs
- **Large patterns**: For dimensions exceeding A2, split across multiple pages with registration marks
- **Scale reference**: Include 10 cm reference line for manual verification
- **Registration marks**: Place crosses at page boundaries for multi-page assembly

### Layout Optimization
- **Flap placement**: Position flap at the top of the pattern for easy cutting
- **Dimension labels**: Keep text ≥5 mm from page edges to avoid printer clipping
- **Hole visibility**: Ensure holes are clearly visible and not obscured by text
- **Fold line marking**: Use dashed lines for fold lines to distinguish from cut lines

## Common Issues and Solutions

### Problem: Flap Doesn't Close Properly
- **Cause**: Insufficient flap overlap or incorrect button placement
- **Solution**: Ensure flap overlap ≥7.5 cm and button is 2.5 cm from flap edge
- **Validation**: Test closure with actual device and verify alignment

### Problem: Hole Misalignment Across Flap
- **Cause**: Incorrect mirror calculation across fold line
- **Solution**: For left side holes at (x, y), use (PW-x, y) for right side holes
- **Validation**: Fold test paper and verify hole alignment

### Problem: Button Misalignment
- **Cause**: Button and socket not properly positioned relative to each other
- **Solution**: Button distance from flap edge should equal socket distance from entry edge
- **Validation**: Mark positions on test material and test closure

### Problem: Pattern Too Large for Page
- **Cause**: Pattern dimensions exceed standard page sizes
- **Solution**: Split across multiple A2 pages with 4 cm overlap and registration marks
- **Validation**: Check that all pattern elements fit within page boundaries

### Problem: Incorrect Entry Orientation
- **Cause**: Confusion between narrow-side and wide-side entry calculations
- **Solution**: Use clear variable names and double-check dimension assignments
- **Validation**: Compare pattern dimensions with expected device orientation

## Testing and Validation

### Automated Tests
- **Geometry validation**: All dimensions match calculated values
- **Hole alignment**: Mirror symmetry across fold line verified
- **Button/socket alignment**: Proper distance relationships maintained
- **PDF dimensions**: Pages match target dimensions (A2, A3, A4)
- **Scale verification**: 39.37 px/cm ratio confirmed

### Manual Validation
- **Print test pattern** and verify scale with ruler
- **Test hole alignment** by folding paper and checking alignment
- **Verify button placement** by marking on test material
- **Check flap overlap** and closure mechanism with actual device
- **Test physical capacity** with device and case

## Assembly Instructions

1. **Print pattern** at 100% scale on appropriate paper size
2. **Cut leather** following pattern outline
3. **Mark holes** using pattern as guide
4. **Sew seams** starting from bottom corners, working up
5. **Install snaps** at marked positions
6. **Fold at bottom** line to create back panel
7. **Test flap closure** with device inside
8. **Apply finish** (conditioner, edge sealant)

## Material Considerations

### Leather Selection
- **Thickness**: 2-3 oz vegetable tanned leather for flexibility
- **Size**: Minimum 90 × 70 cm for most flap designs
- **Grain direction**: Align with pattern length for optimal strength

### Thread and Hardware
- **Thread length**: ~3.5 × total seam length
- **Snap buttons**: Size 16 or 18 for secure closure
- **Optional**: Rivets for reinforcement at stress points

## Design Variations

### Flap Height Adjustments
- **Standard**: 8-9 cm flap for secure coverage
- **Compact**: 6-7 cm flap for thinner cases or easier access
- **Extended**: 10-12 cm flap for maximum security or thick cases

### Button Placement Options
- **Standard**: 2.5 cm from flap edge for optimal closure
- **Close**: 1.5 cm from edge for minimal flap extension
- **Extended**: 3.5 cm from edge for maximum flap coverage

### Entry Edge Design
- **Straight 90° corners**: Clean device insertion (recommended)
- **Rounded corners**: Aesthetic preference, may complicate insertion
- **Finger notch**: Additional feature for easier device removal

## File Naming Convention

Use descriptive file names that indicate purpose and design:
- `CHEHOL_MACBOOK16_UAG_klapan_na_shirokoy_lechalo_A2.pdf`
- `CHEHOL_MACBOOK16_UAG_klapan_na_uzkoy_lechalo_A3.pdf`
- `CHEHOL_MACBOOK16_UAG_v13_kontrol_posadki_A4.pdf`

This naming convention provides clear identification of:
- Item type (CHEHOL = sleeve)
- Device and case (MACBOOK16_UAG)
- Flap design (klapan)
- Entry orientation (na_shirokoy/na_uzkoy = on wide/narrow side)
- Format (lechalo = pattern, kontrol = assembly guide)

## Version History

- **v9**: Two-panel design, no flap, top-loading
- **v10**: Single-piece, narrow-side entry, no flap
- **v11**: Single-piece, wide-side entry, no flap
- **v12**: Single-piece, narrow-side entry with flap
- **v13**: Single-piece, wide-side entry with flap (current)

Each version maintains UAG case compatibility and uses identical construction methods, differing only in entry orientation and flap presence.
