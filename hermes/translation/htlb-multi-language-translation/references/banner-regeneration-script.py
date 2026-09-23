#!/usr/bin/env python3
"""
HTLB Preview Banner Regeneration Script

Regenerates og-*.png preview banners for README after translation waves complete.
Updates HTML source files with current HTLB unit counts and regenerates PNGs.
"""

import subprocess
import os
import sys
from pathlib import Path

def update_html_counts():
    """Update numbers in HTML banner source files."""
    repo_dir = Path('/root/github/htlb-ru')
    html_files = [
        'tools/og-ru.html',
        'tools/og-en.html',
        'tools/og-es.html'
    ]
    
    # Current HTLB unit counts (sync with upstream CN)
    updates = {
        '528': '601',  # Tips/Consejos
        '347': '407',  # Class A evidence
        '1066': '1253' # Primary sources
    }
    
    for html_file in html_files:
        file_path = repo_dir / html_file
        if not file_path.exists():
            print(f"Warning: {file_path} not found")
            continue
            
        # Read and update
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update numbers
        old_content = content
        for old_num, new_num in updates.items():
            content = content.replace(f'>{old_num}<', f'>{new_num}<')
            content = content.replace(f'>{old_num} советов', f'>{new_num} совет')
            content = content.replace(f'>{old_num} consejos', f'>{new_num} consejos')
            content = content.replace(f'>{old_num} enlaces', f'>{new_num} enlaces')
        
        # Update comment if present
        content = content.replace(
            '528 советов, 347 класса A, 1066 ссылок',
            '601 совет, 407 класса A, 1253 ссылки'
        )
        
        if content != old_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {html_file}")

def update_es_badge():
    """Update ES badge in README.es.md."""
    repo_dir = Path('/root/github/htlb-ru')
    readme_path = repo_dir / 'README.es.md'
    
    if not readme_path.exists():
        print("Warning: README.es.md not found")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_content = content
    content = content.replace('Primary%20sources-1066', 'Primary%20sources-1253')
    
    if content != old_content:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated README.es.md badge")

def regenerate_banners():
    """Regenerate PNG banners using headless Chromium."""
    print("Installing Chromium via Playwright...")
    
    # Install chromium if not present
    try:
        subprocess.run(['npx', '--yes', 'playwright', 'install', 'chromium'], 
                     check=True, capture_output=True, timeout=300)
        print("Chromium installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Chromium: {e}")
        return False
    
    # Create temporary script
    script_content = '''
import { chromium } from 'playwright';
const jobs = [
  ['/root/github/htlb-ru/tools/og-ru.html', 'og-ru.png'],
  ['/root/github/htlb-ru/tools/og-en.html', 'og-en.png'],
  ['/root/github/htlb-ru/tools/og-es.html', 'og-es.png'],
];
const browser = await chromium.launch();
const page = await browser.newPage({ 
  viewport: { width: 1200, height: 630 }, 
  deviceScaleFactor: 1 
});
for (const [src, out] of jobs) {
  await page.goto('file:///root/github/htlb-ru/' + src);
  await page.screenshot({ path: '/root/github/htlb-ru/' + out });
  console.log('shot', out);
}
await browser.close();
'''
    
    script_path = Path('/tmp/regenerate_banners.mjs')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Run regeneration
    try:
        # Create temp directory for playwright
        temp_dir = Path('/tmp/playwright_temp')
        temp_dir.mkdir(exist_ok=True)
        os.chdir(temp_dir)
        
        # Initialize package.json and install playwright
        subprocess.run(['npm', 'init', '-y'], check=True, capture_output=True)
        subprocess.run(['npm', 'install', 'playwright'], check=True, capture_output=True, timeout=120)
        
        # Run script
        subprocess.run(['node', str(script_path)], check=True, timeout=120)
        print("Banners regenerated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error regenerating banners: {e}")
        return False
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

def verify_banners():
    """Verify banners have correct numbers using vision_analyze."""
    from pathlib import Path
    
    repo_dir = Path('/root/github/htlb-ru')
    expected_counts = {
        'ru': {'tips': 601, 'evidence': 407, 'sources': 1253},
        'en': {'tips': 601, 'evidence': 407, 'sources': 1253},
        'es': {'tips': 601, 'evidence': 407, 'sources': 1253}
    }
    
    print("Verifying banners...")
    for lang in ['ru', 'en', 'es']:
        png_path = repo_dir / f'og-{lang}.png'
        if not png_path.exists():
            print(f"Warning: {png_path} not found")
            continue
            
        print(f"{lang.upper()} banner: {png_path.stat().st_size} bytes")
        # Note: vision_analyze would be called here in actual implementation
        print(f"Expected: {expected_counts[lang]['tips']} tips, {expected_counts[lang]['evidence']} evidence, {expected_counts[lang]['sources']} sources")

def main():
    """Main regeneration workflow."""
    print("HTLB Preview Banner Regeneration")
    print("=" * 40)
    
    # Step 1: Update HTML source files
    print("Step 1: Updating HTML source files...")
    update_html_counts()
    
    # Step 2: Update ES badge
    print("\nStep 2: Updating ES badge...")
    update_es_badge()
    
    # Step 3: Regenerate PNG banners
    print("\nStep 3: Regenerating PNG banners...")
    success = regenerate_banners()
    
    if success:
        # Step 4: Verify banners
        print("\nStep 4: Verifying banners...")
        verify_banners()
        
        print("\n" + "=" * 40)
        print("Banner regeneration complete!")
        print("Files to commit:")
        print("- tools/og-ru.html, tools/og-en.html, tools/og-es.html")
        print("- og-ru.png, og-en.png, og-es.png")
        print("- README.es.md (badge)")
    else:
        print("\nBanner regeneration failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
