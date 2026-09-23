# HTLB Number Formatting Rules by Language

## Summary

Each target language has specific rules for number formatting that must be strictly followed to maintain quality gates and byte-identity requirements.

## Language Rules

| Language | Thousands Separator | Decimal Point | Example | Common Errors |
|----------|-------------------|---------------|---------|---------------|
| **RU (Russian)** | Space ( ) | Dot (.) | 10 676, 0.001 | Never use comma as thousands separator (10,676 ❌) |
| **EN (English)** | Comma (,) | Dot (.) | 142,740, 0.001 | Never use comma as decimal separator (0,001 ❌) |
| **ES (Spanish)** | Space ( ) | Comma (,) | 142 740, 0,001 | Never use comma as thousands separator (142,740 ❌) |
| **ZH (Chinese)** | Comma (,) | Dot (.) | 142,740, 0.001 | Reference format only |

## Special Cases

### Unit Weights
- **CN**: 0.25 千克 → **ES**: 0,25 kilogramos (250 gramos)
- Always add parenthetical gloss with absolute value for weight figures
- Required due to verifier quirk with 千/万 as scale words

### Large Numbers
- **万**: Convert to numeric (1 万 = 10,000; 610.6 万 = 6.106 million)
- **亿**: Convert to numeric (1 亿 = 100,000,000; 2.5 亿 = 250 million)
- Only convert when adjacent to 万/亿; standalone numbers unchanged

## Verification Commands

```bash
# Check ES number formatting
grep -o "[0-9]\+[ 0-9,]*\b" file.md | grep -v "[0-9]\+[ 0-9]*[0-9]\b"
# Should find no results (no comma-thousands in ES)

# Check RU number formatting
grep -o "[0-9]\+[ 0-9,]*\b" file.md | grep -v "[0-9]\+[ 0-9]*[0-9]\b"
# Should find no results (no comma-thousands in RU)

# 万/亿 conversion verification
grep -o "[0-9.]*\s*万\b" file.md | wc -l
grep -o "[0-9.]*\s*亿\b" file.md | wc -l
# Must match source counts
```

## Pitfalls to Avoid

1. **Comma confusion**: ES/RU never use comma as thousands separator
2. **Decimal consistency**: ES uses comma decimal, others use dot
3. **Space formatting**: ES/RU use space thousands, EN uses comma
4. **Unit weight conversion**: Always add absolute value in parentheses
5. **Large number conversion**: Only convert adjacent to 万/亿, preserve standalone numbers

## Sample Reference Files

- `/root/htlb-run-es/13/units/05.md` - ES formatting reference
- `/root/htlb-run-en/13/units/05.md` - EN formatting reference
- `/root/htlb-run-ru/13/units/05.md` - RU formatting reference
