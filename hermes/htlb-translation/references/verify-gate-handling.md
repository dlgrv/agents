# Verify Gate Failure Handling

## Common Verify.py Failure Modes & Fixes

### 0. Word-Number FAIL Root Cause (RU numerals not folded)
**Problem**: «numbers absent from translation: 80000×2, 120000×2 …» even though the RU text DOES contain the numbers — but spelled as words («восемьдесят с лишним тысяч», «сто двадцать с лишним тысяч»).
**Mechanism**: verify.py `WORD_VALUES` folds only oblique forms «трёх/трем/пяти/семи/восьми/девяти», «двадцать-девяносто», «пятьсот-девятьсот», «сто» and «два/обеих/…». NOT folded: «три/семь/девять/десять/пятьдесят/тысяч/миллион/млрд» as words, so «восемьдесят с лишним тысяч» produces ZERO values (восемьдесят and тысяч are not in the fold list) → CN «8 万» value 80000 is missing → FAIL.
**Fix**: in run units, replace word numbers with digits using book format «80 000 юаней», «50 000–500 000», «7 100 000 юаней», «7 млрд юаней» (CN 亿元 ×0.1 млрд, 万 ×10 000). Legal sentence terms → digits too («до 3 лет», «от 3 до 7», «1 год 6 месяцев условно»), matching ch08/30 convention. Keep: enumerations («пять условий», «две категории», «три вопроса» in headings), semantic ranges CN has as words («в один-пять раз больше», «1 到 5 倍», «один-пять размеров дохода», «два независимых вопроса»).
**Verify numbers WITHOUT running assemble**: replicate norm_numbers()+fold_words() in a scratch script, compare Counter(cn values) − Counter(ru values) per unit (cn_body = lines except «- 来源：»/成本标签; ru_body = except §SRC§). All-empty diff = verify numbers pass.
**Rule of thumb**: if CN shows a digit (incl. X 万/X 亿), RU MUST carry the same value somewhere; a word number that folds to nothing counts as absent.

### 1. Legacy Field Labels
**Problem**: Subagents sometimes use '- Выгода:' instead of '- Эффект:'
**Impact**: Web parser regex `^- (?:收益|Эффект|Benefit)` doesn't match 'Выгода', causing 'Эффект' blocks to disappear from site
**Fix**:
```bash
cd ~/github/HowToLiveBetter
grep -r "- Выгода:" /root/htlb-run-ru/*/units/ | wc -l  # Count instances
sed -i 's/- Выгода:/- Эффект:/g' /root/htlb-run-ru/*/units/*.md  # Bulk replace
```
**Prevention**: Include in field marker rules reminder before each translation wave

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

### 4. CJK Characters in Non-Source Text
**Problem**: Chinese characters appear outside of sources, tags, or legitimate gloss patterns
**Allowed zones**: Sources (§SRC§), tags (§TAG§), glosses `(低保 — ...)`, legal titles
**Fix**:
```bash
grep -P "[\u4e00-\u9fff]" book/ru/*.md | grep -v "§SRC§\|§TAG§\|（\[\|\]\)" | head  # Find violations
```
**Special handling**: Legal/regulation titles in English text (e.g., "统筹地区 — ...") are allowed

### 5. Prohibited Calques
**Problem**: Direct translation of Chinese-specific terms that don't exist in Russian
**Common offenders**: когорт, популяц, exposure, quartile, confounding
**Fix**:
```bash
grep -r "когорт\|популяц" book/ru/ | head  # Find instances
# Replace with natural Russian equivalents:
# когорт → группа (for study groups)
# популяц → группа населения (for population)
```
**Rule**: Use natural Russian terminology, not literal translations of Chinese academic terms

### 6. Comma Format False Positives
**Problem**: Numbers with comma format like '20,024' or '60,000 IU' trigger false positives in verify.py due to comma parsing rules
**Root cause**: Comma after '0' is interpreted as decimal separator in RU format
**Fix**:
```bash
grep -o "[0-9]*,[0-9]*" book/ru/*.md | head  # Find comma-formatted numbers
# Replace with space format to avoid FP:
sed -i 's/20,024/20 024/g' /root/htlb-run-ru/01/units/33.md
sed -i 's/60,000 IU/60 000 IU/g' /root/htlb-run-ru/06/units/03.md
```
**Rule**: Use space format '20 04' instead of comma format '20,024' for numbers in RU text to avoid verify FP

### 7. Numeric Normalization Failures
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

## Known FP verify.py (not to be crudely fixed)
- "60,000 IU" in RU text is read as decimal (comma = thousands only if not "0..."; one line in ru06). Fix: replace with "60 000 IU" to avoid false positive.
- CN "250 多万粉丝" vs EN paraphrase without number — en09, requires text-level resolution, not script fix.
- Real findings from first run 53/62: calques "когорт" ×13 (ch. 13/28/29/30), "популяц" ×2 (ch. 29), missing numbers in ru10/ru11 — material for a fix wave.
- CJK gloss false positives: Legal titles in English text with CJK characters (e.g., "统筹地区 — ...") are allowed and should not trigger warnings. Verify regex excludes gloss patterns like `(统筹地区 — ...)` or `(副主任医师 — ...)`.
- **Relative path FPs**: verify.py may report broken links for `../docs/` in translated chapters — this is expected and should be ignored. These links are valid from CN book/*.md but need `../../docs/` in book/{ru,en,es}/. Use `tools/check_links.py` for proper link validation instead.

## Pre-Commit Verification Checklist

Before committing any translated chapter:
1. Run `tools/verify.py <NN> --lang ru` and fix all FAILs
2. Check for legacy field labels: `grep -r "- Выгода:" book/ru/`
3. Verify numeric conversions against CN originals
4. Check for number consistency between sections
5. Scan for prohibited calques
6. Run assemble.py and validate web UI

## Post-Fix Verification

After applying fixes:
```bash
cd ~/github/HowToLiveBetter
python3 tools/verify.py <NN> --lang ru
python3 tools/assemble.py /root/htlb-run-<NN>
# Test web UI: open index.html?lang=ru and check all sections
```