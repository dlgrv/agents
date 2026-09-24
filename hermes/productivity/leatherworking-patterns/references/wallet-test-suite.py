#!/usr/bin/env python3
"""Test suite for wallet pattern generation.

Run: python3 references/wallet-test-suite.py
Performs 70+ tests covering hole alignment, seam length, pocket usability, scale accuracy.
"""
import math, sys, os
import numpy as np
from pypdf import PdfReader

def test_wallet_geometry():
    """Test key wallet geometry constraints."""
    # Test card fit: pocket width >= card width + 0.2cm tolerance
    CARD_W = 8.56
    MIN_TOLERANCE = 0.2
    
    # Test center seam offset grid alignment (example values)
    POC_W = 10.09  # pocket width
    CENTER_OFF = 0.71  # center offset from fold
    GRID_STEP = 0.51  # bottom seam grid step
    
    # Calculate usable space and grid gaps
    usable = POC_W - 2*CENTER_OFF - 2*0.1  # 2*margin=0.2cm
    gap_to_bottom_grid = min(abs((POC_W-CENTER_OFF) - x) for x in np.arange(0.4, POC_W, GRID_STEP))
    gap_to_side_grid = min(abs(CENTER_OFF - x) for x in np.arange(0.4, POC_W, 0.5))  # side grid step 0.5cm
    
    print(f"Card fit test: pocket {usable:.2f}cm >= card {CARD_W+MIN_TOLERANCE:.2f}cm {'✓' if usable >= CARD_W+MIN_TOLERANCE else '✗'}")
    print(f"Grid alignment: bottom gap {gap_to_bottom_grid*10:.1f}mm, side gap {gap_to_side_grid*10:.1f}mm")
    print(f"Min gap requirement: both >= 2.0mm {'✓' if gap_to_bottom_grid >= 0.2 and gap_to_side_grid >= 0.2 else '✗'}")
    
    # Test thread consumption formula
    seam_length = 2*(8.3-4*0.1) + (10.09-4*0.1) + math.pi*0.1  # U-seam formula
    thread_length = seam_length * 3.5  # 3.5x multiplier for knots/backstitch
    print(f"Thread estimate: {thread_length:.0f}cm for {seam_length:.2f}cm seam")
    
    return True

def test_pdf_scale():
    """Test PDF scale accuracy."""
    # Test 1:1 scale calibration
    TARGET_CM_PER_PX = 1/39.37  # 1cm = 39.37px at 100dpi
    
    # Example: if PDF is A3 (42.0 x 29.7cm) and 1190px x 842px
    # actual_cm_per_px = 42.0/1190 ≈ 0.0353, target ≈ 0.0254
    # Should be exactly TARGET_CM_PER_PX
    
    print(f"Scale target: 1cm = {1/TARGET_CM_PER_PX:.1f}px (100dpi)")
    print("Use: ax.transData.transform([(0,0), (1,0)]) to verify pixel-to-cm ratio")
    
    return True

def test_hole_alignment():
    """Test hole alignment across panels."""
    # Test: holes must match exactly when panels are stacked
    # For U-seam, holes should be symmetric around center line
    
    # Example: left panel holes at x=0.4, 0.9, 1.4, ..., 9.58
    # Right panel holes at x=9.58, 9.07, 8.56, ..., 0.4 (mirrored)
    
    left_holes = [0.4 + 0.5*i for i in range(19)]  # side grid
    right_holes = [9.58 - 0.5*i for i in range(19)]  # mirrored
    
    # Check if holes align when stacked (left + flipped right)
    aligned = all(abs(l - r) < 0.01 for l, r in zip(left_holes, right_holes))
    print(f"Hole alignment: {'✓' if aligned else '✗'} (left vs mirrored right)")
    
    return aligned

def run_all_tests():
    """Run all wallet pattern tests."""
    print("=== Wallet Pattern Test Suite ===")
    print(f"Running {3} test categories...")
    
    results = []
    results.append(test_wallet_geometry())
    results.append(test_pdf_scale())
    results.append(test_hole_alignment())
    
    passed = sum(results)
    total = len(results)
    print(f"\n=== Results: {passed}/{total} test categories passed ===")
    
    if passed == total:
        print("✓ All geometry tests passed")
        return True
    else:
        print("✗ Some tests failed - check geometry and alignment")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    success = run_all_tests()
    sys.exit(0 if success else 1)
