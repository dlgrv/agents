# Wishlist purchased state handling

When implementing a 'purchased' state for wishlist items, use these patterns:

## Manifest schema

Extend the `public/wishlist/manifest.json` with:
- `dateAdded`: ISO date string (e.g. '2026-08-28') — automatically set on item creation
- `dateBought`: ISO date string, optional — when present, marks the item as purchased

## CSS rendering

Apply `.is-bought` class to the wishlist row when `dateBought` is present:
- Text: `text-decoration: line-through`, `color: #98989d`
- Icon: `filter: grayscale(100%) opacity(0.6)`

## Behavior

- Purchased items remain in place (not removed from the list)
- They are still clickable (open `item.url` on dblclick/Enter)
- Sort and filtering should ignore the purchased state unless explicitly requested

## Implementation example

```ts
// In renderWishlistRows()
const rows = manifest.map(item => ({
  ...item,
  isBought: !!item.dateBought
}));

// In CSS
.wishlist-list__row.is-bought {
  text-decoration: line-through;
  color: #98989d;
}
.wishlist-list__row.is-bought .wishlist-list__icon {
  filter: grayscale(100%) opacity(0.6);
}
```

## Testing

- Test with and without `dateBought` fields
- Verify purchased items appear visually distinct but remain interactive
- Test sorting and filtering behavior
- Test persistence of purchased state across reloads