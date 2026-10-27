# English Translation CJK Handling

## Legal Regulation Title CJK False Positives

Some English chapters contain CJK characters in legal regulation titles that are correctly rendered as glosses:

- **Pattern**: `The General Office of the State Council measures in April 2026 on accelerating the building of pooling region (统筹地区 — the locality where you are insured)`
- **Valid CJK locations**: Only within parentheses after English explanatory text, never standalone
- **Gloss format**: `(CJK term — English explanation)` where CJK provides context for the English

## Detection and Exclusion Rules

When auditing for untranslated Chinese characters (`\u4e00-\u9fff` regex), exclude lines matching these patterns:

1. **Gloss pattern**: `\([^)]*\u4e00-\u9fff[^)]*—[^)]*\)` — any CJK within parentheses with an em dash
2. **Medical term pattern**: `\([^)]*\u4e00-\u9fff[^)]*—[^)]*\)` — e.g., `associate chief physician (副主任医师 — the second-highest level)`
3. **Filing pattern**: `\([^)]*\u4e00-\u9fff[^)]*—[^)]*\)` — e.g., `two different filings (备案 — translation with your insurance)`

## Implementation

```bash
# Audit script example
grep -P '\u4e00-\u9fff' chapter.md | grep -vP '\([^)]*\u4e00-\u9fff[^)]*—[^)]*\)'
```

This will show only actual untranslated Chinese text, not valid glosses.

## Quality Assurance

- After translation, run CJK audit with exclusion rules
- Verify no standalone CJK characters remain in visible text
- Confirm all glosses follow the `(CJK — English)` format
- Check that regulation titles are properly referenced in body text with descriptive English

## Pitfall

Never exclude CJK characters that appear outside of gloss parentheses — these indicate missing translation
