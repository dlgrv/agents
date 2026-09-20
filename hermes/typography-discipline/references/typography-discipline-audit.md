# Typography Audit Reference

## Independent Audit Protocol

When auditing typography-driven designs, use this protocol to verify discipline and identify real-world problems:

### 1. Automated Measurement

**Setup**: Render the page in a headless browser at multiple viewports (1440px, 1920px, 390px mobile, 150% zoom).

**Measurements to collect**:
- **Font family compliance**: All text nodes must use the same declared font family (e.g., Georgia)
- **Size scale compliance**: Only declared sizes allowed (e.g., 12, 13, 17.5, 21, 26, 38px)
- **Case compliance**: No `text-transform: uppercase` except where explicitly permitted
- **Underline compliance**: `text-decoration: none` on all elements
- **Line length**: Characters per line (CPL) in body text (target: 45-75)
- **Contrast ratios**: Calculate WCAG AA compliance for all text/background pairs

**Script template**:
```javascript
// Measure font usage
const fontFamilies = new Set();
const fontSizes = new Set();
document.querySelectorAll('body *').forEach(el => {
  const cs = getComputedStyle(el);
  if (el.offsetWidth && cs.display !== 'none') {
    fontFamilies.add(cs.fontFamily.split(',')[0]);
    fontSizes.add(cs.fontSize);
  }
});

// Measure CPL in body paragraphs
const cpl = [...document.querySelectorAll('.rows .v')]
  .filter(e => e.textContent.length > 200)
  .map(e => {
    const w = e.getBoundingClientRect().width;
    const fs = parseFloat(getComputedStyle(e).fontSize);
    return Math.round(e.textContent.length / (w / (fs * 0.5)));
  });

// Contrast calculation
function lum(rgb) {
  const [r,g,b] = rgb.map(v => {
    v /= 255;
    return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4);
  });
  return 0.2126*r + 0.7152*g + 0.0722*b;
}
function cr(a,b) {
  const l1 = lum(a), l2 = lum(b);
  const [hi,lo] = l1>l2 ? [l1,l2] : [l2,l1];
  return (hi+0.05)/(lo+0.05);
}
```

### 2. Common Problems and Fixes

#### Problem 1: Small Text Contrast Failure
- **Evidence**: 12px labels on #ffffff yield 3.28:1 (fails WCAG AA 4.5:1)
- **Fix**: Use #6f6f6f (5.02:1) or #767676 (4.54:1)
- **Impact**: ~45% of page text may be non-compliant

#### Problem 2: Link Color Contrast
- **Evidence**: Accent links #2481cc on #ffffff = 4.13:1 (fails AA)
- **Fix**: Use #1a6aa8 (5.72:1) with hover #135a8c (7.32:1)
- **Impact**: All functional links may be non-compliant

#### Problem 3: Excessive Line Length
- **Evidence**: 702px column at 17.5px = 75+ CPL (target: 45-75)
- **Fix**: Constrain to 64ch (~560px = 59 CPL)
- **Impact**: Readability and scanning speed reduced

#### Problem 4: CJK Font Inconsistency
- **Evidence**: Chinese characters in Georgia fall back to system sans-serif
- **Fix**: Stack CJK serif fonts: Georgia,"Noto Serif SC",... serif
- **Impact**: Visual inconsistency within paragraphs

#### Problem 5: Missing Hover Affordance
- **Evidence**: No underline or color change on hover for 1623 links
- **Fix**: Add hover state with guaranteed contrast or underline
- **Impact**: Users cannot identify interactive elements

### 3. Verification Checklist

Before declaring typography discipline complete:

- [ ] All text nodes use the same declared font family
- [ ] Font sizes exactly match the declared scale (no outliers)
- [ ] No uppercase transformation except where explicitly permitted
- [ ] No underlines anywhere on the page
- [ ] Line length between 45-75 characters for body text
- [ ] All text/background pairs pass WCAG AA (4.5:1)
- [ ] Hover states provide clear affordance (color change or underline)
- [ ] CJK characters use appropriate serif fallback
- [ ] Icons sized by visual weight, not viewBox dimensions
- [ ] Vertical rhythm consistent (equal spacing between like elements)

### 4. Audit Report Template

```json
{
  "verdict": "Discipline confirmed | Problems found",
  "positives": ["List of confirmed strengths"],
  "problems": [
    {
      "severity": "critical|major|minor",
      "area": " typography area",
      "evidence": "specific measurement result",
      "fix": "specific CSS change"
    }
  ]
}
```

### 5. Tools and Setup

**Browser automation**: Playwright with Chromium
**Viewport testing**: 1440x900, 1920x900, 390x900, 150% zoom
**Contrast testing**: Custom lum/cr functions (not browser defaults)
**CSS analysis**: Computed styles inspection, not just CSS source
