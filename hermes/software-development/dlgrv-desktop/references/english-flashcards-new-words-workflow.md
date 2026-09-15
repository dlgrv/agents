# English Flashcards New Words Workflow

## Adding new words to a lesson set (Tanya mode)

This workflow covers adding new words to lesson-specific sets (e.g., "tanya") while avoiding collisions and maintaining build/test integrity. Follow these steps for each new word or batch of words.

### 1. Word preparation and ID assignment

- **Format**: Provide word/phrase pairs in any format (plain text, CSV, etc.). The agent will parse and normalize.
- **ID rule**: Lesson words MUST have IDs prefixed with `t-` (e.g., `weather` → `t-weather`, `scorching hot` → `t-scorching-hot`). Core words may use any valid slug.
- **Collision check**: Before insertion, verify the chosen ID does not exist in the target set:
  ```bash
  python3 -c "import json; d=json.load(open('public/english/deck.src.json')); ids={w['id'] for w in d['words'] if w.get('set') == 'tanya'}; print([w for w in ['word1','word2'] if w not in ids])"
  ```
- **Set field**: Always specify `"set": "tanya"` (or other lesson set) for new words. The build script defaults to "core" if unset.

### 2. Insertion into deck.src.json

- **Manual insertion**: Add entries to `public/english/deck.src.json` following the existing tuple schema (word, pos, ru, example, exampleRu, set, id, gloss, exampleRuExtra). Ensure:
  - `set` is set to the lesson name (e.g., "tanya")
  - `id` follows the `t-` prefix rule for lesson words
  - All required fields are present
- **Validation**: The build script will reject words without proper `t-` prefix or duplicate IDs.

### 3. Build and verification

- **Run build script**: Compile the updated source into the runtime deck:
  ```bash
  node scripts/build-english-deck.mjs
  ```
- **Verify output**: Check that new words appear in the correct set:
  ```bash
  grep -c '"tanya"' public/english/deck.json
  ```
  The count should match the number of words added.
- **Check tuple structure**: Ensure the build script produces valid tuples (no missing fields, correct field order).

### 4. Testing

- **Unit tests**: Run the sets module tests to verify filtering and tuple generation:
  ```bash
  npx vitest run src/__tests__/english-sets.spec.ts
  ```
- **E2E tests**: Test the UI with the new words:
  ```bash
  npx playwright test e2e/english.spec.ts
  ```
  Focus on mode switching, card display, and progress tracking for the new set.
- **Avoid full test suite**: Skip `npm run check` if it shows pre-existing unrelated failures (window-state, etc.).

### 5. Progress tracking

- **Storage keys**: Each set uses a separate localStorage key:
  - Core: `dlgrv.english.v1`
  - Tanya: `dlgrv.english.v1.tanya`
- **Reset behavior**: The reset button clears only the current set's progress, not others.
- **Theme persistence**: Theme preference is global (`dlgrv.english.theme.v1`) and survives mode switches.

### 6. Development environment

- **Worktree isolation**: Always work in a separate worktree (`~/github/dlgrv.com-tanya`) off `origin/main`.
- **Conflict avoidance**: Before PR, fetch and rebase on main: `git fetch origin main && git rebase origin/main`.
- **Never edit main checkout**: Use the worktree for all feature development.

### Example workflow

1. User provides: "freezing cold - леденящий холод"
2. Agent assigns ID: `t-freezing-cold`
3. Checks collision: `python3 -c "..."` (ID not found)
4. Inserts into deck.src.json with `set: "tanya"`
5. Runs build: `node scripts/build-english-deck.mjs`
6. Verifies: `grep -c '"tanya"' public/english/deck.json` (count increases)
7. Tests: `npx vitest run src/__tests__/english-sets.spec.ts`
8. Commits and creates PR

### Pitfalls to avoid

- **Duplicate IDs**: Lesson words with `t-` prefix can still collide with core words. Always check both sets.
- **Missing set field**: Forgetting `"set": "tanya"` defaults to core, causing unexpected behavior.
- **Build script failures**: Missing fields or incorrect tuple structure will stop the build.
- **Test pollution**: Pre-existing test failures in unrelated modules (window-state, etc.) are not caused by your changes.
- **Storage key mixup**: Never manually edit localStorage keys — let the runtime handle them.
- **Worktree isolation**: Always work in a separate worktree (`~/github/dlgrv.com-tanya`) off `origin/main` to avoid conflicts with other agents' changes.
- **Git workflow**: Never push straight to main — create a branch, commit, push, PR, squash-merge.
- **Build validation**: The build script enforces `t-` prefix for tanya words and rejects duplicates — ensure all new words pass validation before testing.
- **Progress isolation**: Each set uses separate localStorage keys — verify that switching sets doesn't mix progress.
