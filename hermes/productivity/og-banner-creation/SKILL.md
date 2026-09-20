---
name: og-banner-creation
description: Create Open Graph banner images for READMEs.
---

# OG Banner Creation

Create high-quality Open Graph banner images (1200×630 px) for READMEs and social sharing. Supports multi-language content, headless rendering without GUI tools, and follows design consistency with the upstream source.

## Process

1. **Check upstream source** — locate original `tools/og.html` in the repo
2. **Translate content** — create language-specific versions (`tools/og-ru.html`, `tools/og-en.html`)
3. **Adjust layout** — ensure text fits within 1200px width (font size, line breaks, content trim)
4. **Render headless** — use Chromium to generate PNG without Windows
5. **Validate output** — check for clipping, line breaks, text integrity
6. **Integrate** — update README to reference localized banners

## Key constraints

- **Size**: 1200×630 px (social media standard)
- **Font**: Liberation Sans for Cyrillic, fallback to upstream font for Latin
- **Layout**: Centered div wrapper (`<div align="center">`)
- **Headline**: 2 lines maximum, avoid orphan words
- **Topics**: Trim list to fit width (use vision analysis to verify)
- **Chips**: Keep all stat pills intact, no clipping
- **Rendering**: Use `--headless --disable-gpu --no-sandbox --window-size=1200,630`

## Quality gates

Before committing:
- Headline must be exactly 2 lines (no 3rd line, no orphan words)
- Topics line must not be clipped at right edge (200+ px margin)
- All chips/badges must be fully visible
- No stray bars or artifacts at edges
- Text must be readable (no tofu characters for Cyrillic)
- Colors and contrast must match upstream design

## Language handling

- **EN**: Use same content structure as upstream, translate headline only
- **RU**: Translate all visible text, adjust font size for Cyrillic (64px vs 82px)
- **ZH**: Keep original `og.html` (already in Chinese)

## Rendering command

```bash
CHROME=$(find /root -name "chrome" -path "*chrome-linux*" 2>/dev/null | head -1)
[ -z "$CHROME" ] && CHROME=$(which chromium chromium-browser google-chrome 2>/dev/null | head -1)
"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1200,630 --screenshot=output.png file.html
```

## File naming

- `og-en.png` — English version
- `og-ru.png` — Russian version  
- `og.png` — keep original for Chinese

## Integration

Update README references:
- `README.md` → `og-en.png`
- `README.ru.md` → `og-ru.png`
- `README.zh.md` → `og.png` (unchanged)

## Pitfalls

- **Font fallback**: If Liberation Sans not available, use DejaVu Sans or system sans-serif
- **Line breaks**: Always test headline with actual content, not placeholder text
- **Content trim**: Better to trim topics list than to use tiny font
- **Vision verification**: Always render and check with vision model before committing
- **Chromium path**: May vary between environments, always find dynamically

## Success criteria

Banner is ready when:
1. All quality gates pass
2. Files are committed with proper naming
3. README references updated
4. PR opened with clear description
