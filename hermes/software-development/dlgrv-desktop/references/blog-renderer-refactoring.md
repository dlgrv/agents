# Blog renderer refactoring guide

**When:** The `scripts/build-blog-pages.mjs` renderer accumulates technical debt and needs cleanup.
**Goal:** Remove kludges while preserving byte-identical HTML output for all articles.
**Gate:** All 63 blog-renderer.spec.ts tests must pass after each refactoring step.

## Current kludges (as of Sept 2026)

### 1. Placeholder-based TokenStore (MATHPLACEHOLDER/CODEPLACEHOLDER/TABLEPLACEHOLDER)
- **Problem:** Three different placeholder protocols with different restoration loops.
- **Kludge:** Code is restored twice — once in `extractTables`, once in the main loop.
- **Solution:** Unified `TokenStore` class with typed placeholders and ordered restoration (code→table→math or via `restoreAll`).

### 2. Temporary `<oli>` tag for ordered lists
- **Problem:** NUmbered lists are rendered as `<oli>…</oli>` then regex-replaced into `<ol><li>…</li></ol>`.
- **Kludge:** Post-processing regex that fails on nested lists or complex markup.
- **Solution:** Extract numbered lists in the same phase as tables (extract-фаза), render directly as `<ol><li data-ordered>…</li></ol>`.

### 3. Lone `$..$` display math rule as a separate pre-pass
- **Problem:** Math formulas are processed twice — once in a pre-pass to convert `$..$` on its line to display, then again in `renderMath`.
- **Kludge:** Two-phase math handling with duplicated logic.
- **Solution:** Move the lone-$-display rule inside `renderMath` — one math pass, not two.

### 4. Duplicate inline rules in `extractTables`
- **Problem:** `extractTables` has its own inline function that duplicates logic from the main loop.
- **Kludge:** Code duplication between `extractTables` and the main renderer.
- **Solution:** Extract a common `inlineToHtml(code, bold, em, links)` function used by both.

### 5. `normalizeListBreaks` as a separate pre-pass
- **Problem:** List break normalization happens before extraction, but should be part of the list extraction phase.
- **Solution:** Merge `normalizeListBreaks` into the extract-фаза for lists.

### 6. Chain of ~25 `.replace()` calls in `mdToHtml`
- **Problem:** The main `mdToHtml` function is a long chain of string replacements, hard to read and maintain.
- **Kludge:** Monolithic function with mixed concerns (extraction, block rendering, inline rendering, restoration).
- **Solution:** Split into phases: extract (code/math/tables/lists) → block (headings/paragraphs) → inline (strong/em/links/img) → restore.

### 7. Agent vs. manual refactoring cost tradeoffs
- **Problem:** Subagents can take 40+ minutes due to iterative debugging loops and model limitations, while simple fixes can be done in minutes by an agent familiar with the codebase.
- **Kludge:** Long-running subagent sessions with timeouts and context limits.
- **Solution:** When the fix is small (≤3 lines) and the agent knows the codebase, apply it directly with a diff gate. Only delegate to subagents when the task requires many independent checks or large-scale reading. Pattern: `git stash` → baseline capture → manual fix → `diff` → test → commit. Saves 30+ minutes per small fix.

## Safe refactoring approach

1. **Baseline capture:** Run `node scripts/build-blog-pages.mjs`, copy all generated HTML (`public/blog/*/index.html`, `public/blog/index.html`) to `/tmp/before/`.
2. **Iterative refactoring:** Apply one kludge fix at a time. After each change:
   - Rebuild: `node scripts/build-blog-pages.mjs`
   - Diff: `diff -r /tmp/before/ public/blog/` (must be empty)
   - Test: `CI=true npx vitest run src/__tests__/blog-renderer.spec.ts` (must be 63/63 green)
3. **If HTML changes:** Revert the step and document why in the verdict (some changes may fundamentally alter output).
4. **Final verification:** Full diff check + both spec files (blog-renderer.spec.ts + agent-readable.spec.ts).

## Decision points

- **Order of restoration:** Code before table or table before code? Test both and see which preserves existing behavior.
- **List extraction depth:** Should nested lists be handled in the extract phase or left to the block renderer?
- **Math scope:** Should the lone-$-display rule apply to all math or only certain contexts?

## Example refactoring step: Unified TokenStore

```typescript
// Before: three separate placeholders
const MATH_PLACEHOLDER = 'MATHPLACEHOLDERxyz';
const CODE_PLACEHOLDER = 'CODEPLACEHOLDERxyz';
const TABLE_PLACEHOLDER = 'TABLEPLACEHOLDERxyz';

// After: unified store with types
class TokenStore {
  private tokens = new Map<string, {type: 'math' | 'code' | 'table'; content: string}>();
  
  placeholder(type: 'math' | 'code' | 'table', content: string) {
    const id = `TOKEN_${type}_${Date.now()}`;
    this.tokens.set(id, { type, content });
    return id;
  }
  
  restoreAll(html: string) {
    // Restore in correct order: code → table → math
    let restored = html;
    for (const [id, token] of this.tokens) {
      if (token.type === 'code') restored = restored.replace(id, token.content);
    }
    for (const [id, token] of this.tokens) {
      if (token.type === 'table') restored = restored.replace(id, token.content);
    }
    for (const [id, token] of this.tokens) {
      if (token.type === 'math') restored = restored.replace(id, token.content);
    }
    return restored;
  }
}
```

## Step 1 done (unified token store) — verified pitfalls

Step 1 (Sept 2026, branch `feat/blog-binary-classification`) replaced all three placeholder protocols with one `createTokenStore()`: token format `\u0000<type>#<n>\u0000` (type = code|table|math), single `TOKEN_RE`, restoration `store.restoreAll()` once at the end of `mdToHtml`. Byte-identical, 63/63. Non-obvious traps hit on the way:

- **The `.replace(/<p>(TABLEPLACEHOLDER\d+ENDTABLE)<\/p>/g, '$1')` rule is LOAD-BEARING** — it unwraps `<p><table>…</table></p>` (table token lands inside a paragraph built by the `</p><p>` pass). Removing it as "dead code" breaks byte-identity. Port it to the new token format: `/<p>(\x00table#\d+\x00)<\/p>/g → '$1'`.
- **Nested tokens need a FIXPOINT restore, not one pass per type.** A code span inside a table cell is parked INSIDE the parked table HTML, so a single code→table→math cycle leaves the code token unrestored (this is exactly the old "restore code twice" bug the second end-of-chain code pass covered). `restoreAll` must loop `code→table→math` until the string stops changing (bounded, e.g. 10 iterations).
- **The removed full-code `.replace(/`([^`]+)`/g, '<code>$1</code>')` rule was a true no-op** for all current data (it only ever ran over already-restored table/math HTML; both articles have paired backticks per line). Verified before removing; re-verify if articles change.
- **`diff -r /tmp/before public/blog` in an `&&` chain masks a crashed node build** — the diff "passes" when the build never wrote files. Chain: `node build; echo exit: $?` FIRST, then diff; a green diff alone is not evidence.
- `\u0000` never occurs in article markdown and no regex pass reacts to it → token is inert everywhere; NUL-leak check: `grep -rlP '\x00' public/blog/`.
- Biome ignores `scripts/` (pre-commit hook can't flag this file); tests never reference placeholder names, so internal protocol is free to change.

## References

- `src/__tests__/blog-renderer.spec.ts` — test suite for the renderer (44 tests)
- `src/__tests__/agent-readable.spec.ts` — integration tests for blog generation (19 tests)
- `scripts/build-blog-pages.mjs` — the renderer to refactor (~340 lines)