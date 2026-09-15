---
name: pdf-table-wrapping
description: "Fix Reportlab table cell wrapping for professional PDFs"
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pdf, table, reportlab, wrapping, layout]
    category: productivity
    related_skills: [pdf]
---

# PDF Table Wrapping Skill

Fix the Reportlab table cell overflow issue where long text overflows into adjacent columns, making PDF tables unreadable.

## When to Use

- Your PDF table cells contain long descriptions or multi-line text
- Text is overflowing column boundaries and overlapping with adjacent columns
- You need professional-looking tables with automatic word wrapping and proper row heights
- The default raw string rendering in Reportlab tables is causing layout issues

## Problem

By default, Reportlab Table cells render as raw strings with no word wrapping — long text overflows into adjacent columns, making tables unreadable.

## Solution

Always wrap table cell content in Paragraph objects with appropriate leading to enable automatic word wrapping and height adjustment.

## Implementation Pattern

```python
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

styles = getSampleStyleSheet()

def make_table(data, widths):
    # Wrap every cell in a Paragraph for word wrapping and auto height
    wrapped = []
    for r, row in enumerate(data):
        row_paragraphs = []
        for c, cell in enumerate(row):
            # Use appropriate style for header vs data
            style = styles["Heading1"] if r == 0 else styles["BodyText"]
            row_paragraphs.append(Paragraph(str(cell), style))
        wrapped.append(row_paragraphs)
    
    t = Table(wrapped, colWidths=widths, hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('LEADING', (0,0), (-1,-1), 11.5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('LINEBELOW', (0,0), (-1,0), 0.9, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t
```

## Key Points

- Each cell becomes a Paragraph object, not a raw string
- Paragraphs automatically wrap text to column width and adjust row height
- Set appropriate `leading` (line spacing) for readability
- Header rows use bold styles, data rows use normal styles
- Column widths must be set explicitly (in points or mm)

## When to Apply

Use this pattern whenever creating tables with Reportlab, especially:
- Tables with long text descriptions in cells
- Multi-column layouts where text must not overflow
- Tables with variable row heights based on content length
- Professional documents where layout precision matters

## Testing

After implementing, verify:
1. No text overflows column boundaries
2. Row heights adjust automatically for wrapped content
3. Table remains readable at different zoom levels
4. Exported PDF text can be selected normally (not broken into fragments)

## Common Pitfalls

- **Forgetting to wrap cells**: Always convert raw strings to Paragraphs
- **Wrong leading value**: Too low causes text to clip, too high wastes space
- **Ignoring header styles**: Headers should be bold for visual distinction
- **Not setting column widths**: Tables may render with unexpected widths

## Integration

This skill complements the main `pdf` skill. Use it when:
- You encounter text overflow in PDF tables
- You need to create professional-looking technical documentation
- You're working with complex multi-column layouts
- The built-in `pdf_create.py` script needs customization for table handling
