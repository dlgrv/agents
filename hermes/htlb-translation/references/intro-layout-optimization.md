# Intro Paragraph Layout Optimization Reference

## Problem

When Russian text in chapter introductions is longer than the original Chinese text, the `.intro` paragraph may appear cramped with excessive whitespace to the right. This occurs because the default `.intro` CSS limits line length to 72 characters (~600px) while content cards extend to 900px.

## Solution

Remove the `max-width:72ch` constraint from `.intro` and allow it to span the full content width (`max-width:100%`) to match card layout and eliminate visual imbalance.

## Implementation

In CSS, change:
```css
.intro{margin:0 0 20px;color:var(--t2);font-size:14px;max-width:72ch}
```
to:
```css
.intro{margin:0 0 20px;color:var(--t2);font-size:14px;max-width:100%}
```

## Pitfalls

- **Scope**: This fix applies only to web interfaces (index.html), not to markdown source files. Do not alter markdown chapter formatting — the constraint is purely for web rendering optimization.
- **Verification**: After applying the fix, verify that the intro text flows naturally across the full width without awkward line breaks or excessive whitespace on desktop screens. The change should eliminate the "free space" effect on the right side of longer Russian introductions.
- **Fallback**: If full width causes readability issues on very large screens, consider `max-width:85ch` as a compromise between the original 72ch and full width.

## Quality Assurance

- Test on multiple screen sizes (desktop, tablet, mobile)
- Confirm the fix doesn't break existing responsive behavior
- Ensure the change doesn't affect other CSS classes that might depend on the original width constraint
- Check that the intro text maintains proper readability at full width

## Example Before/After

**Before:**
- Intro text appears narrow with large empty space to the right
- Cards below span full width, creating visual imbalance
- Long Russian sentences may wrap unnecessarily early

**After:**
- Intro text spans full content width like cards
- Visual balance restored between intro and content sections
- Russian text flows naturally without artificial width constraints