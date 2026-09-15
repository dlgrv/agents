# Case: FSRS-5 + B1 flashcards deck (dlgrv.com/english, 2026-09)

## FSRS-5 essentials (as ported)

- Canonical source: **py-fsrs v5.1.3** (Python; ts-fsrs is the TS twin). 19 weights `w[0..18]`.
- `D0(r) = w[r-1]` clamped 1..10 (D0(Good)=5.282); `S0(Good)=w[2]=3.173` — FSRS-4.5 values (17 params, different forgetting curve) do NOT apply.
- SInc uses the NEW D after mean-reversion toward w[4] — getting this wrong is the classic memory-port bug.
- Anki-style learning steps kept on top of FSRS: 1 min / 10 min; same-session relearn "echo" (failed card returns ~3 cards later in the same session).
- Grade mapping from UI events: fast swipe right = Easy, slow right = Good, **peeked translation then right = Hard** (no reward for peeking), left = Again/Hard by latency.
- Reaction clock pauses on `visibilitychange` (tab hidden ≠ slow recall).

## Deck building (vocabulary)

- Word list: Oxford 5000 filtered to target CEFR level (B1), deduped against lower levels (A1/A2), ranked by real frequency (`wordfreq` zipf).
- Translations: parsed from ru.wiktionary per-POS; **manual cleanup pass required** — homonyms produce wrong senses (e.g. "glad" → «гладиолус" from a botanical homograph).
- Two directions per card (en→ru / ru→en) chosen randomly at draw — recognition ≠ production; user asked for this explicitly.
- Storage: positional compact JSON (arrays, no repeated keys) + editable `deck.src.json` + build script; ~25 KB for 130 words.
- Progress: `localStorage` only (`dlgrv.english.v1`, short keys, history tuples capped at 32).

## Verification pattern that worked

- Unit tests seeded with constants copied from the reference's own test suite (not self-computed).
- UI verified via the repo's existing Playwright e2e suite extended with feature specs (drag, wheel/trackpad swipe, keyboard, echo, theme persistence) — more reliable than ad-hoc manual browser/preview checks, which stalled on a stuck pane this session.
- Full gate: `npm run check` (tsc + vitest + biome + linter) before commit.
