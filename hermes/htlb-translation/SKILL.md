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

### UI Component Capitalization Rules

When working with Russian web interfaces, apply consistent capitalization to all UI components:

- **Icon buttons**: All icons must use stroke-only Lucide SVGs (24×24 viewBox, 16px rendered, `fill="none"`, `stroke="currentColor"`, `stroke-width="2`), no filled exceptions including GitHub (use `lucide/github` path). All icons must be exactly 16px in width/height with identical stroke color (`currentColor`).
- **Language labels**: Language switcher labels must be small caps UI marks (12px, `font-weight: 600`, `letter-spacing: 0.08em`), not larger than adjacent icons.
- **Sidebar chips**: All filter chip labels must start with a capital letter (e.g., 'очень высокая' → 'Очень высокая', 'жизнь' → 'Жизнь').
- **Money chips**: Chinese-derived chips (少/多) must be translated to Russian with capitalization: 'Мало' / 'Много'
- **Card badge labels**: Values in the LABEL map (e.g., 'бесплатно' → 'Бесплатно', 'небольшие траты' → 'Небольшие траты') must also be capitalized for consistency
- **Field values**: 'Простыми словами', 'Эффект', 'Примечания' values must be capitalized (first letter only) in web UI rendering only (not source markdown). Implementation: Add `if (LANG==='ru') entry.human = entry.human.replace(/^\\s*(.)/, (c)=>c.toUpperCase());` to the parser logic for each field.

**Implementation**: During web interface updates, systematically replace all lowercase chip labels with capitalized versions using regex or string replacement. Verify that `data-v` attributes remain unchanged to preserve filter functionality. For icons, always measure SVG rectangles before committing: ensure identical width/height/color and no `clipped: true`.

**Pitfall**: Preserve `data-v` values (e.g., 少, 多, 否, 是) unchanged — these are internal filter keys, not user-facing text. Only update visible text labels. Never mix filled and stroke icons in the same header.

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

## Скин v2 (editorial, /v2/)

- Архитектура: тот же index.html/JS; `tools/v2.css` подменяет `<style>` при генерации `v2/{ru,en,zh}/index.html` (build_pages.py), `__HTLB_BASE__='../../'` — данные из корня, без дублей. Правки JS — только в корневом index.html; правки скина v2 — только tools/v2.css + rebuild.
- Дизайн-решения пользователя: Ч/Б Georgia-книжка «университетской прессы» (Stanford/Harvard): шкала 36/24/19/17.5, h1 −0.015em, воздух 88px между секциями, hairlines вместо карточек, инвертированное ::selection; тёмная #111/#d0d0d0; **один шрифт — Georgia и в UI, и в тексте (кнопки/kbd/summary явно наследуют стек — кнопки НЕ наследуют font по умолчанию); моно только `<code>`**.
- Проверка скина: jsdom ловит только сборку (528/32, 0 ошибок); стили/фильтры — реальный браузер (playwright-core из /root/github/dlgrv.com/node_modules + chromium-1234, localhost-сервер; карточки прячутся атрибутом `hidden`, не style.display).
- v2-фичи (PR #13, коммит 2ecc078): scroll-spy — подсветка `.sec-link.spy-on` по getBoundingClientRect секций (rAF-батчинг, только при `__HTLB_V2__`); маргиналии — `aside.marg` в карточке, media ≥1440px, ширина 200px; центрует колонку РОДИТЕЛЬ `#list`, поэтому margin-прижатие на .doc не работает — геометрию проверять rect'ом в браузере, не формулой. Грабли: build_pages.py не вставлял `__HTLB_V2__=1` — все v2-ветки JS молча мертвы; ловится только подсчётом .marg/.spy-on в браузерном тесте. Кнопки шапки v2 (0f74a54): ver-switch (v2→v1, `location.pathname.replace('/v2/','/')`+search+hash, видна только при `html.v2` — класс добавляет build_pages.py в ранний скрипт); тема — icon-btn (луна в светлой, солнце в тёмной) вместо ползунка, `.switch` удалён из обоих CSS; index.html общий для v1/v2 — правки CSS шапки вносить в ОБОИХ местах (v1-блок в index.html + tools/v2.css). Грабля: fuzzy-patch может съесть закрывающий `</details>` — после правок шапки проверять childCount `.nav-r` (должно быть 5) и box'ы кнопок в один ряд (одинаковый y, шаг ~42px). Ритм v2 нормирован: шапка 20/12×4, карточка 8/12×3 (12px = базовая ступень), секции 88px.
- Иконки: НЕ рисовать самому — брать готовые inline SVG из Lucide (https://lucide.dev, ISC; lucide-static на unpkg: `https://unpkg.com/lucide-static@0.469.0/icons/<name>.svg`) и переносить пути ДОСЛОВНО с атрибутами `fill="none" stroke="currentColor" stroke-width="2" stroke-linecap/linejoin="round"`. **Все иконки в шапке — строго stroke-стиля, включая GitHub (lucide/github), размер 16px, один currentColor. Никаких filled-исключений и оптического калибра под разные иконки.** Пользователь требует полной стилевой унификации. Перед коммитом мерить rect всех svg: width/height/color/clipped. Ложные срабатывания аудита: скрытый .sun (display:none, w=0) и намеренный 10px шеврон «РУ» — фильтровать display!=none. Грабля деплоя: build_pages.py перегенерирует и v1 (ru/en/zh), и v2 — коммитить ВСЁ; если закоммитить только v2/, живой v1 остаётся со старой шапкой (случилось в PR #13, чинил PR #14). У .lang-dd>summary нужно width:auto;min-width:32px — базовый .icon-btn жёсткий 32px, «РУ»+шеврон клипаются. CSS-каскад v2.css: base-правило .doc идёт ПОСЛЕ media-блоков — любые переопределения ширины .doc добавлять строго после него (равная специфичность, побеждает последний). Поиск на десктопе (≥1100px) центрирован по ОСИ КОНТЕНТА, не окна: `left: calc(50% + var(--side-w)/2 + 4px)` — центр колонки = 50%W + side-w/2 + 4 (формула из padding .content side-w+56 слева, 48 справа); ось поиска = оси H1 и .sec-block (проверять отклонение 0 на 1440/1920). Радиус-словарь v2: 8px = все всплывающие контейнеры (.search, .lang-menu, .pop), 6px = внутренние элементы (пункты меню, кнопка empty-state), 0 = осознанно квадратные .icon-btn. Тени: одна шкала возвышения 4px/16px/.08 (десктоп-попапы и mobile drawer); .pop/.lang-menu должны использовать токены v2 (--pop-bg/--line), не v1 (--bg-elv/--divider). Ширины v2 (PR #15): колонка 750px (внутр. 702), ≥1800px — 900px (852), маргиналии 180px справа (влезают в 1440/1800/1920, no-h-scroll), титул absolute x=24 над сайдбаром при ≥1100px, .nav-in max-width:none на десктопе. doc-head и .sec-block обязаны совпадать по rect l/r — проверять на 1440/1800/1920.
- Грабли v2: `.icon-btn{display:grid}` перебивал `.menu-btn{display:none}` (равная специфичность) — прятать двухклассовым селектором; абсолютный поиск в шапке уходит из потока — `margin-left:auto` переносить на `.nav-r`; ссылки README/book на v2-страницах требуют префикса `../../` (build_pages.py replace по href); эмодзи-иконки (🌐) ломают монохром — текстовые лейблы; Georgia без CJK-глифов — zh нужен CJK-serif фолбэк (TODO); vision_analyze таймаутит пачками — верить computed-style замерам.

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

### English Documentation Translation (2026-09-21)

- **Scope**: Same four docs articles, but translated directly from Chinese to English (not via Russian)
- **Quality**: Apply same field markers (- Cost:, - In plain terms:, etc.) and localization rules as EN chapters
- **Fact-check gate**: Pass E (source-grounded semantic verification) catches meaning changes, verify.py catches formatting issues
- **CJK handling**: Legal regulation titles with glosses `(CJK — English)` are valid and should not trigger verify.py FAIL
- **Pitfall**: verify.py may FAIL on CJK in legal titles — this is expected; use factcheck gate for semantic validation instead
- **Reference**: `references/english-translation-factcheck-handling.md` for detailed pass E gate workflow and CJK false positive handling

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
- **CJK false positives**: Some legal/regulation titles contain CJK characters in the middle of English text (e.g., "The General Office of the State Council measures in April 2026 on accelerating the building of pooling region (统筹地区 — the locality where you are insured)"). These are valid and should not trigger warnings; grep for `\u4e00-\u9fff` should exclude lines with known gloss patterns like `(统筹地区 - ...)` or `(副主任医师 - ...)`
- **Documentation articles**: Use factcheck gate (pass E) for semantic validation instead of verify.py, which may FAIL on CJK in legal titles

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

## Expert Review Integration (2026-09-19)

- **Before publication**, run independent adversarial evaluations of the pipeline
- Generate reverse-engineered attack vectors (malformed JSON, edge-case spans, broken field markers)
- Dispatch 3–4 subagents with different expertise: code quality, translation QA, statistical validation, infrastructure
- Write reports to `tools/validate/results/expert_review_<expert_type>.md`
- Fix all critical findings before publishing (batch-fix when possible, test locally 101/101 OK)
- **Pitfall**: Never merge dirty branches — ensure all transient files are removed before squashing
- **Pitfall**: Test all fixes locally before committing (manifest valid, no test failures)
- **Pitfall**: Batch fixes that share root causes (e.g., schema sync + contract validation)
- **Pitfall**: Post-merge verification mandatory — pipeline must work after squash
- **Pitfall**: Branch name convention — use quality/pipeline-v2 (or similar descriptive name)
- **Pitfall**: Publication is final — ensure all quality gates are passed before publishing
- See `references/expert-review-workflow.md` for detailed execution pattern

## Pipeline v2 (2026-09-18) — Quality Assurance System

**Обновлённый пайплайн с автоматизированной валидацией качества:**

### Архитектура пайплайна
- **Фаза 1**: Инфраструктура валидации — судьи, QE, мутационные тесты, золотой сет
- **Фаза 2**: Запуск и измерение — прогон по FAIL-главам, тренды метрик
- **Фаза 3**: Публикация — squash-коммит в main, cherry-pick в translation/en
- **Единая конфигурация**: `tools/rules/project.yaml` (языки [ru,en], пути юнитов, judge/QE-бэкенды)
- **Тест-драйв подход**: validate-before-enable — каждый пасс доказывает свою эффективность до включения в конвейер

### Ключевые компоненты
- **Судьи**: GLM-5.3-Flash (z.ai) + source-blind (беглость), A/B (эскалация), factcheck (заземление CN-цитатами)
- **QE**: wmt20-comet-qe-da (Mac MPS/Unbabel), шум τ = max(3σ, 0.01), baseline per-unit
- **Мутационный тест**: 60 семантических мутаций (seed=42), catch-rate ≥80%, FP ≤10%
- **Золотой сет**: 60 пар (6 глав × 3 страты × ru/en + 24 случайных + 10 приманок A=B)
- **Style-аудит**: FP-аудит маркеров/кальк/канцелярита (precision ≥80%, recall ≥60%)
- **Единая таксономия**: issue_type в factcheck/judge/mutation_test (reversed_logic, invented, etc.)
- **Unit-first политика**: правки только в юнитах (`/root/htlb-run-<lang>/<NN>/units/`) → re-assemble → verify

### Порядок пассов (жёсткий)
1. **translate** → assemble → verify(FAIL)
2. **factcheck E** (FAIL, заземление CN-цитатами, фильтрация §TAG§/§SRC§)
3. **style A** (WARN, только advisory)
4. **QE B** (advisory, только на Mac)
5. **judge C/D** (advisory, GLM-5.3-Flash)
6. **MQM** (человек, приоритет над QE)
7. **MR + squash** в main, затем cherry-pick в translation/en

### Валидация и метрики
- **Nativeness rate**: доля native vs translationese в золотом сете
- **QE-тренд**: улучшение vs baseline (якорное ru13 ≥2τ)
- **Judge agreement**: согласованность судей (Cohen's κ ≥0.6)
- **Mutation test catch-rate**: ≥80% на семантических мутациях
- **Style FP rate**: ≤40% на аудите (выбрасывать правило, а не тюнить)
- **Grounding check**: каждый cn_span обязан входить в CN-юнит после нормализации и фильтрации

### Публикация
- **Ветка**: `quality/pipeline-v2` → MR → squash в fork/main
- **Содержимое**: код tools/pipeline/ + tools/rules/ + tools/prompts/ + tools/validate/ + docs/validation-protocol.md + docs/translation-playbook.md + SKILL
- **Исключения**: transient-состояние (tools/digest/, tools/.status/), tools/judge/, tools/.qe/
- **После squash**: cherry-pick squash-коммита в активные контентные ветки (translation/en)

### Интеграция с существующим workflow
- **tools/verify.py**: лейблы из `tools/rules/<lang>.json` (Task 10b)
- **tools/status.py**: колонка factcheck-покрытия
- **tools/factcheck.py**: заземлённый fact-check с программной фильтрацией CN-спанов
- **tools/style_check.py**: WARN-only, exit 0, маркеры из `tools/rules/<lang>.json`
- **tools/glossary.json**: закреплённые термины + стилевые правила (RU+EN)

### Особенности для документных статей
- **verify.py**: Может FAIL на CJK в юридических названиях — ожидаемо, игнорировать
- **factcheck.py**: Использовать как основной гейт для семантической проверки
- **CJK в глоссах**: `(название — объяснение)` — валидно, не ошибка перевода

### Pitfalls
- **Unit-first политика**: правка book/ напрямую затирается re-assembly → clobber-питфолл; править только в units
- **Grounding check**: cn_span на служебной строке §SRC§ отбрасывается до отправки судье
- **QE требует Mac**: на VPS — SKIPPED, пасс B самый поздний и advisory
- **Write-first судьи**: субагенты-судьи пишут вердикт в tools/judge/ сразу после юнита (без фазы «анализа»)
- **Seed-репродукция**: все мутации/якоря/деградации зафиксированы seed=42, коммитятся в results/*.json
- **Transient-состояние**: tools/digest/ и tools/.status/ не включаются в коммиты (gitignore)
- **Clone & Publication Rules**: локальный клон `~/github/HowToLiveBetter`, публикация ТОЛЬКО через MR + squash

### Запуск
- **Ретро-прогон E**: 560 CN-юнитов × 2 языка = 1120 вызовов, выборка 3 глав → волны по 32 юнита (≈35 батчей, ~6–7 ч)
- **Первая волна правок**: известные дефекты (ru10/11/13/28/30), unit-first + 1 глава = 1 коммит
- **Метрики**: nativeness rate и QE-тренд vs baseline; stop-условие: обе в шуме τ → пересмотр пассов

### Интеграция с TDD
- **Каждый пасс**: validate-before-enable — доказать эффективность на тестовых данных
- **Мутационный тест**: как TDD-валидация пасса E (catch-rate ≥80%)
- **Золотой сет**: как TDD-валидация пасса judge (κ ≥0.6)
- **Единая таксономия**: issue_type в factcheck/judge/mutation_test (reversed_logic, invented, etc.)
- **Snapshot-тесты**: verify.py до/после рефакторинга (TDD RED-GREEN-REFACTOR для гейтов)

### Рекомендации
- **Проверить**: verify.py snapshot до/после Task 10b (refactor labels из rules)
- **Измерить**: время ретро-прогона E (ожидаемо ~6–7 ч параллельными волнами)
- **Автоматизировать**: watchdog для stalled chapters (40+ минут без writes)
- **Резерв**: при провале GLM-судьи — локальный Qwen3-30B-A3B или Gemma 3 27B (Mac M5 Pro 48GB)

## Upstream Sync Verification (проверка дельты апстрима, 2026-09-21)

Апстрим может переписывать историю (recreate), поэтому **сравнивать коммиты бесполезно — сравнивать контент**: `git diff main origin/main -- 'book/*.md'` (пусто = CN-база идентична), счёт `^### ` по затронутым главам CN=RU=EN, `git diff` по `docs/核实记录/` (у нас только НАШИ добавленные файлы = ок).

Порядок сверки новой порции записей апстрима (проверено на 6e15cdf, дельта = 0):
1. CN-база: diff `book/*.md` (исключая ru/en) — пустой → записи уже взяты.
2. Переводы: grep ключевых терминов новых записей в book/ru, book/en; гейт `tools/verify.py NN --lang ru|en` — OK, lost=0.
3. Глоссарий: новые термины (напр. eGFR) во всех трёх README + счётчик «N терминов/条术语/terms» в summary согласован с таблицей.
4. Статистика (528 条, A 347) совпадает с апстримом.
5. 核实记录: новые файлы верификации — байт-в-байт через `git diff main origin/main -- 'docs/核实记录/<файл>'`.
6. Ожидаемые «ложные» различия: README.zh.md vs README.md (наша EN-primary политика), инфраструктура апстрима, которую мы не зеркалим (epub workflow, реклама/ads, sitemap, sync-stats.ps1).

Если дельта = 0 — субагентов НЕ создавать, честно отчитаться с пруфами. Не изготавливать работу, когда проверка показала, что её нет.

## Clone & Publication Rules (2026-09-18)

- Локальный клон: `~/github/HowToLiveBetter` (раньше был `~/github/htlb-ru` — переименован, имя «ru» вводило в заблуждение; пайплайн двуязычный CN→RU/EN). Не использовать старый путь.
- **Публикация в main форка — ТОЛЬКО через MR + squash-merge** (правило пользователя): рабочая ветка от `fork/main` → push → `gh pr create --repo dlgrv/HowToLiveBetter` → `gh pr merge N --squash --delete-branch`. Прямой push в main запрещён. Пример: tools-пайплайн опубликован MR #2 (squash → commit `2ad4ab3`).
- **Ветка — только от свежего `fork/main`** (`git fetch fork main && git checkout -B <branch> fork/main`), НЕ от локального `main` — он обычно отстаёт после squash-мержей, PR выходит с конфликтами; лечится rebranch + `git cherry-pick <sha>` + force-push. `gh pr merge` без номера PR с флагом `--repo` падает ("argument required") — всегда указывать номер. `origin` = upstream (push запрещён, это норма), пушить в `fork`.
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
- **Documentation articles**: verify.py FAIL on CJK in legal titles is expected; use factcheck gate (pass E) for semantic validation instead. CJK in `(title — explanation)` patterns are valid glosses, not translation errors.

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
