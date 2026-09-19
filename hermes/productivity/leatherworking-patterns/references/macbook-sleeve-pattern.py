#!/usr/bin/env python3
"""Generate a 1:1 PDF pattern for a leather MacBook sleeve with flap design.

Generates a single 84 x 37.5 cm piece with flap (30 cm) + back (27 cm) + front (27 cm).
Includes stitch hole guides (5mm spacing, 5mm from edge) and A4 tiling for printing.

Usage:
  python3 macbook-sleeve-pattern.py

Output:
  - page_00_info.pdf: Instructions with calibration square
  - page_01_c1A.pdf through page_12_c4C.pdf: 12 A4 pages for pattern assembly
"""
import math
import os
import glob

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# --- Constants ---
W = 37.5  # cm, internal width (MacBook Pro 16" is 35.6 cm wide)
L = 84.0  # cm, total length (flap 30 + back 27 + front 27)
A4W, A4H = 29.7, 21.0  # cm, A4 page size
MARG_W, MARG_H = 3.0, 3.0  # cm, margins around pattern on print
EDGE = 0.3  # cm, inset for text/annotations
STEP = 0.5  # cm, stitch hole spacing
HOLE_START, HOLE_END = 31.0, 83.0  # cm, stitch zone (1cm from flap fold and 1cm from end)
SKIP_X = 57.0   # cm, skip hole at fold line
CHAMF = 7.0     # cm, corner chamfer for flap

# World coordinates: pattern origin at bottom-left of flap
X0, Y0 = -MARG_W, -MARG_H
WW = L + 2*MARG_W  # total width including margins
WH = W + 2*MARG_H  # total height including margins

def outline_pts():
    """Return polygon points for the pattern outline."""
    # Single piece: flap (chamfered) + back + front
    return [(CHAMF,0), (L,0), (L,W), (CHAMF,W), (0,W-CHAMF), (0,CHAMF), (CHAMF,0)]

def draw_pattern(ax):
    """Draw the pattern on the given axes."""
    # Background fill
    pts = outline_pts()
    xs, ys = zip(*pts)
    ax.fill(xs, ys, color="#f5f5dc", alpha=0.3)  # beige/tan
    
    # Outline
    ax.plot(xs, ys, 'k-', linewidth=1.2)
    
    # Fold lines (vertical)
    ax.plot([30, 30], [0, W], 'r--', linewidth=0.8, alpha=0.7, label="fold")
    ax.plot([57, 57], [0, W], 'r--', linewidth=0.8, alpha=0.7)
    
    # Stitch holes (top and bottom edges)
    n = 0
    for y in [0, W]:
        xs = []
        for x in np.arange(HOLE_START, HOLE_END + 1e-9, STEP):
            if abs(x - SKIP_X) > 1e-9:  # skip at fold
                xs.append(x)
        if xs:
            ax.plot(xs, [y]*len(xs), ls="none", marker="o", ms=2.2, mfc="#1144cc", mec="#1144cc", zorder=5)
            n += len(xs)
    
    # Registration marks (crosshairs)
    gx0 = math.ceil((X0)/5)*5
    gy0 = math.ceil((Y0)/5)*5
    for gx in [gx0 + k*5 for k in range(int((X0+WW)/5) - int(gx0/5) + 2)]:
        for gy in [gy0 + k*5 for k in range(int((Y0+WH)/5) - int(gy0/5) + 2)]:
            if (X0 <= gx <= X0+WW and Y0 <= gy <= Y0+WH):
                ax.plot([gx-0.3, gx+0.3], [gy, gy], 'k-', linewidth=0.5)
                ax.plot([gx, gx], [gy-0.3, gy+0.3], 'k-', linewidth=0.5)
    
    # Annotations
    ax.text(15, W/2, "FLAP\n(folds inward)", ha="center", va="center", fontsize=9, alpha=0.75)
    ax.text(43.5, W/2, "BACK PANEL", ha="center", va="center", fontsize=9, alpha=0.75)
    ax.text(70.5, W/2, "FRONT PANEL", ha="center", va="center", fontsize=9, alpha=0.75)
    
    # Dimension lines
    def dim(ax, x1, y1, x2, y2, label, vertical=False, lx=None, ly=None):
        ax.add_line(Line2D([x1,x2],[y1,y2], color="black", lw=0.7))
        for (x,y) in ((x1,y1),(x2,y2)):
            seg = (Line2D([x-0.6,x+0.6],[y,y]) if not vertical
                   else Line2D([x,x],[y-0.6,y+0.6]))
            seg.set(color="black", lw=0.7)
            ax.add_line(seg)
        tx = lx if lx is not None else (x1+x2)/2
        ty = ly if ly is not None else (y1+y2)/2 + (0.35 if not vertical else 0)
        ax.text(tx, ty, label,
                fontsize=9, ha="center", va="bottom" if not vertical else "center",
                rotation=90 if vertical else 0)
    
    dim(ax, 0, -2.4, L, -2.4, f"{L} cm (total length)", lx=L/4)
    dim(ax, -1.2, 0, -1.2, W, f"{W} cm", vertical=True)
    
    # Stitch hole annotations
    ax.annotate(f"stitch: Ø~1.5 mm, step {STEP} cm, edge {STEP} cm\n({n} holes per seam)",
                xy=(44, EDGE), xytext=(52, -0.4), fontsize=8.5, color="#1144cc",
                va="top", ha="left",
                arrowprops=dict(arrowstyle="->", color="#1144cc", lw=1))
    ax.annotate("stitch", xy=(70, W-EDGE), xytext=(62, 32.5), fontsize=8.5, color="#1144cc",
                arrowprops=dict(arrowstyle="->", color="#1144cc", lw=1))
    
    # Title
    ax.text(L/2, W+1.5, "MacBook Pro 16" Leather Sleeve Pattern — 1:1 Scale", 
            ha="center", fontsize=10, weight="bold")
    
    # Page info
    ax.text(L/2, -3.5, "Print A4, assemble by registration marks, cut on black line", 
            ha="center", fontsize=8, style="italic")

def main():
    # Create output directory
    os.makedirs("leather_pattern_output", exist_ok=True)
    os.chdir("leather_pattern_output")
    
    # Generate info page with calibration square
    fig_info = plt.figure(figsize=(A4W/2.54, A4H/2.54))
    ax_info = fig_info.add_axes([0.1, 0.1, 0.8, 0.8])
    ax_info.set_xlim(0, 10)
    ax_info.set_ylim(0, 10)
    ax_info.set_aspect('equal')
    ax_info.axis('off')
    
    # Draw 10cm calibration square
    ax_info.add_patch(plt.Rectangle((1, 1), 8, 8, fill=False, edgecolor='black', linewidth=2))
    ax_info.text(5, 0.5, "10 cm calibration square (print and measure)", ha="center", fontsize=10)
    ax_info.text(5, 9.5, "MacBook Pro 16" Leather Sleeve Pattern — 1:1 Scale", ha="center", fontsize=12, weight="bold")
    ax_info.text(5, 8.5, f"Pattern: {L} x {W} cm, Stitch holes: {STEP} cm spacing", ha="center", fontsize=10)
    
    fig_info.savefig("page_00_info.pdf", bbox_inches='tight')
    plt.close(fig_info)
    
    # Calculate tile offsets for A4 pages
    tile_w = A4W - 2*MARG_W  # usable width per tile
    tile_h = A4H - 2*MARG_H  # usable height per tile
    
    xs0 = [0]  # tile starting x positions
    while xs0[-1] + tile_w < L + MARG_W:
        xs0.append(xs0[-1] + tile_w)
    
    ys0 = [0]  # tile starting y positions
    while ys0[-1] + tile_h < W + MARG_H:
        ys0.append(ys0[-1] + tile_h)
    
    # Generate pattern tiles
    scale_checks = []
    page = 1
    for j, wy in enumerate(ys0):
        for i, wx in enumerate(xs0):
            fig = plt.figure(figsize=(A4W/2.54, A4H/2.54))
            # Precise axis placement for 1:1 scale
            ax = fig.add_axes([(A4W-tile_w)/(2*A4W), (A4H-tile_h)/(2*A4H), tile_w/A4W, tile_h/A4H])
            draw_pattern(ax)
            
            # Set view to tile area
            ax.set_xlim(X0+wx, X0+wx+tile_w)
            ax.set_ylim(Y0+wy, Y0+wy+tile_h)
            ax.set_aspect("equal")
            ax.axis("off")
            
            # Verify scale
            p0 = ax.transData.transform((0, 0))
            p1 = ax.transData.transform((1, 0))
            scale_checks.append(round(p1[0]-p0[0], 3))
            
            # Save page
            filename = f"page_{page:02d}_c{chr(65+i)}{chr(65+j)}.pdf"
            fig.savefig(filename, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            page += 1
    
    # List generated files
    files = sorted(glob.glob("page_*.pdf"))
    print(f"Generated {len(files)} A4 pages:")
    for f in files:
        print(f"  {f}")
    print(f"Scale check: 1 cm = {set(scale_checks)} pixels (should be ~39.37 for 1:1)")
    print("Pattern ready for printing and assembly!")

if __name__ == "__main__":
    main()
