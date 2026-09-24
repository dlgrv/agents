#!/usr/bin/env python3
"""
Multi-tier wallet pattern validation script
Automated audit for complex wallet patterns with multiple tiers, center seams,
and independent validation of geometry, hole alignment, and usability.
"""

import sys
import subprocess
import json
import re
from pathlib import Path

def run_wallet_generation():
    """Run the wallet pattern generator and capture output"""
    try:
        result = subprocess.run(
            [sys.executable, "make_wallet_v5.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Generation timed out"

def extract_metrics(stdout):
    """Extract key metrics from wallet generation output"""
    metrics = {}
    
    # Extract dimensions
    dim_match = re.search(r'closed ([\d.]+)x([\d.]+)', stdout)
    if dim_match:
        metrics['closed_width'] = float(dim_match.group(1))
        metrics['closed_height'] = float(dim_match.group(2))
    
    # Extract tier information
    tier_matches = re.findall(r'tier([123]): ([\d.]+)x([\d.]+) holes (\d+)/(\d+)', stdout)
    for i, match in enumerate(tier_matches, 1):
        metrics[f'tier{i}_width'] = float(match[1])
        metrics[f'tier{i}_height'] = float(match[2])
        metrics[f'tier{i}_holes'] = int(match[3])
        metrics[f'tier{i}_total_holes'] = int(match[4])
    
    # Extract card and bill fits
    card_match = re.search(r'card: ([\d.]+) >= ([\d.]+)', stdout)
    if card_match:
        metrics['card_width'] = float(card_match.group(1))
        metrics['card_min_width'] = float(card_match.group(2))
    
    bill_match = re.search(r'bills: ([\d.]+) >= ([\d.]+)', stdout)
    if bill_match:
        metrics['bill_width'] = float(bill_match.group(1))
        metrics['bill_min_width'] = float(bill_match.group(2))
    
    # Extract thread usage
    thread_match = re.search(r'thread: ~([\d.]+) cm', stdout)
    if thread_match:
        metrics['thread_cm'] = float(thread_match.group(1))
    
    # Extract layout parameters
    layout_matches = re.findall(r'([A-Z_]+)=([\d.]+)', stdout)
    for match in layout_matches:
        if match[0] in ['PX0', 'PR_X', 'POC_W', 'LIN_W', 'CENTER_OFF', 'K_HALF']:
            metrics[match[0]] = float(match[1])
    
    return metrics

def validate_geometry(metrics):
    """Validate basic geometry constraints"""
    issues = []
    
    # Check card fit
    if 'card_width' in metrics and 'card_min_width' in metrics:
        card_gap = metrics['card_width'] - metrics['card_min_width']
        if card_gap < 0.1:  # Less than 1mm gap
            issues.append(f"CRITICAL: Card too tight by {abs(card_gap):.2f}cm")
        elif card_gap < 0.2:  # Less than 2mm gap
            issues.append(f"MAJOR: Card gap only {card_gap:.2f}cm (recommend >0.2cm)")
    
    # Check bill fit
    if 'bill_width' in metrics and 'bill_min_width' in metrics:
        bill_gap = metrics['bill_width'] - metrics['bill_min_width']
        if bill_gap < 0.1:
            issues.append(f"CRITICAL: Bills too tight by {abs(bill_gap):.2f}cm")
        elif bill_gap < 0.2:
            issues.append(f"MAJOR: Bill gap only {bill_gap:.2f}cm (recommend >0.2cm)")
    
    # Check center seam offset
    if 'CENTER_OFF' in metrics:
        center_off = metrics['CENTER_OFF']
        if center_off < 0.6:  # Too close to fold
            issues.append(f"MAJOR: Center offset {center_off:.2f}cm too close to fold (minimum 0.6cm)")
        
        # Check grid alignment (avoid 5mm grid nodes)
        grid_step = 0.5  # 5mm
        grid_pos = center_off / grid_step
        if abs(grid_pos - round(grid_pos)) < 0.05:  # Within 0.25mm of grid node
            issues.append(f"MAJOR: Center offset aligns with grid node (risk of hole collision)")
    
    # Check page boundaries
    if 'PX0' in metrics and 'PR_X' in metrics and 'POC_W' in metrics:
        right_edge = metrics['PR_X'] + metrics['POC_W']
        page_width = 42.0  # A2 width
        margin = page_width - right_edge
        if margin < 0.3:  # Less than 3mm margin
            issues.append(f"CRITICAL: Right edge extends beyond page by {abs(margin):.2f}cm")
        elif margin < 0.5:  # Less than 5mm margin
            issues.append(f"MAJOR: Right margin only {margin:.2f}cm (recommend >0.5cm)")
    
    return issues

def validate_hole_counts(metrics):
    """Validate hole counts and symmetry"""
    issues = []
    
    # Check each tier has expected holes
    for i in range(1, 4):
        tier_key = f'tier{i}_holes'
        total_key = f'tier{i}_total_holes'
        if tier_key in metrics and total_key in metrics:
            if metrics[tier_key] != metrics[total_key]:
                issues.append(f"WARNING: Tier {i} has {metrics[tier_key]}/{metrics[total_key]} holes")
    
    # Check total holes reasonable (should be around 3.5x seam length)
    if 'thread_cm' in metrics:
        expected_holes = metrics['thread_cm'] / 0.5  # Assuming 5mm pitch
        total_holes = sum(metrics.get(f'tier{i}_holes', 0) for i in range(1, 4))
        if abs(total_holes - expected_holes) > 50:  # Allow some variance
            issues.append(f"WARNING: Hole count {total_holes} vs expected ~{expected_holes:.0f}")
    
    return issues

def run_test_suite():
    """Run the existing test suite"""
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_wallet_v5.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test suite timed out"

def parse_test_results(stdout):
    """Parse test suite output for failures"""
    lines = stdout.split('\n')
    passed = 0
    failed = []
    
    for line in lines:
        if 'passed' in line:
            passed_match = re.search(r'(\d+)/\d+ passed', line)
            if passed_match:
                passed = int(passed_match.group(1))
        elif '✗' in line:
            failed.append(line.strip())
    
    return passed, failed

def main():
    """Main audit workflow"""
    print("=== Multi-Tier Wallet Pattern Audit ===")
    
    # Step 1: Generate pattern
    print("\n1. Generating pattern...")
    gen_success, gen_stdout, gen_stderr = run_wallet_generation()
    if not gen_success:
        print(f"Generation failed: {gen_stderr}")
        return 1
    
    # Step 2: Extract metrics
    print("\n2. Extracting metrics...")
    metrics = extract_metrics(gen_stdout)
    if not metrics:
        print("No metrics extracted")
        return 1
    
    print(f"Pattern dimensions: {metrics.get('closed_width', 'N/A')}x{metrics.get('closed_height', 'N/A')} cm")
    print(f"Card fit: {metrics.get('card_width', 'N/A')} >= {metrics.get('card_min_width', 'N/A')} cm")
    print(f"Bill fit: {metrics.get('bill_width', 'N/A')} >= {metrics.get('bill_min_width', 'N/A')} cm")
    
    # Step 3: Validate geometry
    print("\n3. Validating geometry...")
    geometry_issues = validate_geometry(metrics)
    for issue in geometry_issues:
        print(f"  {issue}")
    
    # Step 4: Validate hole counts
    print("\n4. Validating hole counts...")
    hole_issues = validate_hole_counts(metrics)
    for issue in hole_issues:
        print(f"  {issue}")
    
    # Step 5: Run test suite
    print("\n5. Running test suite...")
    test_success, test_stdout, test_stderr = run_test_suite()
    if not test_success:
        print(f"Test suite failed: {test_stderr}")
        return 1
    
    passed, failed = parse_test_results(test_stdout)
    print(f"Tests passed: {passed}/70")
    for failure in failed:
        print(f"  {failure}")
    
    # Step 6: Summary
    print("\n=== Audit Summary ===")
    total_issues = len(geometry_issues) + len(hole_issues) + len(failed)
    
    if total_issues == 0 and passed == 70:
        print("✅ All checks passed - pattern is ready for production")
        return 0
    else:
        print(f"❌ Found {total_issues} issues across geometry, holes, and tests")
        if geometry_issues:
            print(f"  - {len(geometry_issues)} geometry issues")
        if hole_issues:
            print(f"  - {len(hole_issues)} hole count issues")
        if failed:
            print(f"  - {len(failed)} test failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())
