#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка PDF на переполнение код-блоков и вёрстку.

Используется для проверки PDF-сборки перед финальной верификацией.
Проверяет длину строк в код-блоках и наличие ключевых строк.

Usage:
python check_pdf_layout.py input.pdf

Требует: pypdf
"""
import sys
from pathlib import Path
from pypdf import PdfReader

def check_pdf_layout(pdf_path, max_code_chars=108):
    """Check PDF for code block overflow and layout issues."""
    try:
        reader = PdfReader(pdf_path)
        print(f"PDF: {pdf_path}")
        print(f"Pages: {len(reader.pages)}")
        
        # Extract all text
        full_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            full_text += text
            
        # Check for key content
        checks = [
            ("ЧАСТЬ I", "Part I header"),
            ("ЧАСТЬ II", "Part II header"),
            ("ЧАСТЬ III", "Part III header"),
            ("type=xhttp", "XHTTP protocol"),
            ("encryption=none", "Encryption setting"),
            ("2ip.ru", "External service test"),
            ("giszhkh.ru", "External service test"),
            ("allow-domains", "GitHub routing"),
            ("vless://", "VLESS protocol"),
            ("roscomvpn", "Happ profile"),
        ]
        
        print("\nContent verification:")
        for check, desc in checks:
            found = check in full_text
            print(f"  {desc}: {'OK' if found else 'MISSING'}")
        
        # Check for code block overflow
        print("\nCode block check:")
        longest_line = 0
        longest_code = ""
        
        # Check source files for code blocks
        source_files = [
            "/root/vpn_report_2026-09-26.md",
            "/root/vpn_ios_stealth_audit_2026-09-26.md",
            "/root/.hermes/cache/scratch/vpn_research/part3_instruction.md"
        ]
        
        for src in source_files:
            if not Path(src).exists():
                print(f"  Source file not found: {src}")
                continue
                
            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find code blocks
            in_code = False
            for line in content.splitlines():
                if line.strip().startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    if len(line) > longest_line:
                        longest_line = len(line)
                        longest_code = line
        
        print(f"  Longest code line: {longest_line} chars (max: {max_code_chars})")
        if longest_line > max_code_chars:
            print(f"  ❌ OVERFLOW: {longest_code}")
        else:
            print(f"  ✅ OK")
        
        # Check file size
        file_size = Path(pdf_path).stat().st_size
        print(f"\nFile size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        return {
            "pages": len(reader.pages),
            "content_ok": all(check in full_text for check, _ in checks),
            "code_overflow": longest_line > max_code_chars,
            "file_size": file_size
        }
        
    except Exception as e:
        print(f"Error checking PDF: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_pdf_layout.py input.pdf")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    result = check_pdf_layout(pdf_path)
    
    if result:
        status = "PASS" if result["content_ok"] and not result["code_overflow"] else "FAIL"
        print(f"\nOverall status: {status}")
        sys.exit(0 if status == "PASS" else 1)
    else:
        sys.exit(1)