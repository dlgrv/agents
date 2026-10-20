# Editorial Redesign Workflow

## When to Use This Skill
Use when user references dlgrv.com or asks for:
- 'clean', 'minimalist', 'editorial' design
- 'Georgia serif' typography
- 'hairline separators' or 'monochrome color'
- Book guides, blogs, content-focused sites

## Step-by-Step Process

### 1. Reference Site Analysis
- When user provides URL (e.g., https://dlgrv.com/blog/logistic-regression/):
  - Use browser tools to extract exact design tokens
  - Map typography, colors, spacing, component structures
  - Preserve functionality while applying editorial styling

### 2. Vibe-Based Design
- When user gives vibe words only:
  - Apply minimalist editorial archetype
  - Set tokens based on Georgia serif + system-ui UI
  - Build with consistent spacing and typography
  - Review against anti-pattern checklist

### 3. Anti-Pattern Checklist
- ❌ Warm cream (#F4F1EA) + terracotta (#D97757)
- ❌ Generic rounded cards with soft shadows
- ❌ ALL-CAPS eyebrow labels
- ❌ Default fonts (Inter, Roboto, Arial)
- ❌ Linear/ease-in-out transitions

### 4. Quality Assurance
- **DESIGN.md must exist** before any UI work
- **Concrete reference = contract**—match pixels unless deviation allowed
- **Never weaken UX for performance**—hit 100 Lighthouse without dropping content
- **Done = visual QA evidence**—screenshots at multiple resolutions

## Example Implementation
```css
/* Core tokens from dlgrv.com */
:root {
  --bg: #FFFFFF;
  --text: #333333;
  --mut: #999999;
  --line: #E5E5E5;
  --serif: Georgia, serif;
  --sans: system-ui, -apple-system, sans-serif;
}

/* Typography */
.content { font: 17.5px/1.7 var(--serif); }
.nav { font: 13px/1.5 var(--sans); }

/* Layout */
.content { max-width: 680px; margin: 0 auto; padding: 0 48px 128px; }

/* Components */
article { border-bottom: 1px solid var(--line); padding-bottom: 16px; }
button { font: 13px/1.5 var(--sans); padding: 6px 12px; }
```

## Common Use Cases
- Book reading interfaces (HTLB project)
- Blog layouts (dlgrv.com style)
- Documentation sites
- Content-focused landing pages