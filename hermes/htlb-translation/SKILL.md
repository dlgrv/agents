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
- Do not translate sources — they are injected byte-for-byte by assemble.py
- Watchdog only reports when something is wrong or complete; silent during normal progress
- Load this skill before any translation work to ensure correct field markers and workflow

## Subagent Pitfall

- **Never let subagents spend time on analysis or planning** — they must write files immediately
- Each subagent gets one unit (not a whole chapter) and must write it to its file upon completion
- Do not let subagents study existing chapters for style — provide a style sample in the task instead
- Subagents must not return JSON summaries — only write the translated unit file
- If a subagent stalls, restart it with stricter instructions: 'work = write files, no analysis'
