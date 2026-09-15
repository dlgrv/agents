# Blog articles: pipeline, renderer limits, TOC/typography

READ before adding or editing an article in `public/blog/`. Session source: `how-llm-works`
(Sept 2026) — the whole LLM-explainer workflow incl. a TOC redesign the user drove.

## Pipeline (how an article ships)

1. `public/blog/<slug>/index.md` — the article (markdown, subset below).
2. Add an entry to `public/blog/index.json` (list rendered on /blog/) — keep its title/annotation
   in sync with the article h1 (they drifted once; a skills-checklist audit caught it).
3. `npm run build:pages` → `scripts/build-blog-pages.mjs` renders HTML, injects slug into sitemap.
4. Verify: `npx vitest run src/__tests__/agent-readable.spec.ts` (asserts sitemap contains the
   slug, article HTML exists, ≥500 chars) + `npx biome check <changed files>`. ~600 unit tests
   must stay green; pre-existing `tsc` errors in `english-swipe.spec.ts` on the branch are NOT
   yours (triage per SKILL.md § npm run check).
5. Preview: serve on **`npx vite --port 5175 --strictPort`** — the user's bookmarks/expectations
   point at 5175 (config's 4923 is often busy and Vite silently drifts to 517x otherwise;
   `--strictPort` ends the drift). If the port is held, `lsof -ti tcp:5175 | xargs kill` first.
   The server dies between calls/sessions — restart, then poll `curl -s -o /dev/null -w
   '%{http_code}'` until 200 BEFORE Playwright screenshots (ERR_CONNECTION_REFUSED there = dead
   server, not broken SVG). Then `desktop_preview` the live URL.

### Preview server resilience (added Sept 2026)

**On the Linux server**, the preview stand (`http://193.148.253.171:4173/blog/`) is now a
systemd service (`dlgrv-stand.service`) to avoid crashing between sessions. It auto-restarts
on failure and logs to `/tmp/stand-health.log`. **Do NOT run `bash scripts/preview-stand.sh`**
or `vite preview` — those are legacy. For debugging, use:
- `systemctl status dlgrv-stand` — service status
- `journalctl -u dlgrv-stand -f` — live logs
- `systemctl restart dlgrv-stand` — force restart
4. Verify: `npx vitest run src/__tests__/agent-readable.spec.ts` (asserts sitemap contains the
   slug, article HTML exists, ≥500 chars) + `npx biome check <changed files>`. ~600 unit tests
   must stay green; pre-existing `tsc` errors in `english-swipe.spec.ts` on the branch are NOT
   yours (triage per SKILL.md § npm run check).
5. Preview: serve on **`npx vite --port 5175 --strictPort`** — the user's bookmarks/expectations
   point at 5175 (config's 4923 is often busy and Vite silently drifts to 517x otherwise;
   `--strictPort` ends the drift). If the port is held, `lsof -ti tcp:5175 | xargs kill` first.
   The server dies between calls/sessions — restart, then poll `curl -s -o /dev/null -w
   '%{http_code}'` until 200 BEFORE Playwright screenshots (ERR_CONNECTION_REFUSED there = dead
   server, not broken SVG). Then `desktop_preview` the live URL.

### Server stand (agent runs on the Linux server; user reads via a public URL)

When Hermes runs server-side, the repo clone is `/root/github/dlgrv.com` and preview is the
stand: **systemd service `dlgrv-stand.service`** — one rebuild of blog pages + figures, then a **3s
watchdog** re-running `build-blog-pages.mjs` + `build-figures.py` whenever
`public/blog/**`, `pages.css` or the scripts change, under **vite dev (live-reload) on :4173**.
Static `vite preview`/`dist/` was replaced deliberately — it served stale builds; the user
wants edits visible immediately, and with the watchdog editing `index.md` alone is enough (no
manual rebuild/restart; the user's tab updates itself). `scripts/stand-health.sh` is obsolete;
use `journalctl -u dlgrv-stand -f` for logs.

Verify-before-report loop for every edit: sleep ~6s (watchdog interval), then
`curl -s http://193.148.253.171:4173/blog/<slug>/ | grep -c '<phrase from the new text>'` — report
done only at count 1 (and 0 for a removed phrase). Grepping immediately after the save races
the watchdog. If the user reports Cyrillic mojibake, check the SERVED bytes first
(`curl -s <url> | grep 'кириллица'`) — clean UTF-8 on disk and in the response means a client
display artifact, not file corruption.

## Renderer subset (build-blog-pages.mjs) — WRITE INSIDE IT

Supported: `## / #` → h3, `**bold**`, `*italic*`, `` `inline code` ``, `- ` bullet lists,
`[text](#anchor)` links (in-page anchors) and `[text](https://…)` external links (open in a new
 tab — the URL rule once matched only anchors, so external URLs got rewritten into relative
 `/blog/<slug>/https:…` paths; check any new link kind against that rewrite), `![alt](<slug>/<file>.svg)` → `<img loading="lazy">`
(figure files live next to `index.md` in the article dir). Anchors are auto-generated on headings.

NOT supported (leaks raw markdown into HTML — rewrite before building):
- ``` fenced code blocks — use inline code or prose instead;
- `>` blockquotes; tables; numbered lists GLUE INTO ONE PARAGRAPH (only `- ` works).

## Figures: hand-written SVG for diagrams, matplotlib→PNG for plots

Decision the user approved for the zero-client-JS static site (session `how-llm-works`, Sept 2026):

- **Diagrams (pipeline, boxes-and-arrows): hand-written SVG** checked into `public/blog/<slug>/`.
  Matplotlib is bad at block diagrams; hand SVG gives full editorial control of the layout.
- **Function plots / distributions (curves, bars, softmax): matplotlib → PNG** via
  `scripts/build-blog-figures.py` (run `python3 scripts/build-blog-figures.py`, then
  `npm run build:pages`). Draws from real math (numpy), not hand-guessed Bézier curves.
  **PNG fallback:** SVGs can fail lazy-loading or CSS filters; PNG ensures all diagrams render.
  **Max width: 760px** (previously full-width, up to 1221px); all figures are now compact and centered.
  **Text scale:** sub-annotations increased from 12.5 to 13.5 to maintain readability at reduced size.
- **Text collisions in matplotlib:** When multiple annotations are stacked vertically near a panel's bottom (e.g., a caption and a sub-caption), adjust their y-coordinates to avoid overlap. Use `note(ax, line, (0.5, -0.13), ...)` and `note(ax, sub, (0.5, -0.26), ...)` to spread them apart. Vision analysis after rendering is required to confirm no text is obscured.
- **Centered layout:** All figures must be explicitly centered in the article (equal left/right margins). Measure DOM offsets to verify, never rely on visual alignment; matplotlib figures use `figsize` and bbox padding to achieve this, hand-written SVGs require explicit `width`/`height` attributes and CSS centering.
- **Grayscale palette:** INK #111, MUTED #666, WARM #555, FAINT #e3e33, ACCENT #111. No colors except pure black/gray.
- **Typography scale:** Title 16, axis labels 13.5, annotations 13, sub-annotations 13.5 italic MUTED. Use Georgia serif everywhere (DejaVu Serif in matplotlib), no sans-serif leaks.
- **Annotation placement:** Never place text directly on curves; use leader lines to empty quadrants. Annotate computed values (e.g., "пик ≈ 0.39") with a white background rect if it overlaps data.
- **No layout shift:** Explicitly set `width` and `height` on every SVG/PNG root element to reserve space before load. Lazy-loading images can cause reflow if not dimensioned.
- **MathML rendering:** Ensure LaTeX formulas use `$...$` and `$$...$$`; never mix with unicode superscripts (σ, ¹⁰) — use mathtext `"10$^{-3}$"` for scientific notation.
**Formulas: MathML (Temml)** — LaTeX `$...$` and `$$...$$` prerendered to native MathML Core via `temml.cjs` in `build-blog-pages.mjs`. MathML inherits Georgia serif font from the article, no client JS, no client CSS, and renders natively in Chrome 109+, Safari 14+, Firefox. **No KaTeX** — it forces a separate font and breaks the serif typography. See `references/math-rendering.md` for setup and best practices.  
**See `references/blog-figures-pitfalls.md`** for common rendering issues and fixes: text collision avoidance, centered layout enforcement, PNG fallback usage, and annotation best practices.
**Mermaid: rejected for now** — needs client JS (or a prerender step the site doesn't have).

## Naive reader review workflow

**Before publishing**, validate that an article is understandable to non-technical readers:

1. Spawn a subagent with persona: `Ты — НАИВНЫЙ читатель без технического образования (гуманитарий, ML-термины не знаешь). Ты УЖЕ читал предыдущую версию статьи и оставил 12 запинок. Статью переписали. Твоя задача — перечитать её СВЕЖИМ взглядом (как будто видишь впервые) и проверить, закрыты ли проблемы.`
2. Provide the updated article at `/tmp/reader-task/article.md` and a list of previous pain points.
3. The subagent must return a structured report:
   - For each previous pain point: ЗАКРЫТО/НЕ ЗАКРЫТО + citation or new issue
   - New pain points if any
   - Step ratings (1–5)
   - Final verdict: publishable or not
4. Iterate fixes until the naive reader report shows all CLOSED and ratings ≥4.

**Template for the task context** (customize for each article):
```markdown
Ты — НАИВНЫЙ читатель без технического образования (гуманитарий, ML-термины не знаешь). Ты УЖЕ читал предыдущую версию статьи о [тема] и оставил [N] запинок. Статью переписали. Твоя задача — перечитать её СВЕЖИМ взглядом (как будто видишь впервые) и проверить, закрыты ли проблемы.

ПРЕДЫДУЩИЕ ЗАПИНКИ, которые должны были исправить:
1. [описание проблемы]
2. ...

ФОРМАТ ОТВЕТА: для каждой из [N] — ЗАКРЫТО/НЕ ЗАКРЫТО + цитата исправленного места (если закрыто) или описание проблемы (если нет). Затем: НОВЫЕ запинки, если появились. Затем: оценки шагов 1–[X] от 1 до 5. Затем: финальный вердикт — можно ли публиковать. Отчёт сохрани в /tmp/reader-task/naive-reader-report-v2.md.
```

Style — one rule the user set for ALL figures, hand SVG and matplotlib alike: **the article font
(Georgia serif) and grayscale ONLY**. No sans-serif/mono accents (system-ui kickers, Menlo token
labels were all removed), no hue anywhere. Palette: `#111 / #333 / #555 / #666 / #e3e3e3 /
#f5f5f5 / #fff`; "accent" = pure black + gray fill, a "final" block stands out via light-gray
fill + bold (not color); light-gray micro-labels darken to `#666` so they survive B/W printing.
matplotlib: `svg.fonttype: none` (text stays selectable/crisp), `savefig.bbox: tight`, and
**`mathtext.fontset: custom` with rm/it/bf = Georgia** — otherwise mathtext and missing-glyph
fallback (σ, ¹⁰, →) leak DejaVu Sans into the SVG. Panels near-square and large with fonts
sized up (a wide 4:1 multi-panel strip was rejected as unreadable; 2×2 grid of ~square panels
won). Every figure centers horizontally in the article (explicit user request — no
left-aligned figures); verify with real DOM offsets (left/right gaps equal), not by eye. Verify before shipping: `grep -o '#[0-9a-fA-F]\{3,6\}' f.svg | sort -u` shows grayscale
only, `grep DejaVu f.svg` = 0, `font-family` = Georgia everywhere.

Honest-data rules (user-driven):

- compute curves from the real formulas — true σ(x), true softmax(logits/T) on seeded logits;
- annotate COMPUTED numbers («пик ≈ 0.39»), label assumptions («сигмоида (худший случай)»);
- shared Y-scale (`sharey`) when panels are compared; per-panel caption line: bold takeaway +
  italic nuance.

Verification loop (caught 3 defects over 2 rounds):

1. Serve the SVG through the dev server, screenshot it with Playwright, `vision_analyze`, fix,
   repeat. Hand-coded diagram coordinates WILL be wrong first try (text collisions, arrow
   overshooting the box).
2. "Huge empty space below the figure" on a screenshot is usually the browser VIEWPORT, not the
   SVG — check `grep -o 'viewBox="[^"]*"' file.svg` (or `sips`) before "fixing" a tight bbox
   that isn't broken.
3. "Empty space to the LEFT of a centered figure" usually means the INK doesn't fill the viewBox:
   the `<img>` is centered as a whole, but dead space inside the SVG lands on one side (typical
   after reserving width for a right-hand label column the text never reaches — 28% of width was
   once measured empty). Measure the ink bbox before relayouting: `qlmanage -t -s 800 -o /tmp
   f.svg`, then PIL/numpy — threshold `<240`, `mask.any(axis=0)` → first/last inked column;
   rebalance block widths/label positions (or shrink the viewBox) until left and right padding
   are both ~3–9%. Fix the LAYOUT, never add CSS offsets to compensate.
4. Set explicit `width`/`height` attributes (= rounded viewBox dims) on every hand-written SVG
   root. viewBox alone + `loading="lazy"` lets the browser reserve the default 300×150 (or 0)
   until load — geometry measurements come back wrong and the page shifts (same
   no-layout-shift rule as images/fonts in SKILL.md).
5. matplotlib Cyrillic: Georgia lacks superscript glyphs — unicode `10⁻³` emits "Glyph missing"
   warnings; use mathtext `"10$^{-3}$"` instead.

## TOC (Оглавление) — minimal style the user stripped down themselves

Markdown form: `## Оглавление` followed directly by a `- ` list of `[title](#anchor)` links.
The build script wraps it into `<nav class="post-toc"><p>Содержание</p><ul>…`. The style evolved
through user corrections — an early gray card, then caps kicker + top rule + hairlines +
intro/outro italics + bolded terms were ALL rejected one by one. Final form (do not re-add any
of the removed decoration):
- plain link list: NO bullets, NO top rule, NO hairline separators between items;
- NO bold inside items and NO `toc-intro`/`toc-outro` classes — all items equal;
- kicker «СОДЕРЖАНИЕ» stays, but in the SAME serif as the body (a sans/system-ui kicker next to
  serif items reads as a font bug); compact line spacing (the airy leading was called out too).
Ordering pitfall (still true for any future item post-processing): `<li>` wrapping and `<a>`
conversion happen BEFORE text transforms, so a regex anchored on `(<li>…<a…>)` misses text inside
links — run transforms on the final string.

Completeness gate (user-caught gap): every stage named in the overview pipeline must have its own
step heading + TOC entry — «эмбеддинги» and «softmax» were buried inside other steps' prose/titles
and the reader couldn't find them. Name the stage in the step title, not just the prose.

CSS lives in `public/static/pages.css` under `.tl_article--post .post-toc` — keep it minimal
(no borders, no per-item decoration).

## Article typography & voice (user requirements)

- `.tl_article--post` class on article pages only (pages.css): 17.5px/1.7 — «типографика как в CV»,
  Telegraph-editorial chrome. Don't widen it to the whole site.
- **Цельный текст, not Q&A.** User: «давай не вопрос за вопросом, а оформим это как цельный
  понятный текст». Dialogue history is raw material, not the format.
- **Math must be walked with numbers** («каждая формула — прогнать числа глазами»). Textbook-
  style presentation was called too hard; the fix that landed: after every formula a small
  concrete numeric example COMPUTED with execute_code (never invented on the spot), plus a «это
  НЕ X» disambiguation where confusion is likely — layer width (d_model) vs context window got
  its own mini-table.
- **Define every term at first use, BEFORE the sentence that relies on it.** A section that
  opened «попадают в стопку слоёв» and used нейроны/ширина unexplained was rejected
  («сначала объясни про скрытые слои»); the fix: one plain-language paragraph (нейрон =
  крошечный счётчик, слой = тысячи счётчиков, сеть = десятки слоёв), THEN the property
  (same-width flow).
- **Rhythm: every paragraph hooks into the previous one — no orphan warning-paragraphs.** The
  width-vs-context block lands only after a lead-in from the width discussion («С шириной
  связана вторая величина, которую с ней часто путают»). When two sentences state one fact in
  different words, UNIFY them — «вектор той же ширины» + «выходит ровно один вектор» read as a
  contradiction; resolve into one sentence (один вектор на токен, той же ширины, «начитанный»
  слоями).
- **Numbered user feedback = a checklist: clear EVERY point in the same pass and verify each
  against the file before reporting done.** Delivering points 1/3/4 and silently skipping 2
  forces the user to re-ask and re-paste — a whole extra round-trip.
- **Close multi-stage flows with a glossary tie-up.** After text → токенизация → токены → номера
  → эмбеддинг, answer the beginner questions explicitly: token ≠ word («помочь» may be 2
  tokens), what the word-splitting step is called, whether the token is the word-piece or the
  number, what exactly an embedding is.
- **All examples in Russian.** English word-analogy examples (walked/walk/swim) get swapped for
  Russian ones («шёл» − «иду» = стрелка прошедшего времени; same arrow on «плыву» → «плыл»).
- **Intro: diagram first, then the chat example.** The pipeline image goes right after the
  lead-in line («…посмотрим на весь путь:») — no textual pipeline line duplicating the diagram.
  The generation example: each pass adds exactly ONE token, the model replies naturally (greets
  back), and a word splits mid-answer («по|мог») to demonstrate token ≠ word.
- **No drive-by personal anecdotes in the body** («из-за которого Леонид однажды застрял» was
  cut — the reader has no context for it). The person appears only in the authorship framing.
- **Structure = the data path** (user proposed, confirmed): tokens → hidden layers → ReLU →
  logits → temperature → streaming first; **training LAST** (it explains what the forward pass
  already showed). Simple numeric examples for every abstraction.
- **Authorship convention:** author = «Hermes Agent на GLM 5.3 Flash», framed as a конспект of
  the dialogue with the site author (Лёня). Honest attribution the user explicitly set — never
  present the article as the user's own writing, never as disembodied "AI wrote a blog post".
- Long explainer prose goes through **/sepia** (route: tech article) BEFORE building; then adapt
  the sepia output to the renderer subset (sepia loves fences/quotes the renderer can't render).
- **Footer: one service line, not a paragraph.** Each article page ends with an agent/indexer
  pointer (where the markdown source lives). It was a 4-line explanatory block ("This HTML
  document is the shareable full-page version…"); user asked to shrink it — now a single
  12px gray line under a hairline: `Markdown source: /blog/<slug>/index.md · more at /blog`.
  Keep it one line; the `<link rel="alternate">` in `<head>` already covers machines, the
  footer is a redundant courtesy.
