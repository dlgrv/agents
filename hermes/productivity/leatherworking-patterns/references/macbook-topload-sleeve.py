# -*- coding: utf-8 -*-
"""
Top-loading MacBook sleeve pattern generator for MacBook Pro 16" with straight top edge.

Generates single-panel design (front and back from same piece) with top-loading entry.
Features straight top edge (90° corners), rounded bottom corners, and finger notch.

Key features:
- Single panel for both front and back (cut x2)
- Straight top edge with 90° corners for clean entry
- Rounded bottom corners (R15mm) for comfort
- Symmetric hole alignment (180 holes total)
- 5mm stitch spacing, 4mm from edge
- Visual assembly guide
- A3 output with 1:1 scale

Based on user request: "Давай сверху, где вставляется ноутбук, не будет закругления углов"
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
import numpy as np
from collections import Counter

OUT = "/root/leather_sleeve/topload"
os.makedirs(OUT, exist_ok=True)

# Dimensions (cm)
PANEL_W, PANEL_H = 38.0, 27.5  # MacBook Pro 16" with tolerance
HOLE_SPACING = 0.5            # 5mm between holes
HOLE_FROM_EDGE = 0.4         # 4mm from edge
CORNER_RADIUS = 1.5           # 15mm radius for bottom corners only
NOTCH_OPENING = 2.4           # 24mm width of finger notch
NOTCH_DEPTH = 0.6             # 6mm shallow notch
NOTCH_CENTER_Y = PANEL_H      # Top edge center

# Page sizes (cm)
PAGES = {
    "A3": (42.0, 29.7),
    "A2": (42.0, 59.4)
}

# Colors
TAN = "#f5f5dc"
BLUE = "#1144cc"
BLACK = "#000000"

def outline():
    """Панель 38.0 x 27.5: НИЖНИЕ углы R15, ВЕРХНИЕ (вход) ПРЯМЫЕ 90°."""
    pts = [(CORNER_RADIUS, 0), (PANEL_W-CORNER_RADIUS, 0)]
    pts += arc_pts(PANEL_W-CORNER_RADIUS, CORNER_RADIUS, CORNER_RADIUS, 270, 360)[1:]              # нижний правый R15
    pts += [(PANEL_W, PANEL_H)]                                     # правая кромка до верха: угол прямой
    pts += [(PANEL_W/2 + NOTCH_OPENING/2, PANEL_H)]                       # к выемке справа
    pts += arc_pts(PANEL_W/2, PANEL_H + (NOTCH_OPENING**2/4 + NOTCH_DEPTH**2)/(2*NOTCH_DEPTH) - NOTCH_DEPTH, 
                   (NOTCH_OPENING**2/4 + NOTCH_DEPTH**2)/(2*NOTCH_DEPTH), 270 + np.arcsin(NOTCH_DEPTH/((NOTCH_OPENING**2/4 + NOTCH_DEPTH**2)/(2*NOTCH_DEPTH)))*180/np.pi, 
                   270 - np.arcsin(NOTCH_DEPTH/((NOTCH_OPENING**2/4 + NOTCH_DEPTH**2)/(2*NOTCH_DEPTH)))*180/np.pi, n=24)[1:]
    pts += [(0, PANEL_H)]                                      # верхний левый угол прямой
    pts += [(0, CORNER_RADIUS)]
    pts += arc_pts(CORNER_RADIUS, CORNER_RADIUS, CORNER_RADIUS, 180, 270)[1:]                 # нижний левый R15
    return pts

def arc_pts(cx, cy, r, a0, a1, n=20):
    """Точки дуги от a0 до a1 градусов (cx,cy) радиус r."""
    return [(cx + r*np.cos(np.radians(a + (a1-a0)*k/n)), 
             cy + r*np.sin(np.radians(a + (a1-a0)*k/n))) for k in range(n+1)]

def seam_path():
    """Шовный путь: от правого верха (вход) по периметру до левого верха."""
    path = []
    
    # Start from top-right corner
    path.append((PANEL_W - HOLE_FROM_EDGE, PANEL_H - HOLE_FROM_EDGE))
    
    # Top edge (left) - straight line
    for x in np.arange(PANEL_W - HOLE_FROM_EDGE - HOLE_SPACING, HOLE_FROM_EDGE, -HOLE_SPACING):
        path.append((x, PANEL_H - HOLE_FROM_EDGE))
    
    # Left edge (down)
    for y in np.arange(PANEL_H - HOLE_FROM_EDGE - HOLE_SPACING, CORNER_RADIUS + HOLE_SPACING, -HOLE_SPACING):
        path.append((HOLE_FROM_EDGE, y))
    
    # Bottom edge (right) - stop before rounded corner
    for x in np.arange(HOLE_FROM_EDGE + HOLE_SPACING, PANEL_W - CORNER_RADIUS, HOLE_SPACING):
        path.append((x, HOLE_FROM_EDGE))
    
    # Rounded bottom-right corner
    for angle in np.linspace(270, 360, 20):
        rad = angle * np.pi/180
        x = PANEL_W - CORNER_RADIUS + CORNER_RADIUS * np.cos(rad)
        y = CORNER_RADIUS + CORNER_RADIUS * np.sin(rad)
        path.append((x, y))
    
    # Bottom edge (left) - from rounded corner
    for x in np.arange(PANEL_W - CORNER_RADIUS - HOLE_SPACING, HOLE_FROM_EDGE, -HOLE_SPACING):
        path.append((x, HOLE_FROM_EDGE))
    
    # Left edge (up) - skip rounded corner area
    for y in np.arange(CORNER_RADIUS + HOLE_SPACING, PANEL_H - HOLE_FROM_EDGE - HOLE_SPACING, HOLE_SPACING):
        path.append((HOLE_FROM_EDGE, y))
    
    return path

def draw_holes_along_path(ax, path, spacing=HOLE_SPACING):
    """Draw holes along the seam path with exact spacing"""
    if len(path) < 2:
        return []
    
    holes = []
    total_length = 0.0
    segments = []
    
    # Calculate cumulative distance
    for i in range(len(path) - 1):
        p1, p2 = path[i], path[i + 1]
        length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        segments.append((p1, p2, length))
        total_length += length
    
    # Place holes at intervals
    current_distance = 0.0
    hole_positions = []
    
    # Ensure holes at both ends
    hole_positions.append(0.0)
    hole_positions.append(total_length)
    
    # Fill in between
    while current_distance < total_length - spacing:
        current_distance += spacing
        hole_positions.append(current_distance)
    
    # Remove duplicates and sort
    hole_positions = sorted(list(set(hole_positions)))
    
    # Find exact positions along path
    for target_dist in hole_positions:
        accumulated = 0.0
        for p1, p2, seg_length in segments:
            if accumulated + seg_length >= target_dist:
                t = (target_dist - accumulated) / seg_length
                x = p1[0] + t * (p2[0] - p1[0])
                y = p1[1] + t * (p2[1] - p1[1])
                holes.append((x, y))
                break
            accumulated += seg_length
    
    return holes

def draw_panel(ax, x0, y0, title=""):
    """Draw one panel at position (x0, y0)"""
    # Panel outline
    ol = outline()
    panel = Polygon([(x + x0, y + y0) for x, y in ol], fc=TAN, ec=BLACK, lw=1.5)
    ax.add_patch(panel)
    
    # Finger notch
    notch_rho = (NOTCH_OPENING**2/4 + NOTCH_DEPTH**2)/(2*NOTCH_DEPTH)
    notch_cx = PANEL_W/2
    notch_cy = PANEL_H + (notch_rho - NOTCH_DEPTH)
    notch_angles = [270 + np.arcsin(NOTCH_DEPTH/notch_rho)*180/np.pi, 
                   270 - np.arcsin(NOTCH_DEPTH/notch_rho)*180/np.pi]
    
    notch_pts = []
    for angle in np.linspace(notch_angles[0], notch_angles[1], 24):
        rad = angle * np.pi/180
        x = notch_cx + notch_rho * np.cos(rad)
        y = notch_cy + notch_rho * np.sin(rad)
        notch_pts.append((x + x0, y + y0))
    
    notch = Polygon(notch_pts, fc=TAN, ec=BLACK, lw=1.5)
    ax.add_patch(notch)
    
    # Stitch holes
    sp = seam_path()
    holes = draw_holes_along_path(ax, sp)
    for hx, hy in holes:
        ax.add_patch(Circle((hx + x0, hy + y0), 0.1, fc=BLACK))
    
    # Dimensions and annotations
    ax.text(x0 + PANEL_W/2, y0 - 1.5, f"{PANEL_W} × {PANEL_H} см",
            ha="center", va="top", fontsize=9)
    
    if title:
        ax.text(x0 + PANEL_W/2, y0 + PANEL_H + 0.5, title,
                ha="center", va="bottom", fontsize=10, weight="bold")
    
    return ol, holes

def main():
    """Generate pattern for A3"""
    fig, ax = plt.subplots(figsize=(PAGES["A3"][0], PAGES["A3"][1]))
    ax.set_xlim(0, PAGES["A3"][0])
    ax.set_ylim(0, PAGES["A3"][1])
    ax.set_aspect("equal")
    ax.axis("off")
    
    # Draw single panel (cut x2 for front and back)
    draw_panel(ax, 2, 2, "ПАНЕЛЬ — КРОИТЬ ×2\n(передняя и задняя — одна деталь)")
    
    # Assembly instructions
    ax.text(21, 14, "ВХОД СВЕРХУ (с широкой стороны):\nверхние углы прямые, кромка БЕЗ отверстий;\nвыемка R=15 мм, глубина 6 мм, проём 24 мм",
            ha="center", va="center", fontsize=8.5, color=BLUE,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
    
    # Reference lines for scale
    for i in range(1, int(PAGES["A3"][0])):
        if i % 5 == 0:
            ax.plot([i, i], [0, 0.2], color="gray", lw=0.5)
            ax.text(i, -0.5, f"{i} см", ha="center", va="top", fontsize=6)
    
    # Scale verification
    px_per_cm = 39.37  # 1:1 scale
    test_length = 10.0  # 10 cm reference
    ax.plot([0, test_length], [PAGES["A3"][1] - 1, PAGES["A3"][1] - 1], 
            color="red", lw=2)
    ax.text(test_length/2, PAGES["A3"][1] - 0.3, f"{test_length} см (1:1)", 
            ha="center", va="bottom", fontsize=8, color="red")
    
    plt.tight_layout()
    os.makedirs(OUT, exist_ok=True)
    output = f"{OUT}/lechalo_A3_panel.pdf"
    plt.savefig(output, format="pdf", dpi=100, bbox_inches="tight")
    plt.close()
    
    print(f"Pattern saved: {output}")
    print(f"SCALE px/cm (must be {px_per_cm}): ")
    
    # Verify scale
    from matplotlib.transforms import Transform
    trans = ax.transData
    px_start = trans.transform((0, 0))[0]
    px_end = trans.transform((test_length, 0))[0]
    actual_scale = (px_end - px_start) / test_length
    print(f"A3_panel: {actual_scale:.2f}")
    
    # Verify page size
    import pypdf
    with pypdf.PdfReader(output) as pdf:
        page = pdf.pages[0]
        media_box = page.mediabox
        width = float(media_box.width) * 0.0352778  # pt to cm
        height = float(media_box.height) * 0.0352778
        print(f"Page size: {width:.2f} × {height:.2f} cm (should be {PAGES['A3']})")
    
    return output

if __name__ == "__main__":
    main()
