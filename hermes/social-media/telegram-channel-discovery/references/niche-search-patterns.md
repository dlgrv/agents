# Niche Telegram Channel Search Patterns

## Archive/Designer Fashion
- **lyzem query**: 'japanese archive', 'archival revolution', 'архивная мода'
- **Expected results**: Mostly dead stubs; real content lives in private groups
- **Validation**: Look for actual posts, not just 'Send Message'

## Men's Style & Fashion
- **lyzem query**: 'мужской стиль', 'lookfinder', 'clothes hunter', 'yepman_blog'
- **Live channels**: @lookfinder, @Clotheshunter, @yepman_blog, @lebonmot
- **Themes**: Style breakdowns, shopping guides, vintage aesthetics

## Streetwear/Rapper Style
- **lyzem query**: 'гардероб рэпера', 'strimer garderob similar', 'streetwear'
- **Reality**: Most moved to private marketing groups; no active public channels
- **Fallback**: Check media articles for mentions of active streetwear accounts

## Japanese Aesthetic
- **lyzem query**: 'japanese street style', 'japan vibe clothes', 'японский вайб'
- **Result**: Mix of dead channels and lifestyle accounts
- **Better platforms**: Instagram, Tumblr for Japanese street fashion

## Fashion Media Articles
- **Sources**: Buro247, TheBlueprint, Vogue Russia
- **Method**: Extract t.me mentions from published articles
- **Filter out**: Media site bots (e.g., @buro247_bot)

## Rate Limit Handling
- lyzem.com: 0.3s delay between requests
- t.me direct fetch: Often blocked; use only for validation
- User-Agent rotation: Mac Safari headers work best for lyzem