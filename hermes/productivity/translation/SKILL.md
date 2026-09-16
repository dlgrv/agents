---
name: translation
description: Use when translating books/docs or reviewing translations.
---

# Translation projects (LLM-translated books/docs, incl. upstream OSS contributions)

## Standing user preferences
- Translations must read naturally in the target language — NOT literal 1:1 ("не 1-в-1, а очень читаемым и приятным"). Functional equivalence over word-for-word; plain-language explainer lines (e.g. 说人话) must read as living speech, not calque.
- For upstream OSS: write to the author in THEIR language (Chinese author → Chinese issue), not the user's language.
- Verify structure with scripts, never by eye: item/heading/tag/DOI counts must match the source exactly.

## Procedure

1. **License & upstream first.** Check LICENSE (Unlicense/public domain = everything allowed), open issues, CONTRIBUTING.md. If the goal is upstreaming, open an issue in the author's language proposing the translation BEFORE translating. Fork; add `translation/<lang>` branches; add a language selector (links to the translations) at the top of the main README.
2. **Fix conventions BEFORE translating** — write a TRANSLATION.md into the fork (starter: `templates/TRANSLATION.md`):
   - Byte-faithful list: citation/source lines (translate ONLY the field label), DOIs, URLs, all numbers and units, machine-tag comments (e.g. `<!-- 成本标签: ... -->`), regulation titles + document numbers.
   - Field-label mapping table per target language.
   - Per-file header: status line ("Unofficial translation of …; in case of discrepancy the original prevails") + back-link — with the relative path RE-ADJUSTED for the new depth (`book/en/x.md` → root is `../../README.md`, not `../README.md`).
   - Country-context rule: facts true only for the source country are translated faithfully, never "fixed"; chapters citing that country's law get a one-line disclaimer under the heading.
3. **Delegate translation, verify centrally.** One subagent per language, dispatched in parallel (bulk I/O — keep the main context lean). Main agent verifies programmatically: heading/item counts, tag-comment counts, doi.org-line counts source vs translation, and zero untranslated text outside the byte-faithful zones.
4. **Review with the MQM rubric** (`references/quality-rubric.md`) via separate reviewer subagents: (a) fidelity/terminology against the source, (b) structure/links/conventions. Reviewer output must give concrete replacement wording, not "awkward".

## Pitfalls
- A subagent doing long-form generation (whole-chapter translation + JSON verdict) can burn the entire run on reasoning and never write the output file. Instruct translators to WRITE THE OUTPUT FILE FIRST (or per-chapter), then compose the summary/JSON.
- Trust grep, not the task statement, for source counts — stated counts have been wrong before; the binding constraint is translation == source.
- If a translation subagent dies or its output is rejected, the work is usually NOT lost: full transcripts persist under `~/.hermes/cache/delegation/` (`subagent-summary-*.txt`, `live/<delegation-id>/task-N.log`). Recover the drafted text from the cache and re-dispatch a small "assemble" agent pointing at the cache path — never retranslate from scratch.
- Preserving links ≠ preserving paths: keep link text/targets but re-adjust relative depth for the new file location; visible text of file-reference links stays as-is.

GitHub mechanics (fork, issues, PRs) → `github` skill.
