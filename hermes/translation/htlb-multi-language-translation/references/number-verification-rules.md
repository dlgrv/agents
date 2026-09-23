# HTLB Number Verification Rules

## Verifier Quirks and Fixes

### Scale Word Folding Error

**Problem**: ES verify folds scale words only to the immediately preceding number, not to entire phrases.

**Example**:
- CN: «880 000 亿元和 8080 亿元»
- Wrong ES: «880 000 y 808 000 millones de yuanes» → verify misses 880,000 (no scale word)
- Correct ES: «880 000 millones y 808 000 millones de yuanes» → both numbers get scale words

**Fix**: Distribute scale words to each number individually.

### Large Number Conversion (亿)

**Problem**: CN «亿» = 100,000,000, but translators often treat it as billion (1,000,000,000).

**Examples**:
- CN: 6234.86 亿元 → 623,486 billion (not 6234.86 billion)
- CN: 2.5 亿 → 250 million (not 2.5 billion)
- Fix: Divide by 10 when converting 亿 to numeric value

### Number Preservation

**Rule**: All numeric values must be preserved exactly; only formatting changes.
- CN «6234.86 亿元» → ES «623 486 millones» (not «6234.86 millones»)
- CN «12 万元» → ES «12 000 yuanes» (not «12 yuanes»)

### Weight Figures

**Problem**: Verifier reads 千 inside 千克 as scale ×1000: «0.25 千克» → key «250».

**Fix**: Add parenthetical gloss with absolute value.
- CN: 0.25 千克 → ES: 0,25 kilogramos (250 gramos)

### Regulatory Document IDs

**Rule**: Paraphrase in body text, keep citations byte-faithful.
- Body: CN 国食药监办〔2010〕432号 → ES (documento 〔2010〕 n.º 432)
- Citations: Keep hanzi unchanged

## Verification Commands

```bash
# Check for missing scale words (ES/RU)
grep -o "[0-9]\+[ 0-9,]*\s*(?:millones|mil|millón)" file.md
# Should find all large numbers with scale words

# Check 亿 conversions
grep -o "[0-9.]*\s*亿" file.md | while read line; do
  num=$(echo "$line" | sed 's/[^0-9.]//g')
  result=$(echo "$num / 10" | bc)
  echo "CN $line → should be $result billion"
done

# Check comma-thousands forbidden in ES/RU
grep -o "[0-9]\+,[0-9]\+" file.md
# Should find no results
```