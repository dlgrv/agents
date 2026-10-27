# HTLB Natural Language Verification Guide

## Purpose

Verification subagent instructions for checking Russian translation naturalness and avoiding literal translation artifacts.

## Verification Scope

Check 5 chapters at a time for:
- Natural Russian flow (no awkward phrasing)
- Consistent terminology across chapters
- Proper localization annotations
- No untranslated Chinese terms outside sources
- Field marker consistency

## Subagent Instructions Template

```
Task: Verify natural Russian language in chapters [01, 11, 14, 19, 26]

Check each chapter for:
1. Natural Russian flow (avoid literal translation artifacts)
2. Consistent field marker usage across chapters
3. Proper localization annotations without over-annotation
4. Emergency numbers and procedures correctly localized
5. No untranslated Chinese terms outside sources

Report format:
- Chapter number
- Issues found (list specific examples)
- Quality score (1-5)
- Critical fixes needed

Work = write verification report only. Do not modify files.
```

## Common Issues to Catch

### Literal Translation Artifacts
- **Chinese word order**: Avoid 'в случае если' → use 'если'
- **Redundant phrases**: Remove 'в действительности' → just state facts
- **Passive voice**: Convert to active where possible
- **Excessive formality**: Use everyday Russian

### Localization Issues
- **Over-annotation**: More than 2 annotations per paragraph
- **Missing annotations**: Emergency numbers without country equivalents
- **Inconsistent terminology**: Different terms for same concept

### Field Marker Issues
- **Inconsistent formatting**: Different spacing or capitalization
- **Missing markers**: Field markers not converted to Russian
- **Incorrect placement**: Field markers in wrong sections

## Quality Standards

- **Score 5**: Perfect natural Russian, proper annotations
- **Score 4**: Minor issues, no critical problems
- **Score 3**: Some awkward phrasing, needs improvement
- **Score 2**: Significant literal translation artifacts
- **Score 1**: Unreadable, requires complete rewrite

## Verification Workflow

1. Assign verification subagents to batches of 5 chapters
2. Each subagent checks for natural language and localization
3. Consolidate reports and identify systemic issues
4. Fix critical issues across all chapters
5. Repeat until all chapters score 4+
