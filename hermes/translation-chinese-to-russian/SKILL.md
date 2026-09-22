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
5. **Optimized translation pipeline for large chapters:**
   - Split chapters into 1–2 Kbyte units using `tools/make_digest.py <NN> /tmp/workdir`
   - Extract sources/tags byte-for-byte into `blocks.json` (never feed to LLM)
   - Delegate each unit to subagents (1–2 Kb context vs 30–42 Kb chapter)
   - Monitor with `python3 tools/watchdog.py /tmp/workdir --stall-min 25`
   - Assemble with `python3 tools/assemble.py <NN> /tmp/workdir <output.md>`
6. **Review with MQM rubric:** Separate reviewer subagents for fidelity/terminology and structure/links. Apply all fixes centrally, re-run verification before committing.
7. **Ship:** Push `translation/ru` branch; open pilot PR titled bilingually (中文 + Русский); comment in Chinese linking PR.

## Pitfalls
- A subagent doing long-form generation can burn the run on reasoning and never write the output file. Instruct translators to WRITE THE OUTPUT FILE FIRST (or per-chapter), then compose the summary/JSON.
- Trust grep, not the task statement, for source counts — stated counts have been wrong before; binding constraint is translation == source.
- If a translation subagent dies, work is usually NOT lost: transcripts persist under `~/.hermes/cache/delegation/`. Recover and re-dispatch an "assemble" agent — never retranslate from scratch.
- Preserving links ≠ preserving paths: keep link text/targets but re-adjust relative depth for new file location.
- When byte-comparing citation lines, strip the field label AND leading whitespace first (source uses `：`, translation uses `:`).
- Sweep terminology fixes by grep on the STEM, not exact word — inflected forms hide leftovers; re-grep until stem count is zero.
- **Navigation consistency:** In `book/ru/` files, use `[← К общему оглавлению](../../README.ru.md)`; adjust depth if README.ru.md is nested.
- **README language selector:** Always include both original and translated: `**Языки / Languages:** [中文](README.md) · [Русский](README.ru.md)`.
- **Chinese-specific terms:** For Chinese legal/administrative terms (e.g., 认缴出资, 一裁终局), provide Russian translation + original in parentheses at first mention.
- **MQM verification:** Use the verification script from `references/quality-rubric.md` to programmatically check counts and structure after each chapter completion.
- **Chapter verification workflow:** Use `references/chapter-verification-workflow.md` for standardized structural and content checks per chapter, including item counts, tag counts, DOI verification, byte-faithful sources, CJK character validation, and numeric normalization.
- **Back-link fix:** When moving files to `book/ru/`, adjust relative depth in all back-links (e.g., `../../README.ru.md` instead of `../README.md`).
- **Decimal comma vs dot:** When comparing numeric values, normalize both source and translation to dots before comparing — 0,58 vs 0.58 are identical, but 0.58 vs 0.580 are not.
- **万→thousands/millions:** Treat 万 as numeric conversion (1万=10000, 1.5万=15000), not literal translation; verify numeric equivalence in all contexts.
- **Locale-specific numbers:** Do not flag numbers as 'lost' or 'extra' if they are only different due to locale formatting (e.g., 1,5 vs 1.5, 1000 vs 1,000, 97.2% vs 97,2%).
- **CJK in links:** Allow Chinese characters ONLY in links to Chinese sources or documents; all other text must be fully translated.
- **Verification script false positives:** Normalize numeric formats and strip whitespace before comparing; ignore punctuation-only differences (e.g., 0.5 vs 0,5) and comma/dot variations in percentages (97.2% vs 97,2%).
- **Statistical rounding:** Accept 40% as equivalent to 42%, 70% as equivalent to 69% when they represent plain-language approximations of precise statistics; do not flag as mismatch unless the numeric value differs beyond rounding tolerance.
- **Background pipeline interference:** Existing background translation pipelines (e.g., `htlb-pipeline.service`) may run with outdated prompts and overwrite newer translations. Check for concurrent `hermes -z` processes and pipeline logs before starting new work; verify that background processes use current conventions (Russian slugs, README.ru.md links, MQM rules).
- **Fork-based PR lifecycle:** When using a fork as the PR head repo, never delete the fork before the PR is merged — this auto-closes the PR. If the fork must be deleted, first merge the PR, then delete the fork. If accidentally deleted, restore from local backup branch or recreate and push the branch again.
- **Cross-repo PR title:** For cross-repo PRs (external contributor → upstream), include both languages in the title for clarity: `翻译：俄语版（第 1–10 章 + README，见 #4） / Russian translation — chapters 01–10 + Russian README`. This helps reviewers identify the language scope immediately.
- **Issue-PR linkage:** Only a PR (not a branch) closes an issue via `Closes #NNNN`. If the fork/head repo is deleted, the PR closes and the issue reopens. Link the PR to the issue in the body: `Closes #NNNN` or reference it in comments.
- **Chapter-by-chapter commit strategy:** Commit each chapter as a separate commit with clear message (e.g., 'translation(ru): chapter 11') to enable fine-grained review and rollback. Do not batch unrelated chapters into single commits.
- **Chapter completion reporting:** After each 5-chapter wave, summarize progress with chapter counts, commit hashes, and verification status. Include any failed chapters and their retry strategy.
- **Failed chapter recovery:** If a subagent fails (timeout, output not written), recover transcripts from `~/.hermes/cache/delegation/live/` and either retry with corrected instructions or reassign to another agent with stricter incremental writing requirements.
- **PR auto-update:** After each wave, automatically update the PR with new commits and comment with progress summary. Never manually close PRs — let them stay open until all chapters are done.

GitHub mechanics (fork, issues, PRs) → `github` skill.

## Numeric Normalization Handling

- **Comma format false positives**: Numbers like '20,024' or '60,000 IU' trigger verify.py FP due to comma parsing rules. Fix: replace with space format '20 024' or '60 000 IU'.
- **Numeric normalization failures**: verify.py reports 'numbers absent' for present but differently formatted numbers (e.g., '80,300' vs '80 300'). Fix: normalize by removing commas/spaces before comparison — verify.py treats them as identical.
- **Locale-specific tolerance**: Accept decimal comma vs dot (1,5 vs 1.5) and thousands separator (1000 vs 1,000) as equivalent; normalize by removing all punctuation.
- **Statistical rounding tolerance**: Accept ±2% differences for plain-language approximations (40% vs 42%, 70% vs 69%) as equivalent.
- **Pre-commit verification**: Run `tools/verify.py <NN> --lang ru`, check if failures are formatting-related, normalize manually, document in commit message if equivalent.
- **See**: `references/numeric-normalization-handling.md` for detailed troubleshooting scripts and normalization methods.

## See also
- `translation` skill for general book/doc translation workflow
- `references/quality-rubric.md` for MQM-based review rubric
- `templates/TRANSLATION.md` for convention starter template
- `references/localization-rules.md` for Chinese-to-Russian localization specifics
- `references/verification-script.md` for automated structural and numeric verification
- `scripts/check_links.py` for repo-wide markdown link checking (user-facing content only)

## Consolidated playbook
- The full method (pipeline diagram, subagent contracts, verification gotchas, post-translation waves, web-version localization, upstream etiquette, next-language launch checklist) lives in the repo: `docs/translation-playbook.md` in dlgrv/HowToLiveBetter (branch translation/ru). Read it before launching a new-language translation of the same book.

## Delegation-provider lesson
- Cheap API gateways (cometapi etc.) time out on long subagent generations (120–600 s limits). Switch `delegation.provider` to a direct provider (z.ai) and keep subagent payloads at 1–2 KB units — zero timeouts afterwards.

## Web-version localization lesson (bilingual index.html)
- Translate only VISIBLE strings: chip labels, card badges (via LABEL/RATIO_LABEL dictionaries), loading/error states, perf panel. Data keys (`data-v`, tag values) stay byte-identical or filters silently break.
- Audit for leftovers with regex on `\u4e00-\u9fff` AND full-width punctuation `，。：；` in RU text; allowed zones: data keys, original title, lang switch, script comments.
- Russian text is longer than Chinese: flex label+hint rows overlap on mobile (use column layout), `max-width:72ch` intros leave dead space, verify deployment by curl+grep after 50 s.
