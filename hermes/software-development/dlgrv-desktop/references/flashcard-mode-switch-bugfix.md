# Mode Switch DOM Cleanup Bugfix

## Problem
When switching between flashcard sets (e.g., core → tanya), old stack elements remained in the DOM under the new card. This caused visual artifacts: two `data-slot="top"` elements, one visible, one hidden behind.

## Root Cause
The `advance()` function assumes the old top card has already flown out via `commitSwipe()`. However, during a mode switch there is no swipe — the UI jumps directly to the new set's first card. The old stack elements were never cleaned up.

## Solution
In `promote()` function, manually remove all old stack elements before advancing:

```javascript
function promote() {
  // Remove old stack elements if they exist
  const slots = document.querySelectorAll('[data-slot]');
  for (const slot of slots) {
    if (['top', 'back0', 'back1'].includes(slot.dataset.slot)) {
      slot.remove();
    }
  }

  // Clear slot references
  window.slots = {};

  // Now advance safely
  advance();
}
```

## Pitfall
Never assume `commitSwipe` runs during mode switches — it only triggers on user swipes. Always clean up manually when switching sets programmatically.

## Verification
- Test mode switch with e2e: `npx playwright test e2e/english.spec.ts -g 'mode toggle'`
- Check for duplicate `data-slot="top"` elements after switch
- Ensure only one card visible at all times