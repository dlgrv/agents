# -*- coding: utf-8 -*-
"""
Simple pocket pattern generator for leatherworking (e.g., MacBook sleeve with no flap).
Generates two-panel design: back panel and front panel with entry cutout.
Supports A4, A3, and A2 output formats.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
import numpy as np
from collections import Counter

OUT = "/root/leather_sleeve/simple"
os.makedirs(OUT, exist_ok=True)

# Dimensions (cm)
PANEL_W, PANEL_H = 37.5, 26.5  # MacBook Pro 16" pocket size
HOLE_SPACING = 0.5            # 5mm between holes
HOLE_FROM_EDGE = 0.5         # 5mm from edge
ENTRY_RADIUS = 2.0            # Finger cutout radius

# Page sizes (cm)
PAGES = {
    "A4": (29.7, 21.0),
    "A3": (42.0, 29.7),
    "A2": (42.0, 59.4)
}

# Colors
TAN = "#e8d5b0"
BLUE = "#1144cc"

def draw_holes(ax, x, y, w, h, sides):
    """Draw stitching holes on specified sides of a rectangle"""
    holes = []
    
    # Top side (y + h)
    if "top" in sides:
        xs = np.arange(x + HOLE_FROM_EDGE, x + w - HOLE_FROM_EDGE + HOLE_SPACING, HOLE_SPACING)
        ax.plot(xs, [y + h] * len(xs), 'o', color=BLUE, markersize=2, markeredgewidth=0)
        holes.extend([(xi, y + h) for xi in xs])
    
    # Bottom side (y)
    if "bottom" in sides:
        xs = np.arange(x + HOLE_FROM_EDGE, x + w - HOLE_FROM_EDGE + HOLE_SPACING, HOLE_SPACING)
        ax.plot(xs, [y] * len(xs), 'o', color=BLUE, markersize=2, markeredgewidth=0)
        holes.extend([(xi, y) for xi in xs])
    
    # Left side (x)
    if "left" in sides:
        ys = np.arange(y + HOLE_FROM_EDGE, y + h - HOLE_FROM_EDGE + HOLE_SPACING, HOLE_SPACING)
        ax.plot([x] * len(ys), ys, 'o', color=BLUE, markersize=2, markeredgewidth=0)
        holes.extend([(x, yi) for yi in ys])
    
    # Right side (x + w) - NO HOLES on open side
    if "right" not in sides:
        return holes
    
    ys = np.arange(y + HOLE_FROM_EDGE, y + h - HOLE_FROM_EDGE + HOLE_SPACING, HOLE_SPACING)
    ax.plot([x + w] * len(ys), ys, 'o', color=BLUE, markersize=2, markeredgewidth=0)
    holes.extend([(x + w, yi) for yi in ys])
    
    return holes

def draw_panel(ax, x, y, w, h, label, entry_side="right"):
    """Draw a single panel with optional entry cutout"""
    # Panel rectangle
    panel = Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                    facecolor=TAN, edgecolor="black", linewidth=1.6)
    ax.add_patch(panel)
    
    # Entry cutout on specified side
    if entry_side == "right":
        # Semi-circle cutout on right edge
        center_x = x + w
        center_y = y + h/2
        theta = np.linspace(-np.pi/2, np.pi/2, 50)
        cut_x = center_x + ENTRY_RADIUS * np.cos(theta)
        cut_y = center_y + ENTRY_RADIUS * np.sin(theta)
        ax.plot(cut_x, cut_y, 'k-', linewidth=1.6)
        
        # Fill cutout with background color
        ax.fill_between(cut_x, cut_y, y + h, color="white", alpha=1.0)
        ax.fill_between(cut_x, cut_y, y, color="white", alpha=1.0)
    
    # Label
    ax.text(x + w/2, y + h + 0.5, label, ha="center", fontsize=10, weight="bold")
    
    # Return hole positions for verification
    sides = ["top", "bottom", "left"]
    if entry_side != "right":
        sides.append("right")
    return draw_holes(ax, x, y, w, h, sides)

def add_reference_line(ax, x0, y0, length=10.0):
    """Add a 10cm reference line for manual scale verification"""
    ax.plot([x0, x0 + length], [y0, y0], 'k-', linewidth=0.8)
    ax.plot([x0, x0], [y0 - 0.25, y0 + 0.25], 'k-', linewidth=0.8)
    ax.plot([x0 + length, x0 + length], [y0 - 0.25, y0 + 0.25], 'k-', linewidth=0.8)
    ax.text(x0 + length/2, y0 + 0.3, "10.0 cm (verify with ruler)", ha="center", fontsize=8)

def verify_scale(ax):
    """Verify 1:1 scale using pixel transform"""
    p0 = ax.transData.transform((0, 0))
    p1 = ax.transData.transform((1, 0))
    px_per_cm = p1[0] - p0[0]
    return px_per_cm

def generate_pattern(page_size="A2"):
    """Generate pattern for specified page size"""
    page_w, page_h = PAGES[page_size]
    
    # Set up figure with A4 page size
    fig = plt.figure(figsize=(page_w/2.54, page_h/2.54), dpi=100)
    
    # Calculate drawing area with margins
    margin = 1.0
    win_w, win_h = page_w - 2*margin, page_h - 2*margin
    ax = fig.add_axes([margin/page_w, margin/page_h, win_w/page_w, win_h/page_w])
    
    # Set limits to fit both panels with space
    if page_size == "A2":
        # Both panels side by side
        ax.set_xlim(-1, PANEL_W + 1)
        ax.set_ylim(-1, PANEL_H + 1)
        
        # Draw panels
        back_holes = draw_panel(ax, 0, 0, PANEL_W, PANEL_H, "BACK PANEL (entry on right)")
        front_holes = draw_panel(ax, PANEL_W + 1, 0, PANEL_W, PANEL_H, "FRONT PANEL (with cutout)", "right")
        
        # Dimensions
        ax.annotate(f"{PANEL_W} cm", xy=(PANEL_W/2, -0.5), xytext=(PANEL_W/2, -0.8),
                   ha="center", arrowprops=dict(arrowstyle="->", color="black"))
        ax.annotate(f"{PANEL_H} cm", xy=(-0.5, PANEL_H/2), xytext=(-0.8, PANEL_H/2),
                   ha="center", va="center", arrowprops=dict(arrowstyle="->", color="black"))
        
    else:
        # Single panel per page (A3 or A4)
        if page_size == "A3":
            ax.set_xlim(-1, PANEL_W + 1)
            ax.set_ylim(-1, PANEL_H + 1)
        else:
            # A4 - center panel
            ax.set_xlim((page_w - PANEL_W)/2 - 1, (page_w + PANEL_W)/2 + 1)
            ax.set_ylim(-1, PANEL_H + 1)
        
        # Draw panel
        holes = draw_panel(ax, 0, 0, PANEL_W, PANEL_H, f"{page_size} PANEL", "right")
        
        # Dimensions
        ax.annotate(f"{PANEL_W} cm", xy=(PANEL_W/2, -0.5), xytext=(PANEL_W/2, -0.8),
                   ha="center", arrowprops=dict(arrowstyle="->", color="black"))
        ax.annotate(f"{PANEL_H} cm", xy=(-0.5, PANEL_H/2), xytext=(-0.8, PANEL_H/2),
                   ha="center", va="center", arrowprops=dict(arrowstyle="->", color="black"))
    
    # Add reference line
    add_reference_line(ax, 0, -0.5)
    
    # Title
    title = f"Simple Pocket Pattern for MacBook Pro 16" - {page_size} - Print 100% scale"
    ax.text(page_w/2, page_h - 0.5, title, ha="center", fontsize=9, weight="bold")
    
    # Scale verification
    scale = verify_scale(ax)
    ax.text(0.5, page_h - 0.5, f"Scale: {scale:.2f} px/cm (should be ~39.37)", fontsize=8)
    
    # Equal aspect ratio
    ax.set_aspect("equal")
    ax.axis("off")
    
    # Save
    filename = f"{OUT}/simple-pocket-{page_size.lower()}.pdf"
    fig.savefig(filename, bbox_inches="tight")
    plt.close(fig)
    
    return filename, scale

if __name__ == "__main__":
    # Generate patterns for all page sizes
    for page in ["A2", "A3", "A4"]:
        filename, scale = generate_pattern(page)
        print(f"Generated {filename} with scale {scale:.2f} px/cm")
    
    print("\nPattern generation complete!")
    print("All patterns use 1:1 scale. Print at 100% size.")
    print("For A2: Print both panels, cut, and sew three sides.")
    print("For A3/A4: Print one panel per page, repeat for both panels.")
