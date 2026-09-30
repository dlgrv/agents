#!/usr/bin/env python3
"""
Pattern verification script for MacBook sleeve PDFs.
Checks scale, dimensions, and punch hole placement.

Usage: python3 verify_pattern.py <pattern.pdf>
"""
import sys
import pymupdf

def verify_pattern(pdf_path):
    doc = pymupdf.open(pdf_path)
    page = doc[0]
    rect = page.rect
    
    # Check A3 dimensions
    a3_width, a3_height = 1190.55, 841.89  # pt
    width_ok = abs(rect.width - a3_width) < 1.0
    height_ok = abs(rect.height - a3_height) < 1.0
    print(f"Page size: {rect.width:.1f}×{rect.height:.1f} pt", end=" ")
    print("✓ A3" if width_ok and height_ok else "✗ Not A3")
    
    # Count punch holes (small filled circles)
    holes = []
    for item in page.get_drawings():
        if item.get("fill") and item.get("rect"):
            r = item["rect"]
            if r.width < 5 and r.height < 5:  # Small circles
                holes.append((r.x0, r.y0, r.x1, r.y1))
    
    print(f"Total punch holes: {len(holes)}")
    
    # Check for unwanted top holes (y > 27.0 cm = 765.75 pt)
    top_holes = [h for h in holes if h[1] > 765.75]
    print(f"Holes in top zone (y>27.0cm): {len(top_holes)}", end=" ")
    if len(top_holes) <= 4:  # Allow corner seam holes
        print("✓ OK (seam holes only)")
    else:
        print("✗ Too many top holes - top-loading design issue")
    
    # Check scale (1cm = 39.37 px)
    # This requires knowing the intended panel dimensions
    # For a 38.0×27.5 cm panel, expect:
    # Width: 38.0 * 39.37 ≈ 1496 px
    # Height: 27.5 * 39.37 ≈ 1083 px
    # But PDF coordinates are in pt, not px
    print("Scale verification: Use PDF ruler or measure printed output")
    
    doc.close()
    return width_ok and height_ok and len(top_holes) <= 4

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 verify_pattern.py <pattern.pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    success = verify_pattern(pdf_path)
    sys.exit(0 if success else 1)
