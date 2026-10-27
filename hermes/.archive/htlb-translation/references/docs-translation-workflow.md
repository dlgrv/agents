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
cd ~/github/HowToLiveBetter
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
cd ~/github/HowToLiveBetter
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

### Gates for docs long reads (2026-09-21, EN wave lessons)

- **verify.py false-FAILs on docs articles**: its CJK whitelist is calibrated for chapter cards (CJK legal only in source lines/glosses), while long reads cite regulation titles 《…》 with glosses in body text and tables. Classify every CJK token with a script (《titles》, (CJK (translit — gloss)) parentheticals, source lines, header link) — if all classified, the FAIL is a known false positive, not a blocker.
- **Link gate must resolve relative paths FROM THE FILE** (`os.path.join(dirname(file), target)`), never from repo root — otherwise broken paths from subfolders (docs/en/ → `../核实记录/…`) pass the check. An independent review caught exactly this bug (docs/en/做平台要办哪些证.md copied a CN link verbatim) that the root-based gate had missed.
- **Pass E for articles**: judge subagent per article (prompt = tools/prompts/judge-factcheck.md; recover from commit a791033 if missing) → strict JSON verdict → run through tools/validate/factcheck.py --stdin-verdict (grounding gate, cn_span verbatim). 4/4 grounded:true, 72 assertions, 0 issues on the EN wave.
- **Number gate**: every number in CN must appear in EN as-is or as a legal conversion (万=10,000 → million, 亿=100,000,000); "598 checks / 13 diffs" were all legal conversions (610.6万→6.106M etc.).
- **Sweep all chapters after relinking**: the EN wave fixed `../README.md`→`../../README.md` back-links only in the 5 touched chapters; review found 27 more chapters with the same pre-existing broken links. Fix the pattern repo-wide in one commit, not per-chapter.
- **Automated gates (2026-09-21, wired into .github/workflows/check-links.yml on every PR/push to main)**: `tools/check_links.py` (relative links resolved FROM THE FILE, scope root/book/docs, code fences skipped) and `tools/check_content.py` (CJK-leak classifier + CJK-free filenames in book|docs/{en,ru} + tri-language parity 01–32 + badge stats 528/347/1066 recomputed from book/*.md). CJK-leak calibration method: run → classify every hit (gloss 《》-title, source bullet, doc-ID 〔…〕号, quoted term) → either fix the TEXT (real leak) or extend the narrowest regex; rule ORDER matters (specific title-idiom rules before generic CJK+paren).

## Pitfalls

- **Don't skip**: These are the only remaining Chinese content and actively referenced
- **Small units**: Use 5-10 line units for docs (vs 20-50 for chapters) due to shorter length
- **Link updates**: Must update all references in chapters and README after translation
- **Consistency**: Apply same field markers and localization techniques as main corpus
