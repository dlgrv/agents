#!/usr/bin/env python3
"""
HTLB Field Value Capitalization Fix Script

This script fixes lowercase starts in field values across all HTLB languages.
It enforces the rule that every field value must start with a capital letter.
"""

import re
import glob
import sys

def fix_capitalization(file_path, lang):
    """Fix lowercase starts in field values for a given language."""
    # Language-specific field labels
    labels = {
        'ru': r'(?:Стоимость|Простыми словами|Эффект|Уровень доказательности|Примечания)',
        'en': r'(?:Cost|In plain terms|Benefit|Evidence grade|Notes)',
        'es': r'(?:Costo|En términos sencillos|Beneficio|Nivel de evidencia|Notas)'
    }
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count fixes
    fixes = 0
    
    # Pattern to find lowercase starts in field values
    pattern = rf'(?m)^- (?:{labels[lang]}): ([^\W\d_])'
    
    # Replace lowercase starts with uppercase
    def replace_match(match):
        nonlocal fixes
        fixes += 1
        field_value = match.group(1)
        return field_value.upper() + field_value[1:]
    
    new_content = re.sub(pattern, replace_match, content)
    
    if fixes > 0:
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {fixes} lowercase starts in {file_path}")
    
    return fixes

def main():
    """Main function to fix capitalization across all HTLB units."""
    if len(sys.argv) < 2:
        print("Usage: python3 capitalization-fix-script.py <language> [chapter]")
        print("Languages: ru, en, es")
        sys.exit(1)
    
    lang = sys.argv[1]
    chapter = sys.argv[2] if len(sys.argv) > 2 else None
    
    if lang not in ['ru', 'en', 'es']:
        print(f"Error: Invalid language '{lang}'. Use: ru, en, es")
        sys.exit(1)
    
    # Find files
    if chapter:
        pattern = f'/root/htlb-run-{lang}/{chapter}/units/*.md'
        files = glob.glob(pattern)
    else:
        pattern = f'/root/htlb-run-{lang}/*/units/*.md'
        files = glob.glob(pattern)
    
    if not files:
        print(f"No files found for language {lang}, chapter {chapter or 'all'}")
        return
    
    total_fixes = 0
    for file_path in files:
        fixes = fix_capitalization(file_path, lang)
        total_fixes += fixes
    
    print(f"Total fixes for {lang}: {total_fixes}")
    
    if total_fixes > 0:
        print("Run verification: python3 tools/wave_pipeline.py <chapters>")
    else:
        print("All field values already start with capital letters")

if __name__ == '__main__':
    main()
