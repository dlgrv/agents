---
name: blog-coherence-audit
description: Audit blog posts for coherence and logical flow.
---

# Blog coherence audit

Use when editing technical blog posts (especially for dlgrv.com) to catch logical gaps, term inconsistencies, and broken references between sections.

## Audit categories

### 1. Symbols before introduction

- Every variable ($z$, $w$, $T$, etc.) must be introduced by name before use
- Check: symbols appear in text before formulas, not just in formulas
- Fix: add plain-text definition (e.g., «let's call the result z») before formula

### 2. Term consistency

- Same concept = same term throughout (no «logit» vs «score» vs «slot» for the same thing)
- English terms in parentheses must have analogies or be cut
- Fix: unify terminology at first mention

### 3. Cross-step bridges

- Start of section N must not assume knowledge from section N-1 without reference
- Check: «as we saw in step 2» or «remember from before» where needed
- Fix: add bridge phrase or move concept earlier

### 4. Anaphora clarity

- «It», «this», «our», «that» must refer to the immediately preceding noun
- Check: ambiguous pronouns in complex sentences
- Fix: replace with explicit noun (e.g., «our model» instead of «it»)

### 5. Numbers with source

- Every number must have a source (computed, promised earlier, or example)
- Check: «4096», «~4 times», «0.25» without context
- Fix: add brief justification («4096 — typical model width», «0.25 — max sigmoid value»)

### 6. Formula context

- Every formula must have plain-language explanation
- Check: formulas without surrounding text explaining their purpose
- Fix: add one sentence before/after: «This formula shows how we compute…»

### 7. Machine-readable metadata placement

- Agent-facing metadata (index.json, llms.txt, openapi.json) must not intrude on human-readable content
- Check: machine-readable blocks appear at the top of the page, displacing the main article
- Fix: relocate agent metadata to a visually distinct, unobtrusive section at the bottom of the page with clear styling (e.g., muted colors, small font, border-top)
- Never remove metadata entirely — it's needed for search and scraping

### 8. Formula display context (NEW 2026-09)

- **Inline vs display:** Small formulas (1–2 lines, ≤2 rows) can be inline ($...$); multi-line matrices, long equations, or examples with multiple columns must be display ($$...$$)
- **Browser rendering limitation:** Inline MathML with multi-row matrices often renders with incorrect vertical stretch in browsers (skewed brackets, partial height)
- **Fix:** Always use display mode ($$...$$) for matrices with 3+ rows or equations spanning multiple lines
- **Best practice:** Prefer display mode for any formula that is not a single inline expression

### 9. Math notation in code spans (NEW 2026-09)

- **Rule:** Mathematical expressions (formulas, derivatives, ratios, Greek symbols, ≤≥≠) must use $...$, not backticks (`...`)
- **Code spans for:** Python code, variable names (`.shape`, `np.`), syntax (`def`, `import`), operators (`:=`)
- **Fix:** Replace all code spans containing `=`, `<`, `>`, `≤`, `≥`, `≠`, `±`, `×`, `÷`, `∑`, `∏`, `∫`, `√`, `∞`, or ratios like `dJ/dw` with $...$
- **Pitfall:** `dJ/dw`, `db`, `b` are derivatives/variables, not code — they must be in LaTeX
- **Tool:** Run `npm run check:math` to catch violations; this is now part of `npm run check` (CI gate)
- **Why:** Math in code spans renders as monospace, breaks LaTeX rendering, and confuses readers expecting code

## Workflow

1. Read the post section by section (## heading to next ##)
2. For each category, flag issues with:
   - Exact quote
   - Location (L line number)
   - Reader impact («feels like X is missing»)
   - Fix suggestion (one line)
3. Group by severity: critical (breaks understanding), medium (confusing but not blocking), minor (style)
4. Report without editing — get user approval before fixes

## Pitfalls

- **Symbol over-introduction**: Avoid multiple symbols in one formula without text definitions
- **Cross-step reference**: Always bridge between sections with explicit references
- **Formula without context**: Never present a formula without explaining what it represents
- **Term drift**: Same concept must use same term throughout (no synonyms without explanation)
- **Metadata intrusion**: Agent metadata blocks human-readable content → relocate to bottom with visual separation
- **Inline matrix rendering bug**: Inline $...$ with multi-row matrices often renders with skewed brackets due to browser MathML stretch limitations → always use $$...$$ for matrices with 3+ rows
- **Display mode preference**: Prefer display mode ($$...$$) for any formula that is not a single inline expression to avoid browser rendering quirks
