# Multi-Tier Wallet Debugging Workflow

This document outlines the systematic debugging approach used to resolve critical issues in complex wallet patterns with multiple tiers and center seams.

## Problem Discovery

1. **Independent Audit:** Always run an independent audit using a subagent with no prior knowledge of the pattern. This prevents confirmation bias and catches issues you might miss.

2. **Classification System:** Categorize issues by severity:
   - **CRITICAL:** Physical impossibilities (card doesn't fit, page boundary violations)
   - **MAJOR:** Design flaws that prevent proper function (hole collisions, misaligned seams)
   - **MINOR:** Documentation or minor usability issues

3. **Address in Order:** Fix CRITICAL issues first, then MAJOR, then MINOR. Each fix may affect later categories.

## Critical Issue Resolution

### Card Fit Issues

**Problem:** Card physically doesn't fit in pocket due to center seam placement
**Solution:** 
- Increase pocket width (LIN_W) to create more space
- Adjust center offset (CENTER_OFF) to balance space and grid alignment
- Verify usable space = pocket_width - 2*center_offset - 2*margin ≥ card_width + tolerance

**Example:**
- Original: LIN_W=9.58, CENTER_OFF=1.25 → usable space too small
- Fixed: LIN_W=10.09, CENTER_OFF=0.71 → 8.98cm usable ≥ 8.56cm card

### Page Boundary Violations

**Problem:** Increasing pocket width causes elements to extend beyond page
**Solution:**
- Calculate maximum allowed width: page_width - PX0 - margin - 2*POC_W
- Adjust PX0 (left margin) if needed to accommodate wider elements
- Verify all elements stay within ≥3mm printable margins

**Example:**
- Original: PX0=21.6, POC_W=10.09 → right edge at 41.69cm
- Fixed: PX0=21.0, POC_W=10.09 → right edge at 41.48cm (within 42.0cm page)

## Major Issue Resolution

### Hole Alignment Problems

**Problem:** Center seam aligns with stitch holes, causing shared holes between panels
**Solution:**
- Check center offset against both horizontal and vertical grids
- Ensure minimum 2mm gap from grid nodes for 5mm step
- If alignment occurs, adjust center offset or increase pocket width

**Example:**
- Grid step: 0.5cm (5mm)
- Minimum gap: 0.1cm (1mm from each side)
- Acceptable offsets: 0.6, 0.7, 0.8, 0.9cm (avoid 0.5, 1.0, 1.5, etc.)

### Tier Height Optimization

**Problem:** Tier heights don't provide adequate card protrusion
**Solution:**
- Design tiers with increasing heights (e.g., 2.65, 3.65, 4.65cm)
- Ensure each tier extends above the one below by 0.3-0.5cm
- Verify top edge of tier N is above bottom edge of tier N-1

**Example:**
- Tier 1 (back): 4.65cm height
- Tier 2 (middle): 3.65cm height (sits on top of tier 1)
- Tier 3 (front): 2.65cm height (sits on top of tier 2)
- Result: Cards in tier 3 protrude 0.3cm above tier 2

## Test Suite Maintenance

When modifying pattern parameters, update tests accordingly:

1. **Geometry Tests:** Update thresholds for new dimensions
2. **Hole Count Tests:** Verify left/right panel symmetry
3. **Boundary Tests:** Ensure all elements stay within page limits
4. **Grid Alignment Tests:** Check center offset against grids

**Example Test Updates:**
- Old: `abs(gap - 1.0) < 0.1` → New: `abs(gap - 0.71) < 0.1`
- Old: hardcoded `1.0*PX` → New: `g["bx"]*PX`

## Verification Process

1. **Regenerate Pattern:** Apply all fixes and regenerate PDF
2. **Run Tests:** Execute updated test suite
3. **Manual Inspection:** Use PDF tools to verify layout
4. **Independent Check:** Run audit script to catch any remaining issues

## Common Pitfalls to Avoid

1. **Test Drift:** Don't forget to update test expectations when changing geometry
2. **Coordinate Mismatch:** Use the same variable names in drawing and test code
3. **Margin Violations:** Always check ≥3mm margins from page edges
4. **Grid Alignment:** Verify center offset against both horizontal and vertical grids
5. **Hole Count Parity:** Ensure left and right panels have matching hole counts when mirrored

## Success Metrics

A pattern is ready when:
- All tests pass (70/70)
- No CRITICAL or MAJOR issues remain
- Card and bill fit with ≥0.2cm clearance
- All elements stay within printable margins
- Center offset avoids grid nodes by ≥2mm
- Thread length is realistically estimated (3.5x seam length)

## Tools Used

- `delegate_task` for independent audits
- `patch` for precise code changes
- `terminal` for running generation and tests
- `search_files` for locating test code
- `execute_code` for quick validation checks
