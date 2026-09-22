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

## Source verification and fact-checking

When working with translated content, especially in domains like health, safety, and finance, verify all claims against authoritative sources:

### Verification workflow

1. **Identify TODO flags** — Look for «待核实»/TODO markers in source text
2. **Prioritize by impact** — Focus on safety-critical claims (medical, emergency, financial) first
3. **Use authoritative sources** — Prefer primary sources (CDC, WHO, S&P, official PDFs)
4. **Capture exact citations** — Include direct quotes from source pages
5. **Cross-check with secondary sources** — Use Wayback/WARCs when live sites block access
6. **Update sources section** — Replace TODO with full citation including DOI/URL

### Source verification protocol

**Step 1: Identify and categorize TODO markers**
- Scan for «待核实»/TODO flags in source text
- Categorize by priority (see table below)
- Focus first on safety-critical claims (medical, emergency, financial)

**Step 2: Source lookup and citation extraction**
- Use exact-match search for the claim in official sources
- Capture direct quotes from source pages/PDFs
- Preserve original phrasing and punctuation
- Include full citation with DOI/URL and access date

**Step 3: Cross-verification**
- Use Wayback snapshots if WAF blocks live sites
- Cross-check DOI metadata with Crossref API
- Verify PDF text extraction matches claimed content
- Ensure multiple sources agree on key facts

**Step 4: Source replacement**
- Replace TODO with full citation including exact quote
- Update evidence等级 (C→B for verified sources)
- Remove «待核实» marker
- For author experience claims (作者经验), keep with disclaimer

### Source types by priority

| Priority | Source type | Examples | Handling | Verification method |
|---------|-------------|----------|----------|-------------------|
| **Critical** | Health/safety agencies | CDC, WHO, NPS, CPSC | Replace TODO with exact citation | Wayback if WAF blocked |
| **High** | Financial/statistical | S&P, CNNIC, official PDFs | Replace TODO with official data | Crossref/PDF text extraction |
| **Medium** | Industry standards | NFPA, ERC, AAP | Replace with official guidance | Archive.org lookup |
| **Low** | Author experience | Marked as 作者经验 | Keep as is, add disclaimer | None needed |

### Verification commands

```bash
# Wayback snapshot for WAF-blocked sites
python3 -c "import urllib.request, re; t = urllib.request.urlopen(...).read().decode('utf-8'); print(re.search(r'65%', t).group())"

# Crossref DOI lookup
curl -s "https://api.crossref.org/works/10.1111/j.1540-6261.2010.01598.x" | jq '.message.title[0]'

# PDF text extraction
pdftotext -layout /path-to/report.pdf - | grep -A 5 "人均每周"

# Independent review protocol
gh issue create --title "Fact-check verification" --body "Provide exact quote from source: [citation]"
```

### Common patterns to verify

- **Emergency numbers**: 120 → 103/112, 119 → 101, 110 → 102
- **Financial statistics**: SPIVA fund underperformance rates, CNNIC internet usage data
- **Medical guidance**: CPR steps, choking protocols, CO detector placement
- **Government agencies**: 民政 → органы соцзащиты, 卫健委 → Минздрав
- **Legal terms**: 低保 → дибао (with gloss), 兵役法 → закон о воинской обязанности

### Quality gates

- **All citations must have URLs/DOIs** — No bare «来源：作者经验» without disclaimer
- **Exact quote matching** — Source text must match the cited passage exactly
- **Live URL verification** — Check that cited URLs resolve (use Wayback if blocked)
- **PDF verification** — Official PDFs must be extractable and match claimed content
- **Cross-source consistency** — Multiple sources should agree on key facts
- **Independent review required** — Critical claims require verification by second reviewer

### Pitfalls

- **WAF blocking** — Many official sites block automated access; use Wayback snapshots
- **PDF extraction failures** — Some PDFs are images-only; use OCR or official text versions
- **Outdated statistics** — Always check publication dates; use most recent available data
- **Translation artifacts** — Verify that translated terms match source concepts exactly
- **Missing context** — Some facts require country-specific context; add translator notes when needed
- **False positives in search** — Use exact-match search with quoted phrases, not keyword matching
- **Citation glue errors** — Never combine multiple source sentences into one citation
- **Source title mismatch** — Verify that cited titles match actual source documents
- **Date verification** — Always check that cited sources are current (e.g., ERC 2021 does not contain claimed sections)
- **Wayback date drift** — Use earliest possible Wayback snapshot to avoid page changes

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
- **万/亿 conversion verification:** Always run number-preservation script after translation to confirm all 万/亿 conversions are preserved (0 lost). Convert adjacent to 万/亿 only; standalone numbers unchanged.
- **Unit-based QA for retrofits:** When checking inserted [рус. «…»] in source lines, split large batches into units of 10–15 lines per subagent. Whole-chapter checks are slow (50+ minutes) and prone to timeout; unit-based QA completes in 1–3 minutes per unit. Subagents must write only JSON verdicts — no file edits — to avoid conflicts in shared worktrees.
- **QA verdict workflow:** After subagent reports, aggregate issues centrally and fix using exact string matching with patch. Never let multiple agents write to the same files during QA.
- **CJK punctuation artifacts:** Watch for stray Chinese punctuation in translated text (e.g. `，` instead of `,` or `… …` instead of `…`). Use regex to scan for these patterns and replace them with proper Russian equivalents.
- **Double ellipsis fix:** Loading status text may contain `… …` due to copy-paste artifacts from animated elements. Replace with single `…` and check CSS for ::after animations that could reintroduce the issue.
- **Layout sync:** After text updates, re-check CSS for layout issues like misaligned headings (flexbox wrapping, text overflow) — Russian text is longer and may break responsive layouts.
- **Propagation delay:** After pushing commits, wait 50+ seconds for GitHub Pages propagation before verifying live site changes; use `curl -s <url> | grep -o 'text pattern'` to confirm fixes
- **Upstream hash sync:** Verify main repo content (book/, docs/) matches upstream exactly via hash comparison; empty result means CN chapters identical
- **Issue resolution protocol:** Allow 1–2 days for author response to completion announcements; conclude issue resolved after 48 hours if no response.
- **Merge conflicts:** When merging branches, check `.gitignore` for conflicts — automatic merge tools may miss file-specific exclusions like `tools/` directories.
- **Pages rebuild delay:** GitHub Pages rebuilds take 1-2 minutes after push; always wait before verification to avoid false negatives.
- **PR auto-merge detection:** GitHub may auto-close and merge a PR when the branch is merged to target — check PR state after merge and add closing comment if needed.
- **Live site verification:** Verify multiple URLs after deployment: index.html, README.md, sample book chapters, upstream links — single file checks miss cascading failures.
- **Spanish translation subagent errors:** Spanish subagents may translate numbers as words instead of digits (e.g., 'Treinta minutos' instead of '30 minutos'), breaking byte-identity gates. Always verify numeric preservation after Spanish translation and fix any word-form numbers to digit-form to match source.
- **Spanish decade/era number preservation:** Spanish subagents may convert '1990 年代' to 'años noventa' instead of preserving '1990' as digits. Always verify that era numbers remain in digit form ('años 1990') to maintain byte-identity with source.
- **Spanish numeric format consistency:** Spanish subagents may introduce word-form numbers in contexts requiring digit-form (e.g., 'mil' instead of '1000'). Always verify that all numeric values match the source exactly and replace word-form numbers with digit-form equivalents.

## Multi-language extension

This workflow has been extended for Chinese-to-English, Chinese-to-Russian, and Chinese-to-[target-language] translations (HowToLiveBetter EN/ES/HI projects). The core principles apply to all target languages, with language-specific adaptations.

### Language prioritization

Based on Octoverse 2025 GitHub developer populations and audience overlap:
- **Spanish:** High priority — one language covers 20+ countries, low English overlap in LatAm, significant real-world impact
- **Hindi:** Secondary priority — massive user base, but most Indian GitHub users read English; broader audience appeal
- **Other languages:** Portuguese (Brazil), Japanese (stable market) — evaluate on case-by-case basis

### Core workflow differences

- **Primary language shift:** README.md is now English-primary; Chinese original moved to README.zh.md, Russian to README.ru.md
- **No retrofit needed:** Unlike Russian, English bodies contain no free-standing Chinese titles to retrofit with [eng. "…"] — CJK confined to machine zones (tags, sources, link targets)
- **Source preservation:** All source lines (来源：/DOI/URLs) remain byte-identical per QA requirement; only field label punctuation may differ (`：`→`:`)
- **Status line translation:** Translate visible text in status lines and back-links; keep link targets byte-identical to source
- **Language detection:** Use `navigator.language` for automatic language selection, fallback to English for unknown languages
- **Trilingual+ UI:** Implement language dropdown in top-right corner with expandable toggle
- **Language-specific considerations:**
  - Spanish: Consider regional variations (Spain vs LatAm) — default to neutral Spanish unless specified
  - Hindi: Consider script (Devanagari) and potential audience (broader than just GitHub users)
  - All languages: Maintain consistent terminology glossaries across chapters
- **UI/UX consistency:** Apply the same search placeholder logic across all languages — use short form everywhere (Search/Поиск/搜索/Buscar) and ensure proper centering on all viewports

### Number conversion for 万/亿

- **Convert 万 → numeric:** 1 万 = 10,000; 610.6 万 = 6.106 million
- **Convert 亿 → numeric:** 1 亿 = 100,000,000; 2.5 亿 = 250 million
- **Verify preservation:** Run number-preservation script to confirm no loss during translation
- **Units and statistics:** HR/RR/OR/CI values must be identical; percentages and statistical terms preserved
- **Context-aware conversion:** Only convert when adjacent to 万/亿; standalone numbers unchanged
- **Glossary consistency:** Document all 万/亿 conversions in glossary for reference

### Verification checklist

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
- [ ] README.md is English-primary with language switcher
- [ ] Zero CJK in body text outside machine zones
- [ ] Language dropdown implemented and functional
- [ ] Automatic language detection working
- [ ] 万/亿 conversions preserved (script verification: 0 lost)
- [ ] Search placeholder consistency: short form (Search/Поиск/搜索/Buscar) used everywhere, centered on mobile and desktop
- [ ] Mobile viewport testing: header layout verified (search between hamburger and icons, no overflow)

### Upstream communication protocol

When proposing or announcing translations to upstream authors:

1. **Open issue early:** Propose translation plan in Chinese upstream issue to avoid confusion
2. **Clarify fork-only policy:** Explicitly state that translation lives in fork, no PR to main (per author request)
3. **Highlight QA rigor:** Emphasize byte-identity of sources, machine tags, and verification scripts
4. **Provide website link:** When complete, provide live site URLs (zh/ru/en) for README integration
5. **Request README updates:** Ask author to update language links in main README to point to dedicated URLs (/ru/, /en/)
6. **Follow up:** Allow 1–2 days for author response before concluding issue closed

## Post-deployment verification

After deployment, verify:

1. **Content sync:** Check that main repo content (book/, docs/) matches upstream exactly via hash comparison
2. **README structure:** Verify language links are correctly updated
3. **Issue resolution:** Confirm upstream issues are closed or updated with translation status
4. **Release notes:** Document translation completion and website URLs in MR description

### Hash verification command
```bash
cd /path/to/repo
echo "=== upstream content sync ==="
git -c core.quotepath=false ls-tree -r origin/main --name-only book/ | while IFS= read -r f; do h1=$(git rev-parse "origin/main:$f" 2>/dev/null); h2=$(git rev-parse "fork/main:$f" 2>/dev/null); [ "$h1" != "$h2" ] && echo "DIFF: $f"; done
echo "(empty above = CN chapters identical)"
```

## References

- MQM quality rubric: `../translation/references/quality-rubric.md`
- Localization techniques: `references/localization-techniques.md`
- Retrofit QA workflow: `references/retrofit-qa.md`
- Server pipeline: `../translation/references/server-pipeline.md`
- Website deployment: `references/website-deployment.md`
- English translation workflow: `references/english-translation-workflow.md`
- Spanish translation QA: `references/spanish-translation-qa.md`
- Upstream communication protocol: `references/upstream-communication.md`
- TRANSLATION.md template: `../translation/templates/TRANSLATION.md`
- Source verification protocol: `references/source-verification.md`

## Scripts

- English translation watchdog: `scripts/htlb-en-watchdog.py`