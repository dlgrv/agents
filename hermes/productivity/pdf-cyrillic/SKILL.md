---
name: pdf-cyrillic
description: "PDF generation with Russian text and table wrapping"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pdf, cyrillic, russian, table, reportlab, wrapping]
    category: productivity
    related_skills: [pdf]
---

# PDF Cyrillic Support Skill

Generate PDFs with proper Russian/Cyrillic text rendering and professional tables with automatic word wrapping. Fixes the default Helvetica font limitation that causes square characters (□) or replacement symbols (�).

## When to Use

- Creating PDFs with Russian text
- Building reports with Cyrillic content
- Generating tables with long Russian text descriptions
- Professional documents requiring proper Cyrillic typography
- PDFs that will be viewed on systems with default fonts

## Prerequisites

```bash
python -m pip install reportlab
```

## Font Registration

Always register DejaVu fonts before using Cyrillic text:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Linux (DejaVu)
pdfmetrics.registerFont(TTFont("DVS", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVS-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVSM", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
registerFontFamily("DVS", normal="DVS", bold="DVS-Bold", italic="DVS", boldItalic="DVS-Bold")

# macOS (Arial Unicode MS)
pdfmetrics.registerFont(TTFont("ArialUnicodeMS", "/System/Library/Fonts/Arial Unicode.ttf"))

# Windows (Arial)
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
```

## Cyrillic Styles

```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

cyrillic_styles = {
    "title": ParagraphStyle(
        name="CyrillicTitle",
        fontName="DVS",
        fontSize=16,
        leading=20,
        spaceAfter=8,
        textColor="#111111"
    ),
    "header": ParagraphStyle(
        name="CyrillicHeader",
        fontName="DVS-Bold",
        fontSize=12.5,
        leading=16,
        spaceBefore=14,
        spaceAfter=5,
        textColor="#0f3d6e"
    ),
    "body": ParagraphStyle(
        name="CyrillicBody",
        fontName="DVS",
        fontSize=8.6,
        leading=12.2,
        spaceAfter=3.5,
        alignment=TA_LEFT
    ),
    "bullet": ParagraphStyle(
        name="CyrillicBullet",
        fontName="DVS",
        fontSize=8.6,
        leading=12.2,
        spaceAfter=2.5,
        leftIndent=10,
        bulletIndent=2
    )
}
```

## Table with Auto-Wrapping

```python
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.units import mm
import re

def fmt(s: str) -> str:
    """Convert markdown to HTML for ReportLab"""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(>", ">gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r'<font face="DVSM" size="7.6">\1</font>', s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<link href="\2" color="#1a56b0"><u>\1</u></link>', s)
    s = s.replace("⚠️", "(!) ").replace("⚠", "(!) ")
    return s

def make_cyrillic_table(rows, page_width=180*mm, margin=18*mm):
    """Create table with Cyrillic support and auto-wrapping"""
    AVAIL = page_width - 2 * margin
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    data = []
    for i, r in enumerate(rows):
        st = cyrillic_styles["header"] if i == 0 else cyrillic_styles["body"]
        data.append([Paragraph(fmt(c), st) for c in r])
    
    # Set column widths
    if ncols <= 3:
        widths = [AVAIL * 0.30, AVAIL * 0.45, AVAIL * 0.25][:ncols]
    elif ncols == 4:
        widths = [AVAIL * 0.22, AVAIL * 0.30, AVAIL * 0.30, AVAIL * 0.18]
    else:
        widths = [AVAIL / ncols] * ncols
    
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3d6e")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9db3c8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]))
    return t
```

## Complete Example

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER

def create_cyrillic_pdf(output_path):
    # Register fonts
    pdfmetrics.registerFont(TTFont("DVS", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DVS-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    registerFontFamily("DVS", normal="DVS", bold="DVS-Bold")
    
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                          title="Отчёт по VPN",
                          author="Hermes Agent")
    
    story = []
    
    # Title
    story.append(Paragraph("VPN для России — исследование 26.09.2026", cyrillic_styles["title"]))
    story.append(HRFlowable(width="100%", thickness=1, color="#0f3d6e", spaceAfter=6))
    
    # Header
    story.append(Paragraph("1. Обзор блокировок", cyrillic_styles["header"]))
    story.append(Paragraph("ТСПУ продолжает блокировать VPN-сервисы волнами. Последняя волна затронула 90% популярных сервисов.", cyrillic_styles["body"]))
    story.append(Spacer(1, 6))
    
    # Table
    table_data = [
        ["Сервис", "Статус", "Цена", "Страна"],
        ["VPN Red Shield", "Работает", "$10", "США"],
        ["Durev VPN", "Работает", "$5.99", "Кыргызстан"],
        ["VPN Liberty", "Частично", "$6", "VLESS/SS"],
        ["BlancVPN", "Частично", "$10", "Эстония"]
    ]
    story.append(make_cyrillic_table(table_data))
    story.append(Spacer(1, 10))
    
    # Bullet list
    story.append(Paragraph("Рекомендации:", cyrillic_styles["header"]))
    recommendations = [
        "Использовать AmneziaWG с низким портом (≤9999)",
        "Ротировать IP каждые 2-3 недели",
        "Иметь запасной VPN на случай блокировок"
    ]
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", cyrillic_styles["bullet"]))
    
    doc.build(story)
    return output_path
```

## Common Pitfalls

- **Missing font files**: Install DejaVu fonts (`sudo apt install fonts-dejavu` on Ubuntu)
- **Wrong font path**: Adjust path to match your system (DejaVu, Arial Unicode MS, Arial)
- **Text overflow**: Use Paragraph objects instead of raw strings for automatic wrapping
- **Markdown parsing**: Handle `&`, `<`, `>` escaping in HTML conversion
- **Table borders**: Set explicit TableStyle for professional appearance
- **Leading values**: Too low causes text clipping, too high wastes space

## Verification

After generating PDF:
1. Check that Cyrillic characters display correctly (no squares or ?)
2. Verify table text doesn't overflow column boundaries
3. Confirm page margins are respected (text doesn't touch edges)
4. Test PDF on different viewers (Adobe Reader, Chrome, Firefox)

## Integration

Use this skill with the main `pdf` skill when:
- You need Cyrillic text support
- Creating professional reports with Russian content
- Building tables with long Russian descriptions
- Ensuring PDF compatibility across different systems