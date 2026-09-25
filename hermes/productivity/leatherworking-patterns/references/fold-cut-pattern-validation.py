#!/usr/bin/env python3
"""Validation script for fold/cut leather wallet patterns (no-sew designs).

Usage:
    python3 references/fold-cut-pattern-validation.py pattern.pdf

Validates:
- Single-piece layout (no separate panels)
- Fold lines and gouge lines
- Button/rivet hole placement
- Overall dimensions
"""
import sys
import fitz  # pymupdf
from pathlib import Path

def analyze_fold_cut_pattern(pdf_path):
    """Analyze a PDF pattern for fold/cut wallet characteristics."""
    doc = fitz.open(pdf_path)
    page = doc[0]  # Most patterns are single-page
    
    # Get page dimensions
    page_rect = page.rect
    width = page_rect.width
    height = page_rect.height
    
    # Extract text content
    text = page.get_text()
    
    # Extract drawings (contours, lines, holes)
    drawings = page.get_drawings()
    
    # Analyze fold lines (typically dashed or dotted)
    fold_lines = []
    gouge_lines = []
    button_holes = []
    
    for drawing in drawings:
        # Analyze path type
        path = drawing["path"]
        items = path.items()
        
        # Check for fold indicators (dashed lines, specific keywords)
        if "fold" in text.lower() or "crease" in text.lower():
            fold_lines.append(drawing)
        
        # Check for gouge lines (diagonal lines on back)
        if "gouge" in text.lower() or "score" in text.lower():
            gouge_lines.append(drawing)
        
        # Check for button holes (small circles/ellipses)
        if drawing["type"] == "ellipse" or drawing["type"] == "circle":
            if drawing["rect"].width < 10:  # Small holes
                button_holes.append(drawing)
    
    # Check for single-piece layout
    # Look for continuous outline without separate panels
    outlines = [d for d in drawings if d["type"] in ["rect", "polygon"]]
    
    results = {
        "page_size": (width, height),
        "fold_lines_found": len(fold_lines),
        "gouge_lines_found": len(gouge_lines),
        "button_holes_found": len(button_holes),
        "outlines_count": len(outlines),
        "has_single_piece": len(outlines) <= 2,  # Main outline + maybe fold lines
        "text_indicators": {
            "fold_keywords": [kw for kw in ["fold", "crease", "bend"] if kw in text.lower()],
            "gouge_keywords": [kw for kw in ["gouge", "score", "cut line"] if kw in text.lower()],
            "button_keywords": [kw for kw in ["snap", "rivet", "button", "hole"] if kw in text.lower()]
        }
    }
    
    return results

def validate_pattern(results):
    """Validate if pattern matches fold/cut criteria."""
    validation = {
        "is_fold_cut": True,
        "issues": [],
        "recommendations": []
    }
    
    # Check for single piece
    if not results["has_single_piece"]:
        validation["issues"].append("Multiple panels detected - may be sewn pattern")
        validation["is_fold_cut"] = False
    
    # Check for fold lines
    if results["fold_lines_found"] == 0 and not results["text_indicators"]["fold_keywords"]:
        validation["issues"].append("No fold lines detected")
        validation["recommendations"].append("Look for dashed lines or fold indicators")
    
    # Check for gouge lines
    if results["gouge_lines_found"] == 0 and not results["text_indicators"]["gouge_keywords"]:
        validation["issues"].append("No gouge lines detected")
        validation["recommendations"].append("Look for diagonal scoring lines on back")
    
    # Check for button holes
    if results["button_holes_found"] == 0 and not results["text_indicators"]["button_keywords"]:
        validation["issues"].append("No button/rivet holes detected")
        validation["recommendations"].append("Look for snap or rivet placement indicators")
    
    return validation

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 references/fold-cut-pattern-validation.py pattern.pdf")
        return 1
    
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    try:
        results = analyze_fold_cut_pattern(pdf_path)
        validation = validate_pattern(results)
        
        print(f"Pattern Analysis for: {pdf_path}")
        print(f"Page size: {results['page_size'][0]:.1f} x {results['page_size'][1]:.1f} units")
        print(f"Fold lines: {results['fold_lines_found']}")
        print(f"Gouge lines: {results['gouge_lines_found']}")
        print(f"Button holes: {results['button_holes_found']}")
        print(f"Single piece: {'Yes' if results['has_single_piece'] else 'No'}")
        
        print("\nText Indicators:")
        for category, keywords in results["text_indicators"].items():
            if keywords:
                print(f"  {category}: {', '.join(keywords)}")
        
        print("\nValidation:")
        print(f"Is fold/cut pattern: {'Yes' if validation['is_fold_cut'] else 'No'}")
        
        if validation["issues"]:
            print("\nIssues:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
        
        if validation["recommendations"]:
            print("\nRecommendations:")
            for rec in validation["recommendations"]:
                print(f"  - {rec}")
        
        return 0 if validation["is_fold_cut"] else 1
        
    except Exception as e:
        print(f"Error analyzing pattern: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
