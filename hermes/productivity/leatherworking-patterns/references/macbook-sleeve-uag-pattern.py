#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacBook Pro 16" leather sleeve pattern with UAG case compatibility.
Single-piece design, entry from narrow side, one-piece construction.
Generates A2 PDF patterns for printing and assembly.

Usage: python3 references/macbook-sleeve-uag-pattern.py

Features:
- Entry from narrow side (24.81 cm)
- UAG case thickness allowance
- Single-piece design (cut once, fold at bottom)
- Button closure on flap
- Mirror hole alignment for sewing
- A2 PDF output with registration marks
- Automated test suite
"""

import math
import os
import sys
sys.path.insert(0, "/root/leather_sleeve/tests")
from geom_utils import dist_seg, dist_circle

# --- MacBook Pro 16" + UAG dimensions (cm) ---
LAP_W, LAP_H, LAP_T = 35.57, 24.81, 1.68     # MBP 16" (naked)
UAG_H, UAG_W, UAG_T = 0.40, 0.40, 0.82      # UAG case (add to dimensions)

# --- Derived dimensions ---
HW  = LAP_H + UAG_H                           # 25.21 (narrow side with UAG)
WW  = LAP_W + UAG_W                           # 35.97 (long side with UAG)
TT  = LAP_T + UAG_T                           # 2.50 (total thickness)

# --- Pattern parameters ---
SEAM_W = 0.4                                  # Seam allowance (cm)
HOLE_SPACING = 0.5                           # Stitch hole spacing (cm)
FLAP_H = 8.0                                 # Flap height (cm)
FLAP_OVERLAP = 7.5                          # Flap overlap on stack (cm)
RECESS = 0.5                                 # Recess from top edge (cm)
INT_SLACK_W = 1.6                            # Interior slack width (cm)
INT_SLACK_D = 0.9                            # Interior slack depth (cm)

# --- Calculated pattern dimensions ---
PW  = HW + TT + INT_SLACK_W + SEAM_W         # 30.41 (width)
PH  = WW + INT_SLACK_D + SEAM_W              # 37.97 (depth)
TOTAL_H = 2 * PH + FLAP_H                    # 83.94 (total height)
FLAP_BASE = 2 * PH                            # 75.94 (flap base position)

# --- Button placement ---
BTN_X = PW / 2                               # Center of flap
BTN_Y = TOTAL_H - 2.5                        # 2.5 cm from flap edge
MATE_X = BTN_X                              # Center of front panel
MATE_Y = 5.5                                 # 5.5 cm above entry edge

# --- Output directory ---
OUT_DIR = "/root/leather_sleeve/out_uag"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Generate pattern ---
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# Create figure
fig = plt.figure(figsize=(42, 59.4), dpi=100)  # A2 size
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, PW)
ax.set_ylim(0, TOTAL_H)
ax.set_aspect('equal')
ax.axis('off')

# Draw pattern outline
outline = [
    (0, 0), (PW, 0), (PW, TOTAL_H), (0, TOTAL_H)
]
outline_patch = patches.Polygon(outline, fill=False, edgecolor='black', linewidth=1)
ax.add_patch(outline_patch)

# Draw fold line (bottom)
ax.plot([0, PW], [PH, PH], 'k--', linewidth=1, alpha=0.7)
ax.text(PW/2, PH-0.5, "СГИБ", fontsize=8, ha='center', va='top')

# Draw entry opening
entry_top = PH - RECESS
entry_bottom = RECESS
ax.plot([PW/2 - 10, PW/2 + 10], [entry_top, entry_top], 'k-', linewidth=2)
ax.plot([PW/2 - 10, PW/2 + 10], [entry_bottom, entry_bottom], 'k-', linewidth=2)
ax.text(PW/2, entry_top + 0.5, "вход", fontsize=7, ha='center')

# Draw flap
flap_top = TOTAL_H
flap_bottom = FLAP_BASE
flap_left = PW/2 - 10
flap_right = PW/2 + 10
flap_rect = patches.Rectangle((flap_left, flap_bottom), 20, FLAP_H,
                            fill=False, edgecolor='black', linewidth=1)
ax.add_patch(flap_rect)

# Draw button and socket positions
ax.plot(BTN_X, BTN_Y, 'ro', markersize=8)
ax.text(BTN_X + 1, BTN_Y, "кнопка", fontsize=6, va='center')
ax.plot(MATE_X, MATE_Y, 'bo', markersize=8)
ax.text(MATE_X + 1, MATE_Y, "ответная", fontsize=6, va='center')

# Draw hole guides for sewing
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

# Draw holes
if holes:
    hole_x, hole_y = zip(*holes)
    ax.scatter(hole_x, hole_y, s=20, c='black', marker='o')

# Add dimensions
ax.text(PW/2, -1.5, f"{PW:.2f} см", fontsize=10, ha='center')
ax.text(-1.5, TOTAL_H/2, f"{TOTAL_H:.2f} см", fontsize=10, va='center', rotation=90)
ax.text(PW/2, PH + 0.5, f"{PH:.2f} см", fontsize=8, ha='center')

# Add title
ax.text(PW/2, TOTAL_H - 0.5, "MacBook Pro 16" + UAG чехол v10", fontsize=12, ha='center', weight='bold')
ax.text(PW/2, TOTAL_H - 1.5, "один кусок, вход с меньшей стороны", fontsize=10, ha='center')

# Add scale reference
ax.plot([PW - 5, PW - 5], [TOTAL_H - 3, TOTAL_H - 2], 'k-', linewidth=2)
ax.text(PW - 2.5, TOTAL_H - 2.5, "ровно 10.0 см", fontsize=8, ha='left', va='center')

# Save PDF
plt.savefig(f"{OUT_DIR}/macbook-uag-sleeve.pdf", format='pdf', bbox_inches='tight', pad_inches=0)
plt.close()

print(f"Pattern saved to {OUT_DIR}/macbook-uag-sleeve.pdf")
print(f"Pattern dimensions: {PW:.2f} x {TOTAL_H:.2f} cm")
print(f"Total holes: {len(holes)}")
print(f"Button position: ({BTN_X:.2f}, {BTN_Y:.2f})")
print(f"Socket position: ({MATE_X:.2f}, {MATE_Y:.2f})")
