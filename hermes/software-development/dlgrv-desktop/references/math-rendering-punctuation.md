# Math rendering: punctuation attachment

Best practice for preventing line breaks between formulas and punctuation in blog articles.

## Problem

When an inline formula `$...$` is at the end of a line and the next character is punctuation (.,;:?!), browsers may break the line between the formula and the punctuation, leaving the punctuation orphaned on a new line alone:

```
У нас $n_x = 12288$ .
   ^
   punctuation alone
```
This happens because the formula is an inline element, and the punctuation is a separate text node.

## Solution

Move punctuation INSIDE the math span, before the closing `</span>`, so it inherits the `white-space: nowrap` property:

- ❌ Wrong: `$...$ .` → `</math></span>.`
- ✅ Correct: `$...$.` → `</math>.</span>`

This ensures the punctuation and formula stay together on the same line. The browser will break before the formula instead, keeping the entire unit intact.

## Implementation

In `scripts/build-blog-pages.mjs`, after `store.restoreAll()`, replace:

```js
// OLD (WJ-based)
return restored.replace(/(<\/span>)([.,;:!?)])/g, '$1\u2060$2');

// NEW (move punctuation inside)
return restored.replace(
  /<\/math><\/span>([.,;:!?])/g,
  '<\/math>$1</span>',
);
```

## Verification

After building, check that:
1. All punctuation appears inside `</math>.</span>` (not outside)
2. No orphaned punctuation appears on new lines in the rendered HTML
3. Test with both Chrome and Firefox (browsers differ in line-breaking rules)

## Why WORD JOINER (U+2060) fails

WORD JOINER is designed to prevent breaks within text, but browsers often ignore it between different inline elements (like `</math>` and `</span>` or between `</span>` and a following text node). Moving punctuation inside the nowrap span is more reliable.
