#!/usr/bin/env python3
"""Tote bag pattern generator for leatherworking.

Generates PDF patterns for oversized leather tote bags with:
- Two main panels (front/back) with gusset side panels
- Handle-rolls (rolled handles) with top fold construction
- Stitch hole guides (5mm spacing)
- A2/A3/A4 tiling with registration marks
- 1:1 scale calibration

Usage:
    python3 references/tote-bag-pattern.py

Output:
    tote-bag-pattern-A2.pdf (5 pages: 2× panel, 2× gusset, 1× handle)

Design:
    - Oversized tote: 55×38×22 cm (W×H×D)
    - Gusset: 22 cm side + 55 cm bottom + 22 cm side = 99 cm total
    - Handle rolls: 37×12 cm, rolled to Ø~3.5 cm
    - Top fold: 3 cm fold line with handles sandwiched inside
    - Stitch holes: 5mm spacing from edges
    - Registration marks: red crosses for page alignment

Requirements:
    Python 3.8+, matplotlib, numpy, pymupdf
    pip install matplotlib numpy pymupdf
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import pymupdf

# Configuration
PANEL_W, PANEL_H = 57.0, 42.0  # cm (oversized tote panels)
GUSSET_W, GUSSET_H = 99.0, 26.0  # cm (22+55+22 side+bottom+side)
HANDLE_W, HANDLE_H = 37.0, 12.0  # cm (rolled handle)
SEAM_ALLOWANCE = 1.0  # cm
HOLE_SPACING = 0.5  # cm
PAGE_W, PAGE_H = 42.0, 59.4  # A2 cm
FOLD_LINE = 3.0  # cm top fold for handle attachment

# Colors
CUT_COLOR = 'black'
FOLD_COLOR = 'green'
ZONE_COLOR = 'blue'
REG_COLOR = 'red'
TEXT_COLOR = 'black'


def panel_path():
    """Main panel outline (rectangle with rounded corners)."""
    return np.array([
        [0, 0],
        [PANEL_W, 0],
        [PANEL_W, PANEL_H],
        [0, PANEL_H],
        [0, 0]
    ])


def gusset_path():
    """Gusset strip: side 22 + bottom 55 + side 22."""
    return np.array([
        [0, 0],
        [GUSSET_W, 0],
        [GUSSET_W, GUSSET_H],
        [0, GUSSET_H],
        [0, 0]
    ])


def handle_path():
    """Handle strip for rolled handles."""
    return np.array([
        [0, 0],
        [HANDLE_W, 0],
        [HANDLE_W, HANDLE_H],
        [0, HANDLE_H],
        [0, 0]
    ])


def panel_holes():
    """Stitch holes along panel edges (left, bottom, right). Top edge is open."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, PANEL_H, HOLE_SPACING):
        holes.append([0, y])
    # Bottom edge (left to right)
    for x in np.arange(0, PANEL_W, HOLE_SPACING):
        holes.append([x, 0])
    # Right edge (bottom to top)
    for y in np.arange(0, PANEL_H, HOLE_SPACING):
        holes.append([PANEL_W, y])
    return np.array(holes)


def gusset_holes():
    """Stitch holes along gusset edges (left, bottom, right). Top edge is open."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, GUSSET_H, HOLE_SPACING):
        holes.append([0, y])
    # Bottom edge (left to right)
    for x in np.arange(0, GUSSET_W, HOLE_SPACING):
        holes.append([x, 0])
    # Right edge (bottom to top)
    for y in np.arange(0, GUSSET_H, HOLE_SPACING):
        holes.append([GUSSET_W, y])
    return np.array(holes)


def handle_holes():
    """Handle holes: short edges only (rolled handles)."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, HANDLE_H, HOLE_SPACING):
        holes.append([0, y])
    # Right edge (top to bottom)
    for y in np.arange(0, HANDLE_H, HOLE_SPACING):
        holes.append([HANDLE_W, y])
    return np.array(holes)


def draw_text(ax, x, y, text, size=10, weight='normal'):
    """Draw text with consistent styling."""
    ax.text(x, y, text, fontsize=size, weight=weight, color=TEXT_COLOR,
            ha='center', va='bottom', transform=ax.transData)


def dim_line(ax, x1, y1, x2, y2, label):
    """Draw dimension line with label."""
    ax.plot([x1, x2], [y1, y1], 'k-', lw=0.5)
    ax.plot([x1, x1], [y1-0.1, y1+0.1], 'k-', lw=0.5)
    ax.plot([x2, x2], [y1-0.1, y1+0.1], 'k-', lw=0.5)
    ax.text((x1+x2)/2, y1-0.3, label, fontsize=8, ha='center', va='top')


def add_registration_marks(ax):
    """Add red registration crosses at page corners."""
    for x, y in [(2, 2), (PAGE_W-2, 2), (PAGE_W-2, PAGE_H-2), (2, PAGE_H-2)]:
        ax.plot([x-0.5, x+0.5], [y, y], color=REG_COLOR, lw=1.5)
        ax.plot([x, x], [y-0.5, y+0.5], color=REG_COLOR, lw=1.5)


def add_scale_reference(ax):
    """Add 10 cm scale reference line."""
    ax.plot([5, 15], [PAGE_H-5, PAGE_H-5], 'k-', lw=1.5)
    ax.plot([5, 5], [PAGE_H-5.2, PAGE_H-4.8], 'k-', lw=1.5)
    ax.plot([15, 15], [PAGE_H-5.2, PAGE_H-4.8], 'k-', lw=1.5)
    ax.text(10, PAGE_H-3, '10 см', fontsize=9, ha='center', va='top')


def page_panel_half(ax, x_from, x_to, part_no, total_parts, junction_x_list):
    """Draw panel part with holes and annotations."""
    off = -x_from
    span = x_to - x_from
    clip = mpatches.Rectangle((0, 0), span, PAGE_H, transform=ax.transData)
    clip.set_visible(False)
    ax.add_patch(clip)
    
    # Draw panel outline
    p = panel_path() + [off, 0]
    poly = mpatches.Polygon(p, closed=True, fill=False, ec=CUT_COLOR, lw=1.8)
    ax.add_patch(poly)
    poly.set_clip_path(clip)
    
    # Draw holes
    lh, bh, rh = panel_holes()
    for hl in (lh, bh, rh):
        h = hl + [off, 0]
        m = (h[:, 0] >= 0) & (h[:, 0] <= span)
        ax.plot(h[m, 0], h[m, 1], '.', ms=2.2, color=CUT_COLOR, clip_path=clip)
    
    # Dimensions
    y0 = 0.5
    dim_line(ax, off + 0, y0, off + PANEL_W, y0, f'{PANEL_W:g}')
    dim_line(ax, off + PANEL_W + 0.5, y0, off + PANEL_W + 0.5, y0 + PANEL_H, f'{PANEL_H:g}')
    
    # Title and annotations
    title = f'Полотно {part_no}/{total_parts}'
    if total_parts > 1:
        title += f' (всего полотен {total_parts}, кроить ×2)'
    draw_text(ax, off + PANEL_W/2, PAGE_H-1, title, size=12, weight='bold')
    
    # Fold line
    if FOLD_LINE > 0:
        ax.plot([off, off + PANEL_W], [PAGE_H - FOLD_LINE, PAGE_H - FOLD_LINE], 
                color=FOLD_COLOR, ls='--', lw=1.2)
        ax.text(off + 1, PAGE_H - FOLD_LINE - 0.5, f'подгиб канта {FOLD_LINE} см', 
                fontsize=8, color=FOLD_COLOR)
    
    add_registration_marks(ax)
    add_scale_reference(ax)


def page_gusset_half(ax, x_from, x_to, part_no, total_parts):
    """Draw gusset part with holes and zone markings."""
    off = -x_from
    span = x_to - x_from
    clip = mpatches.Rectangle((0, 0), span, PAGE_H, transform=ax.transData)
    clip.set_visible(False)
    ax.add_patch(clip)
    
    # Draw gusset outline
    p = gusset_path() + [off, 0]
    poly = mpatches.Polygon(p, closed=True, fill=False, ec=CUT_COLOR, lw=1.8)
    ax.add_patch(poly)
    poly.set_clip_path(clip)
    
    # Draw holes
    lh, bh, rh = gusset_holes()
    for hl in (lh, bh, rh):
        h = hl + [off, 0]
        m = (h[:, 0] >= 0) & (h[:, 0] <= span)
        ax.plot(h[m, 0], h[m, 1], '.', ms=2.2, color=CUT_COLOR, clip_path=clip)
    
    # Zone markings: side 22 | bottom 55 | side 22
    ylab = GUSSET_H + 1.0
    for x0, x1, name in [(0, 22, 'бок 22'), (22, 77, 'дно 55'), (77, 99, 'бок 22')]:
        ax.plot([x0 + off, x1 + off], [ylab, ylab], color=ZONE_COLOR, lw=1.5)
        ax.text((x0 + x1)/2 + off, ylab + 0.3, name, fontsize=9, 
                color=ZONE_COLOR, ha='center', va='bottom')
    
    # Title
    draw_text(ax, off + GUSSET_W/2, PAGE_H-1, f'Gusset {part_no}/{total_parts}', 
              size=12, weight='bold')
    
    # Fold line
    if FOLD_LINE > 0:
        ax.plot([off, off + GUSSET_W], [PAGE_H - FOLD_LINE, PAGE_H - FOLD_LINE], 
                color=FOLD_COLOR, ls='--', lw=1.2)
        ax.text(off + 1, PAGE_H - FOLD_LINE - 0.5, f'подгиб канта {FOLD_LINE} см', 
                fontsize=8, color=FOLD_COLOR)
    
    add_registration_marks(ax)
    add_scale_reference(ax)


def page_handle_half(ax, x_from, x_to, part_no, total_parts):
    """Draw handle strip with holes and assembly instructions."""
    off = -x_from
    span = x_to - x_from
    clip = mpatches.Rectangle((0, 0), span, PAGE_H, transform=ax.transData)
    clip.set_visible(False)
    ax.add_patch(clip)
    
    # Draw handle outline
    p = handle_path() + [off, 0]
    poly = mpatches.Polygon(p, closed=True, fill=False, ec=CUT_COLOR, lw=1.8)
    ax.add_patch(poly)
    poly.set_clip_path(clip)
    
    # Draw holes (short edges only)
    lh, rh = handle_holes(), handle_holes()
    for hl in (lh, rh):
        h = hl + [off, 0]
        m = (h[:, 0] >= 0) & (h[:, 0] <= span)
        ax.plot(h[m, 0], h[m, 1], '.', ms=2.2, color=CUT_COLOR, clip_path=clip)
    
    # Dimensions
    y0 = 0.5
    dim_line(ax, off + 0, y0, off + HANDLE_W, y0, f'{HANDLE_W:g}')
    dim_line(ax, off + HANDLE_W + 0.5, y0, off + HANDLE_W + 0.5, y0 + HANDLE_H, f'{HANDLE_H:g}')
    
    # Title
    draw_text(ax, off + HANDLE_W/2, PAGE_H-1, f'Ручка-валик {part_no}/{total_parts}', 
              size=12, weight='bold')
    
    # Assembly instructions
    inst_y = PAGE_H - 8
    ax.text(off + 1, inst_y, '1. ×2 + gusset:', fontsize=9, weight='bold')
    ax.text(off + 1, inst_y - 1.2, '   - Ручки зажать внутри канта', fontsize=8)
    ax.text(off + 1, inst_y - 2.4, '   - Прошить по периметру', fontsize=8)
    
    ax.text(off + 1, inst_y - 3.8, '2. Отверстия:', fontsize=9, weight='bold')
    ax.text(off + 1, inst_y - 4.8, '   - Ø~3.5 мм', fontsize=8)
    ax.text(off + 1, inst_y - 5.8, '   - Шаг 5 мм', fontsize=8)
    
    ax.text(off + 1, inst_y - 7, '3. Сборка:', fontsize=9, weight='bold')
    ax.text(off + 1, inst_y - 8, '   - 2 ручки + gusset', fontsize=8)
    ax.text(off + 1, inst_y - 9, '   - Скрутить в трубку', fontsize=8)
    
    add_registration_marks(ax)
    add_scale_reference(ax)


def create_pdf():
    """Generate complete tote bag pattern PDF."""
    # Calculate page layout
    # Panel: 57 cm wide, split across 2 pages with 4 cm overlap
    panel_parts = [
        (0, 42, 1, 2),    # Page 1: 0-42 cm
        (38, 57, 2, 2)   # Page 2: 38-57 cm (4 cm overlap)
    ]
    
    # Gusset: 99 cm wide, split across 2 pages with 4 cm overlap
    gusset_parts = [
        (0, 42, 1, 2),    # Page 3: 0-42 cm
        (95, 99, 2, 2)   # Page 4: 95-99 cm (4 cm overlap)
    ]
    
    # Handle: 37 cm fits on one page
    handle_parts = [(0, 37, 1, 1)]  # Page 5
    
    # Create PDF
    doc = pymupdf.open()
    
    # Page 1: Panel part 1
    fig, ax = plt.subplots(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    page_panel_half(ax, *panel_parts[0])
    plt.tight_layout(pad=0.5)
    fig.canvas.draw()
    page = doc.new_page(width=PAGE_W*72/2.54, height=PAGE_H*72/2.54)
    img = fig.canvas.tostring_rgb()
    page.insert_image(0, 0, width=PAGE_W*72/2.54, height=PAGE_H*72/2.54, stream=img)
    plt.close(fig)
    
    # Page 2: Panel part 2
    fig, ax = plt.subplots(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    page_panel_half(ax, *panel_parts[1])
    plt.tight_layout(pad=0.5)
    fig.canvas.draw()
    page = doc.new_page(width=PAGE_W*72/2.54, height=PAGE_H*72/2.54)
    img = fig.canvas.tostring_rgb()
    page.insert_image(0, 0, width=PAGE_W*72/2.54, height=PAGE_H*72/2.54, stream=img)
    plt.close(fig)
    
    # Page 3: Gusset part 1
    fig, ax = plt.subplots(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    page_gusset_half(ax, *gusset_parts[0])
    plt.tight_layout(pad=0.5)
    fig.canvas.draw()
    page = doc.new_page(width=PAGE_W*72/2.54, height=PAGE_H*72/2.54)
    img = fig.canvas.tostring_rgb()
    page.insert_image(0, 0, width=PAGE_W*72/2.54, height=PAGE_H*72/2.54, stream=img)
    plt.close(fig)
    
    # Page 4: Gusset part 2
    fig, ax = plt.subplots(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    page_gusset_half(ax, *gusset_parts[1])
    plt.tight_layout(pad=0.5)
    fig.canvas.draw()
    page = doc.new_page(width=PAGE_W*72/2.54, height=PAGE_H*72/2.54)
    img = fig.canvas.tostring_rgb()
    page.insert_image(0, 0, width=PAGE_W*72/2.54, height=PAGE_H*72/2.54, stream=img)
    plt.close(fig)
    
    # Page 5: Handles
    fig, ax = plt.subplots(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    page_handle_half(ax, *handle_parts[0])
    plt.tight_layout(pad=0.5)
    fig.canvas.draw()
    page = doc.new_page(width=PAGE_W*72/2.54, height=PAGE_H*72/2.54)
    img = fig.canvas.tostring_rgb()
    page.insert_image(0, 0, width=PAGE_W*72/2.54, height=PAGE_H*72/2.54, stream=img)
    plt.close(fig)
    
    # Save PDF
    filename = 'tote-bag-pattern-A2.pdf'
    doc.save(filename)
    doc.close()
    print(f'Saved {filename}')
    return filename


if __name__ == '__main__':
    create_pdf()
