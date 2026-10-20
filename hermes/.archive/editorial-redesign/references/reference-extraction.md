# Browser-Based Reference Extraction

## How to Extract Design Tokens from Reference Sites

When user provides a URL (e.g., https://dlgrv.com/blog/logistic-regression/), use browser tools to extract exact design tokens:

### 1. Browser Inspection
- Open reference site in browser
- Use dev tools to inspect elements
- Extract computed styles for key components

### 2. Token Mapping
- **Typography**: Font family, size, line-height, letter-spacing
- **Colors**: Background, text, border, shadow colors
- **Spacing**: Padding, margin, gap values
- **Components**: Border-radius, box-shadow, transition properties

### 3. Implementation
- Map extracted tokens to your project's CSS variables
- Implement matching styles
- Preserve functionality while upgrading aesthetics

### 4. Verification
- Take screenshots at multiple resolutions
- Compare against reference site
- Ensure all interactive elements work

## Example: dlgrv.com Token Extraction
```javascript
// Example of token extraction
const tokens = {
  typography: {
    book: 'Georgia, serif',
    bookSize: '17.5px',
    bookLineHeight: '1.7',
    ui: 'system-ui, -apple-system, sans-serif',
    uiSize: '13px',
    uiLineHeight: '1.5'
  },
  colors: {
    light: {
      bg: '#FFFFFF',
      text: '#333333',
      mut: '#999999',
      line: '#E5E5E5'
    },
    dark: {
      bg: '#111111',
      text: '#D0D0D0',
      mut: '#666666',
      line: '#333333'
    }
  },
  layout: {
    maxWidth: '680px',
    padding: {
      desktop: '48px',
      mobile: '20px'
    }
  }
};
```

## Tools to Use
- Browser dev tools (Elements tab)
- getComputedStyle() method
- Screen capture tools
- CSS variable mapping