---
name: htlb-es-translation
description: HTLB Spanish translation workflow and conventions.
---

# HowToLiveBetter Spanish translation (HTLB ES)

## Standing user preferences
- Translations must read naturally in international Spanish (es-419-compatible), no regional slang, no exclamation marks, live prose not calque. Functional equivalence over word-for-word; plain-language explainer lines (说人话) must read as living speech, not calque.
- Field labels: 成本 → `- Costo: `, 说人话 → `- En términos sencillos: `, 收益 → `- Beneficio: `, 证据等级 → `- Nivel de evidencia: A/B/C`, 备注 → `- Notas: ` (keep the grade letter A/B/C unchanged).
- **Regulatory document IDs**: CN hanzi (e.g. 国食药监办〔2010〕432号) must be paraphrased in Spanish with the issuing office name + "(documento 〔2010〕 n.º 432)" pattern per the EN translation; never keep hanzi in body text (except in citation lines, which are byte-faithful).
- Numbers: digits with ES style (space thousands, decimal comma); 万→×10 000 written out; never round or invent. Unit-weight figures (e.g. 0.25 千克) require parenthetical gloss with absolute value (e.g. "0,25 kilogramos (250 gramos)") due to verifier quirk.
- Chapter intros: translate back-link → `[← Volver al índice](../README.md)`; the `# N. ...` heading (keep the number); intro paragraph. No §TAG§/§SRC§ markers in intros.
- Units: 元 → yuanes; keep mmHg, mg, %, °C as-is.
- **Number formatting**: ES uses space as thousands separator (142 740) and comma as decimal (0,001); never use comma as thousands separator (e.g. 142,740 is incorrect).

## Procedure

1. **Stage chapter 32 and docs** if missing:
   - Chapter 32: 12 units in `/root/htlb-run-es/32/units/` (00.md intro, 01-11.md units)
   - Standalone docs: `/root/htlb-run-es/docs/` (Home-Emergency-Kit.md, What-Licenses-A-Platform-Needs.md, Should-You-Stop-To-Help-A-Stranger.md, Is-Marriage-Worth-It.md)
2. **Delegate translation** — one subagent per chapter (25-31), one for ch32, one for docs (4 files). Each subagent follows strict unit translation rules (see below).
3. **Verify with assemble.py + verify.py**:
   - `python3 tools/assemble_es.py <chapter> /root/htlb-run-es/<chapter> book/es/out-<chapter>.md`
   - `python3 tools/verify.py <chapter> --lang es --file book/es/out-<chapter>.md`
   - Verify: assemble byte-identical, verify OK (numbers lost=0, no extra items)
4. **Deploy to book/es/**:
   - For chapters: copy `book/es/out-<chapter>.md` to `book/es/<slug>.md` with status line and adjusted back-link
   - For docs: copy staged files to `book/es/docs/` with status line and adjusted relative paths
   - Update README.es.md with ES slugs
5. **Commit and push** to `fork/translation/es-w1` branch

## Unit translation rules (for chapters only)

- Field labels: 成本 → `- Costo: `, 说人话 → `- En términos sencillos: `, etc.
- Keep the line `§TAG§` and the line `§SRC§` EXACTLY where they are (§TAG§ right after the heading, §SRC§ as the last content line). Never translate, move, or DUPLICATE them.
- Do NOT translate source/citation lines — if a unit contains a `- 来源：...` line, replace it with just the `§SRC§` marker line (marker must be the last content line).
- Keep the HTML comment `<!-- 成本标签: ... -->` byte-identical IF the source unit already has one.
- Keep markdown structure: `### N. ...` keeps its number; list-item order unchanged; no new headings.
- Chapter intro 00.md: translate back-link → `[← Volver al índice](../README.md)`, the `# N. ...` heading, and the intro paragraph. No §TAG§/§SRC§ markers.
- **Number preservation**: All numeric values must match source exactly; ES formatting applies only to display (142 740 not 142,740; 0,001 not 0.001).

## Doc translation rules (standalone docs)

- Line 1: `> Unofficial translation of [docs/<CN-filename>.md](../<CN-filename>.md). In case of discrepancies the Chinese original takes precedence.`
- Keep the same heading structure, table columns, and section order as EN; tables keep row order.
- Numbers: digits with ES style (space thousands, decimal comma); 万→×10 000 written out; never round or invent.
- Law/regulation names: Spanish paraphrase, no hanzi in body text; hanzi only in parenthetical glosses where EN keeps them.
- Style: neutral international Spanish, no exclamations, live prose; links and URLs kept verbatim.
- 元 → yuanes.
- **Number formatting**: ES uses space as thousands separator (142 740) and comma as decimal (0,001); never use comma as thousands separator (e.g. 142,740 is incorrect).

## Pitfalls
- **Regulatory document ID translation**: CN hanzi in body text (e.g. in Notas fields) must be manually replaced with office paraphrase + "(documento 〔2010〕 n.º 432)" per EN pattern. This is a byte-faithfulness override for regulatory IDs only; other byte-faithful zones (citation lines, DOIs) must remain untouched.
- **Unit-weight figures**: CN «0.25 千克» must become «0,25 kilogramos (250 gramos)» due to verifier quirk — the 千 inside 千克 is read as a scale word and folds to key 250, so the absolute value in parentheses is required.
- **Never insert `<!-- 成本标签 ... -->` comment lines into units** — the assembler injects them via §TAG§; a hand-inserted copy breaks the gate.
- **GitHub counter reset**: Use `git merge -s ours upstream/main --allow-unrelated-histories` to set "behind: 0". Records upstream history as ancestor without changing files; future "behind" shows actual new commits. Document in `docs/upstream-sync.md` as one-time history anchor.
- **Verify counts with grep, not stated counts**: grep the source for actual item/heading/tag/doi counts and match against translation, never trust stated counts.
- **Merge conflicts**: When pulling upstream/main (e.g. to sync with new chapters or infrastructure), use `git merge --allow-unrelated-histories origin/main`. Resolve conflicts in wrapper files (README.md, index.html, og.png) by preferring the fork's version (EN wrapper), but adopt upstream's EPUB link and Spanish language addition if present. Never merge upstream's Chinese content into the fork's English wrapper.
- **README language addition**: When upstream adds new languages, update README.md to include the new language row using the pattern: `🇪🇸 Español → read on the site` (pointing to the site, not the repo). If upstream already added EN/RU, match their format (short link names, repo link at end).
- **CI gate removal**: If upstream CI workflows are specific to their README structure (e.g., epub-workflow tied to Chinese README), remove them from the fork's main branch to avoid failures. The fork's CI should only contain infrastructure needed for the English wrapper and translations.
- **Relative link convention**: Use `../../docs/es/<slug>.md` for chapter links to docs/es/ files, and `../<CN-original>.md` for docs/es/ backlinks to CN originals, matching the repo's RU link convention.
- **Check links locally**: Run `python3 tools/check_links.py` and `python3 tools/check_content.py` before committing to catch broken relative links or content parity issues.
- **Squash-merge PRs**: Use `gh pr merge --squash` with descriptive subject and body for translation PRs to maintain clean main branch history.
- **Site display regex**: If website displays empty fields (e.g. 'Fuentes (0)' or blank Costo/Beneficio cards), the regex in `index.html` parseReadme is missing Spanish field labels. Add ES alternatives to all regex patterns: `Costo|Cost` (not just `Cost`), `Beneficio|Benefit` (not just `Benefit`), etc. Test regex with `python3 -c "import re; md=open('book/es/out-<chapter>.md').read(); print(len(re.findall(r'- (?:成本|Стоимость|Costo|Cost)[：:](.*)', md)))"` to verify all 528 entries are parsed.
- **Banner image alt**: README.es.md must reference `og-es.png` (not og-en.png) with Spanish alt text describing the banner content (e.g. "cambia menos dinero, tiempo y esfuerzo por más vida, dinero y libertad personal"). Regenerate `tools/og-es.html` with translated text, then render with Playwright for final PNG.
- **Regenerate language pages after parser fix**: When fixing site parser regexes (e.g. adding Spanish field labels to parseReadme), **always run `python3 tools/build_pages.py`** after updating `index.html`. This copies the fixed parser to `es/index.html`, `en/index.html`, `ru/index.html`, `zh/index.html`, and `v1/*`. Without this step, users see old parser in `/es/` and translation cards display empty fields. Commit all regenerated pages together with the parser fix.
- **Stop cron watchdogs before MR**: Before submitting PRs or merging, pause cron jobs (e.g. `hermes cron pause <job-id>`) to prevent automatic runs that may overwrite local changes or cause conflicts. Use `hermes cron list` to find job IDs and `hermes cron resume <job-id>` to restore. **Double-check: run `hermes cron list` again to confirm paused**.
- **Branch cleanup after PR merge**: When translation branches are merged, immediately delete local and remote branches to avoid clutter and prevent accidental work on stale branches. Use `git branch -D <branch>` and `git push fork --delete <branch>` — branches with merged PRs are safe to delete, and stale branches cause confusion when reactivating old work. Verify deletion with `git branch` and `git ls-remote --heads fork`.

## Verification checklist

- assemble.py: byte-identical to source
- verify.py: headings=8 tags=8 sources=8 numbers=X (lost=0, extra=Y)
- No source-language text outside byte-faithful zones
- Regulatory IDs paraphrased in body text (not hanzi)
- Numbers in ES style (space thousands, decimal comma)
- Field labels correctly mapped
- Status line and back-link present and correctly adjusted
- **Upstream sync**: When merging upstream/main, keep fork's English wrapper, adopt EPUB link/Spanish if present, never merge Chinese content
- **Regex coverage**: After deploying Spanish translation, verify all 528 entries parse correctly by running `python3 -c "import re; md=open('book/es/out-<chapter>.md').read(); print(len(re.findall(r'- (?:成本|Стоимость|Costo|Cost)[：:](.*)', md)))"` — must return 528
- **Banner alt**: Confirm README.es.md references `og-es.png` with Spanish alt text; verify no Chinese text remains in `tools/og-es.html` before rendering

## References

- [server-pipeline.md](../translation/references/server-pipeline.md) — batch execution on server
- [quality-rubric.md](../translation/references/quality-rubric.md) — MQM-based review
- [TRANSLATION.md](../translation/templates/TRANSLATION.md) — general translation conventions template
- [es-number-style.md](references/es-number-style.md) — Spanish number formatting rules
- [es-regulatory-ids.md](references/es-regulatory-ids.md) — regulatory document ID translation pattern
- [upstream-sync.md](references/upstream-sync.md) — upstream sync procedure for infrastructure
- [ci-gate-removal.md](references/ci-gate-removal.md) — CI workflow cleanup for upstream-specific infrastructure
- [build-pages-procedure.md](references/build-pages-procedure.md) — regenerate language pages after parser fixes
- [cron-workflow.md](references/cron-workflow.md) — pause cron jobs before PR work to prevent conflicts
