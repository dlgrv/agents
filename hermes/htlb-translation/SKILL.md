---
name: htlb-translation
description: "Chinese-to-Russian book translation with chunked units"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [translation, chinese, russian, book, htlb, chunking]
    related_skills: [github-pr-workflow]
---

# HTLB Translation

README policy (fork dlgrv/HowToLiveBetter): `README.md` = English primary (from translation/en onward), `README.zh.md` = renamed Chinese original, `README.ru.md` = Russian; all three linked via a Languages: line. Commit 8126ee6. Workflow

Workflow for translating the HowToLiveBetter book from Chinese to Russian. Uses chunked units (not whole chapters) and incremental commits with explicit developer approval before any git/PR action.

## Core Principle

**Never create a branch, commit, or PR unless the developer explicitly asks for it.** This overrides general assumptions that finishing a task implies shipping a commit. Always require an explicit instruction to commit/branch/PR in the same turn.

## 1. Chapter Preparation

Each chapter is split into units by `tools/digest.py`. Units are stored in `/root/htlb-run/<chapter>/units/` with placeholders `§TAG§` and `§SRC§` that are filled by `assemble.py` later.

```bash
# Prepare run directory for a chapter (e.g. chapter 16)
cd ~/github/HowToLiveBetter
mkdir -p /root/htlb-run/16/units
cp tools/digest/16/units/*.md /root/htlb-run/16/units/
for n in 00 01 02 03 04 05 06 07; do echo "§TAG§" >> /root/htlb-run/16/units/$n.md; echo "§SRC§" >> /root/htlb-run/16/units/$n.md; done
```

### Unit File Structure

Each unit file must contain:
1. Chapter header (exact format per TRANSLATION.md)
2. Empty lines
3. Translated content with field markers
4. §TAG§ placeholder (on its own line)
5. §SRC§ placeholder (on its own line)

## 2. Unit Translation

Translate each unit incrementally. Each unit must be written to its file immediately after translation (no JSON reports until all units are done).

```bash
# Use delegation or manual translation per unit
# Each unit file contains:
# - Line 1: chapter header (exact format per TRANSLATION.md)
# - Empty lines
# - Content with field markers: 成本→Стоимость, 说人话→Простыми словами, etc.
# - §TAG§ and §SRC§ lines (placeholders, leave untouched)

# Write translated unit back to file immediately
write_file /root/htlb-run/16/units/01.md "translated content...\n\n§TAG§\n§SRC§"
```

### Field Marker Rules

- 成本 → Стоимость
- 说人话 → Простыми словами
- 收益 → Эффект
- Выгода → Эффект (legacy label must be replaced with Эффект)
- 证据等级 → Уровень доказательности (A/B/C remain)
- 备注 → Примечания
- All numbers/dosages are byte-for-byte (§ numbers remain)
- No slang: cohort/exposure/quartile/confounding/population/low-evidence
- Live Russian, not literal translation
- "Простыми словами" without numbers outside "Эффект"
- No exclamation marks
- Headers with verbs

### Web UI Capitalization Rules

When translating content for web interfaces (such as the Russian index.html and README.ru.md), apply automatic capitalization to field values:

- **Простыми словами values**: Capitalize first letter (e.g., 'пристёгнутый ремень...' → 'Пристёгнутый ремень...')
- **Эффект values**: Capitalize first letter (e.g., 'по оценке...' → 'По оценке...')
- **Примечания values**: Capitalize first letter (e.g., 'цифры NHTSA...' → 'Цифры NHTSA...')

**Implementation**: Add `if (LANG==='ru') entry.human = entry.human.replace(/^\s*(.)/, (c)=>c.toUpperCase());` to the parser logic for each field. This ensures consistent capitalization across all translated entries in the web interface while preserving the original lowercase formatting in markdown files.

**Pitfall**: Do not apply this capitalization to the field labels themselves (Стоимость, Эффект, Примечания), only to their values. Field labels should remain as defined in the field marker rules.

## Intro Paragraph Layout Optimization

Russian text in chapter introductions is longer than the Chinese original; the default `.intro{max-width:72ch}` leaves dead space on the right while cards run to 900px. Fix: `.intro{max-width:100%}` in index.html only (never touch markdown). Scope and verification: `references/intro-layout-optimization.md`.

## Sidebar UI Capitalization Rules

When working with sidebar filter chips in Russian web interfaces, apply consistent capitalization to all user-facing chip labels:

- **Chip labels**: All filter chips must start with a capital letter (e.g., 'очень высокая' → 'Очень высокая', 'жизнь' → 'Жизнь')
- **Money chips**: Special case — Chinese-derived chips (少/多) must be translated to Russian with capitalization: 'Мало' / 'Много'
- **Card badge labels**: Values in the LABEL map (e.g., 'бесплатно' → 'Бесплатно', 'небольшие траты' → 'Небольшие траты') must also be capitalized for consistency
- **Section header alignment**: Use CSS `flex-direction: column` and `align-items: flex-start` for `.gt` elements to prevent header/helper text overlap on mobile screens

**Implementation**: During web interface updates, systematically replace all lowercase chip labels with capitalized versions using regex or string replacement. Verify that `data-v` attributes remain unchanged to preserve filter functionality.

**Pitfall**: Preserve `data-v` values (e.g., 少, 多, 否, 是) unchanged — these are internal filter keys, not user-facing text. Only update the visible chip text labels.

**Quality Check**: After applying capitalization, verify that no Chinese characters remain in visible text by scanning for `\u4e00-\u9fff` ranges in chip labels and card badge text.

## 3. Assembly and Validation

When all units of a chapter are translated, use `assemble.py` to inject sources and validate:

```bash
cd ~/github/HowToLiveBetter
python3 tools/assemble.py /root/htlb-run/16
```

This script:
- Injects sources from `tools/digest/16/sources/` byte-for-byte
- Validates field markers and unit count
- Checks for missing/incomplete units
- Outputs translated chapter to `book/16-...-ru.md`

## 4. Git Workflow (only on explicit ask)

Only branch/commit/PR when the developer explicitly asks in the same turn.

```bash
# Example (only if asked to commit)
git checkout -b translation/16-chronic-disease
# ... (add files, commit, PR as per github-pr-workflow)
```

### Branch naming: `translation/<chapter>-description`
### Commit message: `feat(translation): translate chapter <chapter>`

## 5. Watchdog for Long Translations

Use cron watchdog for multi-chapter translations:

```bash
# Create cron job (once per session)
cronjob_manage action=create name=htlb-translation-watchdog no_agent=true script=htlb-watchdog.sh schedule="30m"
```

The watchdog:
- Checks for stalled chapters (no writes for 40+ minutes)
- Reports completed chapters (all units translated)
- Silent when all is progressing normally

## Pitfalls

- Never infer permission to commit/branch/PR from "task done" — always require explicit ask in the same turn
- Always leave §TAG§ and §SRC§ placeholders intact in units — they are filled later by assemble.py
- Numbers must be byte-for-byte; never add or remove numbers from "Эффект"
- Field markers must be exact: 成本→Стоимость, 说人话→Простыми словами, **收益/Выгода→Эффект**, etc.
- Do not translate sources — they are injected byte-by-byte by assemble.py
- Watchdog only reports when something is wrong or complete; silent during normal progress
- Load this skill before any translation work to ensure correct field markers and workflow
- **Legacy label trap**: New translations sometimes use '- Выгода:' instead of '- Эффект:'. This breaks the web parser (regex expects 'Эффект'), causing 'Эффект' blocks to disappear from the site. Always replace 'Выгода' with 'Эффект' in all units before assembly.

## Subagent Pitfall

- **Never let subagents spend time on analysis or planning** — they must write files immediately
- **Batch-reading trap**: subagents may read ALL unit files first (transcript active, 0 writes), then die on timeout before writing anything. Detect: many `read_file` calls, 0 writes, 0 files changed. Steer: "STOP READING. One file per step, overwrite each before the next." Prevention: in every task prompt write "do NOT re-read conventions or reference files — everything is in this task; start writing immediately". Watchdog cron (3m interval, no_agent script) alerts on 3 conditions: silence ≥6 min, chapter complete (→ assemble), reads-without-writes.
- Each subagent gets one unit (not a whole chapter) and must write it to its file upon completion
- Do not let subagents study existing chapters for style — provide a style sample in the task instead
- Subagents must not return JSON summaries — only write the translated unit file
- If a subagent stalls, restart it with stricter instructions: 'work = write files, no analysis'

## Subagent Timeout Recovery

- **Timeout pattern**: When subagents stall (25+ minutes with no writes, transcript shows many `read_file` calls but 0 `write_file`), they are stuck in analysis/reading loop
- **Recovery**: Reset pristine units from digest source, restart with HARD PROCESS RULE: first tool call must be `write_file` of the translated unit — no reading other units, no analysis, no planning
- **Detection**: Check transcript for ≥10 lines with only `read_file` and 0 `write_file` calls; check file timestamps for last write >15 minutes ago
- **Prevention**: In every task prompt, enforce: "your FIRST tool call must be a write_file of the translated NN.md. You may NOT read any unit other than the one you are currently translating in this same step."

## Localization and Realia Handling

- **Legal/official identifiers**: Court case numbers (最高法知民终 51 号), document codes (国食药监办〔2010〕432 号), and other Chinese legal/administrative identifiers must be preserved byte-for-byte per TRANSLATION.md — they function like DOIs and are not translated
- **Emergency numbers**: When translating emergency service numbers (e.g. 120), add localization in parentheses: 'звоните 120 (для Китая — 112/103, для РФ — 103)'
- **Country-specific procedures**: Add translator's comments in brackets for procedures that vary by country: '[в Китае — процедура X, в РФ — процедура Y]'
- **Realia glossing**: For culturally specific terms, add translator's notes: '[в Китае: X — традиционная практика Y]'
- **Units and measurements**: Convert Chinese units to metric/Russian equivalents where appropriate (e.g. 'цзинь (≈500 г)', 'ли (≈500 м)')
- **Hot-line analog placement**: Chinese emergency numbers (120, 110, 12356, 96110, etc.) remain in item titles as original realia; Russian equivalents are moved to translator notes at chapter start (see `references/localization-techniques.md` technique 9)
- **Term validation**: Never add invented Chinese terms 'pro запас' — verify all terms exist in book/*.md using grep before adding to localization examples (see `references/localization-techniques.md` technique 10)
- **Numeric conversion trap**: Chinese 万/亿/千/万亿 must be converted to Russian тыс/млрд/млрд/трлn with correct magnitude — verify conversions against original CN values (e.g., 90895.5 亿 = 9 089.55 млрд, not 90895.5 млрд)
- **Number preservation**: Numbers in 'Простыми словами' must match CN 说人话 — if CN says '9.6 万人', RU should say '96 000 человек', not reuse '96,217' from 'Эффект' section
- **See**: `references/localization-techniques.md` for complete catalog of 10 localization techniques with examples

## Web UI Layout Optimization

When working with Russian web interfaces (index.html), be aware of layout constraints that may cause visual imbalance between text sections:

- **Intro paragraph width constraint**: The `.intro` CSS class limits line length to 72 characters (~600px), while content cards extend to 900px. For longer Russian text, this creates excessive whitespace to the right of the introduction.
- **Fix**: Remove `max-width:72ch` and set `max-width:100%` for `.intro` to match card layout and eliminate visual imbalance.
- **Scope**: This optimization applies only to web interfaces, not markdown source files.
- **Verification**: After applying the fix, confirm that intro text flows naturally across the full width without awkward line breaks or excessive whitespace.
- **Reference**: `references/intro-layout-optimization.md` for detailed implementation instructions and quality assurance procedures.

## Trilingual Web UI (ru/en/zh)

- **index.html is now trilingual**: `LANG` accepts `ru|en|zh`; data source per lang: ru → `README.ru.md`+`book/ru/`, en → `README.md`+`book/en/`, zh → `README.zh.md`+`book/`. Language switcher = `<details class="lang-dd">` dropdown top-right in `.nav-r` (click on menu item → `__setLang` → `?lang=` + localStorage `htlb-lang`).
- **Machine tag keys stay CJK everywhere**: `data-v` attrs (少/多/否/些/是/极高/高/一般/死亡率/金钱/时间/自由), the `<!-- 成本标签: ... -->` parser, ratio computation, and `COST_W` weights are language-independent keys; only visible labels come from the `I18N[LANG]` dict (`T().ratio/lens/moneyL2/timeL2/willL2`). Never translate `data-v` values.
- **Field-label parser regexes are tri-lingual**: `- (?:成本|Стоимость|Cost)` etc. for all six fields; glossary heading regex has an EN branch (`/^## Reading the numbers/`), and the glossary header-row skip must include `Term` as well as `термин`.
- **Contested/TODO detection is per-lang**: dispute = zh `争议`, ru `Спорно`, en `Contested` (regex branch on LANG); todo matches `待核实|TODO|to be verified`.
- **Capitalization of field values**: ru and en yes (T().cap), zh no — values in zh files start without capital.
- **Testing without a real browser**: browser tool blocks localhost. Use jsdom (`npm i jsdom` in /tmp) with `runScripts:'dangerously'`, polyfill fetch (read files from repo dir), IntersectionObserver, PerformanceObserver, requestAnimationFrame, scrollTo; then assert per-lang: title, htmlLang, field labels, chips text, cards=498, sections=31, glossary terms, dispute/todo badge counts, filter clicks (Freedom → 82), search. Extract single big script; don't eval script blocks concatenated naively (`const` collisions).
- **Default language = navigator.language** (`ru*/zh*/en*` prefix match, unknown → `en`); priority: `?lang=` > localStorage > system > `en`.
- **Full-page i18n audit checklist** (things easy to miss): `meta description/keywords/author`, `og:title/description/locale/site_name`, `twitter:*`, JSON-LD `@graph[].name/description/abstract/inLanguage/about` (rewrite at runtime via `JSON.parse` → mutate → `textContent`), nav button `aria-label`/`title` (menu, theme, GitHub, README icon — README icon `href` must also switch: `README.ru.md`/`README.md`/`README.zh.md`), the dynamically built "All sections" chip (use `T().allSections` in its template, not a hardcoded string), `<html lang>`. Audit by rendering with jsdom and scanning every UI surface for foreign-language text; card-body CJK/RU "leaks" that are legitimate: transliteration+gloss `(低保 — …)` and Chinese law titles in descriptive references (per TRANSLATION.md convention).
- **When patching a large JS dict programmatically, anchor on exact unique strings and re-verify structure after each batch** (`const I18N` count==1, `function T()` count==1, file still ends with `</html>`, `node --check` on the extracted main script). Splitting on `'   cap:true },'` misplaces the zh block because zh ends `'cap:false }'` without comma — locate each dict's tail individually before inserting.
## Per-language Pages URLs

- Live URLs: root `/` = auto-detect (`navigator.language` → fallback `en`, then `?lang=`/localStorage), `/ru/`, `/en/`, `/zh/` = forced language. The upstream author can link any of them directly from the original README.
- **Mechanism**: subdir `index.html` files are GENERATED from root `index.html` via `tools/build_pages.py` (run from repo root after every root-file edit; commit the outputs). The generator swaps the bootstrap placeholder after `<head>` for `<script>window.__HTLB_LANG__='<lang>';window.__HTLB_BASE__='../';</script>` and rewrites canonical/og:url to `https://dlgrv.github.io/HowToLiveBetter/<lang>/`.
- **Relative-path trap**: subdir pages sit one level deeper, so every relative fetch (`README.ru.md`, `book/ru/…`) must be prefixed with `../`. The page does this itself: when `__HTLB_BASE__` is set it wraps `window.fetch` (skips absolute, `/`-rooted and `../` URLs). CSS/`og.png` refs are either absolute or inline.
- `__setLang(l)` navigates to `new URL(l+'/', new URL(BASE||'.', location.href))` — works both from root and from any subdir.
- Editing rule: change ONLY root `index.html`, then regenerate; never hand-edit `ru|en|zh/index.html`.
- **Upstream links to the fork** (author cites dlgrv in upstream README): after EN-primary merge the two referenced targets stay valid — `blob/main/README.ru.md` (file kept, only header lines edited) and Pages root (index.html untouched by EN branch; site rebuilds from main). Verify with API `contents?ref=main` 200 + HTML HEAD 200.

## Source Title Retrofits

- **Chinese article/document titles**: Add Russian translation in brackets immediately after Chinese title: `中国人健康指南 [рус. «Руководство по здоровью китайцев»]`
- **Format**: `[рус. «…»]` for Russian, `[eng. "..."]` for English titles
- **Placement**: After Chinese title, before author/journal info or parentheses (for laws)
- **Preservation**: Original Chinese title, author names, journal names, DOIs, URLs, HTML tags, dates, and document codes remain byte-for-byte unchanged
- **Scope**: Only applies to source lines (starting with `- Источники:`), never to main text content
- **Verification**: After retrofit, verify that all source lines with Chinese titles have the annotation, while English-only source lines remain untouched
- **Batch processing**: Use balanced batches of 4-6 chapters per subagent to maintain speed and consistency

## Documentation Articles Translation

- **Scope**: Translate four long docs articles (家庭应急装备清单, 结婚划不划算, 遇到陌生人出事该不该停, 做平台要办哪些证) referenced by chapters and README
- **Volume**: 2.5K/3.2K/1.8K/2K hanzi, 89/123/55/69 lines respectively — small enough for one parallel wave of 4 subagents
- **Workflow**: Same as chapters (digest → units → translation → assemble), but units are smaller (5-10 lines per unit)
- **Integration**: After translation, update all chapter and README links from `(на китайском)` to point to new Russian docs files
- **Quality**: Apply same field markers, localization rules, and QA as main chapters; verify cross-references work correctly
- **Pitfall**: Do not skip these — they are the only remaining Chinese content in the Russian edition and actively referenced

## English Translation Launch (2026-09-18)

- **Pilot wave**: Always start with chapters 01 (smallest) and 13 (largest) to test all pipeline components (digest, assemble, web UI capitalization, EN field labels)
- **EN field labels**: Use `- Cost:`, `- In plain terms:`, `- Benefit:`, `- Evidence grade:`, `- Notes:` (not Russian equivalents)
- **EN slug naming**: Two-digit prefix + English title slug (e.g., `01-Do-Not-Die-Early.md`), recorded in TRANSLATION.md naming table
- **EN-specific localization**: China-specific concepts on first use: transliteration + short gloss (e.g., "dibao (低保 — means-tested minimum subsistence allowance)")
- **Legal/regulation titles**: Not translated; refer descriptively in body text, exact names stay in sources (injected)
- **万-notation**: Numeric conversion (2 万 = "20,000 yuan")
- **Status line**: Translate visible text, keep link targets byte-identical
- **Unit-based QA**: Same proven approach as RU — slice into ~10-line pairs for parallel verification subagents
- **Wave planning**: Group chapters by unit count (5 chapters per wave), pilot wave validates full pipeline before mass translation
- **Commit strategy**: One chapter per commit (clear message: `translation(en): chapter NN`), enable GitHub Pages in fork
- **Issue management**: Issue title in Chinese only, body in Chinese with brief EN note; preserve author comments, remove third-party non-CN comments
- **Fork main merge**: Only after complete translation, merge `translation/en` → `main` in fork, then delete branch
- **PR workflow**: Create PR from `translation/en` to `main` in fork, auto-merge if fast-forward, close after merge
- **Quality check**: After each wave, verify byte-identical sources, field labels, and no Chinese characters in visible text (regex `\u4e00-\u9fff`)
- **CJK false positives**: Some legal/regulation titles contain CJK characters in the middle of English text (e.g., "The General Office of the State Council measures in April 2026 on accelerating the building of pooling region (统筹地区 — the locality where you are insured)"). These are valid and should not trigger warnings; grep for `\u4e00-\u9fff` should exclude lines with known gloss patterns like `(统筹地区 — ...)` or `(副主任医师 — ...)`

## Issue Management for External Repositories

- **Issue title**: Always keep issue title in the target language only (no mixed languages)
- **Issue body**: Use target language only, with brief English note if needed
- **Comments**: Remove all comments not in the target language (user's or third-party)
- **Fork maintenance**: Translations live in fork; issue tracks progress and links to PR
- **Author responses**: Preserve non-target-language comments from repository owner (do not delete author's own comments)
- **Third-party comments**: Remove non-target-language comments from other users (keep only target-language comments)
- **Issue description**: Update to reflect current status (complete/in progress) with live links to fork/PR

## Fork Main Branch Merging

- **Timing**: Merge `translation/ru` → `main` in the fork when the translation is complete (not before)
- **Prerequisite**: Ensure `translation/ru` is based on latest `fork/main` (check with `git merge-base`)
- **Fast-forward**: If no conflicts (typical), merge directly; else resolve conflicts manually
- **Branch cleanup**: After merge, delete `translation/ru` unless explicitly kept for ongoing work
- **PR workflow**: Create PR in fork (dlgrv/HowToLiveBetter) from `translation/ru` to `main`, auto-merge if fast-forward, close after merge
- **Author notification**: Provide clean link to fork's main branch (without branch name in URL) for author's README
- **Pages option**: Enable GitHub Pages in fork for live web reading at `dlgrv.github.io/HowToLiveBetter/`
- **Pitfall**: Never merge incomplete translations — wait until all chapters and docs articles are done

### Issue Management Workflow

1. Update issue title to reflect target language only
2. Clean up comments: remove non-target-language comments (except author's own)
3. Update issue body with current status and live links
4. Preserve author's response comments (even if not in target language)
5. Add brief English note if needed for clarity

**Pitfall**: Issue title must be in target language only — mixed titles confuse readers and violate repository conventions.

### Example Issue Structure

**Title**: `Russian translation (俄语版) — tracked in PR #7 / fork`

**Body (target language + brief English)**:
- Complete status in target language
- Link to fork README for live reading
- Link to PR for changelog
- Translation conventions summary
- Brief English note about future English version

**Comments**: Only target-language comments (remove user's mixed-language comments)

## QE/метрики: факты ревью 2026-09-18

- wmt22-cometkiwi-da и XCOMET-XL/XXL — CC-BY-NC-SA-4.0 + gated (НЕ Apache); в опенсорс-репо и коммерческий прод нельзя. Apache-замены: wmt20-comet-qe-da, wmt22-comet-da, MetricX-24.
- zh→ru для cometkiwi — out-of-distribution (пары нет в обучающих данных); zh→en — in-distribution. До гейта — валидация на 30–50 сегментах.
- CometKiwi почти не чувствителен к перефразированию (TransAgents App. B) и sentence-level с лимитом 512 токенов → только advisory-сигнал, не гейт.
- Source-blind судья валиден только для беглости; точность всегда с источником (error-span MQM, GEMBA-MQM). Парные сравнения со swap, tie при несогласии (Zheng et al. MT-Bench).
- Судья пассов C/D — GLM-5.3-Flash через API z.ai (решение Лёни 2026-09-18; сильный, уже оплачен, локальный стек не нужен). Офсеты: self-preference (судья = семья переводчика) → A/B против контролируемых деградаций, а не против второго GLM-вывода; невоспроизводимость API → в вердиктах логировать model id + дату + prompt_hash, при смене весов — дешёвая ревалидация золотого сета (60 пар). Если κ(судья, Лёня) < 0.4 — запасные: локальный Qwen3-30B-A3B или Gemma 3 27B (Mac M5 Pro 48GB).
- Порядок пассов: translate → assemble → verify(FAIL) → fact-check E(FAIL, заземление CN-цитатами) → style A(WARN) → QE B(advisory) → judge C/D(advisory) → MQM(человек, приоритет над QE) → MR+squash.

## Clone & Publication Rules (2026-09-18)

- Локальный клон: `~/github/HowToLiveBetter` (раньше был `~/github/htlb-ru` — переименован, имя «ru» вводило в заблуждение; пайплайн двуязычный CN→RU/EN). Не использовать старый путь.
- **Публикация в main форка — ТОЛЬКО через MR + squash-merge** (правило пользователя): рабочая ветка от `fork/main` → push → `gh pr create --repo dlgrv/HowToLiveBetter` → `gh pr merge N --squash --delete-branch`. Прямой push в main запрещён. Пример: tools-пайплайн опубликован MR #2 (squash → commit `2ad4ab3`).
- После squash в main — cherry-pick squash-коммита в активные контентные ветки (`translation/en`), чтобы инструменты не разъезжались.
- В коммиты инструментов не брать transient-состояние: `tools/digest/`, `tools/.status/` (в .gitignore).

## Pipeline tools (2026-09-18, в репо `tools/`)

Пайплайн двуязычен по конструкции (CN→RU и CN→EN — оба трека равноправны; требование пользователя).

- **`tools/glossary.json`** — закреплённые термины, у каждого сразу RU и EN эквивалент + стилевые правила обоих языков. Наполнять ТОЛЬКО после grep-проверки по book/*.md (запрещено добавлять термины «про запас»). `make_digest.py` генерирует `units/NN.gloss.md` — только термины данного юнита (в юните 00 — все термины главы + [STYLE] правила); gloss-файлы кладут в задачу сабагента-переводчика вместе с юнитом, в assemble они не попадают.
- **`tools/verify.py <NN> --lang ru|en [--file X]`** — гейт перед коммитом: заголовки/теги/поля/источники (байт-тождество с допуском [рус. «…»]/[eng. "…"] ретрофитов), числа в пространстве ЗНАЧЕНИЙ (万/亿/千/万亿 ↔ тыс/млн/млрд/трлн, прописные числительные, месяцы, дистрибутивный масштаб «от 81 до 138 тыс.» = «8.1 万 到 13.8 万»; исчезло = FAIL, стало реже = WARN), CJK вне легальных зон (источники/теги/глоссы/цитаты-реалии/блок «Примечание переводчика»), запрещённые кальки ≤1 на файл (RU), jargon HR/RR/OR/CI в строке «Простыми словами/In plain terms» (WARN, оба языка). Пишет tools/.status/<NN>-<lang>.ok для status.py.
- **`tools/status.py [NN…]`** — дашборд волны: файлы RU/EN, свежесть verify-маркера («изм.» = правили после проверки), прогресс юнитов /root/htlb-run, активные волны.

### Known FP verify.py (not to be crudely fixed)
- "60,000 IU" in RU text is read as decimal (comma = thousands only if not "0..."; one line in ru06). Fix: replace with "60 000 IU" to avoid false positive.
- CN "250 多万粉丝" vs EN paraphrase without number — en09, requires text-level resolution, not script fix.
- Real findings from first run 53/62: calques "когорт" ×13 (ch. 13/28/29/30), "популяц" ×2 (ch. 29), missing numbers in ru10/ru11 — material for a fix wave.
- CJK gloss false positives: Legal titles in English text with CJK characters (e.g., "统筹地区 — ...") are allowed and should not trigger warnings. Verify regex excludes gloss patterns like `(统筹地区 — ...)` or `(副主任医师 — ...)`.

## Quality Assurance Techniques

- **Parallel subagent verification**: After translation wave, run verification subagents to check:
  - Natural Russian flow (avoid literal translation artifacts)
  - Consistent field marker usage across chapters
  - Proper localization annotations without over-annotation
  - Emergency numbers and procedures correctly localized
  - No untranslated Chinese terms outside sources
- **Verification workflow**: Use separate subagents for each quality aspect (natural language, localization consistency, field markers) with strict 'work = write reports' instruction
- **Verification scope**: Check 5 chapters at a time to maintain speed while catching systemic issues
- **Fix priority**: Natural language issues > localization consistency > field marker accuracy
- **Unit-based QA (proven 2026-09-18)**: For source fidelity checks, slice into small units (~10 line pairs) and run parallel verification subagents that write verdict JSON files (no file editing). Aggregate issues programmatically and apply fixes centrally. See `references/subagent-instructions.md` for unit QA script details
- **Reference**: `references/natural-language-verification.md` for detailed verification instructions and quality standards
- **Web UI capitalization**: For web interfaces (index.html, README.ru.md), apply automatic capitalization to field values (Простыми слова, Эффект, Примечания) using conditional logic in the parser. See `references/web-ui-capitalization.md` for implementation details and QA procedures
- **Consolidated playbook**: `docs/translation-playbook.md` in the repo is the single source of truth for the whole method (pipeline, subagent contracts, verification, post-waves, web, upstream, EN-launch checklist). Read it before launching another-language translation; this skill keeps only the operational bits
- **Verify.py gate**: Always run `tools/verify.py <NN> --lang ru|en` before committing. Common failure modes and fixes are documented in `references/verify-gate-handling.md`
