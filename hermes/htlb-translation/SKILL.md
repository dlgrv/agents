---
name: htlb-translation
description: "Chinese-to-Russian book translation with chunked units"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [translation, chinese, russian, book, htlb, chunking]
    related_skills: [github-pr-workflow]
---

# HTLB Translation Workflow

Workflow for translating the HowToLiveBetter book from Chinese to Russian. Uses chunked units (not whole chapters) and incremental commits with explicit developer approval before any git/PR action.

## Core Principle

**Never create a branch, commit, or PR unless the developer explicitly asks for it.** This overrides general assumptions that finishing a task implies shipping a commit. Always require an explicit instruction to commit/branch/PR in the same turn.

## 1. Chapter Preparation

Each chapter is split into units by `tools/digest.py`. Units are stored in `/root/htlb-run/<chapter>/units/` with placeholders `§TAG§` and `§SRC§` that are filled by `assemble.py` later.

```bash
# Prepare run directory for a chapter (e.g. chapter 16)
cd ~/github/htlb-ru
mkdir -p /root/htlb-run/16/units
cp tools/digest/16/units/*.md /root/htlb-run/16/units/
for n in 00 01 02 03 04 05 06 07; do echo "§TAG§" >> /root/htlb-run/16/units/$n.md; echo "§SRC§" >> /root/htlb-run/16/units/$n.md; done
```

### Unit File Structure

Each unit file must contain:
1. Chapter header (exact format per TRANSLATION.md)
2. Empty lines
3. Translated content with field markers
4. §TAG§ placeholder (on its own line)
5. §SRC§ placeholder (on its own line)

## 2. Unit Translation

Translate each unit incrementally. Each unit must be written to its file immediately after translation (no JSON reports until all units are done).

```bash
# Use delegation or manual translation per unit
# Each unit file contains:
# - Line 1: chapter header (exact format per TRANSLATION.md)
# - Empty lines
# - Content with field markers: 成本→Стоимость, 说人话→Простыми словами, etc.
# - §TAG§ and §SRC§ lines (placeholders, leave untouched)

# Write translated unit back to file immediately
write_file /root/htlb-run/16/units/01.md "translated content...\n\n§TAG§\n§SRC§"
```

### Field Marker Rules

| Chinese | Russian | Notes |
|---------|--------|-------|
| 成本 | Стоимость | Cost/expense field |
| 说人话 | Простыми словами | Simple language field |
| 收益 | Эффект | Benefit/effect field |
| 证据等级 | Уровень доказательности | Evidence level (A/B/C remain) |
| 备注 | Примечания | Notes/remarks field |

### Translation Rules

- **Numbers**: Always byte-for-byte copy (§ numbers remain unchanged)
- **Slang**: Never translate: cohort/exposure/quartile/confounding/population/low-evidence
- **Style**: Live Russian, not literal translation
- **Headers**: Must start with verbs
- **Simple language field**: No numbers outside "Эффект" section
- **Exclamation marks**: None allowed
- **Sources**: Never translate — injected byte-by-byte by assemble.py

### Field Marker Rules

- 成本 → Стоимость
- 说人话 → Простыми словами
- 收益 → Эффект
- 证据等级 → Уровень доказательности (A/B/C remain)
- 备注 → Примечания
- All numbers/dosages are byte-for-byte (§ numbers remain)
- No slang: cohort/exposure/quartile/confounding/population/low-evidence
- Live Russian, not literal translation
- "Простыми словами" without numbers outside "Эффект"
- No exclamation marks
- Headers with verbs

## 3. Assembly and Validation

When all units of a chapter are translated, use `assemble.py` to inject sources and validate:

```bash
cd ~/github/htlb-ru
python3 tools/assemble.py /root/htlb-run/16
```

This script:
- Injects sources from `tools/digest/16/sources/` byte-for-byte
- Validates field markers and unit count
- Checks for missing/incomplete units
- Outputs translated chapter to `book/16-...-ru.md`

## 4. Git Workflow (only on explicit ask)

Only branch/commit/PR when the developer explicitly asks in the same turn.

```bash
# Example (only if asked to commit)
git checkout -b translation/16-chronic-disease
# ... (add files, commit, PR as per github-pr-workflow)
```

### Branch naming: `translation/<chapter>-description`
### Commit message: `feat(translation): translate chapter <chapter>`

## 5. Watchdog for Long Translations

Use cron watchdog for multi-chapter translations:

```bash
# Create cron job (once per session)
cronjob_manage action=create name=htlb-translation-watchdog no_agent=true script=htlb-watchdog.sh schedule="30m"
```

The watchdog:
- Checks for stalled chapters (no writes for 40+ minutes)
- Reports completed chapters (all units translated)
- Silent when all is progressing normally

## Pitfalls

- Never infer permission to commit/branch/PR from "task done" — always require explicit ask in the same turn
- Always leave §TAG§ and §SRC§ placeholders intact in units — they are filled later by assemble.py
- Numbers must be byte-for-byte; never add or remove numbers from "Эффект"
- Field markers must be exact: 成本→Стоимость, 说人话→Простыми словами, etc.
- Do not translate sources — they are injected byte-by-byte by assemble.py
- Watchdog only reports when something is wrong or complete; silent during normal progress
- Load this skill before any translation work to ensure correct field markers and workflow

## Subagent Pitfall

- **Never let subagents spend time on analysis or planning** — they must write files immediately
- Each subagent gets one unit (not a whole chapter) and must write it to its file upon completion
- Do not let subagents study existing chapters for style — provide a style sample in the task instead
- Subagents must not return JSON summaries — only write the translated unit file
- If a subagent stalls, restart it with stricter instructions: 'work = write files, no analysis'

## Localization and Realia Handling

- **Legal/official identifiers**: Court case numbers (最高法知民终 51 号), document codes (国食药监办〔2010〕432 号), and other Chinese legal/administrative identifiers must be preserved byte-for-byte per TRANSLATION.md — they function like DOIs and are not translated
- **Emergency numbers**: When translating emergency service numbers (e.g. 120), add localization in parentheses: 'звоните 120 (для Китая — 112/103, для РФ — 103)'
- **Country-specific procedures**: Add translator's comments in brackets for procedures that vary by country: '[в Китае — процедура X, в РФ — процедура Y]'
- **Realia glossing**: For culturally specific terms, add translator's notes: '[в Китае: X — традиционная практика Y]'
- **Units and measurements**: Convert Chinese units to metric/Russian equivalents where appropriate (e.g. 'цзинь (≈500 г)', 'ли (≈500 м)')
- **See**: `references/localization-techniques.md` for complete catalog of 8 localization techniques with examples

## Source Title Retrofits

- **Chinese article/document titles**: Add Russian translation in brackets immediately after Chinese title: `中国人健康指南 [рус. «Руководство по здоровью китайцев»]`
- **Format**: `[рус. «…»]` for Russian, `[eng. "..."]` for English titles
- **Placement**: After Chinese title, before author/journal info or parentheses (for laws)
- **Preservation**: Original Chinese title, author names, journal names, DOIs, URLs, HTML tags, dates, and document codes remain byte-for-byte unchanged
- **Scope**: Only applies to source lines (starting with `- Источники:`), never to main text content
- **Verification**: After retrofit, verify that all source lines with Chinese titles have the annotation, while English-only source lines remain untouched
- **Batch processing**: Use balanced batches of 4-6 chapters per subagent to maintain speed and consistency

## Quality Assurance Techniques

- **Parallel subagent verification**: After translation wave, run verification subagents to check:
  - Natural Russian flow (avoid literal translation artifacts)
  - Consistent field marker usage across chapters
  - Proper localization annotations without over-annotation
  - Emergency numbers and procedures correctly localized
  - No untranslated Chinese terms outside sources
- **Verification workflow**: Use separate subagents for each quality aspect (natural language, localization consistency, field markers) with strict 'work = write reports' instruction
- **Verification scope**: Check 5 chapters at a time to maintain speed while catching systemic issues
- **Fix priority**: Natural language issues > localization consistency > field marker accuracy
- **Reference**: `references/natural-language-verification.md` for detailed verification instructions and quality standards
