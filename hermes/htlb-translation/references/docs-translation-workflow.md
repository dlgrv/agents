# HTLB Documentation Articles Translation Guide

## Overview

Translate four long documentation articles referenced by chapters and README:
- 家庭应急装备清单 (Home Emergency Equipment List) — 2,458 hanzi, 89 lines
- 结婚划不划算 (Is Marriage Worth It) — 3,243 hanzi, 123 lines
- 遇到陌生人出事该不该停 (Should You Stop for Strangers in Trouble) — 1,825 hanzi, 55 lines
- 做平台要办哪些证 (What Licenses Are Needed to Launch a Platform) — 1,957 hanzi, 69 lines

## Workflow

### 1. Digest Phase

```bash
# Create digest for docs article
cd ~/github/htlb-ru
python3 tools/digest.py docs/家庭应急装备清单.md --units-dir /root/htlb-run/docs/家庭应急装备清单/units
```

Each unit contains:
- 5-10 lines of content
- Field markers (成本, 说人话, etc.)
- §TAG§ and §SRC§ placeholders

### 2. Unit Translation

Use 4 parallel subagents, one per article. Each subagent:
- Translates units immediately (no analysis)
- Writes to unit files upon completion
- Follows same field marker rules as chapters

### 3. Assembly

```bash
# Assemble translated docs
cd ~/github/htlb-ru
python3 tools/assemble.py /root/htlb-run/docs/家庭应急装备清单
python3 tools/assemble.py /root/htlb-run/docs/结婚划不划算
python3 tools/assemble.py /root/htlb-run/docs/遇到陌生人出事该不该停
python3 tools/assemble.py /root/htlb-run/docs/做平台要办哪些证
```

### 4. Integration

Update all chapter and README links:
- Remove `(на китайском)` annotations
- Change links from `docs/家庭应急装备清单.md` to `docs/ru/家庭应急装备清单.md`
- Update README.md to reference Russian docs versions

## Quality Control

- Apply same localization rules as main chapters
- Verify cross-references work correctly
- Check that no Chinese text remains outside sources
- Run unit-based QA on critical sections

## Pitfalls

- **Don't skip**: These are the only remaining Chinese content and actively referenced
- **Small units**: Use 5-10 line units for docs (vs 20-50 for chapters) due to shorter length
- **Link updates**: Must update all references in chapters and README after translation
- **Consistency**: Apply same field markers and localization techniques as main corpus
