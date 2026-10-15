#!/usr/bin/env python3
"""
Duffle bag pattern generator for leatherworking.

Generates PDF patterns for travel duffle bags with zipper closure.
Designed for capacity: 2 pairs of shoes + clothing.

Usage:
    python3 references/duffel-bag-pattern.py

Output:
    lechalo_dorozhnaya_sumka_50x30x22_molnia_A2.pdf (9 pages)

Design:
    - Size: 50×30×22 cm (W×H×D)
    - Zipper closure along full top edge
    - Two main panels (front/back) with gusset side panels
    - Gusset: 22×30 cm (side×height), cut ×2
    - Bottom: 50×24 cm (width×depth)
    - Top strips: 50×13 cm (width×height), ×2 for zipper
    - Handles: 30×12 cm strips, rolled to Ø~3.5 cm
    - Seam allowance: 1 cm
    - Stitch holes: 5mm spacing from edges
    - Registration marks: red crosses for page alignment
    - Page format: A2 (42.0×59.4 cm)

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
PANEL_W, PANEL_H = 52.0, 32.0  # cm (50×30 + seam allowance)
P_END_W, P_END_H = 24.0, 32.0  # cm (22×30 + seam allowance)
P_BOT_W, P_BOT_H = 52.0, 24.0  # cm (50×22 + seam allowance)
P_TOP_W, P_TOP_H = 52.0, 13.0  # cm (50×11 + seam allowance)
P_HANDLE_W, P_HANDLE_H = 30.0, 12.0  # cm (rolled handle)
SEAM_ALLOWANCE = 1.0  # cm
HOLE_SPACING = 0.5  # cm
PAGE_W, PAGE_H = 42.0, 59.4  # A2 cm

# Colors
CUT_COLOR = 'black'
FOLD_COLOR = 'green'
ZONE_COLOR = 'blue'
REG_COLOR = 'red'
TEXT_COLOR = 'black'


def panel_path():
    """Main panel outline (rectangle)."""
    return np.array([
        [0, 0],
        [PANEL_W, 0],
        [PANEL_W, PANEL_H],
        [0, PANEL_H],
        [0, 0]
    ])


def end_path():
    """End panel outline (rectangle)."""
    return np.array([
        [0, 0],
        [P_END_W, 0],
        [P_END_W, P_END_H],
        [0, P_END_H],
        [0, 0]
    ])


def bottom_path():
    """Bottom panel outline (rectangle)."""
    return np.array([
        [0, 0],
        [P_BOT_W, 0],
        [P_BOT_W, P_BOT_H],
        [0, P_BOT_H],
        [0, 0]
    ])


def top_path():
    """Top strip outline (rectangle)."""
    return np.array([
        [0, 0],
        [P_TOP_W, 0],
        [P_TOP_W, P_TOP_H],
        [0, P_TOP_H],
        [0, 0]
    ])


def handle_path():
    """Handle strip for rolled handles."""
    return np.array([
        [0, 0],
        [P_HANDLE_W, 0],
        [P_HANDLE_W, P_HANDLE_H],
        [0, P_HANDLE_H],
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


def end_holes():
    """Stitch holes along end panel edges (left, bottom, right). Top edge is open."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, P_END_H, HOLE_SPACING):
        holes.append([0, y])
    # Bottom edge (left to right)
    for x in np.arange(0, P_END_W, HOLE_SPACING):
        holes.append([x, 0])
    # Right edge (bottom to top)
    for y in np.arange(0, P_END_H, HOLE_SPACING):
        holes.append([P_END_W, y])
    return np.array(holes)


def bottom_holes():
    """Stitch holes along bottom panel edges (left, bottom, right)."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, P_BOT_H, HOLE_SPACING):
        holes.append([0, y])
    # Bottom edge (left to right)
    for x in np.arange(0, P_BOT_W, HOLE_SPACING):
        holes.append([x, 0])
    # Right edge (bottom to top)
    for y in np.arange(0, P_BOT_H, HOLE_SPACING):
        holes.append([P_BOT_W, y])
    return np.array(holes)


def top_holes():
    """Stitch holes along top strip edges (left, right)."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, P_TOP_H, HOLE_SPACING):
        holes.append([0, y])
    # Right edge (top to bottom)
    for y in np.arange(0, P_TOP_H, HOLE_SPACING):
        holes.append([P_TOP_W, y])
    return np.array(holes)


def handle_holes():
    """Handle holes: short edges only (rolled handles)."""
    holes = []
    # Left edge (top to bottom)
    for y in np.arange(0, P_HANDLE_H, HOLE_SPACING):
        holes.append([0, y])
    # Right edge (top to bottom)
    for y in np.arange(0, P_HANDLE_H, HOLE_SPACING):
        holes.append([P_HANDLE_W, y])
    return np.array(holes)


def draw_text(ax, x, y, text, size=10, weight='normal'):
    """Draw text with consistent styling."""
    ax.text(x, y, text, fontsize=size, weight=weight, color=TEXT_COLOR,
            ha='center', va='bottom', transform=ax.transData)


def dim_line(ax, x1, y1, x2, y2, text):
    """Draw dimension line with label."""
    if abs(x1 - x2) > abs(y1 - y2):  # Horizontal
        ax.plot([x1, x2], [y1, y1], 'k-', lw=0.5)
        ax.plot([x1, x1], [y1-0.1, y1+0.0], 'k-', lw=0.5)
        ax.plot([x2, x2], [y1-0.1, y1+0.0], 'k-', lw=0.5)
        ax.text((x1+x2)/2, y1-0.3, text, fontsize=8, ha='center', va='top')
    else:  # Vertical
        ax.plot([x1, x1], [y1, y2], 'k-', lw=0.5)
        ax.plot([x1-0.1, x1+0.0], [y1, y1], 'k-', lw=0.5)
        ax.plot([x1-0.1, x1+0.0], [y2, y2], 'k-', lw=0.5)
        ax.text(x1-0.3, (y1+y2)/2, text, fontsize=8, ha='right', va='center')


def reg_crosses(ax):
    """Add red registration crosses at page corners."""
    for x, y in [(2, 2), (PAGE_W-2, 2), (PAGE_W-2, PAGE_H-2), (2, PAGE_H-2)]:
        ax.plot([x-0.5, x+0.5], [y, y], color=REG_COLOR, lw=1.5)
        ax.plot([x, x], [y-0.5, y+0.5], color=REG_COLOR, lw=1.5)


def scale_bar(ax, length, y_pos):
    """Add scale bar of given length at y position."""
    ax.plot([6, 6 + length], [y_pos, y_pos], 'k-', lw=1.5)
    ax.plot([6, 6], [y_pos-0.2, y_pos+0.2], 'k-', lw=1.5)
    ax.plot([6 + length, 6 + length], [y_pos-0.2, y_pos+0.2], 'k-', lw=1.5)
    ax.text(6 + length/2, y_pos-0.5, f'{length} см', fontsize=9, ha='center', va='top')


def title(ax, text):
    """Add centered title at top of page."""
    ax.text(PAGE_W / 2, PAGE_H - 2, text, ha='center', va='bottom',
            fontsize=11, weight='bold', color=TEXT_COLOR)


def new_page():
    """Create new figure with A2 size and setup."""
    fig = plt.figure(figsize=(PAGE_W/2.54, PAGE_H/2.54), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def page_piece_split(make_ax, w, h, x_splits, name, croit=None):
    """Split wide piece across pages with overlap."""
    figs = []
    overlap = 4.0  # cm
    for i, (x0, x1) in enumerate(x_splits):
        fig, ax = make_ax()
        piece = np.array([[x0, 0], [x1, 0], [x1, h], [x0, h], [x0, 0]])
        poly = mpatches.Polygon(piece, closed=True, fill=False, ec=CUT_COLOR, lw=1.8)
        ax.add_patch(poly)
        
        # Holes
        holes = []
        for y in np.arange(0, h, HOLE_SPACING):
            holes.append([x0, y])
            holes.append([x1, y])
        for x in np.arange(x0, x1, HOLE_SPACING):
            holes.append([x, 0])
            holes.append([x, h])
        if holes:
            hx, hy = zip(*holes)
            ax.scatter(hx, hy, s=20, c='black', marker='o')
        
        # Dimensions
        dim_line(ax, x0, h + 0.5, x1, h + 0.5, f'{x1-x0:g}')
        dim_line(ax, x1 + 0.5, 0, x1 + 0.5, h, f'{h:g}')
        
        # Title and notes
        title_text = f'{name} {i+1}/{len(x_splits)}'
        if croit:
            title_text += f' ({croit})'
        title(ax, title_text)
        
        # Assembly note
        if len(x_splits) > 1:
            ax.text(PAGE_W/2, 6, f'Сборка: склейка по красным крестам, перекрытие {overlap} см',
                    ha='center', fontsize=9)
        
        reg_crosses(ax)
        scale_bar(ax, 2, PAGE_H - 3)
        figs.append(fig)
    return figs


def page_ends(make_ax):
    """End panels (one per page)."""
    figs = []
    for i, name in enumerate(('Торец ЛЕВЫЙ', 'Торец ПРАВЫЙ')):
        fig, ax = make_ax()
        draw_piece(ax, P_END_W, P_END_H, 6, 8, name,
                   note='22×30, кроить ×2 (лев+прав)')
        dim_line(ax, 6, 7, 6 + P_END_W, 7, f'{P_END_W:g}')
        dim_line(ax, 6 + P_END_W + 0.7, 8, 6 + P_END_W + 0.7, 8 + P_END_H,
                 f'{P_END_H:g}')
        ax.text(PAGE_W / 2, PAGE_H - 6,
                'Торцы: швы по 3 сторонам (верх — в шов с полосами '
                'верха и молнией)', ha='center', fontsize=9)
        reg_crosses(ax)
        scale_bar(ax, 2, PAGE_H - 3)
        title(ax, f'Дорожная сумка 50×30×22 — торцы {i + 1}/2')
        figs.append(fig)
    return figs


def draw_piece(ax, w, h, x, y, name, note=None):
    """Draw single piece with outline and holes."""
    piece = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]])
    poly = mpatches.Polygon(piece, closed=True, fill=False, ec=CUT_COLOR, lw=1.8)
    ax.add_patch(poly)
    
    # Holes
    holes = []
    for dy in np.arange(0, h, HOLE_SPACING):
        holes.append([x, y + dy])
        holes.append([x + w, y + dy])
    for dx in np.arange(0, w, HOLE_SPACING):
        holes.append([x + dx, y])
        holes.append([x + dx, y + h])
    if holes:
        hx, hy = zip(*holes)
        ax.scatter(hx, hy, s=20, c='black', marker='o')
    
    # Label
    draw_text(ax, x + w/2, y + h + 0.5, name, size=10, weight='bold')
    if note:
        draw_text(ax, x + w/2, y + h + 1.8, note, size=8)
    
    # Dimensions
    dim_line(ax, x, y - 0.5, x + w, y - 0.5, f'{w:g}')
    dim_line(ax, x + w + 0.5, y, x + w + 0.5, y + h, f'{h:g}')


def page_tops(make_ax):
    """Top strips for zipper."""
    fig, ax = make_ax()
    draw_piece(ax, P_TOP_W, P_TOP_H, 6, 8, 'Полоса верха 1',
               note='50×13, кроить ×2')
    draw_piece(ax, P_TOP_W, P_TOP_H, 6 + P_TOP_W + 4, 8, 'Полоса верха 2',
               note='50×13, кроить ×2')
    ax.text(PAGE_W / 2, 6, 'Полосы верха: между ними вшивается молния',
            ha='center', fontsize=9)
    reg_crosses(ax)
    scale_bar(ax, 2, PAGE_H - 3)
    title(ax, 'Дорожная сумка 50×30×22 — полосы верха')
    return fig


def page_handles(make_ax):
    """Handle strips with assembly instructions."""
    fig, ax = make_ax()
    draw_piece(ax, P_HANDLE_W, P_HANDLE_H, 6, 8, 'Ручка-валик',
               note='30×12, кроить ×2')
    ax.text(6, 6, '1. ×2 + инструкция:', fontsize=9, weight='bold')
    ax.text(6, 4.8, '   - Ручки зажать внутри канта', fontsize=8)
    ax.text(6, 3.6, '   - Прошить по периметру', fontsize=8)
    ax.text(6, 2.4, '2. Отверстия:', fontsize=9, weight='bold')
    ax.text(6, 1.2, '   - Ø~3.5 мм', fontsize=8)
    ax.text(6, 0, '   - Шаг 5 мм', fontsize=8)
    reg_crosses(ax)
    scale_bar(ax, 2, PAGE_H - 3)
    title(ax, 'Дорожная сумка 50×30×22 — ручки')
    return fig


def main():
    """Generate complete duffle bag pattern PDF."""
    pdf = pymupdf.open()  # Create empty PDF
    
    # Page 1-2: Main panels (front/back)
    for f in page_piece_split(new_page, PANEL_W, PANEL_H,
                              [(0.0, 30.0), (26.0, 52.0)],
                              'Полотно', 'КРОИТЬ ×2'):
        pdf.savefig(f); plt.close(f)
    
    # Page 3-4: End panels
    for f in page_ends(new_page):
        pdf.savefig(f); plt.close(f)
    
    # Page 5-6: Bottom
    for f in page_piece_split(new_page, P_BOT_W, P_BOT_H,
                              [(0.0, 30.0), (26.0, 52.0)],
                              'Дно', 'дно'):
        pdf.savefig(f); plt.close(f)
    
    # Page 7: Top strips
    pdf.savefig(page_tops(new_page)); plt.close('all')
    
    # Page 8: Handles
    pdf.savefig(page_handles(new_page)); plt.close('all')
    
    # Save PDF
    filename = 'lechalo_dorozhnaya_sumka_50x30x22_molnia_A2.pdf'
    pdf.save(filename)
    pdf.close()
    print(f'saved {filename}')
    return filename


if __name__ == '__main__':
    main()
