# HTLB Subagent Instructions

## For Translation Subagents

**Task:** Translate one unit (not a whole chapter) immediately upon receiving it.

### Strict Instructions

- **Work = write files** — no analysis, no planning, no style study
- Write the translated unit to its file immediately upon completion
- Do not return JSON summaries — only write the file
- Do not study existing chapters for style — use the provided style sample in the task
- If you stall, restart with: 'work = write files, no analysis'

### Unit Translation Rules

| Chinese | Russian | Notes |
|---------|--------|-------|
| 成本 | Стоимость | Cost/expense field |
| 说人话 | Простыми словами | Simple language field |
| 收益 | Эффект | Benefit/effect field |
| 证据等级 | Уровень доказательности | Evidence level (A/B/C remain) |
| 备注 | Примечания | Notes/remarks field |

### Translation Constraints

- **Numbers**: Always byte-for-byte copy (§ numbers remain unchanged)
- **Slang**: Never translate: cohort/exposure/quartile/confounding/population/low-evidence
- **Style**: Live Russian, not literal translation
- **Headers**: Must start with verbs
- **Simple language field**: No numbers outside "Эффект" section
- **Exclamation marks**: None allowed
- **Sources**: Never translate — injected byte-by-byte by assemble.py

### File Structure

Each unit file must contain:
1. Chapter header (exact format per TRANSLATION.md)
2. Empty lines
3. Translated content with field markers
4. §TAG§ placeholder (on its own line)
5. §SRC§ placeholder (on its own line)

### Example Task Template

```
Translate unit /root/htlb-run/16/units/01.md

Use this style sample (from chapter 17):
- Стоимость: 0 юаней; заявление подаётся по месту жительства ребёнка
- Простыми словами: если ребёнок родился 1 января 2025 года или позже и проживает в Китае
- Эффект: план, изданный совместно Канцелярией ЦК КПК и Госсоветом
- Уровень доказательства: A
- Примечания: это единая для всей страны минимальная планка

Write result back to /root/htlb-run/16/units/01.md immediately. No analysis, no planning — just write.
```

## Pitfall

- **Never let subagents spend time on analysis or planning** — they must write files immediately
- Each subagent gets one unit (not a whole chapter) and must write it to its file upon completion
- Do not let subagents study existing chapters for style — provide a style sample in the task instead
- Subagents must not return JSON summaries — only write the translated unit file
- If a subagent stalls, restart it with stricter instructions: 'work = write files, no analysis'

## Unit-based QA (proven 2026-09-18)

Slice for checks too, not just for translation: QA of 316 source lines ran as 32 units (~10 line pairs each) over 8 parallel subagents — done in ~12 min vs 50+ min for whole-chapter batches, zero stalls. Recipe:
- Generate unit files containing ZH original + RU line pairs and a 3-point instruction header (translation correct / position correct / payload intact).
- Subagents are READ-ONLY: they write only verdict JSON (`{unit, checked, issues:[{file,line,problem}]}`), fixes are applied centrally by the orchestrator. Never let QA subagents edit book/ in a shared worktree.
- Verify verdict count == unit count before aggregating; aggregate issues in Python, not by hand.

### Verification-script gotchas (caused false mismatches)

- Strip insertions to compare payload with the original: `[рус. «…»]` titles may contain NESTED «…» quotes — strip from `' [рус. '` to the next `]`, not with a `[^»]*»` regex (nested-quotes lines fail otherwise, e.g. ch17).
- RU label is `- Источники:` with an optional trailing space (chapter-wide convention); ZH is `- 来源：` with none — normalize `^- Источники:\s?` vs `^- 来源：` before comparing, else every line 'differs'.
- Compare per-line after label strip, not whole-file; label bytes must not leak into the diff.

### English Translation QA (2026-09-18)

For English translation fidelity checks, use the same unit-based QA approach but with stricter number/meaning/term checks:
- Slice chapters into ~4-item units for parallel verification subagents
- Check every number/price/HR/RR/OR/CI/percentage/count/date in ZH body appears in EN with same value and role (万→numeric conversion is fine, 六成→60% is fine)
- Verify no dropped conditions, no added advice, no reversed logic, no softened hard claims, no invented facts
- Check 'In plain terms' contains no numbers beyond what ZH '说人话' has, is natural spoken English
- Ensure China-specific terms have transliteration + one-time gloss (dibao (低保 — ...))
- Confirm field labels are exactly `- Cost:`, `- In plain terms:`, `- Benefit:`, `- Evidence grade:`, `- Notes:`
- Flag any untranslated Chinese term in English body (except law/regulation references)
- TONE: no exclamation marks, no marketing language, restrained register
- Output verdict JSON (`{unit, verdict:PASS|FAIL, issues:[{item,type:...,zh,en,why}]}`), never edit files
- Use 10 parallel subagents, each assigned a group of 14-15 units; aggregate results programmatically

### QA Fix and Commit Protocol

When QA reveals defects:
- **Never edit book/ files directly** — always fix the source unit files in `/root/htlb-run-en/<chapter>/units/` and re-assemble
- **Fix pattern**: Find the problematic unit, correct the error in the unit file, then run `python3 tools/assemble_en.py <chapter> /root/htlb-run-en/<chapter> /tmp/<chapter>.md` and verify the diff matches only the intended fix
- **Unit sync**: After fixing book/ files, mirror the fix into the corresponding unit file to prevent reassembly regression (assemble.py overwrites units with the latest book/ content)
- **Commit message**: Format as `en QA fixes: <brief description>` (e.g., "万分之五 rate, dibao gloss, 轻伤二级 grade, non-epidural")
- **Push strategy**: Always push fixes immediately after verification — QA is not complete until fixes are committed and pushed to the branch
- **Verification after fix**: Re-run assembly and compare against the fixed book/ file expecting only the intended diff lines (counters/sources must remain byte-identical)

**Pitfall**: Direct editing of book/ files without updating units causes reassembly to clobber fixes. Always fix units first, then reassemble, then verify the diff is exactly what you intended.
