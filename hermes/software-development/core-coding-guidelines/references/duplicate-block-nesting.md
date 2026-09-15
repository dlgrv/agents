# Duplicate Block Nesting Anti-Pattern

## Symptom

A component renders the same title/border/header twice — once from the outer wrapper (`CollapsibleSection` providing `title` + border) and again from an inner `shellStyle` div (providing its own `<h4>`, border, padding, background, and `headerExtra`).

```
┌─ CollapsibleSection "Bid Runtime" ──────────────┐
│  ▾ Bid Runtime         Автообновление: 5 c       │  ← outer title + headerExtra
│ ┌─ shellStyle (border+padding+bg) ─────────────┐ │
│ │  Bid Runtime                                  │ │  ← inner h4 (DUPLICATE)
│ │  Bid attempts кампании в реальном времени     │ │
│ │  Автообновление: 5 c                          │ │  ← inner headerExtra (DUPLICATE)
│ │  [filters][metrics][charts]                   │ │
│ └───────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

## Root cause

When a component was refactored from standalone (`shellStyle` with its own border/title) to wrapped in `CollapsibleSection` (which provides title + border + `headerExtra`), the inner `shellStyle` div was left in place. The component renders both layers.

This happens when:
- A `collapsible` prop controlled whether to use `CollapsibleSection` (with title) or render directly (with `shellStyle` + manual `<h4>`)
- The `collapsible` prop was removed (always use `CollapsibleSection`), but the inner `shellStyle` div + manual title wasn't cleaned up

## Fix

Remove the inner `shellStyle` div. Replace with a plain `<div style={{ display: 'grid', gap: 14 }}>` for layout only. Remove the duplicate `<h4>` and duplicate `{refreshStatus}` — `CollapsibleSection` already renders `title` as `<h4>` and `headerExtra` in the header row.

```tsx
// ❌ Before — duplicate title/border/refreshStatus
const content = (
  <div style={shellStyle}>
    <div style={{ display: 'flex', justifyContent: 'space-between', ... }}>
      <div>
        <h4>Bid Runtime</h4>                    {/* DUPLICATE of CollapsibleSection title */}
        <p>Bid attempts кампании...</p>
      </div>
      {refreshStatus}                           {/* DUPLICATE of headerExtra */}
    </div>
    <RuntimeFilters ... />
    ...
  </div>
)

return (
  <CollapsibleSection title="Bid Runtime" headerExtra={refreshStatus}>
    {content}
  </CollapsibleSection>
)

// ✅ After — single title/border from CollapsibleSection
const content = (
  <div style={{ display: 'grid', gap: 14 }}>
    <p style={{ margin: 0, fontSize: 12, color: colors.textMuted }}>
      Bid attempts кампании в реальном времени
    </p>
    <RuntimeFilters ... />
    ...
  </div>
)

return (
  <CollapsibleSection title="Bid Runtime" headerExtra={refreshStatus}>
    {content}
  </CollapsibleSection>
)
```

After removing `shellStyle` usage, also remove the orphaned `runtimeShellStyle as shellStyle` import.
