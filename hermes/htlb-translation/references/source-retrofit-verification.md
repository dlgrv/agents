# HTLB Source Title Retrofit Verification Guide

## Purpose

Verification subagent instructions for checking Chinese source titles have Russian translations in `[рус. «…»]` format.

## Verification Scope

Check all source lines (starting with `- Источники:`) for:
- Chinese titles have `[рус. «…»]` annotation
- English-only source lines remain untouched
- Original Chinese/English titles, authors, DOIs, URLs, dates unchanged
- No unintended changes to non-title parts of source lines

## Subagent Instructions Template

```
Task: Verify source title retrofits in chapters [01, 11, 16, 20, 24, 30]

Check each chapter's "- Источники:" lines for:
1. Chinese titles have [рус. «…»] annotation
2. English-only source lines remain untouched
3. Original titles, authors, DOIs, URLs, dates preserved byte-for-byte
4. No unintended changes to non-title parts

Report format:
- Chapter number
- Source lines checked
- Retrofits found
- Issues (missing annotations, corrupted data, etc.)
- Quality score (1-5)

Work = write verification report only. Do not modify files.
```

## Common Issues to Catch

### Missing Annotations
- Chinese titles without `[рус. «…»]`
- Inconsistent application across chapters

### Data Corruption
- Changes to original Chinese titles
- Altered authors, DOIs, URLs, dates
- Modified HTML tags or document codes

### Format Errors
- Wrong bracket types (use [ ] not ( ))
- Missing closing «» or quotes
- Spacing issues around annotations

## Quality Standards

- **Score 5**: All Chinese titles annotated, no data corruption
- **Score 4**: Minor format issues, all annotations present
- **Score 3**: Some missing annotations, no corruption
- **Score 2**: Multiple missing annotations, some corruption
- **Score 1**: Widespread missing annotations or data corruption

## Verification Workflow

1. Assign verification subagents to batches of 4-6 chapters
2. Each subagent checks source lines for proper retrofits
3. Consolidate reports and identify systemic issues
4. Fix missing annotations or data corruption
5. Repeat until all chapters score 4+