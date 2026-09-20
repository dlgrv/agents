# -*- coding: utf-8 -*-
"""
Pocket sleeve pattern generator for MacBook Pro 16" with user-configurable notch.

Generates two-panel design (back + front with entry notch) with symmetric hole alignment.
Supports shallow (6mm) or deep (10mm) finger notch as user preference.

Key features:
- Unified seam path with holes at both ends
- Symmetric hole distribution (198 holes per panel)
- Configurable notch depth (shallow vs deep)
- 5mm stitch spacing, 4mm from edge
- Visual assembly guide with notch annotation
- A2/A3/A4 output with registration marks
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
import numpy as np
from collections import Counter

OUT = "/root/leather_sleeve/pocket"
os.makedirs(OUT, exist_ok=True)

# Dimensions (cm)
PANEL_W, PANEL_H = 37.5, 26.5  # MacBook Pro 16" pocket size
HOLE_SPACING = 0.5            # 5mm between holes
HOLE_FROM_EDGE = 0.4         # 4mm from edge (user preference)
CORNER_RADIUS = 1.0           # 10mm radius for corners
NOTCH_OPENING = 2.0           # 20mm width of finger notch
NOTCH_DEPTH = 0.6             # 6mm shallow notch (user preference)
NOTCH_CENTER_Y = PANEL_H / 2  # Center notch vertically

# Page sizes (cm)
PAGES = {
    "A4": (29.7, 21.0),
    "A3": (42.0, 29.7),
    "A2": (42.0, 59.4)
}

# Colors
TAN = "#f5f5dc"
BLUE = "#1144cc"
BLACK = "#000000"

def generate_seam_path():
    """Generate the seam path with symmetric hole placement"""
    path = []
    
    # Start from bottom-right corner with offset
    path.append((PANEL_W - HOLE_FROM_EDGE, HOLE_FROM_EDGE))
    
    # Bottom edge (left)
    for x in np.arange(PANEL_W - HOLE_FROM_EDGE - HOLE_SPACING, HOLE_FROM_EDGE, -HOLE_SPACING):
        path.append((x, HOLE_FROM_EDGE))
    
    # Left edge (up)
    for y in np.arange(HOLE_FROM_EDGE + HOLE_SPACING, PANEL_H - HOLE_FROM_EDGE, HOLE_SPACING):
        path.append((HOLE_FROM_EDGE, y))
    
    # Top edge (right)
    for x in np.arange(HOLE_FROM_EDGE + HOLE_SPACING, PANEL_W - HOLE_FROM_EDGE, HOLE_SPACING):
        path.append((x, PANEL_H - HOLE_FROM_EDGE))
    
    # Right edge (down) - stop before notch
    for y in np.arange(PANEL_H - HOLE_FROM_EDGE - HOLE_SPACING, NOTCH_CENTER_Y + NOTCH_DEPTH, -HOLE_SPACING):
        path.append((PANEL_W - HOLE_FROM_EDGE, y))
    
    # Finger notch (shallow arc, downward direction)
    rho = (NOTCH_OPENING**2/4 + NOTCH_DEPTH**2) / (2*NOTCH_DEPTH)
    cx_arc = PANEL_W - HOLE_FROM_EDGE + (rho - NOTCH_DEPTH)
    theta_start = 180 + np.arcsin(NOTCH_DEPTH/rho) * 180/np.pi
    theta_end = 180 - np.arcsin(NOTCH_DEPTH/rho) * 180/np.pi
    
    # Arc from bottom to top (through deepest point)
    for angle in np.linspace(theta_start, theta_end, 20):
        rad = angle * np.pi/180
        x = cx_arc + rho * np.cos(rad)
        y = NOTCH_CENTER_Y + rho * np.sin(rad)
        path.append((x, y))
    
    # Continue down right edge to complete
    for y in np.arange(NOTCH_CENTER_Y - NOTCH_DEPTH, HOLE_FROM_EDGE, -HOLE_SPACING):
        path.append((PANEL_W - HOLE_FROM_EDGE, y))
    
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
                y = p1[ references/pocket-sleeve-pattern.py