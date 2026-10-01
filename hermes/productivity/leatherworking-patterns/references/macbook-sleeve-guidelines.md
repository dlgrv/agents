# MacBook Sleeve Pattern Design Guidelines

## Design Principles

### Single-Piece Construction
- Use a single piece of leather with a fold line for structural integrity
- The fold becomes the back panel, eliminating the need for a separate back
- Calculate interior dimensions as: panel_height - fold_thickness - seam_allowance
- Include registration marks for precise folding alignment

### Entry Orientation
- **Narrow side entry (MacBook Pro 16")**: Device enters from the 24.81 cm side
  - Pattern width: device_width + case_width + thickness + slack
  - Pattern depth: device_length + case_length + depth_slack
- **Wide side entry**: Device enters from the 35.97 cm side
  - Pattern width: device_length + case_length + thickness + slack
  - Pattern depth: device_width + case_width + depth_slack

### UAG Case Compatibility
- Always add case dimensions to laptop dimensions: 35.57 × 24.81 × 1.68 + 0.40 × 0.40 × 0.82
- Include additional slack: +1.6 cm width (prevents jamming), +0.9 cm depth
- Interior width calculation: >= laptop_width + case_width + thickness + slack
- Interior depth calculation: >= laptop_length + case_length + depth_slack

### Button and Socket Placement
- Button on flap: 2.5 cm from flap edge, centered horizontally
- Socket on front panel: 5.5 cm above entry edge, centered horizontally
- Ensure button distance from flap edge equals socket distance from entry edge

### Hole Alignment
- **Mirror alignment**: For single-piece construction, holes on left and right sides must be mirror images across the fold line
- **Spacing**: 5 mm between holes, 4 mm from edges
- **Count**: Ensure even number of holes for proper pairing when panels are sewn
- **Placement**: Place holes at both endpoints of seam paths to avoid offset

## Pattern Generation

### Dimensions Calculation
```python
# MacBook Pro 16" + UAG
LAP_W, LAP_H, LAP_T = 35.57, 24.81, 1.68     # Laptop dimensions
UAG_H, UAG_W, UAG_T = 0.40, 0.40, 0.82      # UAG case dimensions
HW = LAP_H + UAG_H                           # 25.21 (narrow side with case)
WW = LAP_W + UAG_W                           # 35.97 (long side with case)
TT = LAP_T + UAG_T                           # 2.50 (total thickness)

# Pattern parameters
SEAM_W = 0.4                                  # Seam allowance
INT_SLACK_W = 1.6                            # Interior slack width
INT_SLACK_D = 0.9                            # Interior slack depth
FLAP_H = 8.0                                 # Flap height

# Calculated dimensions
PW = HW + TT + INT_SLACK_W + SEAM_W         # 30.41 (width)
PH = WW + INT_SLACK_D + SEAM_W              # 37.97 (depth)
TOTAL_H = 2 * PH + FLAP_H                    # 83.94 (total height)
```

### Hole Generation
```python
# Left side holes
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((SEAM_W, y))
    holes.append((SEAM_W, TOTAL_H - y))

# Right side holes (mirrored)
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((PW - SEAM_W, y))
    holes.append((PW - SEAM_W, TOTAL_H - y))

# Top edge holes (flap)
for x in range(SEAM_W, PW - SEAM_W, HOLE_SPACING):
    holes.append((x, TOTAL_H - SEAM_W))
```

### Print Layout
- **A2 format**: 42.0 × 59.4 cm for single-piece patterns
- **Registration marks**: Place crosses at page overlap boundaries for multi-page patterns
- **Overlap**: 4 cm standard overlap for A2 multi-page patterns
- **Scale reference**: Include 10 cm reference line for manual verification

## Common Issues and Solutions

### Problem: Insufficient Interior Space
- **Cause**: Using naked laptop dimensions without case and slack
- **Solution**: Always calculate interior_width >= laptop_width + case_width + thickness + slack

### Problem: Hole Misalignment
- **Cause**: Using same y-coordinates for left and right sides instead of mirroring
- **Solution**: For left side holes at (x, y), use (PW-x, y) for right side holes

### Problem: Button Misalignment
- **Cause**: Button too close to fold line
- **Solution**: Place button 2.5 cm from flap edge, socket 5.5 cm above entry edge

### Problem: Pattern Too Large for Page
- **Cause**: Pattern dimensions exceed standard page sizes
- **Solution**: Split across multiple A2 pages with 4 cm overlap and registration marks

### Problem: Incorrect Device Orientation
- **Cause**: Swapping width and depth calculations
- **Solution**: Use clear variable names: DEVICE_WIDTH (narrow side), DEVICE_LENGTH (long side)

## Testing and Validation

### Automated Tests
- Verify geometry calculations match expected dimensions
- Test hole alignment and spacing
- Validate button and socket positions
- Check PDF page size matches target dimensions
- Test physical capacity with actual device measurements

### Manual Validation
- Print test pattern and verify scale with ruler
- Test hole alignment by folding paper and checking alignment
- Verify button placement by marking on test material
- Check flap overlap and closure mechanism

## Material Considerations

### Leather Selection
- Use 2-3 oz vegetable tanned leather for flexibility
- Ensure leather is large enough for pattern (minimum 90 × 70 cm)
- Consider grain direction for optimal strength

### Thread Selection
- Use waxed polyester or nylon thread for durability
- Thread length ≈ 3.5 × total seam length
- Include extra length for knots and backstitching

### Hardware
- Use snap buttons (size 16 or 18) for secure closure
- Consider rivets for reinforcement at stress points
- Use grommets if pattern requires holes larger than stitching guides

## Assembly Instructions

1. **Print pattern** at 100% scale on A2 paper
2. **Cut leather** following pattern outline
3. **Mark holes** using pattern as guide
4. **Sew seams** starting from bottom corners, working up
5. **Install snaps** at marked positions
6. **Fold at bottom** line to create back panel
7. **Test fit** with device and case
8. **Apply finish** (conditioner, edge sealant)

## Troubleshooting

### Device Too Tight
- Check interior dimensions against actual measurements
- Increase slack allowances if needed
- Verify case dimensions are accurate

### Flap Doesn't Close Properly
- Check button and socket alignment
- Verify flap overlap calculation
- Ensure no obstructions in interior

### Holes Don't Align
- Check hole spacing and mirror alignment
- Verify pattern was printed at correct scale
- Ensure leather was cut precisely along pattern lines

### Pattern Doesn't Fit on Leather
- Check leather size requirements
- Consider alternative layout or pattern scaling
- Verify pattern dimensions against available material