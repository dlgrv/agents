#!/usr/bin/env python3
"""
Pilot wave validator for HTLB translation deltas.

Validates pilot chapters (01, 13, 33) after delta mapping and fresh unit preparation.
Checks pipeline integrity before mass translation.
"""

import os
import re
import json
import subprocess
from pathlib import Path

def check_unit_counts(chapter_path, run_dir):
    """Verify unit counts match between CN and translation."""
    # Count CN units
    cn_units_dir = Path(chapter_path) / 'units'
    cn_units = [f for f in cn_units_dir.glob('*.md') if not f.name.endswith('.gloss.md')]
    
    # Count translation units
    trans_units_dir = Path(run_dir) / chapter_path / 'units'
    trans_units = [f for f in trans_units_dir.glob('*.md') if not f.name.endswith('.gloss.md')]
    
    return len(cn_units), len(trans_units)

def check_field_markers(chapter_path, lang):
    """Verify field markers are correct for language."""
    field_labels = {
        'ru': ['Стоимость', 'Простыми словами', 'Эффект', 'Уровень доказательности', 'Примечания'],
        'en': ['Cost', 'In plain terms', 'Benefit', 'Evidence grade', 'Notes'],
        'es': ['Costo', 'En términos sencillos', 'Beneficio', 'Nivel de evidencia', 'Notas']
    }
    
    expected_labels = field_labels.get(lang, [])
    if not expected_labels:
        return False, "Unknown language"
    
    # Check each unit
    units_dir = Path(chapter_path) / 'units'
    for unit_file in units_dir.glob('*.md'):
        if unit_file.name.endswith('.gloss.md'):
            continue
            
        with open(unit_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for legacy labels
        if lang == 'ru' and 'Выгода:' in content:
            return False, f"Legacy label 'Выгода:' found in {unit_file.name}"
        if lang == 'es' and 'Ganancia:' in content:
            return False, f"Legacy label 'Ganancia:' found in {unit_file.name}"
        
        # Check for required labels
        for label in expected_labels:
            if label not in content:
                return False, f"Missing label '{label}' in {unit_file.name}"
    
    return True, "All field markers correct"

def check_assembly(chapter_path, run_dir, lang):
    """Test assembly process for chapter."""
    try:
        if lang == 'es':
            cmd = ['python3', 'tools/assemble_es.py', chapter_path, run_dir, f'book/{lang}/out-{chapter_path}.md']
        else:
            cmd = ['python3', 'tools/assemble.py', run_dir]
        
        result = subprocess.run(cmd, cwd='/root/github/HowToLiveBetter', 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return False, f"Assembly failed: {result.stderr}"
        
        return True, "Assembly successful"
    except subprocess.TimeoutExpired:
        return False, "Assembly timed out"
    except Exception as e:
        return False, f"Assembly error: {str(e)}"

def check_verify(chapter_path, lang):
    """Test verification process for chapter."""
    try:
        output_file = f'book/{lang}/out-{chapter_path}.md'
        cmd = ['python3', 'tools/verify.py', chapter_path, '--lang', lang, '--file', output_file]
        
        result = subprocess.run(cmd, cwd='/root/github/HowToLiveBetter', 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return False, f"Verification failed: {result.stderr}"
        
        return True, "Verification successful"
    except subprocess.TimeoutExpired:
        return False, "Verification timed out"
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def main():
    # Configuration
    repo_dir = Path('/root/github/HowToLiveBetter')
    pilot_chapters = ['01', '13', '33']
    languages = ['ru', 'en', 'es']
    
    print("=== HTLB Pilot Wave Validation ===")
    print(f"Testing chapters: {', '.join(pilot_chapters)}")
    print(f"Languages: {', '.join(languages)}")
    print()
    
    overall_success = True
    
    for chapter in pilot_chapters:
        print(f"\n=== Chapter {chapter} ===")
        
        for lang in languages:
            print(f"  Language: {lang}")
            
            chapter_path = f"{chapter}-Экстренные-случаи" if lang == 'ru' else \
                          f"{chapter}-Do-Not-Die-Early" if lang == 'en' else \
                          f"{chapter}-No-Te-Dejes-Morir-Lentamente"
            
            run_dir = f'/root/htlb-run-{lang}/{chapter}'
            
            # Check unit counts
            cn_count, trans_count = check_unit_counts(f'book/{chapter}', run_dir)
            print(f"    Unit counts - CN: {cn_count}, Translation: {trans_count}")
            
            if cn_count != trans_count:
                print(f"    ❌ Unit count mismatch!")
                overall_success = False
                continue
            
            # Check field markers
            markers_ok, markers_msg = check_field_markers(f'book/{chapter}', lang)
            print(f"    Field markers: {'✅' if markers_ok else '❌'} {markers_msg}")
            
            if not markers_ok:
                overall_success = False
                continue
            
            # Check assembly
            assembly_ok, assembly_msg = check_assembly(chapter, run_dir, lang)
            print(f"    Assembly: {'✅' if assembly_ok else '❌'} {assembly_msg}")
            
            if not assembly_ok:
                overall_success = False
                continue
            
            # Check verification
            verify_ok, verify_msg = check_verify(chapter, lang)
            print(f"    Verification: {'✅' if verify_ok else '❌'} {verify_msg}")
            
            if not verify_ok:
                overall_success = False
                continue
            
            print(f"    ✅ {lang} chapter {chapter} validation complete!")
    
    print("\n=== Final Result ===")
    if overall_success:
        print("✅ All pilot chapters passed validation!")
        print("Ready for mass translation waves.")
    else:
        print("❌ Some pilot chapters failed validation.")
        print("Fix issues before proceeding with mass translation.")
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    exit(main())
