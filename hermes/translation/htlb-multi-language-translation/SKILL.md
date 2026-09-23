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

### Critical Checks

- **Byte-identity**: Source lines (来源：/DOI/URLs) must match exactly after field label normalization
- **Count preservation**: Heading/item/tag/DOI counts must match source exactly
- **Number formatting**: Apply language-specific thousands/decimal rules consistently
- **No CJK outside machine zones**: Chinese text only in tags, sources, link targets
- **Field labels**: Correct mapping from CN to target language (e.g., 成本→Costo)

## Common Pitfalls

### Number Formatting Errors

- **ES**: Never use comma as thousands separator (142,740 → 142 740)
- **RU**: Never use comma as thousands separator (10,676 → 10 676)
- **All languages**: Preserve numeric values exactly; only change formatting
- **Unit weights**: Add parenthetical gloss for weight figures (0.25 千克 → 0,25 kilogramos (250 gramos))
- **Large numbers (亿)**: CN «X 亿元» = X/10 billion yuan (亿 = 100 million = 0.1 billion; 6234.86 亿元 = 623.486 billion yuan — NOT 6234.86 billion)
- **Multiple numbers with same unit**: When several numbers share one unit (millions/billions), WRITE the unit at each number: '880,000 million and 808,000 million', not '880,000 and 808,000 million'

### Source Line Handling

- **Never translate source/citation lines**: Replace `- 来源：...` with `§SRC§` marker
- **Keep HTML comments byte-identical**: `<!-- 成本标签: ... -->` if present in source
- **Preserve markdown structure**: `### N. ...` numbering, list order, no new headings

### Regulatory Document IDs

- **Paraphrase in body text**: CN hanzi → office name + "(documento 〔year〕 n.º number)"
- **Keep citation lines byte-faithful**: Never alter hanzi in citation lines or DOIs

## Workflow Steps

1. **Task generation**: Create wave specifications with unit counts and file paths
2. **Subagent dispatch**: Deploy parallel subagents per chapter/language
3. **Quality verification**: Run verification scripts after each batch
4. **Steer corrections**: Send updates to running agents for specification errors
5. **Batch coordination**: Progress through waves sequentially

## Reference Files

- **Sample translations**: `/root/htlb-run-{lang}/{chapter}/units/05.md` (for formatting reference)
- **Source digest**: `/root/github/htlb-ru/tools/digest/{chapter}/units/NN.md`
- **Task specifications**: `/tmp/wave_specs.json`
- **Unit counts**: `/tmp/zh_counts_head.json`

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

- **Parallel subagents**: Process multiple chapters simultaneously
- **Task batching**: Group related tasks to reduce overhead
- **Cache recovery**: Use delegation transcripts for recovery if agents fail
- **Pre-verification**: Check file existence before dispatching tasks

## Troubleshooting

- **Agent timeouts**: Use smaller units for long chapters
- **Formatting drift**: Regular verification with number preservation scripts
- **Source mismatches**: Verify digest files match upstream Chinese content
- **Count discrepancies**: Use grep, not stated counts, for verification

## Success Metrics

- **Zero numeric losses**: All 万/亿 conversions and numeric values preserved
- **Byte-identical sources**: Citation lines match source exactly
- **Count preservation**: All heading/item/tag/DOI counts match
- **Language compliance**: Number formatting follows language-specific rules
- **Wave completion**: All chapters in a wave completed successfully
- **Batch coordination**: Parallel subagents limited to 10 per wave to avoid delegation limits
- **Multiple number handling**: When several numbers share one unit (millions/billions), write the unit at each number

## Integration with HTLB Infrastructure

- **Run directories**: `/root/htlb-run-{lang}/{chapter}/units/`
- **Digest source**: `/root/github/htlb-ru/tools/digest/{chapter}/units/`
- **Verification tools**: `tools/verify.py`, `tools/assemble_{lang}.py`
- **Deployment**: Copy to `book/{lang}/` with status lines and back-links
- **Repository management**: Commit to fork branches with descriptive messages
