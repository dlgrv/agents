# Typography Discipline Reference

## One Font, Infinite Hierarchy

### Core Rule
Never mix serif/sans-serif/UI fonts on the same page. All text must derive from a single typeface family.

### Implementation
```css
/* Force all UI elements to inherit the primary font family */
button, input, kbd, select, textarea, summary {
  font-family: var(--primary-font, Georgia);
}

/* Remove font switching for hierarchy */
h1, h2, h3, h4, h5, h6 {
  font-family: inherit;
}

/* Use weight/size/tracking instead of font changes */
.display-text {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.body-text {
  font-size: 1.125rem;
  font-weight: 400;
  letter-spacing: 0.01em;
  line-height: 1.6;
}

.label-text {
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
```

### Exceptions
- **Code elements**: `code { font-family: 'SF Mono', Consolas, monospace; }`
- **Technical kbd**: `kbd { font-family: inherit; font-size: 0.875em; }`
- **Brand logos**: Never override font on logo SVGs
- **External content**: User-pasted text with embedded fonts (warn if mixed)

## Icon Optical Calibration

### The Problem
Raw SVG viewBox dimensions don't match visual weight. An 18/24 document icon appears smaller than a 24/24 GitHub octocat at the same pixel size.

### The Solution
Size icons by their visual weight, not viewBox math:

```css
/* Icon sizing by visual weight */
.icon-document {
  width: 20px;
  height: 20px;
}

.icon-github {
  width: 15px;
  height: 15px;
}

.icon-chevron {
  width: 10px;
  height: 10px;
}

/* Group icons with consistent visual weight */
.nav-icons .icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Calibration Process
1. **Identify the heaviest visual element** in the icon set
2. **Set its size as the baseline** (e.g., 20px for a filled document icon)
3. **Scale other icons proportionally** based on visual weight
4. **Test at actual pixel sizes** — don't rely on math alone

## Typography Pitfalls

### Common AI Mistakes
- **"Georgia for body, Inter for buttons"** → Violates one-font rule. Force buttons to Georgia.
- **"Bold headers, regular body" only** → Add Medium (500) and SemiBold (600) for subtle hierarchy.
- **"All caps for subheaders"** → Try lowercase italics or sentence case instead.
- **"Numbers in proportional font"** → Use `font-variant-numeric: tabular-nums` for data.
- **"Orphaned single words"** → Use `text-wrap: balance` or `text-wrap: pretty`.

### Spacing Discipline
- **Line length**: 65-80 characters max for body text
- **Line height**: 1.5-1.6 for body, 1.1-1.2 for headers
- **Paragraph spacing**: 1.5-2x line height, never equal to line height
- **Header margins**: Bottom margin should be 1-1.5x the header's own height

## Implementation Checklist

Before finalizing typography:
- [ ] All text elements use the same font family
- [ ] No browser defaults in buttons/inputs/kbd
- [ ] Icons sized by visual weight, not viewBox
- [ ] Hierarchy achieved through size/weight/tracking, not font switching
- [ ] Line length and spacing follow discipline rules
- [ ] No orphaned words or unbalanced text wrapping
- [ ] Numbers use tabular figures in data contexts
- [ ] No emojis in UI icons — replaced with SVG/text

## Example: Book Reference Site

```css
:root {
  --primary-font: Georgia, serif;
}

body {
  font-family: var(--primary-font);
  font-size: 17.5px;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

/* Force all UI to use Georgia */
button, input, kbd, summary {
  font-family: var(--primary-font);
  font-size: 0.9em;
  font-weight: 500;
}

/* Icon calibration */
.ic-doc svg { width: 20px; height: 20px; }
.ic-gh svg { width: 15px; height: 15px; }
.lang-dd summary svg { width: 11px; height: 11px; }
```
