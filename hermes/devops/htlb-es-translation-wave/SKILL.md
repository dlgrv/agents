---
name: htlb-es-translation-wave
description: Use for HTLB CN to ES translation waves and verify gates.
---

# HTLB ES translation waves

Workflow for batching CN→ES chapter translation via delegate_task (proven over 5 waves, 32 chapters + 4 docs).

## Per-wave procedure
1. Stage: copy `tools/digest/<CH>/units/*.md` → `/root/htlb-run-es/<CH>/units/`. Count units EXCLUDING `*.gloss.md` — briefs must state exact file range (00.md..NN.md); wrong counts caused subagents to poll for nonexistent files for 20 min.
2. Brief each subagent: translate-only role, FIRST tool call = write_file; field-label contract (`- Costo:` / `- En términos sencillos:` / `- Beneficio:` / `- Nivel de evidencia: A/B/C` / `- Notas:`); §TAG§/§SRC§ stay where they are; **forbid hand-inserted `<!-- 成本标签 -->` comments** (assembler injects via §TAG§; duplicates break the gate); chapter intro 00.md has NO markers — do not add them.
3. Never trust subagent self-checks — always run gates yourself:
   - `python3 tools/assemble_es.py <CH> /root/htlb-run-es/<CH> book/es/out-<CH>.md`
   - `python3 tools/verify.py <CH> --lang es --file book/es/out-<CH>.md`
   - verify needs the chapter in `book/` and `book/es/` dir to exist (mkdir -p book/es).
4. Final file = status line `> Unofficial translation of [book/<CN>.md](../<CN>.md)...` + body with first line `[← Volver al índice](../../README.md)`. Slug: Title-Case hyphenated Spanish, no accents (e.g. `02-No-Te-Dejes-Morir-Lentamente.md`).
5. README.es.md: replace EN slugs for translated chapters (questions table ~L39-48 AND numbered TOC ~L185-217). Search repo for the actual EN slug (`ls book/en/`) — guessing slugs caused MISSes.
6. Commit + `git push fork HEAD:translation/es-w1`.

## Verifier quirks (recurring FAIL causes)
- `norm_numbers` reads 千 inside 千克 as scale ×1000: CN «0.25 千克» → key «250». Fix like EN: add parenthetical gloss «0,25 kilogramos (250 gramos)».
- CN brackets with bare ratios «(351.3 / 610.6 ≈ 57.5%)» MUST keep their numbers in ES («351,3 / 610,6»), translators tend to drop them for «ambas cifras».
- CN regulatory doc IDs (国食药监办〔2010〕432号): hanzi not allowed in body → paraphrase issuing office + «(documento 〔2010〕 n.º 432)».
- Numbers must stay digits: «Treinta» → «30», «años noventa» → «años 1990»; never invent digits (8.03万 = exactly 80 300).
- WARN «numbers added/extra» are localization inserts — acceptable (RU/EN have more).

## Infra
- Watchdog `/root/.hermes/scripts/htlb-es-watchdog.py`: update LOGS dict per wave (delegation id + task-N per chapter), delete state file `/root/.hermes/cron/htlb-es-watchdog-state.json`, cron fires every 5m.
- Isolation: worktree checkout at /tmp/eswave for gating/commits; translated units live in /root/htlb-run-es/ (outside repo).
- docs/ long reads: no §TAG§/§SRC§, no field labels; mirror EN doc structure; CJK only in parenthetical glosses/links (EN keeps some too; docs have no hard verify gate).
