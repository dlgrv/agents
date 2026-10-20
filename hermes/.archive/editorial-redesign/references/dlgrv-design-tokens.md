# dlgrv.com Design Tokens

Extracted from https://dlgrv.com/blog/logistic-regression/ and related pages.

## Typography
- **Book text**: Georgia 17.5px/1.7 serif
- **UI text**: system-ui, -apple-system, sans-serif 13px/1.5
- **Scale**: H1 28-32px, H2 22-26px, H3 18-20px, body 15-17px, small 12-13px
- **Line height**: 1.4-1.7 for body, 1.2-1.4 for headings
- **Spacing**: -0.02 to -0.05em letter-spacing for display, 0 for body text

## Color System
- **Light mode**: 
  - Background: #FFFFFF
  - Text: #333333
  - Secondary: #666666
  - Muted: #999999
  - Line: #E5E5E5
- **Dark mode**: 
  - Background: #111111
  - Text: #D0D0D0
  - Secondary: #999999
  - Muted: #666666
  - Line: #333333
- **Accents**: Minimal—one color maximum (e.g., #0066CC for links)

## Layout
- **Max-width**: 680-720px for content blocks
- **Sidebars**: Up to 84vw mobile
- **Padding**: 
  - Desktop: 48px horizontal, 128px bottom
  - Mobile: 20px horizontal, 96px bottom
- **Section spacing**: 64px between blocks
- **Component spacing**: 8-16px
- **Responsive**: Mobile-first, breakpoints at 560px, 768px, 1024px

## Components
- **Cards**: No background, no border-radius, hairline separators only
- **Buttons**: System font, no rounded corners unless explicitly requested, minimal padding
- **Navigation**: Top-aligned on desktop, hamburger menu on mobile
- **Lists**: Simple bullets or dashes, no background, minimal spacing

## Anti-Patterns to Avoid
- Warm cream (#F4F1EA) + terracotta (#D97757) combinations
- Generic rounded cards with soft shadows
- ALL-CAPS eyebrow labels
- Default fonts (Inter, Roboto, Arial)
- Linear/ease-in-out transitions (use custom cubic-bezier for motion)