# MacBook Sleeve Pattern Testing and Validation

## Overview

Comprehensive testing procedures for MacBook sleeve patterns to ensure geometric accuracy, hole alignment, physical capacity, and print quality. These tests validate both automated generation and manual assembly processes.

## Test Categories

### 1. Geometry Validation

#### Dimension Accuracy
- **Test**: Verify all calculated dimensions match expected values
- **Expected**: PW, PH, TOTAL_H, FLAP_H within ±0.01 cm of calculated values
- **Method**: Compare pattern output with dimension constants in script
- **Critical**: Pattern dimensions must match physical device requirements

#### Entry Orientation
- **Test**: Confirm pattern orientation matches specified entry side
- **Expected**: Wide-side entry uses PW = device_length + case + slack
- **Narrow-side entry uses PW = device_width + case + slack
- **Method**: Check dimension assignments against entry orientation specification
- **Pitfall**: Swapping width/depth calculations leads to incorrect device orientation

#### UAG Case Compatibility
- **Test**: Verify interior dimensions accommodate device + case + slack
- **Expected**: Interior width ≥ laptop_width + case_width + thickness + slack
- **Interior depth ≥ laptop_length + case_length + depth_slack
- **Method**: Calculate interior dimensions from pattern dimensions
- **Critical**: Insufficient space causes device jamming

### 2. Hole Alignment Tests

#### Mirror Symmetry Across Fold Line
- **Test**: Verify left and right side holes are mirror images across fold line
- **Expected**: For left hole at (x, y), right hole at (PW-x, y)
- **Method**: Extract hole coordinates and verify mirror relationship
- **Pitfall**: Using same y-coordinates instead of mirroring causes misalignment

#### Hole Count and Spacing
- **Test**: Verify hole count matches calculation and spacing is consistent
- **Expected**: Total holes = round(total_seam_length / hole_spacing) + 1 (for open paths)
- **Spacing**: 5 mm between holes, 4 mm from edges
- **Method**: Count holes and measure distances between adjacent holes
- **Critical**: Missing holes cause incomplete seams

#### Hole Placement at Endpoints
- **Test**: Verify holes are placed at both endpoints of seam paths
- **Expected**: Holes at start and end of each seam segment
- **Method**: Check first and last holes on each side
- **Pitfall**: Missing endpoint holes cause offset when panels are sewn

#### Flap Edge Holes
- **Test**: Verify holes along flap free edge for sewing flap to main panel
- **Expected**: Holes spaced 5 mm apart along flap edge
- **Method**: Extract y-coordinates of holes at TOTAL_H - SEAM_W
- **Critical**: Missing flap holes prevent flap attachment

### 3. Button and Socket Alignment

#### Button Position
- **Test**: Verify button is centered on flap, 2.5 cm from flap edge
- **Expected**: BTN_X = PW/2, BTN_Y = TOTAL_H - 2.5
- **Method**: Extract button coordinates from pattern
- **Pitfall**: Button too close to fold line causes misalignment

#### Socket Position
- **Test**: Verify socket is centered on front panel, 5.5 cm above entry edge
- **Expected**: MATE_X = PW/2, MATE_Y = 5.5
- **Method**: Extract socket coordinates from pattern
- **Critical**: Misaligned socket prevents proper closure

#### Button-Socket Alignment
- **Test**: Verify button distance from flap edge equals socket distance from entry edge
- **Expected**: (TOTAL_H - BTN_Y) = (MATE_Y - 0)
- **Method**: Calculate distances and verify equality
- **Pitfall**: Unequal distances prevent proper flap closure

### 4. Print Quality Tests

#### PDF Page Dimensions
- **Test**: Verify PDF pages match target dimensions exactly
- **Expected**: A2 = 42.0 × 59.4 cm, A3 = 42.0 × 29.7 cm, A4 = 29.7 × 21.0 cm
- **Method**: Use pymupdf to measure page dimensions
- **Critical**: Incorrect dimensions cause scaling errors when printing

#### Scale Accuracy
- **Test**: Verify 1:1 scale ratio (39.37 px/cm)
- **Expected**: 1 cm in drawing = 39.37 pixels in output
- **Method**: Use ax.transData.transform() to verify pixel-to-cm ratio
- **Pitfall**: Scale drift causes misalignment of holes and dimensions

#### Text Positioning
- **Test**: Verify all text annotations are within printable area
- **Expected**: All text ≥5 mm from page edges
- **Method**: Extract text coordinates and check distance from page boundaries
- **Pitfall**: Text near edges gets clipped by printers

#### Registration Marks
- **Test**: Verify registration marks are present and correctly positioned
- **Expected**: Cross marks at page boundaries for multi-page patterns
- **Method**: Check for visual elements at page edges
- **Critical**: Missing registration marks prevent page alignment

### 5. Physical Capacity Tests

#### Interior Space Calculation
- **Test**: Verify interior dimensions accommodate device + case + slack
- **Expected**: Interior width ≥ device_width + case_width + thickness + slack
- **Interior depth ≥ device_length + case_length + depth_slack
- **Method**: Calculate interior dimensions from pattern
- **Critical**: Insufficient space causes device jamming

#### Flap Overlap
- **Test**: Verify flap covers device adequately when closed
- **Expected**: Flap overlap ≥7.5 cm for secure coverage
- **Method**: Calculate flap overlap from flap height and entry edge position
- **Pitfall**: Insufficient overlap leaves device exposed

#### Device Insertion Test
- **Test**: Verify device can be inserted and removed easily
- **Expected**: Device fits with slight resistance for security
- **Method**: Test with actual device and case
- **Critical**: Too tight or too loose affects user experience

### 6. Assembly Process Tests

#### Hole Alignment During Assembly
- **Test**: Verify holes align correctly when leather is folded
- **Expected**: Left and right holes align when folded at bottom
- **Method**: Fold test paper and check hole alignment
- **Pitfall**: Mirror calculation errors cause misalignment

#### Button Closure Test
- **Test**: Verify button and socket align properly when flap is closed
- **Expected**: Button snaps into socket securely
- **Method**: Test closure with actual snap buttons
- **Critical**: Misaligned buttons prevent secure closure

#### Fold Line Accuracy
- **Test**: Verify fold line is correctly positioned and marked
- **Expected**: Fold line at y = PH for single-piece construction
- **Method**: Check fold line position in pattern
- **Pitfall**: Incorrect fold line creates poor fit

## Automated Test Suite Structure

```python
# Example test structure for flap-based MacBook sleeve patterns
class TestMacBookSleeveFlap:
    def test_geometry_dimensions(self):
        """Test all calculated dimensions match expected values"""
        assert abs(PW - 30.41) < 0.01
        assert abs(PH - 37.97) < 0.01
        assert abs(TOTAL_H - 84.94) < 0.01
        assert abs(FLAP_H - 9.0) < 0.01

    def test_hole_alignment(self):
        """Test mirror symmetry across fold line"""
        left_holes = [(x, y) for x, y in holes if x < PW/2]
        right_holes = [(PW-x, y) for x, y in left_holes]
        right_holes_actual = [(x, y) for x, y in holes if x > PW/2]
        assert len(right_holes) == len(right_holes_actual)

    def test_button_socket_alignment(self):
        """Test button and socket positioning"""
        assert abs(BTN_X - PW/2) < 0.01
        assert abs(BTN_Y - (TOTAL_H - 2.5)) < 0.01
        assert abs(MATE_X - PW/2) < 0.01
        assert abs(MATE_Y - 5.5) < 0.01

    def test_hole_count(self):
        """Test hole count matches calculation"""
        expected_holes = round(2 * (PH - 2*SEAM_W) / HOLE_SPACING) * 4 + round(PW / HOLE_SPACING)
        assert len(holes) == expected_holes

    def test_pdf_dimensions(self):
        """Test PDF pages match target dimensions"""
        pdf_dims = get_pdf_dimensions("output.pdf")
        assert pdf_dims == (42.0, 59.4)  # A2

    def test_scale_accuracy(self):
        """Test 1:1 scale ratio"""
        ratio = get_pixel_to_cm_ratio()
        assert abs(ratio - 39.37) < 0.1
```

## Test Execution and Reporting

### Test Environment Setup
- **Python 3.8+** with matplotlib, numpy, pypdf
- **Test pattern generation script**: Run pattern generation to create test files
- **Test measurement tools**: pymupdf for PDF validation, custom geometry functions

### Test Execution Order
1. **Generate pattern** using production script
2. **Run automated tests** to check geometry and alignment
3. **Validate PDF dimensions** and scale accuracy
4. **Perform manual validation** with printed test pattern
5. **Test physical assembly** with actual materials

### Test Reporting
- **Pass/Fail status** for each test case
- **Detailed error messages** for failed tests
- **Dimension comparison** tables for geometry tests
- **Hole alignment visualization** for symmetry tests
- **Physical test results** for capacity and assembly tests

## Common Test Failures and Solutions

### Test Failure: Dimension Mismatch
- **Symptom**: Calculated dimensions don't match expected values
- **Cause**: Incorrect dimension calculations or parameter changes
- **Solution**: Review dimension calculation formulas and update test expectations

### Test Failure: Hole Misalignment
- **Symptom**: Mirror symmetry test fails
- **Cause**: Incorrect hole coordinate calculation
- **Solution**: Fix mirror calculation in hole generation code

### Test Failure: Button Misalignment
- **Symptom**: Button or socket positioning test fails
- **Cause**: Incorrect button placement calculation
- **Solution**: Update button coordinate calculations and verify alignment logic

### Test Failure: Scale Drift
- **Symptom**: PDF dimensions don't match target dimensions
- **Cause**: Incorrect matplotlib figure size or DPI settings
- **Solution**: Verify figure size and DPI settings match target dimensions

### Test Failure: Insufficient Interior Space
- **Symptom**: Interior capacity test fails
- **Cause**: Insufficient slack allowances or incorrect case dimensions
- **Solution**: Review slack calculations and verify case dimensions

## Continuous Integration

### Automated Test Suite
- **Run tests** after every pattern generation
- **Test coverage**: Geometry, hole alignment, button placement, PDF quality
- **Integration**: Tests run as part of pattern generation workflow

### Regression Testing
- **Version tracking**: Maintain test expectations for each pattern version
- **Change detection**: Alert when pattern changes affect test results
- **Historical comparison**: Compare test results across pattern versions

### Performance Testing
- **Generation time**: Monitor pattern generation performance
- **Memory usage**: Check for memory leaks in large pattern generation
- **Output size**: Validate PDF file sizes are reasonable

## Advanced Validation Techniques

### 3D Visualization
- **Use**: Create 3D models of folded patterns to verify geometry
- **Benefit**: Early detection of assembly issues before physical prototyping
- **Tools**: Blender, OpenSCAD, or custom Python 3D libraries

### Stress Testing
- **Use**: Test pattern durability under simulated use conditions
- **Benefit**: Identify weak points in design before production
- **Methods**: Simulate repeated insertion/removal, pressure tests

### Material Testing
- **Use**: Test pattern with different leather types and thicknesses
- **Benefit**: Ensure pattern works with various materials
- **Methods**: Test with 2-3 oz leather, thick leather, synthetic materials

## Test Documentation

### Test Case Library
- **Geometry tests**: Dimension accuracy, entry orientation, UAG compatibility
- **Alignment tests**: Mirror symmetry, hole count, spacing
- **Closure tests**: Button placement, socket alignment, flap overlap
- **Print tests**: PDF dimensions, scale accuracy, text positioning
- **Assembly tests**: Hole alignment, button closure, fold line accuracy

### Test Result Archive
- **Version-specific results**: Store test results for each pattern version
- **Performance metrics**: Track generation time and output quality
- **Issue tracking**: Document and resolve test failures

### Best Practices Documentation
- **Test methodology**: Standard procedures for pattern validation
- **Troubleshooting guide**: Solutions for common test failures
- **Quality standards**: Acceptance criteria for pattern validation

## Conclusion

Comprehensive testing ensures MacBook sleeve patterns are geometrically accurate, physically functional, and ready for production. Automated tests catch errors early, while manual validation ensures real-world usability. By following these testing procedures, you can produce high-quality sleeve patterns that meet user expectations and manufacturing requirements.
