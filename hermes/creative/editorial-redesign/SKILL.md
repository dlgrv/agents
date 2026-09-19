---
name: editorial-redesign
description: Minimalist editorial redesign for books and blogs.
---

# Editorial Redesign Skill

## Purpose
Apply minimalist editorial design to book guides, blogs, and content-focused sites. When user references dlgrv.com or asks for 'clean', 'minimalist', 'editorial', or 'Georgia serif' design, use this skill.

## Design System

### Typography
- **Book text**: Georgia 17.5px/1.7 serif for body content
- **UI text**: system-ui, -apple-system, sans-serif for navigation, buttons, metadata
- **Scale**: H1 28-32px, H2 22-26px, H3 18-20px, body 15-17px, small 12-13px
- **Line height**: 1.4-1.7 for body, 1.2-1.4 for headings
- **Spacing**: -0.02 to -0.05em letter-spacing for display, 0 for body text

### Color System
- **Light mode**: White background (#FFFFFF), text #333333, secondary #666666, muted #999999
- **Dark mode**: Background #111111, text #D0D0D0, secondary #999999, muted #666666
- **Accents**: Minimal—one color maximum (e.g., #0066CC for links), use sparingly
- **Borders**: Hairline 1px solid #E5E5E5 (light) or #333333 (dark)

### Layout
- **Max-width**: 680-720px for content blocks, wider for sidebars (up to 84vw mobile)
- **Padding**: Desktop: 48px horizontal, 128px bottom; Mobile: 20px horizontal, 96px bottom
- **Section spacing**: 64px between blocks, 8-16px for component spacing
- **Responsive**: Mobile-first, breakpoints at 560px, 768px, 1024px

### Components
- **Cards**: No background, no border-radius, hairline separators only
- **Buttons**: System font, no rounded corners unless explicitly requested, minimal padding
- **Navigation**: Top-aligned on desktop, hamburger menu on mobile
- **Lists**: Simple bullets or dashes, no background, minimal spacing

## Workflow

### 1. When User References Existing Site
- Extract design tokens from reference site using browser tools
- Match exact typography, colors, spacing, and component structures
- Preserve functionality while applying editorial styling

### 2. When User Gives Vibe Words
- Apply minimalist editorial archetype
- Set tokens based on Georgia serif + system-ui UI
- Build with consistent spacing and typography
- Review against anti-pattern checklist

### 3. Anti-Pattern Checklist
- Avoid warm cream (#F4F1EA) + terracotta (#D97757) combinations
- Avoid generic rounded cards with soft shadows
- Avoid ALL-CAPS eyebrow labels
- Avoid default fonts (Inter, Roboto, Arial)
- Avoid linear/ease-in-out transitions (use custom cubic-bezier for motion)

## Quality Gates
- **No design system = no UI work**—DESIGN.md must exist before components
- **Concrete reference = contract**—match pixels and structure unless deviation allowed
- **Never weaken UX for performance—hit 100 Lighthouse scores without dropping animations or content
- **Done = visual QA evidence**—screenshots at multiple resolutions with interaction states

## Example CSS
```css
/* Typography */
.book-text { font: 17.5px/1.7 Georgia, serif; }
.ui-text { font: 13px/1.5 system-ui, sans-serif; }

/* Color */
:root {
  --bg: #FFFFFF;
  --text: #333333;
  --mut: #999999;
  --line: #E5E5E5;
}
html.dark {
  --bg: #111111;
  --text: #D0D0D0;
  --mut: #666666;
  --line: #333333;
}

/* Layout */
.content { max-width: 680px; margin: 0 auto; }
.sec-block { margin-bottom: 64px; }

/* Components */
article { border-bottom: 1px solid var(--line); padding-bottom: 16px; }
button { font: 13px/1.5 system-ui, sans-serif; }
```