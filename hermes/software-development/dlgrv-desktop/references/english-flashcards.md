# /english — Tinder-style flashcards (public/english/)

Static page at `/english` (PR #90; plan `.hermes/plans/2026-09-07_154246-english-flashcards-swipe.md`).
NOT part of the FSD desktop app — plain static files in `public/english/`:
`index.html` (shell + 3-card stack + inline CSS), `app.js` (render, flip, drag/swipe, wheel,
keyboard, themes), `engine.js` (FSRS-5 scheduling), `queue.js` (session queue + same-session
echo), `deck.json` (130 B1 words). Progress persists in `localStorage['dlgrv.english.v1']`.
e2e: `e2e/english.spec.ts` (7 specs).

## Deck + direction

- `deck.json` uses a compact positional array format (arrays of values, not objects with
  repeated keys) — keep it; there is a converter/validator from the collection pipeline.
- Cards are BIDIRECTIONAL: direction (en→ru / ru→en) is chosen randomly **per queue entry** and
  carried as `{id, dir}`. Never re-roll direction on re-render/peek — the same card changed
  side when promoted (bug we hit). Echo words (failed → repeat same session) get a fresh dir.

## Stack lifecycle rules (4 bugs cost a debugging session — do not regress)

1. **Never reuse a flown-out card element.** After a swipe the top card flies out AND is
   removed from the DOM. It must NOT be recycled into a back slot: `fillSlot` clears the
   inline `opacity: 0` left by the fly-out, so the old card visibly "flies back into the
   deck". Back cards appear as FRESH elements with a fade-in (`card--enter`).
2. **Logical top ≠ DOM order.** Promotion moves content into `slots.top` (elements keep their
   positions), so the first DOM child is NOT the visible top card. The logical top is always
   `slots.top`, marked `data-slot="top"` (`back0`/`back1` similarly). NEVER target
   `stage.firstElementChild` for wheel/keyboard/fly-out — the trackpad swipe then animates an
   invisible flown-out card and "nothing happens" (user hit exactly this).
3. **Attach pointer listeners once per element.** Promoted elements keep their original
   listeners; stale element references + re-attachment caused double commits. `attachPointer(el)`
   reads the module-level `current` at event time (not a snapshot taken at attach).
4. **Input locks.** `animating` (fly-out/promotion in progress) and `dragActive` (pointer down)
   gate pointerdown/pointermove/wheel/keydown alike. Without them, rapid swipes interrupt a
   fly-out mid-flight and one gesture can commit two cards.

Promotion animates via CSS `transform`/`box-shadow` transitions driven by the slot classes
(`card--back0` → unmarked top); swap content WITHOUT resetting classes or forcing reflow — the
old `no-anim`-class + double-rAF hack flickers. Shadow: only the top card carries a shadow in
dark theme — back cards' shadows stack through the stack into a muddy glow (user flagged).

## Input details

- Trackpad two-finger swipe = horizontal `wheel` events: accumulate `deltaX` into the same drag
  offset as pointer-drag; past threshold → commit grade. **macOS natural scrolling inverts
  deltaX** — negate it (`-e.deltaX`); un-inverted, the card moves opposite to the fingers.
- Pointer drag tilts in 3D (`rotateY/rotateX` under `perspective: 1200px`); stamp «ЗНАЮ»/
  «НЕ ЗНАЮ» fades in past half-threshold. Keyboard: ←/→ grade, Space/↑ flip.
- Wiggle hint on load: top card rocks left-right WITH a horizontal shift (±26px) — tilt alone
  was too subtle to read as "swipeable".

## Themes (explicit user requirement)

- Dark = the user's **Cursor editor** theme (`Cursor Dark`) — colors extracted from the user's
  own VSCode/Cursor theme files, not invented. Light = the dlgrv.com blog/cv light palette.
- Stamps: outline style (colored border + colored text) — «ЗНАЮ» `#16C62D`, «НЕ ЗНАЮ» `#FF2D2D`,
  via `--stamp-know`/`--stamp-dont` per theme. A filled bright version (`#00E676`/`#FF1740`
  solid plaque) was tried and REVERTED — don't redo without asking.
- UI copy the user removed (keep removed): direction badges (en→ru/ru→en), the two bottom
  grade buttons (swipe/keyboard only), «тапни для перевода» hint.

## FSRS-5 engine (engine.js)

Ported 1:1 from **py-fsrs v5.1.3** (canonical FSRS-5). Implementing FSRS from memory failed
5/28 tests (wrong SInc usage of the new D, mean-reversion weights); the fix was pulling the
real reference and rewriting exactly — same rule as clone-originals: published algorithm →
real source, never from memory. 28 vitest specs pin canonical values (D0(Good)=5.282,
S0(Good)=w[2]=3.173, …). Tests build cards via a typed helper (string-literal `state` trips
the LSP/lint).

## Verification

```bash
cd /Users/dlgrv/github/dlgrv.com
npm run check                              # tsc + vitest + biome + steiger
npx playwright test e2e/english.spec.ts    # dev server must be up (see server pitfall)
```

e2e targets `.card[data-slot="top"]` — whenever DOM order and logical order can diverge,
target the marker, not `.first()`.

## Deck data sources & enrichment (researched 2026-09-08)

- Word list: **tyypgzl/Oxford-5000-words** (json of Oxford 3000/5000, OALD-derived; no
  license file). `deck.src.json` = list + our curated RU; built into `deck.json` by
  `scripts/build-english-deck.mjs` (compact positional tuples).
- **EN gloss (recommended primary): winterdl/oxford-5000-vocabulary-audio-definition**
  `data/oxford_5000.json` — measured **130/130 coverage** on our words (join by
  `word.lower()`, filter `cefr ∈ {b1,b2}`, disambiguate multi-sense by POS ⊆ ours).
  Sense-match verified correct on all 14 tricky homographs we had hand-fixed. Its example
  text ≡ our existing examples (same OALD source; 17/20 byte-identical, rest whitespace).
  Import OFFLINE into the build script — never live-fetch OALD (OUP ToS forbids scraping).
- **RU examples: NOT from ru.wiktionary** — measured only ~3–5/130 usable EN→RU example
  pairs (regex catches other languages' sections). Translate the 130 existing EN examples
  via LLM batch at import time → `exampleRu` + human skim (~20–30 min).
- Fallback RU cross-check: **Badestrand/russian-dictionary** (CC BY-SA 4.0) — RU-keyed CSVs
  with `translations_en` column; direction is inverted, use only to verify our RU.
- No ready-made EN↔RU CEFR deck with examples exists publicly (checked GitHub/Anki
  dumps) — do not search for one again.
- Attribution line on the page: «Word list © Oxford University Press (Oxford Learner's
  Dictionaries) · RU-переводы: ru.wiktionary.org (CC BY-SA)».
- When adding fields, extend the positional tuple + `FIELDS` map consistently (schema:
  tuple → 8 fields planned); `POS` can lie (`standard` was tagged adjective but RU gloss is
  the noun) — pick the winterdl sense by (RU gloss + pos), not pos alone.

## Multi-set mode (Tanya mode, 2026-09-11)

Support for multiple word sets via a `set` field in `deck.src.json` entries. Each set
has its own learning progress tracked in `localStorage['dlgrv.english.v1']` under a
separate key (`set` + hash of deck content). Use the `set` field to differentiate
between core words (e.g., "core") and lesson-specific words (e.g., "tanya").

### Implementation details

- Deck source format: `deck.src.json` entries include `"set": "core" | "tanya"` (fallback: "core")
- Build script: `scripts/build-english-deck.mjs` filters and compiles per-set decks
- Runtime: `app.js` loads the appropriate deck based on the selected mode
- Progress storage: Each set uses a separate localStorage key to avoid interference
- UI mode switch: Add a toggle button (e.g., "Тетя Таня 👩‍🏫") to switch between sets

### Deck structure example

```json
[
  {"word": "weather", "pos": "noun", "ru": "погода", "example": "The weather is nice today", "exampleRu": "Погода сегодня хорошая", "set": "core"},
  {"word": "scorching hot", "pos": "phrase", "ru": "невыносимо жарко", "example": "It's scorching hot in summer", "exampleRu": "Летом невыносимо жарко", "set": "tanya"},
  {"word": "freezing cold", "pos": "phrase", "ru": "леденящий холод", "example": "It's freezing cold in winter", "exampleRu": "Зимой леденящий холод", "set": "tanya"}
]
```

### Progress isolation (as IMPLEMENTED, PR #111)

- Core: `dlgrv.english.v1` (unchanged) · Tanya: `dlgrv.english.v1.tanya` ·
  Theme is GLOBAL: `dlgrv.english.theme.v1` · Mode choice: `dlgrv.english.mode.v1`
- Each set tracks its own FSRS-5 state and daily counters; reset (long-press theme)
  clears only the current mode's key.

### Implemented mode architecture (do not re-derive)

- Tuple index 9 = `set` (default `core`); validation in `sets.js` `validateWord(w, tanyaIds)`
  (pure, vitest-tested; build script imports it). **All tanya ids prefixed `t-`**
  (`through` → `t-through`) so lesson words may duplicate core words; core ids are NOT
  prefix-banned (future `t-shirt` legit) — build fails only on core-id↔tanya-id collision.
- `switchMode` checklist: save state → swap mode → load state → ensureCards →
  clear echo/stats/done → clear wheelTimer + wheelIgnore → reset animating/dragActive →
  **remove old stack elements + null slots BEFORE advance()** (promote assumes old top
  flew out via commitSwipe; a mode switch has no swipe — stale slots duplicate
  `data-slot="top"`) → advance() → updateModeToggle().
- Mode button disabled while the OTHER set is empty (empty deck = instant sessionDone).
  UI: fixed 120px width, weight 400, centered text (inline-flex), iconbtn hover scale.
- CSS gotcha: a `.pill--small` block placed BEFORE the base `.pill` rule gets overridden
  (equal specificity, later wins) — use `.pill.pill--small` after the base rule.
- window keydown flips on Space/Enter — guard `e.target.tagName === 'BUTTON'` so topbar
  buttons stay keyboard-operable.
- Multi-agent worktree rule (user requirement): /english feature work happens in a
  dedicated worktree (e.g. `~/github/dlgrv.com-tanya`), never the main checkout — other
  agents work concurrently. Fresh worktree: npm install + copy plan; revert
  package-lock.json npm-version drift with `git checkout --`.

### Adding new words to lesson sets (2026-09-11)

- **ID rule**: Lesson words MUST have IDs prefixed with `t-` (e.g., `weather` → `t-weather`, `scorching hot` → `t-scorching-hot`). Core words may use any valid slug.
- **Collision check**: Before insertion, verify the chosen ID does not exist in the target set:
  ```bash
  python3 -c "import json; d=json.load(open('public/english/deck.src.json')); ids={w['id'] for w in d['words'] if w.get('set') == 'tanya'}; print([w for w in ['word1','word2'] if w not in ids])"
  ```
- **Set field**: Always specify `"set": "tanya"` (or other lesson set) for new words. The build script defaults to "core" if unset.
- **Build and verify**: After insertion, run `node scripts/build-english-deck.mjs` and verify with `grep -c '"tanya"' public/english/deck.json`.
- **Testing**: Run `npx vitest run src/__tests__/english-sets.spec.ts` to validate filtering and tuple generation. Skip full `npm run check` if it shows pre-existing unrelated failures.
- **Progress tracking**: Each set uses a separate localStorage key (Core: `dlgrv.english.v1`, Tanya: `dlgrv.english.v1.tanya`). Reset clears only the current set's progress.
