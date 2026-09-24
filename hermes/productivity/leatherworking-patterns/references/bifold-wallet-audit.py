#!/usr/bin/env python3
"""Audit script for bifold wallet patterns with U-seam and slot pockets.

Usage: python3 references/bifold-wallet-audit.py <pattern.pdf>
Performs geometry validation, print checks, and pocket layout analysis.
"""
import math, sys, numpy as np, os
from PIL import Image
from pypdf import PdfReader

def audit_wallet(pdf_path):
    """Audit wallet pattern PDF for critical geometry and layout issues."""
    # Load PDF
    p = PdfReader(pdf_path).pages[0]
    w_cm, h_cm = float(p.mediabox.width)*2.54/72, float(p.mediabox.height)*2.54/72
    print(f"Page size: {w_cm:.2f} x {h_cm:.2f} cm {'✓ A3' if abs(w_cm-42)<0.1 and abs(h_cm-29.7)<0.1 else '✗'}")
    
    # Load PNG (assume exists with same basename)
    png_path = os.path.splitext(pdf_path)[0] + ".png"
    if not os.path.exists(png_path):
        print(f"⚠ PNG preview not found: {png_path}")
        return False
    
    # Pixel analysis for margins
    a = np.array(Image.open(png_path).convert("RGB"))
    Hpx, Wpx = a.shape[:2]; PX = Wpx/w_cm
    r_, g_, b_ = a[:,:,0].astype(int), a[:,:,1].astype(int), a[:,:,2].astype(int)
    ink = (r_<160)|(g_<160)|(b_<160)  # black/blue/red content
    ys, xs = np.where(ink)
    margin_left = xs.min()/PX; margin_right = w_cm - xs.max()/PX
    margin_top = ys.min()/PX; margin_bottom = h_cm - ys.max()/PX
    print(f"Margins: left {margin_left:.2f}, right {margin_right:.2f}, top {margin_top:.2f}, bottom {margin_bottom:.2f} cm")
    safe = all(m >= 0.3 for m in [margin_left, margin_right, margin_top, margin_bottom])
    print(f"Content in safe zones: {'✓' if safe else '✗ (clipping risk)'}")
    
    # TODO: Add hole position validation, seam length checks, pocket slot analysis
    return safe

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 references/bifold-wallet-audit.py <pattern.pdf>")
        sys.exit(1)
    audit_wallet(sys.argv[1])
