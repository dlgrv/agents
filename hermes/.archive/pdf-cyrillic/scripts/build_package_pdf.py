#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка нескольких MD в один PDF (кириллица, таблицы, код-блоки, ссылки).

Использует DejaVu для кириллицы, обрабатывает код-блоки, таблицы, ссылки, разделители.
Автоматически разбивает длинные строки в код-блоках (в случае переполнения).

Usage:
python build_package_pdf.py

Требует: reportlab
"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, KeepTogether,
                                Preformatted)

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

def make_table(rows, page_width=210*mm, margin=18*mm):
    """Create table with auto-wrapping and professional styling"""
    AVAIL = page_width - 2 * margin
    if not rows:
        return Spacer(1, 0)
    
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    data = []
    for i, r in enumerate(rows):
        st = S["cellh"] if i == 0 else S["cell"]
        data.append([Paragraph(fmt(str(c)), st) for c in r])
    
    if ncols <= 3:
        widths = [AVAIL * 0.30, AVAIL * 0.45, AVAIL * 0.25][:ncols]
    elif ncols == 4:
        widths = [AVAIL * 0.22, AVAIL * 0.30, AVAIL * 0.30, AVAIL * 0.18]
    elif ncols == 5:
        widths = [AVAIL * 0.20, AVAIL * 0.28, AVAIL * 0.26, AVAIL * 0.26][:4] + []  # fallback below
        widths = [AVAIL / ncols] * ncols
    else:
        widths = [AVAIL / ncols] * ncols
    
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3d6e")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9db3c8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]))
    return t

def build_package_pdf(sources, out_path, parts):
    """Build PDF from multiple markdown files with part headers"""
    # Register fonts
    FDIR = "/usr/share/fonts/truetype/dejavu/"
    try:
        pdfmetrics.registerFont(TTFont("DVS", FDIR + "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DVS-Bold", FDIR + "DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("DVS-Italic", FDIR + "DejaVuSerif.ttf"))
        pdfmetrics.registerFont(TTFont("DVSM", FDIR + "DejaVuSansMono.ttf"))
        registerFontFamily("DVS", normal="DVS", bold="DVS-Bold", italic="DVS-Italic", boldItalic="DVS-Bold")
    except Exception as e:
        print(f"Warning: Could not register DejaVu fonts: {e}")
        print("Falling back to default fonts (Cyrillic may not display correctly)")
    
    # Define styles
    PAGE_W, PAGE_H = A4
    MARG = 18 * mm
    AVAIL = PAGE_W - 2 * MARG
    
    global S
    S = dict(
        part=ParagraphStyle("part", fontName="DVS-Bold", fontSize=15, leading=19, spaceBefore=2, spaceAfter=4,
                            textColor=colors.HexColor("#7a1010")),
        title=ParagraphStyle("t", fontName="DVS-Bold", fontSize=13.5, leading=17.5, spaceAfter=6,
                             textColor=colors.HexColor("#111111")),
        h2=ParagraphStyle("h2", fontName="DVS-Bold", fontSize=12, leading=15.5, spaceBefore=13, spaceAfter=5,
                          textColor=colors.HexColor("#0f3d6e")),
        h3=ParagraphStyle("h3", fontName="DVS-Bold", fontSize=10.3, leading=13.5, spaceBefore=9, spaceAfter=3,
                          textColor=colors.HexColor("#333333")),
        body=ParagraphStyle("b", fontName="DVS", fontSize=8.6, leading=12.2, spaceAfter=3.5, alignment=TA_LEFT),
        bullet=ParagraphStyle("bl", fontName="DVS", fontSize=8.6, leading=12.2, spaceAfter=2.5, leftIndent=10, bulletIndent=2),
        cell=ParagraphStyle("c", fontName="DVS", fontSize=7.2, leading=9.2),
        cellh=ParagraphStyle("ch", fontName="DVS-Bold", fontSize=7.4, leading=9.4, textColor=colors.white),
        code=ParagraphStyle("code", fontName="DVSM", fontSize=7.6, leading=10, backColor=colors.HexColor("#f2f4f7"),
                            borderPadding=4, spaceBefore=4, spaceAfter=4),
    )
    
    story = []
    
    # Add part headers
    for part_label, part_color in parts:
        story.append(Paragraph(part_label, S["part"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=part_color, spaceAfter=8))
        
        # Process markdown file
        lines = open(sources[len(parts)-1], encoding="utf-8").read().splitlines()
        i, first_h1 = 0, True
        
        while i < len(lines):
            ln = lines[i].rstrip()
            if not ln.strip():
                i += 1; continue
            
            if ln.lstrip().startswith("```"):
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].lstrip().startswith("```"):
                    code_lines.append(lines[i].rstrip())
                    i += 1
                i += 1
                code_text = "\n".join(code_lines) if code_lines else " "
                story.append(KeepTogether([Preformatted(code_text, S["code"])]))
                continue
            
            if ln.startswith("|"):
                block = []
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-{2,}:?", c or "---") for c in row):
                        block.append(row)
                    i += 1
                story.append(make_table(block)); story.append(Spacer(1, 5)); continue
            
            if ln.startswith("### "):
                story.append(Paragraph(fmt(ln[4:]), S["h3"]))
            elif ln.startswith("## "):
                story.append(Paragraph(fmt(ln[3:]), S["h2"]))
            elif ln.startswith("# "):
                if first_h1:
                    first_h1 = False
                else:
                    story.append(Paragraph(fmt(ln[2:]), S["title"]))
            elif ln.strip() == "---":
                story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#bbbbbb"), spaceBefore=6, spaceAfter=6))
            elif ln.lstrip().startswith("- "):
                story.append(Paragraph(fmt(ln.lstrip()[2:]), S["bullet"], bulletText="•"))
            elif re.match(r"^\d+\.\s", ln):
                m = re.match(r"^(\d+)\.\s+(.*)$", ln)
                story.append(Paragraph(f"<b>{m.group(1)}.</b> " + fmt(m.group(2)), S["bullet"]))
            else:
                story.append(Paragraph(fmt(ln), S["body"]))
            i += 1
        
        if len(parts) > 1 and sources.index(sources[len(parts)-1]) < len(sources) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=MARG,
        rightMargin=MARG,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="VPN для России — исследование + инструкция",
        author="Hermes Agent",
        subject="Максимальная стабильность и незаметность VPN в РФ"
    )
    
    def footer(canv, doc):
        canv.saveState()
        canv.setFont("DVS", 7)
        canv.setFillColor(colors.HexColor("#777777"))
        canv.drawString(MARG, 10 * mm, "VPN для России — исследование + инструкция, 26.09.2026")
        canv.drawRightString(PAGE_W - MARG, 10 * mm, f"стр. {doc.page}")
        canv.restoreState()
    
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out_path

if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        sys.exit(0)
    
    # Example usage
    sources = [
        "/root/vpn_report_2026-09-26.md",
        "/root/vpn_ios_stealth_audit_2026-09-26.md",
        "/root/.hermes/cache/scratch/vpn_research/part3_instruction.md"
    ]
    
    parts = [
        ("ЧАСТЬ I. VPN для России — большое исследование (26.09.2026)", "#7a1010"),
        ("ЧАСТЬ II. Аудит: как не палиться с VPN на iPhone в российских приложениях", "#7a1010"),
        ("ЧАСТЬ III. Точная инструкция по настройке (iPhone + Happ + VPS)", "#7a1010")
    ]
    
    out_path = "/root/vpn_full_package_2026-09-26.pdf"
    
    result = build_package_pdf(sources, out_path, parts)
    print(json.dumps({"output": result, "status": "success"}))
