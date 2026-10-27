# Website deployment and verification

## Overview
When deploying translated content to GitHub Pages, follow this workflow to ensure fixes propagate correctly and the site is verified live.

## Deployment workflow

1. **Commit and push:**
   - `git add . && git commit -m "message" && git push fork branch-name`
   - For main branch: `git push fork branch-name:main`

2. **Wait for propagation:**
   - GitHub Pages takes 1-2 minutes after push to update
   - Always wait at least 50 seconds before verification
   - Use `sleep 50` to ensure stability

3. **Verify live changes:**
   - Use `curl -s <url> | grep -o 'pattern'` to confirm text fixes
   - Check for double ellipsis, Chinese punctuation, layout issues
   - Test responsive elements and language switcher

4. **Common fixes to verify:**
   - Loading text: `Загружаю текст…` (not `… …`)
   - Section headings: no flexbox wrapping or overflow
   - Sidebar hints: proper capitalization
   - Breadcrumb navigation: correct Russian text

## Troubleshooting

- If changes don't appear, try `curl -I <url>` to check HTTP status
- If CSS fixes don't work, verify the CSS file was committed and pushed
- For language switcher, check that the HTML `lang` attribute is correct
- Use browser dev tools to inspect element state if layout issues persist

## Example commands
```bash
# After push
git push fork translation/ru 2>&1 | tail -1
sleep 50
curl -s https://dlgrv.github.io/HowToLiveBetter/ | grep -o 'Загружаю текст[^<]*'
```