---
name: htlb-multi-language-translation
description: HTLB Chinese-to-multiple-language translation workflow.
category: translation
tags: [translation, chinese, spanish, english, russian, book]
author: Hermes Agent
license: MIT
version: 1.1
metadata:
  hermes:
    tags: [translation, chinese, spanish, english, russian, book, htlb]
    related_skills: [htlb-es-translation, translation-chinese-to-russian]
---

# HTLB Multi-Language Translation Workflow

## When to Use

Use this skill when translating HTLB (HowToLiveBetter) Chinese self-help book content into multiple languages (Russian, English, Spanish). This workflow handles fresh translations, revised units, quality gates, and verification across all target languages using a wave-based revision system.

## Overview

HTLB (HowToLiveBetter) is a Chinese self-help book translated into multiple languages (Russian, English, Spanish) using a wave-based revision system. This workflow handles fresh translations, revised units, quality gates, and verification across all target languages.

## Core Principles

- **Wave-based processing**: Translation work is organized into waves (W1/W2/W3) where each wave handles a specific set of chapters and revision types
- **Fresh vs Revised units**: Units are categorized as fresh (new translation) or revised (update existing translation to match Chinese source)
- **Language-specific formatting**: Each language has strict number formatting rules (thousands separator, decimal point)
- **Quality gates**: Automated verification ensures byte-identity of source lines, count preservation, and formatting compliance
- **Parallel processing**: Subagents handle chapters in parallel with strict task specifications

## Wave Structure

- **W1**: Fresh translation of chapters 2-31 (excluding chapters with existing translations)
- **W2**: Fresh translation of chapters 32-33 + standalone docs
- **W3**: Revision of existing units in chapters 10, 14, 15, 16, 17, 18, 19, 22, 24, 25, 26, 27, 28, 29, 32
- **Language support**: RU, EN, ES for each wave/chapter combination

## Language Number Formatting Rules

| Language | Thousands Separator | Decimal Point | Example | Notes |
|----------|-------------------|---------------|---------|-------|
| **RU** | Space ( ) | Dot (.) | 10 676, 0.001 | Never comma as thousands separator |
| **EN** | Comma (,) | Dot (.) | 142,740, 0.001 | Never comma as decimal separator |
| **ES** | Space ( ) | Comma (,) | 142 740, 0,001 | Never comma as thousands separator |
| **ZH** | Comma (,) | Dot (.) | 142,740, 0.001 | Source format reference |

## Task Specification Template

Each translation task follows a standardized template:

```json
{
  "wave": "w1|w2|w3",
  "goal": "Wave description (chapter, language, unit counts)",
  "context": "Detailed instructions including:",
  "- Chapter and language specification",",
  "- Fresh vs revised unit handling",",
  "- Field label mapping (CN→target)",",
  "- Number formatting rules",",
  "- Quality verification requirements",",
  "- Source and target file paths",",
  "- Sample reference files",",
  "output_schema": {",
    "type": "object",",
    "properties": {",
      "units_done": {"type": "integer"},",
      "list": {"type": "array", "items": {"type": "integer"}},",
      "chapter": {"type": "string"},",
      "lang": {"type": "string"}",
    },",
    "required": ["units_done"]",
  }",
}
```

## Quality Gates

### Verification Scripts

- **assemble.py**: Ensures byte-identical assembly to source
- **verify.py**: Checks headings, tags, sources, numbers, and count preservation
- **Number preservation scripts**: Verify 万/亿 conversions and numeric formatting compliance
- **wave_pipeline.py**: Batch verification tool for multiple chapters/languages

### Critical Checks

- **Byte-identity**: Source lines (来源：/DOI/URLs) must match exactly after field label normalization
- **Count preservation**: Heading/item/tag/DOI counts must match source exactly
- **Number formatting**: Apply language-specific thousands/decimal rules consistently
- **No CJK outside machine zones**: Chinese text only in tags, sources, link targets
- **Field labels**: Correct mapping from CN to target language (e.g., 成本→Costo)
- **Number completeness**: All numeric values from CN must appear in translation (missing numbers = FAIL)

## Field Value Capitalization Rule

**Rule**: Every field value must start with a capital letter. This applies to:
- Cost/Price values
- Simple explanation text
- Benefit descriptions
- Evidence grade levels
- Notes/comments

**Examples**: 
- `- Cost: 5 000 yuanes` (correct, not `5 000 yuanes`)
- `- Cost: 5 000 yuanes` (correct, not `5 000 yuanes`)
- `- Evidence grade: B` (correct, not `b`)
- `- Notes: This is important` (correct, not `this is important`)

**Implementation**: Use regex `(?m)^- (?:Cost|In plain terms|Benefit|Evidence grade|Notes): ([^\W\d_])` to detect and fix lowercase starts across all languages.

**Script**: `references/capitalization-fix-script.py` — automated fix tool for all units

## Common Pitfalls

### Number Formatting Errors

- **ES**: Never use comma as thousands separator (142,740 → 142 740)
- **RU**: Never use comma as thousands separator (10,676 → 10 676)
- **All languages**: Preserve numeric values exactly; only change formatting
- **Unit weights**: Add parenthetical gloss for weight figures (0.25 千克 → 0,25 kilogramos (250 gramos))
- **Large numbers (亿)**: CN «X 亿元» = X/10 billion yuan (亿 = 100 million = 0.1 billion; 6234.86 亿元 = 623.486 billion yuan — NOT 6234.86 billion)
- **Multiple numbers with same unit**: When several numbers share one unit (millions/billions), WRITE the unit at each number: '880,000 million and 808,000 million', not '880,000 and 808,000 million'
- **Decimal commas in ES**: Replace all decimal dots with commas (0.14 → 0,14) — verify.py expects comma decimal format for ES
- **Space separators in ES**: Replace all decimal dots with commas and comma-thousands with spaces (18.905 → 18 905; 0.14 → 0,14) — verify.py expects both space thousands and comma decimals

### Field Value Capitalization Pitfalls

- **Legacy translations**: Some older units may start values with lowercase letters
- **Subagent consistency**: All subagents must enforce capitalization rule from start
- **Verification**: Use regex to detect lowercase starts across all field values
- **Scope**: Applies to all five field types: Cost/Price, Simple explanation, Benefit, Evidence grade, Notes
- **Automation**: Use `references/capitalization-fix-script.py` for batch fixes

### Alignment and Revision Mapping Pitfalls

- **Alignment map accuracy**: SequenceMatcher ratio may be based on headings only (r=1.0), not actual content similarity. Always verify real content similarity before trusting alignment pairs.
- **Pre vs HEAD revision scope**: When Chinese source updates, pre-version and HEAD units may have different content even with high alignment ratio. Always diff pre vs HEAD units to identify actual changes.
- **Revise task scope**: Ensure revise lists include ALL edited units, not just those with high alignment ratios. Use `difflib.SequenceMatcher` to verify actual content changes between pre and HEAD.
- **Missing revision units**: If subagents report fewer units than expected, verify task specification included all revise slots. Manual revision may be needed for units skipped due to alignment errors.

### Chapter Structure and Slot Mapping

- **CN chapter expansion**: When Chinese chapters add new units (e.g., ch04: 13→18 units), ensure alignment map covers all new slots. Verify unit mapping with actual content diff, not just numbering.
- **Slot numbering changes**: New units may shift existing slot numbers (e.g., pre#10 → HEAD#15). Use git history to locate original unit content and verify actual content matches alignment expectation.
- **Cross-unit content drift**: Units with high alignment ratio may still have significant content changes. Always run content diff before revision to identify actual translation updates needed.

### Source Line Handling

- **Never translate source/citation lines**: Replace `- 来源：...` with `§SRC§` marker
- **Keep HTML comments byte-identical**: `<!-- 成本标签: ... -->` if present in source
- **Preserve markdown structure**: `### N. ...` numbering, list order, no new headings
- **ES decimal consistency**: Replace ALL decimal dots with commas in ES (0.14 → 0,14) and ALL comma-thousands with spaces (18.905 → 18 905) — verify.py strictly expects comma decimals and space thousands

### Regulatory Document IDs

- **Paraphrase in body text**: CN hanzi → office name + "(documento 〔year〕 n.º number)"
- **Keep citation lines byte-faithful**: Never alter hanzi in citation lines or DOIs

### Preview Banner Statistics Synchronization

- **Problem**: Preview banners (og-*.png in README) often show outdated statistics (528/347/1066) after translation waves complete
- **Rule**: Always update banner numbers to match current HTLB unit counts (601/407/1253 for RU/EN/ES)
- **Implementation**: Update HTML source files in `tools/og-{ru,en,es}.html` with current counts, regenerate PNG via headless Chromium (1200×630)
- **Verification**: Use vision_analyze to confirm numbers appear correctly in regenerated PNGs
- **Sync**: Update ES badge in README.es.md to match link count (Primary%20sources-1066 → Primary%20sources-1253)
- **Command**: `npx playwright install chromium; node og_shot.mjs` for banner regeneration
- **Timing**: Update after each major wave completion and before final release deployment

## Workflow Steps

1. **Task generation**: Create wave specifications with unit counts and file paths
2. **Subagent dispatch**: Deploy parallel subagents per chapter/language (limit 10 per batch to avoid delegation limits)
3. **Quality verification**: Run verification scripts after each batch:
   - `python3 tools/wave_pipeline.py CH1 CH2 CH3...` for batch verification
   - `python3 tools/verify.py CH --lang LANG --file book/LANG/out-CH.md` for individual chapters
   - Check for missing numbers, formatting errors, and content alignment
4. **Steer corrections**: Send updates to running agents for specification errors
5. **Batch coordination**: Progress through waves sequentially, handling revision mapping errors
6. **Revision mapping validation**: Before revision tasks, verify actual content changes between pre and HEAD using `difflib.SequenceMatcher`
7. **Preview banner update**: After wave completion, regenerate preview banners:
   - Run `python3 references/banner-regeneration-script.py`
   - Verify numbers with `vision_analyze` if needed
   - Commit changes to repository
   - Update README badges (especially ES links count)

## Reference Files

- **Sample translations**: `/root/htlb-run-{lang}/{chapter}/units/05.md` (for formatting reference)
- **Source digest**: `/root/github/htlb-ru/tools/digest/{chapter}/units/NN.md`
- **Task specifications**: `/tmp/wave_specs.json`
- **Unit counts**: `/tmp/zh_counts_head.json`
- **Alignment maps**: `/tmp/align_map.json` (requires validation against actual content)
- **ES decimal example**: `/root/htlb-run-es/30/units/05.md` - shows correct 18 905 (space thousands) and 0,14 (comma decimal)
- **Revision mapping validation**: `references/revision-mapping-validation.md` (validate actual content changes before revision tasks)
- **Capitalization fix script**: `references/capitalization-fix-script.py` (automated tool for field value capitalization)
- **Banner regeneration script**: `references/banner-regeneration-script.py` (update og-*.png and README badges after wave completion)

## Multi-Language Coordination

- **Parallel language processing**: Same chapters processed simultaneously for RU/EN/ES
- **Consistent terminology**: Maintain glossaries across languages
- **Shared quality gates**: Same verification scripts apply to all languages
- **Wave synchronization**: All languages must complete a wave before moving to next
- **Batch management**: Limit parallel subagents to 10 per wave to avoid hitting delegation limits; split larger batches into multiple calls

## Revision System

- **Fresh units**: Translate from Chinese source to target language
- **Revised units**: Update existing translation to match current Chinese source
- **Delta tracking**: Track changes between Chinese source versions
- **Revision flags**: Mark units as requiring revision in task specifications

## Performance Optimization

- **Parallel subagents**: Process multiple chapters simultaneously (limit 10 per batch)
- **Task batching**: Group related tasks to reduce overhead, split larger batches into multiple calls
- **Cache recovery**: Use delegation transcripts for recovery if agents fail
- **Pre-verification**: Check file existence before dispatching tasks
- **Revision mapping**: Use `difflib.SequenceMatcher` to verify actual content changes before revision tasks

## Troubleshooting

- **Agent timeouts**: Use smaller units for long chapters
- **Formatting drift**: Regular verification with number preservation scripts
- **Source mismatches**: Verify digest files match upstream Chinese content
- **Count discrepancies**: Use grep, not stated counts, for verification
- **Revision mapping errors**: Verify actual content changes with `difflib.SequenceMatcher` when alignment ratios seem incorrect
- **Missing revision units**: If subagents skip units, manually verify task specification included all revise slots and content actually changed
- **Chapter structure changes**: When Chinese chapters expand (e.g., 13→18 units), verify new slot mapping with content diff, not just numbering

## Success Metrics

- **Zero numeric losses**: All 万/亿 conversions and numeric values preserved
- **Byte-identical sources**: Citation lines match source exactly
- **Count preservation**: All heading/item/tag/DOI counts match
- **Language compliance**: Number formatting follows language-specific rules
- **Wave completion**: All chapters in a wave completed successfully
- **Batch coordination**: Parallel subagents limited to 10 per wave to avoid delegation limits
- **Multiple number handling**: When several numbers share one unit (millions/billions), write the unit at each number
- **Revision accuracy**: All revised units actually match current Chinese source content (verified via diff)

## Integration with HTLB Infrastructure

- **Run directories**: `/root/htlb-run-{lang}/{chapter}/units/`
- **Digest source**: `/root/github/htlb-ru/tools/digest/{chapter}/units/`
- **Verification tools**: `tools/verify.py`, `tools/assemble_{lang}.py`, `tools/wave_pipeline.py`
- **Deployment**: Copy to `book/{lang}/` with status lines and back-links
- **Repository management**: Commit to fork branches with descriptive messages
- **Revision mapping tools**: Use `difflib.SequenceMatcher` to verify actual content changes between pre and HEAD versions
