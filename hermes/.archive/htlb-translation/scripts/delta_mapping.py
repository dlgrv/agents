#!/usr/bin/env python3
"""
Delta mapping script for HTLB upstream sync.

Compares CN chapter headers between local and upstream to detect added/removed/moved units.
Generates alignment map and delta reports.
"""

import os
import re
import subprocess
import json
from pathlib import Path

def get_local_headers(chapter_path):
    """Extract headers from local CN chapter file."""
    with open(chapter_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return re.findall(r'^### (.+)$', content, re.MULTILINE)

def get_upstream_headers(chapter_name):
    """Extract headers from upstream CN chapter via API."""
    url = f"https://raw.githubusercontent.com/eternity4719/HowToLiveBetter/main/book/{chapter_name}.md"
    try:
        response = subprocess.run(['curl', '-s', url], capture_output=True, text=True, check=True)
        headers = re.findall(r'^### (.+)$', response.stdout, re.MULTILINE)
        return headers
    except subprocess.CalledProcessError:
        print(f"Warning: Could not fetch upstream headers for {chapter_name}")
        return []

def generate_delta_diff(local_headers, upstream_headers, chapter_name):
    """Generate diff between local and upstream headers."""
    diff_lines = []
    
    # Create unified diff format
    from difflib import unified_diff
    diff = unified_diff(
        upstream_headers,
        local_headers,
        fromfile=f"upstream/{chapter_name}.md",
        tofile=f"local/{chapter_name}.md",
        lineterm=''
    )
    
    return list(diff)

def map_unit_changes(delta_diff):
    """Parse delta diff to identify unit changes."""
    added = []
    removed = []
    moved = []
    
    for line in delta_diff:
        if line.startswith('+') and line.startswith('### '):
            added.append(line[4:].strip())
        elif line.startswith('-') and line.startswith('### '):
            removed.append(line[4:].strip())
    
    # Simple move detection: same header content in removed and added lists
    for removed_header in removed:
        for added_header in added:
            if removed_header == added_header:
                moved.append((removed_header, added_header))
                break
    
    return {
        'added': added,
        'removed': removed,
        'moved': moved
    }

def generate_alignment_map(all_changes, chapters):
    """Generate final alignment map for all chapters."""
    alignment = {}
    
    for chapter in chapters:
        if chapter in all_changes:
            changes = all_changes[chapter]
            alignment[chapter] = {
                'added': changes['added'],
                'removed': changes['removed'],
                'moved': changes['moved']
            }
        else:
            alignment[chapter] = {
                'added': [],
                'removed': [],
                'moved': []
            }
    
    return alignment

def main():
    # Configuration
    repo_dir = Path('/root/github/HowToLiveBetter')
    book_dir = repo_dir / 'book'
    delta_dir = Path('/tmp/zh_delta')
    alignment_file = Path('/tmp/align_final.json')
    
    # Ensure directories exist
    delta_dir.mkdir(exist_ok=True)
    
    # Get all CN chapter files
    chapter_files = [f for f in book_dir.glob('*.md') if f.name != 'README.md']
    chapters = [f.stem for f in chapter_files]
    
    print(f"Processing {len(chapters)} chapters...")
    
    all_changes = {}
    
    for chapter in chapters:
        print(f"  Processing {chapter}...")
        
        # Get headers
        local_path = book_dir / f"{chapter}.md"
        local_headers = get_local_headers(local_path)
        upstream_headers = get_upstream_headers(chapter)
        
        # Generate delta
        delta_diff = generate_delta_diff(local_headers, upstream_headers, chapter)
        changes = map_unit_changes(delta_diff)
        all_changes[chapter] = changes
        
        # Save individual chapter diff
        diff_file = delta_dir / f"{chapter}.diff"
        with open(diff_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(delta_diff))
        
        print(f"    Added: {len(changes['added'])}, Removed: {len(changes['removed'])}, Moved: {len(changes['moved'])}")
    
    # Generate alignment map
    alignment = generate_alignment_map(all_changes, chapters)
    
    # Save alignment map
    with open(alignment_file, 'w', encoding='utf-8') as f:
        json.dump(alignment, f, ensure_ascii=False, indent=2)
    
    print(f"\nDelta mapping complete!")
    print(f"Diffs saved to: {delta_dir}")
    print(f"Alignment map saved to: {alignment_file}")
    
    # Summary
    total_added = sum(len(changes['added']) for changes in all_changes.values())
    total_removed = sum(len(changes['removed']) for changes in all_changes.values())
    total_moved = sum(len(changes['moved']) for changes in all_changes.values())
    
    print(f"\nSummary:")
    print(f"  Total units added: {total_added}")
    print(f"  Total units removed: {total_removed}")
    print(f"  Total units moved: {total_moved}")
    print(f"  Net change: {total_added - total_removed}")

if __name__ == '__main__':
    main()
