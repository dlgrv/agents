---
name: translation-chinese-to-russian
description: Chinese-to-Russian translation workflow with localization.
---

# Chinese to Russian translation workflow

## Standing user preferences
- Translations must read naturally in Russian — NOT literal 1:1 ("не 1-в-1, а очень читаемым и приятным"). Functional equivalence over word-for-word; plain-language explainer lines must read as living speech, not calque. The bar is flawless AND a pleasure to read — living-text readability is the primary criterion; formal pass scores are secondary.
- **Localization:** Replace Chinese-specific jargon with Russian equivalents (e.g., «когорта» → «группа»), adapt phrasing to Russian idioms, adjust file naming to Russian slugs.
- **Navigation:** In translated files, use `[← К общему оглавлению](../../README.ru.md)` for back-links (adjust depth if README.<lang> is nested). Chinese source files stay byte-identical — never alter upstream files.
- **README convention:** Create full README.ru.md with status line, language selector, all numbers/statistics byte-faithful, chapter links to Russian slugs.
- **Verify structure with scripts:** item/heading/tag/DOI counts must match the source exactly; no untranslated text outside byte-faithful zones.

## Procedure

1. **License & upstream first.** Check LICENSE (Unlicense/public domain = everything allowed), open issues, CONTRIBUTING.md. If upstreaming, open issue in Chinese proposing translation before starting. Fork; add `translation/ru` branch.
2. **README.ru.md creation:**
   - Status line: `> Неофициальный перевод файла [README.md](README.md). При расхождениях приоритет у китайского оригинала.`
   - Language selector: `**Языки / Languages:** [中文](README.md) · [Русский](README.ru.md)`
   - All numbers, statistics, structure byte-faithful (498, 323/126/49, 88/248/162…).
   - Chapter links → `book/ru/<russian-slug>.md`.
   - Badges recreate with Russian labels (URL-encode programmatically), same colors/numbers.
   - Anchors point to translated headings (#Оглавление, #Как-читать, etc.).
3. **File naming:** Rename `book/ru/` files to Russian slugs (e.g., `不要早死` → `01-Не-умирайте-рано.md`). Document naming rules in TRANSLATION.md.
4. **Fix conventions before translating:** Write TRANSLATION.md with:
   - Byte-faithful list: citation/source lines (translate ONLY field label), DOIs, URLs, all numbers, machine-tag comments.
   - Field-label mapping (来源→Источники, 成本→Затраты, 收益→Выгода, 证据等级→Уровень доказательности, 备注→Примечания).
   - Per-file header: status line + back-link with adjusted relative depth.
   - Country-context rule: facts true only for China are translated faithfully; law chapters get disclaimer.
5. **Delegate translation, verify centrally:** One subagent per chapter (bulk I/O). Main agent verifies programmatically: heading/item counts, tag-comment counts, doi.org-line counts, zero untranslated text outside byte-faithful zones.
6. **Review with MQM rubric:** Separate reviewer subagents for fidelity/terminology and structure/links. Apply all fixes centrally, re-run verification before committing.
7. **Ship:** Push `translation/ru` branch; open pilot PR titled bilingually (中文 + Русский); comment in Chinese linking PR.

## Pitfalls
- A subagent doing long-form generation can burn the run on reasoning and never write the output file. Instruct translators to WRITE THE OUTPUT FILE FIRST (or per-chapter), then compose the summary/JSON.
- Trust grep, not the task statement, for source counts — stated counts have been wrong before; binding constraint is translation == source.
- If a translation subagent dies, work is usually NOT lost: transcripts persist under `~/.hermes/cache/delegation/`. Recover and re-dispatch an "assemble" agent — never retranslate from scratch.
- Preserving links ≠ preserving paths: keep link text/targets but re-adjust relative depth for new file location.
- When byte-comparing citation lines, strip the field label AND leading whitespace first (source uses `：`, translation uses `:`).
- Sweep terminology fixes by grep on the STEM, not exact word — inflected forms hide leftovers; re-grep until stem count is zero.
- **Navigation consistency:** In `book/ru/` files, use `[← К общему огупление](../../README.ru.md)`; adjust depth if README.ru.md is nested.
- **README language selector:** Always include both original and translated: `**Языки / Languages:** [中文](README.md) · [Русский](README.ru.md)`.
- **Chinese-specific terms:** For Chinese legal/administrative terms (e.g., 认缴出资, 一裁终局), provide Russian translation + original in parentheses at first mention.

GitHub mechanics (fork, issues, PRs) → `github` skill.

## See also
- `translation` skill for general book/doc translation workflow
- `references/quality-rubric.md` for MQM-based review rubric
- `templates/TRANSLATION.md` for convention starter template
- `references/localization-rules.md` for Chinese-to-Russian localization specifics
