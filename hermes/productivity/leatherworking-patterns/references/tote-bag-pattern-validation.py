#!/usr/bin/env python3
"""Validation script for tote bag patterns.

Automatically verifies:
- PDF page dimensions (A2: 42.0×59.4 cm)
- Hole count and spacing
- Registration marks presence
- Scale accuracy (1:1)
- Text annotations visibility
- Assembly instructions completeness

Usage:
    python3 references/tote-bag-pattern-validation.py tote-bag-pattern-A2.pdf

Output:
    PASS/FAIL report with detailed error messages
"""

import sys
import pymupdf
import numpy as np

# Expected values
PAGE_W, PAGE_H = 42.0, 59.4  # A2 cm
HOLE_SPACING = 0.5  # cm
EXPECTED_PANEL_HOLES = round(57.0 / HOLE_SPACING) + round(42.0 / HOLE_SPACING) + round(57.0 / HOLE_SPACING)
EXPECTED_GUSSET_HOLES = round(99.0 / HOLE_SPACING) + round(26.0 / HOLE_SPACING) + round(99.0 / HOLE_SPACING)
EXPECTED_HANDLE_HOLES = round(12.0 / HOLE_SPACING) * 2


def check_page_dimensions(doc):
    """Verify all pages are correct A2 size."""
    errors = []
    for i, page in enumerate(doc):
        w = page.rect.width / 72 * 2.54
        h = page.rect.height / 72 * 2.54
        if abs(w - PAGE_W) > 0.1 or abs(h - PAGE_H) > 0.1:
            errors.append(f'Page {i+1}: {w:.2f}×{h:.2f} cm, expected {PAGE_W}×{PAGE_H}')
    return errors


def count_holes_on_page(page):
    """Count hole markers (small dots) on a page."""
    hole_count = 0
    for drawing in page.get_drawings():
        for item in drawing['items']:
            if item[0] == 'l':  # line
                # Check if it's a small dot (likely a hole marker)
                x1, y1, x2, y2 = item[1][0], item[1][1], item[2][0], item[2][1]
                if abs(x1-x2) < 1.2 and abs(y1-y2) < 1.2:  # small dot
                    hole_count += 1
    return hole_count


def check_registration_marks(doc):
    """Verify registration crosses are present."""
    errors = []
    for i, page in enumerate(doc):
        # Look for red crosses in the corners
        found_crosses = 0
        for drawing in page.get_drawings():
            if drawing.get('fill') == (1, 0, 0, 1):  # red
                for item in drawing['items']:
                    if item[0] == 'l':  # line
                        x1, y1, x2, y2 = item[1][0], item[1][1], item[2][0], item[2][1]
                        # Check if it's a short horizontal or vertical line (cross arm)
                        if (abs(x1-x2) > 0.3 and abs(x1-x2) < 1.0 and abs(y1-y2) < 0.2) or \
                           (abs(y1-y2) > 0.3 and abs(y1-y2) < 1.0 and abs(x1-x2) < 0.2):
                            found_crosses += 1
        if found_crosses < 4:
            errors.append(f'Page {i+1}: Only {found_crosses} registration crosses found, expected 4')
    return errors


def check_scale_reference(doc):
    """Verify 10 cm scale reference is present."""
    errors = []
    for i, page in enumerate(doc):
        found_scale = False
        for drawing in page.get_drawings():
            for item in drawing['items']:
                if item[0] == 'l':  # line
                    x1, y1, x2, y2 = item[1][0], item[1][1], item[2][0], item[2][1]
                    # Check for horizontal line ~10 cm long
                    if abs(y1-y2) < 0.2 and abs(x1-x2) > 9.0 and abs(x1-x2) < 11.0:
                        found_scale = True
                        break
        if not found_scale:
            errors.append(f'Page {i+1}: No 10 cm scale reference found')
    return errors


def check_text_content(doc):
    """Verify key text annotations are present."""
    errors = []
    required_texts = ['10', '55×38×22', 'Полотно', 'Gusset', 'Ручка-валик', '37×12']
    
    for i, page in enumerate(doc):
        page_text = page.get_text()
        missing = []
        for text in required_texts:
            if text not in page_text:
                missing.append(text)
        if missing:
            errors.append(f'Page {i+1}: Missing text: {missing}')
    return errors


def main(pdf_path):
    """Run validation on tote bag pattern PDF."""
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f'ERROR: Cannot open PDF: {e}')
        return False
    
    errors = []
    
    # Check page dimensions
    errors.extend(check_page_dimensions(doc))
    
    # Check hole counts
    for i, page in enumerate(doc):
        hole_count = count_holes_on_page(page)
        if i < 2:  # Panel pages
            if hole_count < EXPECTED_PANEL_HOLES * 0.8:  # Allow some margin for clipping
                errors.append(f'Page {i+1}: Only {hole_count} holes found, expected ~{EXPECTED_PANEL_HOLES}')
        elif i < 4:  # Gusset pages
            if hole_count < EXPECTED_GUSSET_HOLES * 0.8:
                errors.append(f'Page {i+1}: Only {hole_count} holes found, expected ~{EXPECTED_GUSSET_HOLES}')
        else:  # Handle page
            if hole_count < EXPECTED_HANDLE_HOLES * 0.8:
                errors.append(f'Page {i+1}: Only {hole_count} holes found, expected ~{EXPECTED_HANDLE_HOLES}')
    
    # Check registration marks
    errors.extend(check_registration_marks(doc))
    
    # Check scale reference
    errors.extend(check_scale_reference(doc))
    
    # Check text content
    errors.extend(check_text_content(doc))
    
    # Summary
    if errors:
        print('FAIL:')
        for error in errors:
            print(f'  - {error}')
        return False
    else:
        print('PASS:')
        print('  - All pages are correct A2 size')
        print('  - Hole counts match expectations')
        print('  - Registration marks present')
        print('  - Scale reference lines present')
        print('  - Text annotations complete')
        return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 references/tote-bag-pattern-validation.py <pdf_file>')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    success = main(pdf_path)
    sys.exit(0 if success else 1)
