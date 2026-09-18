---
name: chinese-to-russian-book-translation
description: Chinese books to Russian with localization.
tags: [translation, chinese, russian, localization]
---

# Chinese-to-Russian book translation with localization

## Standing user preferences
- Translations must read naturally in Russian — NOT literal 1:1 ("не 1-в-1, а очень читаемым и приятным"). Functional equivalence over word-for-word; plain-language explainer lines (e.g. "Простыми словами:") must read as living speech, not calque.
- Verify structure with scripts, never by eye: item/heading/tag/DOI counts must match the source exactly.
- Batch runs execute on the server agent, not the local Mac — the Mac is only for kickoff and collection.
- Localization required: country-specific facts (emergency numbers, government agencies, legal terms) must be adapted with functional equivalents or marked as source-specific.
- Review with MQM rubric: focus on accuracy, terminology, and fluency (especially bureaucratic calques in Russian).
- Apply ALL reviewer fixes, not only blockers; re-verify after each batch of edits.

## Procedure

1. **License & upstream first.** Check LICENSE, open issues, fork. If upstreaming, propose translation in Chinese to the author.
2. **Set up conventions:**
   - Write TRANSLATION.md with field-label mapping, byte-faithful zones, and localization rules.
   - Decide Russian filename slugs early and record in TRANSLATION.md.
   - Add status lines and back-links with re-adjusted relative depth.
3. **Delegate translation:** One subagent per chapter, parallel dispatch. Verify programmatically: heading/item counts, tag-comment counts, doi-line counts, byte-identity of source lines, zero Chinese text outside allowed zones.
4. **Localize country-specific facts:**
   - Emergency numbers: 120 → 103/112, 119 → 101, 110 → 102
   - Government agencies: 民政 → органы соцзащиты, 卫健委 → Минздрав
   - Legal terms: 低保 → дибао (with gloss), 兵役法 → закон о воинской обязанности
   - Add "Примечание переводчика:" block notes for country-specific chapters.
5. **Review with MQM rubric:** Separate reviewer subagents for fidelity/terminology and structure/conventions. Apply ALL suggested fixes centrally.
6. **Verify after each batch:** Run verification scripts after localization and naturalness edits to ensure counts and byte-identity are preserved.
7. **Commit and push:** One commit per batch, descriptive messages.

## Localization techniques

See `references/localization-techniques.md` for the full catalog:
- Functional equivalents (primary)
- Transcription + gloss
- Functional equivalent + translator's note
- Source-country fact with disclaimer
- Glossary entries
- Block-quote notes in chapter headers

## Pitfalls
- **Translation subagent burnout:** A subagent doing long-form generation can burn the entire run on reasoning and never write the output file. Instruct translators to WRITE THE OUTPUT FILE FIRST.
- **Never trust stated counts** — grep the actual files for source counts; stated counts have been wrong before.
- **Cache recovery:** If a translation subagent dies, recover from cache: transcripts persist under `~/.hermes/cache/delegation/`.
- **Citation byte-comparison:** When comparing citation lines, strip field labels and leading whitespace first (source uses `：`, translation uses `:`).
- **Terminology sweep:** Fix terminology by grep on the STEM, not the exact word — inflected forms hide leftovers.
- **Pre-commit verification:** Always run verification scripts BEFORE committing — manual counts are error-prone.
- **No agent conflicts:** Never merge conflicting edits from multiple agents: verify that a chapter is fully done before merging.
- **Apply all reviewer fixes:** During review phases, apply ALL suggested fixes from reviewers, not only blockers.
- **Exact patching:** When applying reviewer fixes, use patch with exact string matching: adapt only the exact quoted string.
- **Post-edit verification:** After any batch of edits, run verification scripts again: reviewer edits can accidentally alter structure.
- **Bureaucratic calques:** For Chinese-to-Russian translation, calques of Chinese bureaucratic phrasing are common — use MQM fluency dimension to identify and fix these.
- **'Простыми словами' naturalness:** Check specifically for calques in the 'Простыми словами' field: these must read as natural Russian speech.
- **Numeric preservation:** Always verify that numeric values and statistical terms (HR/RR/OR/CI) are unchanged after applying edits.
- **Unit-based QA for retrofits:** When checking inserted [рус. «…»] in source lines, split large batches into units of 10–15 lines per subagent. Whole-chapter checks are slow (50+ minutes) and prone to timeout; unit-based QA completes in 1–3 minutes per unit. Subagents must write only JSON verdicts — no file edits — to avoid conflicts in shared worktrees.
- **QA verdict workflow:** After subagent reports, aggregate issues centrally and fix using exact string matching with patch. Never let multiple agents write to the same files during QA.
- **CJK punctuation artifacts:** Watch for stray Chinese punctuation in translated text (e.g. `，` instead of `,` or `… …` instead of `…`). Use regex to scan for these patterns and replace them with proper Russian equivalents.
- **Double ellipsis fix:** Loading status text may contain `… …` due to copy-paste artifacts from animated elements. Replace with single `…` and check CSS for ::after animations that could reintroduce the issue.
- **Layout sync:** After text updates, re-check CSS for layout issues like misaligned headings (flexbox wrapping, text overflow) — Russian text is longer and may break responsive layouts.
- **Propagation delay:** After pushing commits, wait 50+ seconds for GitHub Pages propagation before verifying live site changes; use `curl -s <url> | grep -o 'text pattern'` to confirm fixes.

## English translation extension

This workflow has been extended for Chinese-to-English translation (HowToLiveBetter EN project):

- **Prompt engineering:** Use a strict 'one unit per step' loop with immediate file writing. First tool call must be `write_file` of the translated unit.
- **Conventions in prompt:** Embed all translation rules inline in the prompt (never reference external files). Include specific field mappings (成本→`- Cost:`, 说人话→`- In plain terms:`, etc.), byte-faithful requirements, and explicit warnings against invented facts.
- **Watchdog automation:** Deploy a cron-based watchdog to monitor delegation logs every 3 minutes and alert if any subagent stalls for ≥6 minutes.
- **Parallel wave dispatch:** Launch chapters in waves (e.g. 5 chapters per batch) with identical prompts and concurrent watchdog monitoring.
- **QA automation:** After assembly, verify: heading/item/tag/DOI counts, source line byte-identity, zero CJK outside machine zones (allowed: link targets, §TAG§/§SRC§ placeholders).
- **Commit strategy:** One commit per completed chapter with descriptive message including verification status (e.g. 'tags/sources byte-identical').
- **Progress tracking:** Maintain a running tally of completed chapters and use delegate_task status queries to monitor active waves.

### English-specific pitfalls
- **Model timeout:** Translation subagents may timeout on long chapters (e.g. ch13 took 3 attempts). Retry with identical prompt + shorter timeout (e.g. 1000s).
- **CJK in output:** The only allowed CJK outside machine zones is byte-identical link targets (e.g. `../docs/遇到陌生人出事该不该停.md`). All other CJK indicates a translation error.
- **Slug convention:** English filenames use kebab-case (e.g. `13-Emergencies.md`), not Chinese characters or pinyin.
- **Status line translation:** Translate visible text in status lines and back-links; keep link targets byte-identical to source.

## Verification checklist

- [ ] Heading count matches source
- [ ] Item count matches source
- [ ] Tag-comment count matches source
- [ ] DOI-line count matches source
- [ ] Source lines are byte-identical (after field label strip)
- [ ] No Chinese text outside allowed zones
- [ ] Emergency numbers and agencies localized
- [ ] Glosses added for recurring terms
- [ ] Block notes for country-specific chapters
- [ ] All reviewer fixes applied
- [ ] Counts preserved after final edits

## References

- MQM quality rubric: `../translation/references/quality-rubric.md`
- Localization techniques: `references/localization-techniques.md`
- Retrofit QA workflow: `references/retrofit-qa.md`
- Server pipeline: `../translation/references/server-pipeline.md`
- Website deployment: `references/website-deployment.md`
- English translation workflow: `references/english-translation-workflow.md`
- TRANSLATION.md template: `../translation/templates/TRANSLATION.md`

## Scripts

- English translation watchdog: `scripts/htlb-en-watchdog.py`