---
name: translation
description: Use when translating books/docs or reviewing translations.
---

# Translation projects (LLM-translated books/docs, incl. upstream OSS contributions)

## Standing user preferences
- Translations must read naturally in the target language — NOT literal 1:1 ("не 1-в-1, а очень читаемым и приятным"). Functional equivalence over word-for-word; plain-language explainer lines (e.g. 说人话) must read as living speech, not calque. The bar is flawless AND a pleasure to read — living-text readability is the primary criterion; formal pass scores are secondary.
- For upstream OSS: write to the author in THEIR language (Chinese author → Chinese issue), not the user's language.
- Verify structure with scripts, never by eye: item/heading/tag/DOI counts must match the source exactly.
- Book-scale batch runs execute on the server agent, not the Mac — the Mac is only for kickoff and collection; the user shuts the Mac mid-run and expects translation to continue.

## Procedure

1. **License & upstream first.** Check LICENSE (Unlicense/public domain = everything allowed), open issues, CONTRIBUTING.md. If the goal is upstreaming, open an issue in the author's language proposing the translation BEFORE translating. Fork; add `translation/<lang>` branches; add a language selector (links to the translations) at the top of the main README.
2. **Fix conventions BEFORE translating** — write a TRANSLATION.md into the fork (starter: `templates/TRANSLATION.md`):
   - Byte-faithful list: citation/source lines (translate ONLY the field label), DOIs, URLs, all numbers and units, machine-tag comments (e.g. `<!-- 成本标签: ... -->`), regulation titles + document numbers.
   - Field-label mapping table per target language.
   - Per-file header: status line ("Unofficial translation of …; in case of discrepancy the original prevails") + back-link — with the relative path RE-ADJUSTED for the new depth (`book/en/x.md` → root is `../../README.md`, not `../README.md`).
   - Country-context rule: facts true only for the source country are translated faithfully, never "fixed"; chapters citing that country's law get a one-line disclaimer under the heading.
   - Decide target-language filename slugs early and record them in TRANSLATION.md as a naming table; add localization wording rules (e.g. "no source-country jargon in body text") to TRANSLATION.md as they emerge, so reviewers can enforce them.
3. **Delegate translation, verify centrally.** One subagent per language, dispatched in parallel (bulk I/O — keep the main context lean). Main agent verifies programmatically: heading/item counts, tag-comment counts, doi.org-line counts source vs translation, and zero untranslated text outside the byte-faithful zones.
4. **Review with the MQM rubric** (`references/quality-rubric.md`) via separate reviewer subagents: (a) fidelity/terminology against the source, (b) structure/links/conventions. Reviewer output must give concrete replacement wording, not "awkward". Apply the reviewers' full fix list centrally (not only blockers), then re-run the scripted verification (counts + byte-identity) before committing.
5. **Ship the pilot.** Push every `translation/<lang>` branch; open ONE pilot PR for a single language, titled bilingually (author's language + English); comment on the upstream issue in the author's language linking the PR. Hold the other languages' PRs until the author confirms location and style — but keep their branches pushed and ready.
6. **Batch runs run headless on the server.** For whole-book translation the driver lives on the worker machine (user's server), not in the local session: per chapter `timeout 5400 hermes -z "<self-contained prompt>" --in <repo> --yolo`, launched as a systemd transient unit (`systemd-run --unit=<name> --collect /bin/bash <driver>.sh`) with an append-only START/DONE/FAIL log and a state file of done chapters so re-runs skip finished work. Full recipe: `references/server-pipeline.md`.

## Pitfalls
- A subagent doing long-form generation (whole-chapter translation + JSON verdict) can burn the entire run on reasoning and never write the output file. Instruct translators to WRITE THE OUTPUT FILE FIRST (or per-chapter), then compose the summary/JSON.
- Trust grep, not the task statement, for source counts — stated counts have been wrong before; the binding constraint is translation == source.
- If a translation subagent dies or its output is rejected, the work is usually NOT lost: full transcripts persist under `~/.hermes/cache/delegation/` (`subagent-summary-*.txt`, `live/<delegation-id>/task-N.log`). Recover the drafted text from the cache and re-dispatch a small "assemble" agent pointing at the cache path — never retranslate from scratch.
- Preserving links ≠ preserving paths: keep link text/targets but re-adjust relative depth for the new file location; visible text of file-reference links stays as-is.
- When byte-comparing citation lines source vs translation, strip the field label AND leading whitespace first (source uses `：`, the translation's label uses `:`); comparing raw colon-splits flags every line as a false diff.
- Sweep terminology fixes by grep on the STEM, not the exact word — inflected forms (especially Russian) hide leftovers in later items; re-grep until the stem count is zero.
- When verifying byte-faithful preservation (citation lines, DOIs, etc.), strip field labels and leading whitespace before comparison — source uses `：`, translation uses `:`; raw colon-split comparison creates false positives.
- Always run verification scripts BEFORE committing — manual counts are error-prone; grep the source for actual item/heading/tag/doi counts and match against translation, never trust stated counts.

## verify.py number-check fixes (HTLB)

When fixing number parsing in `tools/verify.py` (norm_numbers: thousands/decimal separators, scale words, ranges):

1. **A/B corpus diff is the gate, not unit tests.** Before editing, run verify across all `book/{ru,en,es}/*.md` chapters and save per-chapter FAIL/WARN counts; re-run and diff after the edit. Unit tests do not catch a rule that fixes one case but flips a real chapter from OK to FAIL — the corpus diff does (this caught an ES regression unit tests missed).
2. **Corpus census before ambiguity decisions.** For an ambiguous token form (comma-numbers like `1,134`), grep the corpus for that pattern's contexts per language — never decide from grammar intuition or copy a rule between language branches. Corpus facts: **ES body comma = decimal** (thousands use space «25 871»; comma-thousands occur only in «- Fuentes:» source-quote lines, which the number check excludes); **RU comma-groups = thousands** («1,040 человек», «44,573»; ratios use a dot «1.134»).
3. **Distributive ranges**: clone a scale word back to the range's first end («100,000 to 1 million») only when the bare ends are of compatible magnitude (same order); otherwise you fabricate phantom values.
4. **expectedFailure ledger**: adversarial agents file found-but-unfixed bugs as `@unittest.expectedFailure`; after fixing one, strip the marker from the now-passing tests in the same commit — leftover markers silently mask regressions.
5. **Verify delegated commits**: after a subagent reports done, check `git log`/`git status` yourself — they sometimes forget to commit.

GitHub mechanics (fork, issues, PRs) → `github` skill.
