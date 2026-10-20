# Header Layout Best Practices

## Core Principles
- **Search centering**: Anchor search bar exactly at window center (50%) on desktop; use absolute positioning if needed
- **Right cluster anchoring**: Always use `margin-left: auto` on right-side navigation clusters (RU/README/GitHub/switch) to push them to edge
- **Icon calibration**: Equalize optical weight between similar icons (README document ~24px, GitHub octocat ~15px) with consistent gaps (≥20px)
- **Theme switch**: Use plain square knobs, not custom glyphs; ensure contrast with background
- **Hamburger specificity**: Ensure `.icon-btn` class specificity beats generic `.menu-btn` for desktop visibility control

## Implementation Patterns
```css
/* Search centering on desktop */
.search {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: min(420px, 40vw);
}

/* Right cluster anchoring */
.nav-r {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

/* Icon calibration */
.ic-doc svg { width: 24px; height: 24px; }
.ic-gh svg { width: 15px; height: 15px; }
.nav-r > * + * { margin-left: 23px; }

/* Theme switch styling */
.switch .knob {
  border-radius: 0; /* square, not rounded */
  background: var(--mut); /* ensure contrast */
}

/* Hamburger menu specificity */
.icon-btn.menu-btn { display: none; }
@media (max-width: 1099px) {
  .icon-btn.menu-btn { display: grid; }
}
```

## Common Pitfalls
- **Search drift**: Don't rely on flex auto-shrink; absolute position guarantees centering
- **Icon overlap**: README and GitHub icons often have different viewBox sizes — normalize visually
- **Switch contrast**: Gray knobs on white backgrounds are invisible; use muted colors for off-state
- **Menu visibility**: Generic `.menu-btn` can be overridden by `.icon-btn` — use compound selectors

## Verification Steps
1. Measure search bar center: should be exactly 50% of window width
2. Check right cluster distance from edge: should match design tokens
3. Test icon gaps: similar icons should have consistent spacing
4. Verify theme switch visibility in both light/dark modes
5. Confirm hamburger menu is hidden on desktop, visible on mobile