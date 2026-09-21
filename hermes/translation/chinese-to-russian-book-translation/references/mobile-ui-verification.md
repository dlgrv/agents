# Mobile UI verification for multilingual sites

## Overview
When deploying multilingual book translation sites, mobile viewport testing is required to catch layout issues that desktop testing misses. This is especially critical for responsive headers and search functionality.

## Critical mobile issues to verify

### 1. Search input placement
- **Issue:** Search input may shift +195px right on mobile due to `position:relative` + desktop centering rule (`left:50%`)
- **Fix:** Reset with `left:auto` in mobile CSS (≤960px viewport)
- **Verification:** Measure input rect [left..right] vs icon cluster [left..right] at 390px viewport
- **Pass condition:** Input fully contained, no overlap with icons

### 2. Short placeholder universality
- **Issue:** User preferred short search placeholder (Search/Поиск/搜索/Buscar) but it was mobile-only
- **Fix:** Remove viewport condition; use short form everywhere
- **Verification:** Check placeholder text on both mobile and desktop
- **Pass condition:** Short placeholder visible on all viewports

### 3. Icon overflow
- **Issue:** Icons (language, GitHub, theme) may extend beyond viewport edge
- **Fix:** Ensure proper spacing and responsive margins
- **Verification:** Measure rightmost icon vs viewport width
- **Pass condition:** Icons fully visible, no horizontal scroll

### 4. Text column width
- **Issue:** Double padding (.content + .doc) narrows text column on mobile
- **Fix:** Reduce cumulative padding at ≤560px viewport
- **Verification:** Measure text width vs viewport width
- **Pass condition:** Text column ≥ 60% of viewport width

## Verification workflow

1. **Test at 390px and 1280px viewports** (iPhone 8/12 and desktop)
2. **Capture screenshots** for visual review
3. **Measure DOM elements** with JavaScript:
   ```javascript
   const inputRect = document.querySelector('.search input').getBoundingClientRect();
   const iconRect = document.querySelector('.nav-r').getBoundingClientRect();
   console.log('Input:', [inputRect.left, inputRect.right], 'Icons:', [iconRect.left, iconRect.right]);
   ```
4. **Check horizontal scroll:** `document.documentElement.scrollWidth - document.documentElement.clientWidth === 0`

## Example commands
```bash
# After deployment, test mobile layout
cdp('Emulation.setDeviceMetricsOverride', width=390, height=800, deviceScaleFactor=2, mobile=True)
goto_url('https://dlgrv.github.io/HowToLiveBetter/en/')
# Measure elements with JS as above
```

## Pitfalls
- **Cache busting:** Always use cache-busting URLs or force reload when testing fixes
- **CSS specificity:** Mobile fixes must override desktop rules with !important if needed
- **JS state:** Language switcher and search state may affect layout; test both initial load and after interactions
- **Multiple viewports:** Test both small mobile (390px) and tablet (768px) breakpoints

## Mobile viewport cheat sheet
- **iPhone 8/SE:** 375×667 (use 390px for safety margin)
- **iPhone 12/13:** 390×844 (use 390px)
- **Desktop small:** 1280×800
- **Desktop large:** 1920×1080

## Responsive breakpoints to test
- **≤560px:** Text column width fix
- **≤960px:** Search placement and placeholder changes
- **≤1099px:** Header layout adjustments
- **All:** Icon overflow and horizontal scroll