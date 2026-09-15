---
name: tdd-frequency-tier-priority
description: "TDD workflow for frequency-tier priority in flashcard decks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, tdd, flashcards, frequency-tier, priority]
    related_skills: [test-driven-development, dlgrv-desktop]
---

# TDD for Frequency-Tier Priority Implementation

## Overview

This skill captures the workflow for implementing frequency-tier priority in flashcard decks using strict TDD. It emerged from implementing tier-based card prioritization in the dlgrv.com English flashcards system.

## When to Use

- Implementing frequency-tier or similar prioritization systems
- Adding priority-based sorting to queues
- Working with flashcard or learning systems where order matters
- When you need to prove sorting logic works before implementation

## TDD Workflow for Frequency-Tier Priority

### Phase 1: Audit and Tier Assignment

1. **Audit existing words** to assign frequency tiers:
   ```python
   # Subagent task for tier assignment
   delegate_task(
       goal="Audit all words and assign frequency tiers (high/mid/low)",
       context="Review word frequency, usage patterns, and learning priority. 
                High: common everyday words, mid: regular vocabulary, low: idioms/specific terms",
       toolsets=["terminal", "file"]
   )
   ```

2. **Save tier mapping** for reference:
   ```python
   # Save tier data as JSON for reuse
   write_file("tanya_tiers.json", json.dumps(tier_mapping, indent=2))
   ```

### Phase 2: Data Structure Extension

1. **Extend deck schema** to include tier field:
   - Add `tier` field to `deck.src.json` entries
   - Update build script to handle tier field
   - Pass tier through tuple index 10 in compact format

2. **Validation**:
   - Ensure all tanya words have `t-` prefix
   - Validate tier field is one of: 'high', 'mid', 'low'
   - Check for duplicate IDs across sets

### Phase 3: TDD Implementation

#### RED - Write Failing Test

```typescript
// src/__tests__/english-queue.spec.ts
describe('buildQueue with tier priority', () => {
  it('sorts fresh cards by tier: high → mid → low', () => {
    const cards = [
      tiered('t-low-word', 'low'),
      tiered('t-high-word', 'high'),
      tiered('t-mid-word', 'mid')
    ];
    const queue = buildQueue(cards, NOW, { date: 'd', new: 10, rev: 0 });
    
    // High priority cards should come first
    expect(queue.fresh[0].id).toBe('t-high-word');
    expect(queue.fresh[1].id).toBe('t-mid-word');
    expect(queue.fresh[2].id).toBe('t-low-word');
  });
});
```

Run test to verify it fails:
```bash
npx vitest run src/__tests__/english-queue.spec.ts
```

#### GREEN - Minimal Implementation

```typescript
// public/english/queue.js
function buildQueue(cards, now, opts) {
  // Sort fresh cards by tier (high → mid → low)
  const sortedFresh = [...opts.newCards].sort((a, b) => {
    const tierOrder = { high: 0, mid: 1, low: 2 };
    const aTier = a[10] || 'mid'; // Default to mid if no tier
    const bTier = b[10] || 'mid';
    return tierOrder[aTier] - tierOrder[bTier];
  });
  
  return {
    fresh: sortedFresh,
    // ... rest of queue logic
  };
}
```

Run test to verify it passes:
```bash
npx vitest run src/__tests__/english-queue.spec.ts
```

#### REFACTOR - Clean Up

1. Extract tier sorting logic into helper function
2. Improve variable names
3. Add type safety with tuple index constants

### Phase 4: Integration

1. **Update build script** to pass tier data:
   ```typescript
   // scripts/build-english-deck.mjs
   // Add tier to tuple index 10
   const tuple = [
     word.id,
     word.pos,
     word.ru,
     word.example,
     word.exampleRu,
     word.set,
     word.id,
     word.gloss,
     word.exampleRuExtra,
     word.tier || 'mid' // Default tier
   ];
   ```

2. **Update runtime** to use tier data:
   ```typescript
   // public/english/app.js
   const W = {
     // ... existing fields
     TIER: 10 // Tuple index for tier
   };
   
   // Use tier in buildQueue call
   ```

### Phase 5: Full Testing

1. **Unit tests**:
   ```bash
   npx vitest run src/__tests__/english-queue.spec.ts
   npx vitest run src/__tests__/english-sets.spec.ts
   ```

2. **E2E tests**:
   ```bash
   npx playwright test e2e/english.spec.ts
   ```

3. **Build verification**:
   ```bash
   node scripts/build-english-deck.mjs
   python3 -c "import json; d=json.load(open('public/english/deck.json')); print(f'Tiered words: {sum(1 for w in d[\"w\"] if w[10])}')"
   ```

## Common Patterns

### Tier Assignment Strategy

- **High (0)**: Common everyday words, essential vocabulary
- **Mid (1)**: Regular vocabulary, moderate frequency
- **Low (2)**: Idioms, specific terms, low-frequency phrases
- **Default**: 'mid' for words without explicit tier

### Queue Sorting Pattern

```typescript
const tierOrder = { high: 0, mid: 1, low: 2 };
const sorted = array.sort((a, b) => {
  const aTier = a[tierIndex] || 'mid';
  const bTier = b[tierIndex] || 'mid';
  return tierOrder[aTier] - tierOrder[bTier];
});
```

### Data Flow Pattern

1. **Source**: `deck.src.json` with `tier` field
2. **Build**: Script compiles tier into tuple index 10
3. **Runtime**: App uses `W.TIER` (index 10) for sorting
4. **UI**: Cards appear in tier order (high → mid → low)

## Pitfalls to Avoid

1. **Test-first mindset**: Always write failing test before implementation
2. **Default tier**: Words without tier default to 'mid', not undefined
3. **Stable ordering**: Within same tier, maintain original deck order
4. **Tuple index consistency**: Use constants (W.TIER) not magic numbers
5. **Progress isolation**: Each set uses separate localStorage keys

## Verification Checklist

- [ ] RED test fails as expected
- [ ] GREEN test passes with minimal code
- [ ] REFACTOR improves without breaking tests
- [ ] All unit tests pass
- [ ] E2E tests pass
- [ ] Build script produces correct output
- [ ] Tier data flows through entire pipeline
- [ ] Default tier works for non-tiered words

## Integration with dlgrv-desktop Skill

This skill extends the dlgrv-desktop skill's English flashcards functionality. When working on frequency-tier features:

1. Use the dlgrv-desktop skill for project structure and user preferences
2. Use this skill for TDD and tier-specific implementation patterns
3. Follow the worktree isolation rule from dlgrv-desktop
4. Use the existing test patterns from dlgrv-desktop references

## Example Implementation

See the actual implementation in:
- `public/english/queue.js` - Queue sorting logic
- `scripts/build-english-deck.mjs` - Tier compilation
- `src/__tests__/english-queue.spec.ts` - Test examples
- `public/english/app.js` - Runtime usage
