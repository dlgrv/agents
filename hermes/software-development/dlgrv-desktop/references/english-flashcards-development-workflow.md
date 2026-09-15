# English Flashcards Development Workflow

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

### Progress isolation

- Core words: `localStorage['dlgrv.english.v1']`
- Tanya words: `localStorage['dlgrv.english.v1.tanya']` (hash-based key)
- Each set tracks its own FSRS-5 parameters and review history
- Reset button affects only the current set

### Development workflow

- Always develop in a separate worktree (`~/github/dlgrv.com-tanya`) off `origin/main` to avoid conflicts with other agents' changes
- Before PR: `git fetch origin main` and rebase if main has moved
- Never edit files in the main checkout (`~/github/dlgrv.com`) — use the worktree for all feature development
- e2e tests may show pre-existing flaky failures (3-6 out of 48) — these are environment timing issues, not regressions
- Test locally: `npx playwright test e2e/english.spec.ts` (requires dev server on :4923)

### Key implementation patterns

- State management: Use separate localStorage keys per set to avoid progress interference
- Theme persistence: Store theme preference separately from deck progress (`dlgrv.english.theme.v1`)
- Mode switching: Disable the set selector when no words are available for the selected set
- Build script: Extend `scripts/build-english-deck.mjs` to filter by `set` field and generate per-set compact decks
- Runtime filtering: Load the full deck but filter cards by selected set in `app.js`

### Testing strategy

- Unit tests: Use Vitest for sets module (`sets.js` + `sets.d.ts`) with 10 specs covering filtering and tuple generation
- E2E tests: Target `.card[data-slot="top"]` for logical top card, not DOM order
- Test both empty and populated sets to verify UI state and error handling
- Verify theme persistence survives mode switches and page reloads