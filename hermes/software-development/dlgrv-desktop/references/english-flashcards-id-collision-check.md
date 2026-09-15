# English Flashcards ID Collision Check

## Pattern for avoiding duplicate IDs

When adding new words to `deck.src.json`, always check for existing IDs to prevent duplicates that could break progress tracking or cause UI confusion.

### Command to check for safe IDs

```bash
python3 -c "
import json
src = json.load(open('public/english/deck.src.json'))
ids = {w['id'] for w in src['words']}
new_words = ['through', 'generous', 'dedication', 'promised', 'owe', 'i-never-get-into-debt']
safe = [w for w in new_words if w not in ids]
print('Safe to add:', safe)
print('Already exist:', [w for w in new_words if w in ids])
"
```

### Example output

```
Safe to add: ['through', 'generous', 'dedication', 'promised', 'owe', 'i-never-get-into-debt']
Already exist: ['worth', 'property']
```

### Handling existing words

- If a word already exists in the core set (like 'worth', 'property'), skip adding it to avoid breaking existing progress tracking
- Use a different ID if you need to add the same word with different definitions or examples
- Consider whether the existing entry needs updating instead of duplicating

### After insertion

1. Run `node scripts/build-english-deck.mjs` to rebuild the compact deck
2. Verify with `grep -c '"tanya"' public/english/deck.json` that new words are included
3. Run relevant tests: `npx vitest run src/__tests__/english-sets.spec.ts`