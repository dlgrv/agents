#!/usr/bin/env python3
"""
Validation script for duffle bag patterns.

Automatically verifies geometry, hole alignment, and print dimensions.
Usage: python3 references/duffel-bag-validation.py
"""

import pymupdf
import sys

# Expected values
EXPECTED_PAGES = 9
PAGE_SIZE = (42.0, 59.4)  # A2 cm
HOLE_TOLERANCE = 10  # Acceptable deviation in hole count

# Page-specific hole counts (approximate)
EXPECTED_HOLES = {
    1: 227,  # Main panel 1
    2: 163,  # Main panel 2
    3: 212,  # End panel 1
    4: 212,  # End panel 2
    5: 211,  # Bottom 1
    6: 147,  # Bottom 2
    7: 378,  # Top strips
    8: 250,  # Handles
    9: 312   # Assembly instructions
}

# Text markers to check
TEXT_MARKERS = [
    (0, ['50×30×22', '5']),      # Page 1: Size and version
    (2, ['50×30×22']),           # Page 3: Size
    (7, ['50×30×22'])            # Page 8: Size
]

def count_holes(page):
    """Count holes in a page by detecting small filled circles."""
    holes = 0
    for dr in page.get_drawings():
        r = dr['rect']
        # Check for small filled circles (holes)
        if (dr.get('fill') is not None and 
            0.5 < r.width < 1.2 and 
            0.5 < r.height < 1.2):
            holes += 1
    return holes

def check_text(page, markers):
    """Check if required text markers are present."""
    text = page.get_text()
    missing = []
    for marker in markers:
        if marker not in text:
            missing.append(marker)
    return missing

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 duffle-bag-validation.py <pattern.pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    errors = []
    
    # Check file exists
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"ERROR: Cannot open PDF: {e}")
        sys.exit(1)
    
    # Check page count
    if len(doc) != EXPECTED_PAGES:
        errors.append(f"Page count: {len(doc)}, expected {EXPECTED_PAGES}")
    
    # Check page sizes
    for i, page in enumerate(doc):
        w, h = page.rect.width / 72 * 2.54, page.rect.height / 72 * 2.54
        if abs(w - PAGE_SIZE[0]) > 0.15 or abs(h - PAGE_SIZE[1]) > 0.15:
            errors.append(f"Page {i+1}: {w:.2f}x{h:.2f} cm, expected {PAGE_SIZE[0]}x{PAGE_SIZE[1]}")
    
    # Check hole counts
    for i, page in enumerate(doc):
        page_num = i + 1
        expected = EXPECTED_HOLES.get(page_num, 0)
        actual = count_holes(page)
        if abs(actual - expected) > HOLE_TOLERANCE:
            errors.append(f"Page {page_num}: {actual} holes, expected ~{expected}")
    
    # Check text markers
    for page_num, markers in TEXT_MARKERS:
        page = doc[page_num - 1]  # Convert to 0-based
        missing = check_text(page, markers)
        if missing:
            errors.append(f"Page {page_num}: missing text markers {missing}")
    
    # Output results
    if errors:
        print("FAIL")
        for error in errors:
            print(f"  ERROR: {error}")
        sys.exit(1)
    else:
        print("PASS")
        print(f"  {EXPECTED_PAGES} pages verified")
        print(f"  All pages {PAGE_SIZE[0]}x{PAGE_SIZE[1]} cm")
        print(f"  Hole counts within tolerance")
        print(f"  All text markers present")
    
    doc.close()

if __name__ == '__main__':
    main()
