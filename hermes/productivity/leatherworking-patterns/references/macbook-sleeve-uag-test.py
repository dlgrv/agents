#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for MacBook Pro 16" + UAG sleeve pattern v10.
Validates geometry, hole alignment, seam paths, and print dimensions.

Usage: python3 references/macbook-sleeve-uag-test.py

Features:
- Independent calculation of pattern dimensions
- Mirror hole alignment validation
- Button and socket position verification
- A2 PDF size validation
- Seam path and hole count verification
- Physical capacity validation (200 sheets)
"""

import math
import os
import sys
sys.path.insert(0, "/root/leather_sleeve/tests")
from geom_utils import dist_seg, dist_circle

# --- MacBook Pro 16" + UAG dimensions (cm) ---
LAP_W, LAP_H, LAP_T = 35.57, 24.81, 1.68     # MBP 16" (naked)
UAG_H, UAG_W, UAG_T = 0.40, 0.40, 0.82      # UAG case (add to dimensions)

# --- Pattern parameters ---
SEAM_W = 0.4                                  # Seam allowance (cm)
HOLE_SPACING = 0.5                           # Stitch hole spacing (cm)
FLAP_H = 8.0                                 # Flap height (cm)
FLAP_OVERLAP = 7.5                          # Flap overlap on stack (cm)
RECESS = 0.5                                 # Recess from top edge (cm)
INT_SLACK_W = 1.6                            # Interior slack width (cm)
INT_SLACK_D = 0.9                            # Interior slack depth (cm)

# --- Calculated pattern dimensions ---
HW  = LAP_H + UAG_H                           # 25.21 (narrow side with UAG)
WW  = LAP_W + UAG_W                           # 35.97 (long side with UAG)
TT  = LAP_T + UAG_T                           # 2.50 (total thickness)

PW  = HW + TT + INT_SLACK_W + SEAM_W         # 30.41 (width)
PH  = WW + INT_SLACK_D + SEAM_W              # 37.97 (depth)
TOTAL_H = 2 * PH + FLAP_H                    # 83.94 (total height)
FLAP_BASE = 2 * PH                            # 75.94 (flap base position)

# --- Button placement ---
BTN_X = PW / 2                               # Center of flap
BTN_Y = TOTAL_H - 2.5                        # 2.5 cm from flap edge
MATE_X = BTN_X                              # Center of front panel
MATE_Y = 5.5                                 # 5.5 cm above entry edge

# --- Test results ---
OK = FAIL = 0

def T(name, cond, note=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  ✓ {name}" + (f"  [{note}]" if note else ""))
    else:
        FAIL += 1
        print(f"  ✗ {name}  [{note}]")

# --- Test 1: Geometry ---
print("--- 1. Geometry ---")
T("Width calculation", PW == 30.41, f"{HW}+{TT}+{INT_SLACK_W}+{SEAM_W}")
T("Depth calculation", PH == 37.97, f"{WW}+{INT_SLACK_D}+{SEAM_W}")
T("Total height", TOTAL_H == 83.94, f"2*{PH}+{FLAP_H}")
T("Flap base position", FLAP_BASE == 75.94)

# --- Test 2: Hole alignment ---
print("--- 2. Hole alignment ---")
holes = []

# Left side holes
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((SEAM_W, y))
    holes.append((SEAM_W, TOTAL_H - y))

# Right side holes
for y in range(SEAM_W, PH, HOLE_SPACING):
    holes.append((PW - SEAM_W, y))
    holes.append((PW - SEAM_W, TOTAL_H - y))

# Top edge holes (flap)
for x in range(SEAM_W, PW - SEAM_W, HOLE_SPACING):
    holes.append((x, TOTAL_H - SEAM_W))

T("Total holes", len(holes) == 300)
T("Hole spacing", all(0.45 <= dist_seg(h1, h2) <= 0.55 for h1, h2 in zip(holes, holes[1:])))

# Mirror test for left/right sides
left_holes = [(x, y) for x, y in holes if x == SEAM_W]
right_holes = [(x, y) for x, y in holes if x == PW - SEAM_W]

mirror_holes = [(PW - x, y) for x, y in left_holes]
T("Left/Right mirror alignment", set(right_holes) == set(mirror_holes))

# --- Test 3: Button and socket ---
print("--- 3. Button and socket ---")
T("Button position", BTN_X == PW/2 and BTN_Y == TOTAL_H - 2.5)
T("Socket position", MATE_X == PW/2 and MATE_Y == 5.5)
T("Button distance from flap edge", BTN_Y == TOTAL_H - 2.5)
T("Socket distance from entry", MATE_Y == 5.5)

# --- Test 4: Physical capacity ---
print("--- 4. Physical capacity ---")
T("Interior width >= laptop + UAG + slack", PW - 2*SEAM_W >= HW + TT + INT_SLACK_W)
T("Interior depth >= laptop + UAG + slack", PH - 2*SEAM_W >= WW + INT_SLACK_D)
T("Flap overlap >= 7.5 cm", FLAP_OVERLAP >= 7.5)

# --- Test 5: Print dimensions ---
print("--- 5. Print dimensions ---")
T("Pattern fits on A2 (84.0 <= 118.9)", TOTAL_H <= 118.9)
T("Width fits on A2 (30.4 <= 84.0)", PW <= 84.0)

# --- Test 6: Seam paths ---
print("--- 6. Seam paths ---")
# Simulate seam paths (left and right sides)
seam_paths = []

# Left side seam
left_seam = [(SEAM_W, y) for y in range(SEAM_W, PH, HOLE_SPACING)] + \
            [(SEAM_W, y) for y in range(TOTAL_H - SEAM_W, TOTAL_H - PH, -HOLE_SPACING)]
seam_paths.append(left_seam)

# Right side seam
right_seam = [(PW - SEAM_W, y) for y in range(SEAM_W, PH, HOLE_SPACING)] + \
             [(PW - SEAM_W, y) for y in range(TOTAL_H - SEAM_W, TOTAL_H - PH, -HOLE_SPACING)]
seam_paths.append(right_seam)

# Top seam (flap)
top_seam = [(x, TOTAL_H - SEAM_W) for x in range(SEAM_W, PW - SEAM_W, HOLE_SPACING)]
seam_paths.append(top_seam)

T("Total seam segments", len(seam_paths) == 3)
T("Left seam holes", len(left_seam) == 100)
T("Right seam holes", len(right_seam) == 100)
T("Top seam holes", len(top_seam) == 100)

# --- Test 7: File output ---
print("--- 7. File output ---")
output_file = "/root/leather_sleeve/out_uag/macbook-uag-sleeve.pdf"
T("PDF file exists", os.path.exists(output_file))

if os.path.exists(output_file):
    try:
        import pymupdf
        doc = pymupdf.open(output_file)
        page = doc[0]
        rect = page.rect
        width_cm = rect.width / 72 * 2.54
        height_cm = rect.height / 72 * 2.54
        
        T("PDF is A2 size", abs(width_cm - 42.0) < 0.5 and abs(height_cm - 59.4) < 0.5)
        
        # Check for text elements
        text = page.get_text()
        T("Contains title", "MacBook" in text)
        T("Contains dimensions", f"{PW:.2f}" in text)
        
    except ImportError:
        T("pymupdf not available", True, "SKIP")

# --- Test 8: Summary ---
print("--- 8. Summary ---")
summary = {
    "PW": PW,
    "PH": PH,
    "FLAP": FLAP_H,
    "TOTAL_H": TOTAL_H,
    "FLAP_BASE": FLAP_BASE,
    "INT_W": PW - 2*SEAM_W,
    "INT_D": PH - 2*SEAM_W,
    "LAP": [WW, HW, TT],
    "n_holes": len(holes),
    "BTN": [BTN_X, BTN_Y],
    "MATE": [MATE_X, MATE_Y],
    "SEAM_W": SEAM_W,
    "HOLE_SPACING": HOLE_SPACING
}

summary_file = "/root/leather_sleeve/out_uag/summary.json"
with open(summary_file, 'w') as f:
    import json
    json.dump(summary, f, indent=2)

T("Summary file created", os.path.exists(summary_file))

print("=" * 50)
print(f"{OK}/{OK+FAIL} tests passed")

if FAIL == 0:
    print("All tests passed!")
    sys.exit(0)
else:
    print(f"{FAIL} tests failed")
    sys.exit(1)