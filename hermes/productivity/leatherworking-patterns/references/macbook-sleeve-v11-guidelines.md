# MacBook Sleeve Pattern v11 Guidelines

## Overview

MacBook sleeve v11 is a single-piece design with entry from the **wide side** (35.97 cm), optimized for MacBook Pro 16" with UAG case compatibility. This design provides convenient wide-side entry while maintaining structural integrity through a bottom fold.

## Key Features

- **Single-piece construction**: One cut, folded at bottom for structural back
- **Wide-side entry**: Device enters from the 35.97 cm side (long side)
- **UAG case compatibility**: Interior dimensions accommodate MacBook + UAG case with slack
- **Button closure**: Secure snap button system with proper alignment
- **Mirror hole alignment**: Holes on left and right sides mirror across fold line
- **A2 multi-page layout**: Split across two A2 pages with registration marks for assembly

## Design Parameters

```python
# MacBook Pro 16" + UAG dimensions (cm)
LAP_W, LAP_H, LAP_T = 35.57, 24.81, 1.68     # MBP 16" (naked)
UAG_H, UAG_W, UAG_T = 0.40, 0.40, 0.82      # UAG case dimensions

# Derived dimensions
HW = LAP_H + UAG_H                           # 25.21 (narrow side with UAG)
WW = LAP_W + UAG_W                           # 35.97 (long side with UAG)
TT = LAP_T + UAG_T                           # 2.50 (total thickness)

# Pattern parameters
SEAM_W = 0.4                                  # Seam allowance
HOLE_SPACING = 0.5                           # Stitch hole spacing
FLAP_H = 8.0                                 # Flap height
INT_SLACK_W = 1.6                            # Interior slack width
INT_SLACK_D = 0.9                            # Interior slack depth

# Calculated dimensions
PW = WW + TT + INT_SLACK_W + SEAM_W         # 38.77 (width - long side)
PH = HW + INT_SLACK_D + SEAM_W              # 29.91 (depth - narrow side)
TOTAL_H = 2 * PH + FLAP_H                    # 67.82 (total height)
FLAP_BASE = 2 * PH                            # 59.82 (flap base position)

# Button placement
BTN_X = PW / 2                               # Center of flap
BTN_Y = TOTAL_H - 2.5                        # 2.5 cm from flap edge
MATE_X = BTN_X                              # Center of front panel
MATE_Y = 5.5                                 # 5.5 cm above entry edge
```

## Construction Details

### Single-Piece Layout
- Pattern dimensions: 38.77 × 67.82 cm
- Bottom fold line at y = 29.91 cm (becomes the back panel)
- Entry opening at top edge (y = 0) with straight 90° corners
- Flap extends from y = 59.82 to y = 67.82 cm

### Hole Alignment
- Left side holes: mirrored across fold line for proper alignment when folded
- Hole spacing: 5 mm between holes, 4 mm from edges
- Total holes: 236 (118 per side when folded)
- No holes on entry edge or flap free edge

### Button and Socket System
- Button positioned on flap edge, 2.5 cm from free edge
- Socket positioned on front panel, 5.5 cm above entry edge
- Alignment ensures proper closure when flap is folded down

## Multi-Page Layout

### Page Split
- **Page 1**: Covers entry and fold line (y = 0 to 59.4 cm)
- **Page 2**: Covers flap and upper portion (y = 55.4 to 67.82 cm)
- **Overlap**: 4 cm between pages for registration

### Registration System
- Cross marks placed at page boundaries (y = 55.4 and y = 59.4)
- Reference lines indicate scale and orientation
- Text labels guide page alignment during assembly

## Physical Capacity

### Interior Dimensions
- Width: 37.67 cm (accommodates MacBook + UAG + slack)
- Depth: 28.81 cm (accommodates device length with clearance)
- Stack capacity: Can hold MacBook Pro 16" with UAG case plus additional items

### Clearance Allowances
- Width slack: +1.7 cm prevents jamming during insertion/removal
- Depth slack: +0.9 cm provides comfortable fit
- Flap overlap: Covers device stack by 7.5-8.0 cm when closed

## Testing and Validation

### Automated Tests
- Geometry validation: All dimensions match calculated values
- Hole alignment: Mirror symmetry across fold line verified
- Button/socket alignment: Proper distance relationships maintained
- PDF dimensions: Both pages exactly A2 (42.0 × 59.4 cm)
- Scale verification: 39.37 px/cm ratio confirmed

### Manual Verification
- Print test pattern and verify scale with ruler
- Test hole alignment by folding paper and checking alignment
- Verify button placement by marking on test material
- Check flap overlap and closure mechanism

## Assembly Instructions

1. **Print patterns** at 100% scale on A2 paper
2. **Align pages** using registration crosses at overlap boundaries
3. **Cut leather** following combined pattern outline
4. **Mark holes** using pattern as guide
5. **Sew seams** starting from bottom corners, working up
6. **Install snaps** at marked positions
7. **Fold at bottom** line to create back panel
8. **Test fit** with device and case
9. **Apply finish** (conditioner, edge sealant)

## Common Issues and Solutions

### Problem: Device Too Tight
- **Cause**: Insufficient interior width or depth
- **Solution**: Verify interior dimensions against actual measurements
  - Width: 37.67 cm should accommodate 35.97 cm device + 1.7 cm slack
  - Depth: 28.81 cm should accommodate 27.71 cm device + 1.1 cm slack

### Problem: Hole Misalignment
- **Cause**: Incorrect mirror calculation across fold line
- **Solution**: Ensure left side holes at (x, y) correspond to right side holes at (PW-x, y)

### Problem: Button Misalignment
- **Cause**: Incorrect button or socket positioning
- **Solution**: Verify button at 2.5 cm from flap edge and socket at 5.5 cm above entry edge

### Problem: Pattern Too Large for Single Page
- **Cause**: Pattern dimensions exceed standard page sizes
- **Solution**: Use multi-page A2 layout with registration marks for assembly

### Problem: Incorrect Entry Orientation
- **Cause**: Confusion between wide-side and narrow-side entry
- **Solution**: Wide-side entry uses pattern width = device length + case + slack
  - Pattern width: 38.77 cm (device length 35.97 + case + slack)
  - Pattern depth: 29.91 cm (device width 25.21 + slack)

## Material Requirements

### Leather Selection
- Minimum size: 90 × 70 cm (to accommodate 38.77 × 67.82 pattern)
- Thickness: 2-3 oz vegetable tanned leather
- Grain direction: Align with pattern length for optimal strength

### Thread and Hardware
- Thread length: ~3.5 × total seam length (approximately 408 cm)
- Snap buttons: Size 16 or 18 for secure closure
- Optional: Rivets for reinforcement at stress points

## Design Comparison

| Feature | v10 (Narrow Entry) | v11 (Wide Entry) |
|---------|-------------------|------------------|
| Entry Side | 24.81 cm (narrow) | 35.97 cm (wide) |
| Pattern Width | 30.41 cm | 38.77 cm |
| Pattern Depth | 37.97 cm | 29.91 cm |
| Interior Width | 29.61 cm | 37.67 cm |
| Interior Depth | 37.17 cm | 28.81 cm |
| Flap Coverage | 7.5 cm | 7.5-8.0 cm |
| Use Case | Compact fit, easier insertion | Convenient wide-side access |

## File Naming Convention

Use descriptive file names that indicate purpose and version:
- `CHEHOL_MACBOOK16_UAG_vhod_shirokiy_lechalo_A2_list1of2.pdf`
- `CHEHOL_MACBOOK16_UAG_vhod_shirokiy_lechalo_A2_list2of2.pdf`
- `CHEHOL_MACBOOK16_UAG_v11_kontrol_posadki_A4.pdf`

This naming convention provides clear identification of:
- Item type (CHEHOL = sleeve)
- Device and case (MACBOOK16_UAG)
- Entry orientation (vhod_shirokiy = wide entry)
- Format (lechalo = pattern, kontrol = assembly guide)
- Page number (list1of2, list2of2)

## Version History

- **v10**: Single-piece, narrow-side entry (24.81 cm)
- **v11**: Single-piece, wide-side entry (35.97 cm) - new design

Both versions maintain UAG case compatibility and use identical construction methods, differing only in entry orientation and corresponding dimension calculations.
