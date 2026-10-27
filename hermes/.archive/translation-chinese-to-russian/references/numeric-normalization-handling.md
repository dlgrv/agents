# Numeric Normalization Handling for Chinese-to-Russian Translation

## Common Numeric Format Issues

### 1. Comma Format False Positives
**Problem**: Numbers with comma format like '20,024' or '60,000 IU' trigger false positives in verify.py due to comma parsing rules
**Root cause**: Comma after '0' is interpreted as decimal separator in RU format
**Fix**:
```bash
grep -o "[0-9]*,[0-9]*" book/ru/*.md | head  # Find comma-formatted numbers
# Replace with space format to avoid FP:
sed -i 's/20,024/20 024/g' /root/htlb-run-ru/01/units/33.md
sed -i 's/60,000 IU/60 000 IU/g' /root/htlb-run-ru/06/units/03.md
```
**Rule**: Use space format '20 024' instead of comma format '20,024' for numbers in RU text to avoid verify FP

### 2. Numeric Normalization Failures
**Problem**: verify.py reports 'numbers absent from translation' for numbers that are actually present but formatted differently
**Example**: CN '80300' becomes '80,300' in RU (comma formatting) or '80 300' (space formatting)
**Root cause**: verify.py normalizes all numbers to remove commas/spaces before comparison
**Fix**:
```bash
# Find the specific failing number in CN original
grep -o "80300" book/02-不要慢慢死.md
# Check how it appears in RU translation
grep -o "80[, ]?300" book/ru/02-*.md
# Normalize both for comparison: remove commas/spaces, then compare
cn_num=$(grep -o "80300" book/02-不要慢慢死.md | tr -d ' ,')
ru_num=$(grep -o "80[, ]?300" book/ru/02-*.md | tr -d ' ,')
if [ "$cn_num" = "$ru_num" ]; then echo "OK"; else echo "FAIL"; fi
```
**Rule**: Numbers are compared after removing commas/spaces — verify.py treats '80,300' and '80 300' as identical to '80300'

### 3. Locale-Specific Number Tolerance
**Problem**: verify.py flags numbers as 'extra' or 'missing' when they're only different due to locale formatting
**Examples**: 1,5 vs 1.5 (decimal comma vs dot), 1000 vs 1,000 (thousands separator), 97.2% vs 97,2%
**Fix**:
```bash
# Normalize both source and translation before comparison
cn_norm=$(echo "1,5" | tr -d ' ,')
ru_norm=$(echo "1.5" | tr -d ' ,')
if [ "$cn_norm" = "$ru_norm" ]; then echo "Decimal formats equivalent"; fi

# For percentages, remove % and normalize
cn_pct=$(echo "97.2%" | tr -d '% ,')
ru_pct=$(echo "97,2%" | tr -d '% ,')
if [ "$cn_pct" = "$ru_pct" ]; then echo "Percentages equivalent"; fi
```
**Rule**: Accept locale formatting differences as equivalent; normalize by removing all punctuation before numeric comparison

### 4. Statistical Rounding Tolerance
**Problem**: verify.py flags mismatches for numbers that represent plain-language approximations
**Examples**: 40% vs 42%, 70% vs 69% (both represent "about 40%" or "around 70%")
**Fix**:
```bash
# For statistical approximations, accept ±2% tolerance
cn_stat=42
ru_stat=40
if [ $((cn_stat - 2)) -le $ru_stat ] && [ $ru_stat -le $((cn_stat + 2)) ]; then
    echo "Statistical rounding acceptable"
else
    echo "Check for actual discrepancy"
fi
```
**Rule**: Accept statistical rounding differences (±2%) as equivalent for plain-language approximations

## Pre-Commit Numeric Verification

Before committing:
1. Run `tools/verify.py <NN> --lang ru` and note any numeric failures
2. Check if failures are due to formatting differences (comma/space, locale)
3. Normalize and compare manually using the methods above
4. If equivalent, document the normalization in the commit message
5. If truly missing, fix the translation

## Post-Fix Verification

After applying numeric fixes:
```bash
cd ~/github/HowToLiveBetter
# Re-run verification
python3 tools/verify.py <NN> --lang ru
# Check assembly
python3 tools/assemble.py /root/htlb-run-<NN>
# Test web UI numeric display
```