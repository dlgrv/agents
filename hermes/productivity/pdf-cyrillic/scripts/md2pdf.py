#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert Markdown to PDF with Cyrillic support and professional table formatting.

Usage:
python md2pdf.py input.md -o output.pdf
python md2pdf.py input.md --title "My Report" --author "Hermes Agent" -o output.pdf
"""
import argparse
import re
import sys
from pathlib import Path

def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

def main():
    _reconfigure_stdio()
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF with Cyrillic support")
    parser.add_argument("input", help="Input Markdown file path")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file path")
    parser.add_argument("--title", default="", help="PDF title")
    parser.add_argument("--author", default="", help="PDF author")
    args = input()
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable, KeepTogether
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
    except ImportError:
        print("Missing dependency: install with 'python3 -m pip install reportlab'", file=sys.stderr)
        return 2
    
    # Register DejaVu fonts for Cyrillic support
    FDIR = "/usr/share/fonts/truetype/dejavu/"
    try:
        pdfmetrics.registerFont(TTFont("DVS", FDIR + "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DVS-Bold", FDIR + "DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("DVSM", FDIR + "DejaVuSansMono.ttf"))
        registerFontFamily("DVS", normal="DVS", bold="DVS-Bold", italic="DVS", boldItalic="DVS-Bold")
    except Exception as e:
        print(f"Warning: Could not register DejaVu fonts: {e}", file=sys.stderr)
        print("Falling back to default fonts (Cyrillic may not display correctly)", file=sys.stderr)
    
    # Define styles
    PAGE_W, PAGE_H = A4
    MARG = 18 * mm
    AVAIL = PAGE_W - 2 * MARG
    
    styles = {
        "title": ParagraphStyle("t", fontName="DVS-Bold", fontSize=16, leading=20, spaceAfter=8, textColor=colors.HexColor("#111111")),
        "h2": ParagraphStyle("h2", fontName="DVS-Bold", fontSize=12.5, leading=16, spaceBefore=14, spaceAfter=5, textColor=colors.HexColor("#0f3d6e")),
        "h3": ParagraphStyle("h3", fontName="DVS-Bold", fontSize=10.5, leading=14, spaceBefore=9, spaceAfter=3, textColor=colors.HexColor("#333333")),
        "body": ParagraphStyle("b", fontName="DVS", fontSize=8.6, leading=12.2, spaceAfter=3.5, alignment=TA_LEFT),
        "bullet": ParagraphStyle("bl", fontName="DVS", fontSize=8.6, leading=12.2, spaceAfter=2.5, leftIndent=10, bulletIndent=2),
        "cell": ParagraphStyle("c", fontName="DVS", fontSize=7.2, leading=9.2),
        "cellh": ParagraphStyle("ch", fontName="DVS-Bold", fontSize=7.4, leading=9.4, textColor=colors.white)
    }
    
    def fmt(s: str) -> str:
        """Convert markdown to HTML for ReportLab"""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", ">gt;")
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", s)
        s = re.sub(r"`([^`]+)`", r'<font face="DVSM" size="7.6">\1</font>', s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<link href="\2" color="#1a56b0"><u>\1</u></link>', s)
        s = re.sub(r'(?<!href=")(https?://[^)\s<]+)', r'<link href="\1" color="#1a56b0">\1</link>', s)
        s = s.replace("⚠️", "(!) ").replace("⚠", "(!) ")
        return s
    
    def make_table(rows):
        """Create table with auto-wrapping"""
        if not rows:
            return Spacer(1, 0)
        
        ncols = max(len(r) for r in rows)
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        data = []
        for i, r in enumerate(rows):
            st = styles["cellh"] if i == 0 else styles["cell"]
            data.append([Paragraph(fmt(str(c)), st) for c in r])
        
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
    
    def footer(canv, doc):
        canv.saveState()
        canv.setFont("DVS", 7)
        canv.setFillColor(colors.HexColor("#777777"))
        canv.drawString(MARG, 10 * mm, f"{args.title or 'Document'} — страница {doc.page}")
        canv.drawRightString(PAGE_W - MARG, 10 * mm, f"стр. {doc.page}")
        canv.restoreState()
    
    # Read markdown file
    with open(args.input, encoding="utf-8") as f:
        lines = f.read().splitlines()
    
    # Parse markdown and build story
    story = []
    i, first_h1 = 0, True
    in_table = False
    table_rows = []
    
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        
        # Handle tables
        if ln.startswith("|"):
            in_table = True
            table_rows.append([c.strip() for c in ln.strip("|").split("|")])
            i += 1
            continue
        elif in_table:
            # End of table
            if table_rows and not all(re.fullmatch(r":?-{2,}:?", c or "---") for c in table_rows[0]):
                story.append(make_table(table_rows))
                story.append(Spacer(1, 5))
            in_table = False
            table_rows = []
            continue
        
        # Handle headers
        if ln.startswith("### "):
            story.append(Paragraph(fmt(ln[4:]), styles["h3"]))
        elif ln.startswith("## "):
            story.append(Paragraph(fmt(ln[3:]), styles["h2"]))
        elif ln.startswith("# "):
            story.append(Paragraph(fmt(ln[2:]), styles["title"]))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3d6e"), spaceAfter=6))
            first_h1 = False
        elif ln.strip() == "---":
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#bbbbbb"), spaceBefore=6, spaceAfter=6))
        elif ln.lstrip().startswith("- "):
            story.append(Paragraph(fmt(ln.lstrip()[2:]), styles["bullet"], bulletText="•"))
        elif re.match(r"^\d+\.\s", ln):
            m = re.match(r"^(\d+)\.\s+(.*)$", ln)
            story.append(Paragraph(f"<b>{m.group(1)}.</b> " + fmt(m.group(2)), styles["bullet"]))
        else:
            story.append(Paragraph(fmt(ln), styles["body"]))
        i += 1
    
    # Handle table at end of file
    if in_table and table_rows:
        story.append(make_table(table_rows))
    
    # Build PDF
    doc = SimpleDocTemplate(
        args.output,
        pagesize=A4,
        leftMargin=MARG,
        rightMargin=MARG,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=args.title or "",
        author=args.author or "",
        subject="Markdown to PDF conversion"
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    
    print(json.dumps({
        "output": args.output,
        "pages": len(story),
        "title": args.title,
        "author": args.author
    }))
    return 0

if __name__ == "__main__":
    sys.exit(main())