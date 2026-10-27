# HTLB Numeric Formatting Pitfalls

## Common Number-Related Translation Errors

### 1. Number Word Trap
**Problem**: Writing numbers as words instead of digits (e.g., «пять тысяч юаней» instead of «5 000 юаней»)
**Impact**: verify.py cannot find numeric content in translation, causing 'numbers absent' failures
**Root cause**: Subagents may use natural language phrasing instead of required numeric format
**Fix**:
```bash
grep -r '[а-яё]+(?:\s*(тыс|тысяч\w*|миллион\w*|миллиард\w*))' /root/htlb-run-ru/*/units/ | head  # Find word numbers
# Replace with digit format using space for thousands
sed -i 's/пять тысяч юаней/5 000 юаней/g' /root/htlb-run-ru/*/units/*.md
sed -i 's/пятьсот тысяч юаней/500 000 юanей/g' /root/htlb-run-ru/*/units/*.md
```
**Rule**: All monetary amounts, time periods, statistical figures, and measurable quantities must be written in digit format with space-separated thousands (e.g., «5 000 юаней», «30 лет», «96 000 человек»), not as words («пять тысяч», «тридцать лет»)

### 2. Numeric Scale Errors
**Problem**: Chinese 万/亿 converted with wrong magnitude (e.g., 90895.5 亿 → 90895.5 млрд instead of 9 089.55 млрд)
**Root cause**: Copying CN digits but adding incorrect Russian multiplier
**Fix**:
```bash
grep -o "[0-9.]* 亿" book/ru/*.md | head  # Find all 亿 instances
grep -o "[0-9.]* млрд" book/ru/*.md | head  # Check RU versions
# Manual correction: 90895.5 亿 = 9 089.55 млрд
sed -i 's/90895.5 млрд/9 089.55 млрд/g' book/ru/*.md
sed -i 's/25007.5 млрд/2 500.75 млрд/g' book/ru/*.md
```
**Verification**: Cross-check against CN original: `grep -o "90895.5 亿" book/01-不要早死.md`

### 3. Number Leakage Between Sections
**Problem**: Using numbers from 'Эффект' section in 'Простыми словами' section
**Example**: CN 说人话 = '9.6 万人' (96,000), but RU uses '96,217' from 'Эффект'
**Fix**:
```bash
grep -n "96,217" /root/htlb-run-ru/01/units/33.md  # Find instances
grep -o "9.6 万" book/01-不要早死.md  # Check CN original
# Replace '96,217' with '96 000' in Простыми слова section
sed -i '/Простыми слово/,/Эффект:/ s/96,217/96 000/g' /root/htlb-run-ru/01/units/33.md
```
**Rule**: 'Простыми словами' must use rounded/approximate numbers from CN 说人话, not precise stats from 'Эффект'

### 4. Comma Format False Positives
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

### 5. Numeric Normalization Failures
**Problem**: verify.py reports 'numbers absent from translation' for numbers that are actually present but normalized differently
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

## Pre-Commit Numeric Verification Checklist

Before committing any translated chapter:
1. Run `tools/verify.py <NN> --lang ru` and fix all numeric-related FAILs
2. Check for word numbers: `grep -r '[а-яё]+\s*тыс\|миллион\|миллиард' /root/htlb-run-ru/*/units/`
3. Verify numeric conversions against CN originals (万/亿)
4. Check for number consistency between 'Простыми словами' and 'Эффект' sections
5. Scan for comma-formatted numbers and convert to space format
6. Run assemble.py and validate numeric integrity

## Prevention Guidelines for Subagents

- **Always use digit format** for numbers: «5 000», not «пять тысяч»
- **Cross-check 万/亿 conversions** with CN originals for magnitude accuracy
- **Maintain section number consistency**: 'Простыми словами' uses rounded CN 说人话 numbers, 'Эффект' uses precise stats
- **Avoid comma format** in RU text (use spaces for thousands)
- **Verify numeric normalization** by comparing digit-only strings (remove spaces/commas)

## Known Numeric False Positives

- Comma-formatted numbers like '60,000 IU' should be '60 000 IU' to avoid decimal parsing FPs
- verify.py normalizes numbers by removing spaces/commas before comparison
- CN '80300' and RU '80 300' are considered identical by verify.py
- Legal document numbers (最高法知民终 51 号) are exempt from numeric rules
