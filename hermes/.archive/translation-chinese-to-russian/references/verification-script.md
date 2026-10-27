# Verification script for Chinese-to-Russian translation

## Purpose
Automated verification script to catch structural and content mismatches between Chinese source and Russian translation.

## Usage
```bash
python3 htlb_verify.py book/01-不要早死.md book/ru/01-Не-умирайте-рано.md
python3 htlb_verify.py --normalize book/01-不要早死.md book/ru/01-Не-умирайте-рано.md
```

## What it checks
- Item counts per chapter (### X. Title must match)
- Tag-comment counts (<!-- 成本标签: ... -->)
- DOI presence and counts
- Source lines byte-faithful after label translation
- Numeric values (normalizing comma/dot, 万→10000)
- CJK characters outside allowed zones (links, parentheses)
- Back-link relative paths

## Normalization modes
- Standard: strict byte comparison
- Normalized: treats 0,58 ≡ 0.58, 1万 ≡ 10000, ignores locale-specific punctuation

## Common false positives to ignore
- Decimal comma vs dot (0,58 vs 0.58)
- Thousands separators (1,000 vs 1000)
- Percentage formatting (97.2% vs 97,2%)
- Statistical rounding (40% ≈ 42%, 70% ≈ 69%)
- 万 conversion (1万 = 10000, 1.5万 = 15000)

## Exit codes
- 0: All checks passed
- 1: Structural mismatch (items/tags/DOIs)
- 2: Numeric or content mismatch
- 3: Script error

## Example output
```
Реальных расхождений: 183
FAIL гл.01/п.1: Эффект≠收益 потеряны {'248099': 1, '10': 1} лишние {'248': 1, '99': 1, '100': 1}
```

## Integration
Run after each chapter completion and before MQM review to catch systematic errors early.
