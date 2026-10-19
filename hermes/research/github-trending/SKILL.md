---
name: github-trending
description: Use for GitHub trending repos/developers/charts lookups.
---

# GitHub trending charts

## When to Use

Use when the user asks about trending GitHub repositories, trending developers, weekly/daily GitHub charts, or 'what's hot on GitHub'.

GitHub has no official API for trending. Two sources cover every ask:

## 1. Trending pages (scrape)

- Repos: `https://github.com/trending?since=weekly` — `since` is `daily` / `weekly` / `monthly`; language via path `/trending/python`.
- Developers: `https://github.com/trending/developers?since=weekly`.

Run `scripts/trending.py` (stdlib only, prints a markdown table: repo, language, total stars, weekly delta, one-line description):

```
trending.py repos --since weekly [--lang python]
trending.py developers --since weekly
```

Parsing gotchas baked into the script (re-derive by hand only if GitHub changed markup):
- Each trending row is `<article class="Box-row">` on the repos page and `<article class="Box-row d-flex" id="pa-...">` on the developers page.
- Repo URL is the `href` inside the row's `<h2>`, NOT the first `/...` href in the article — first-href regexes catch login/sponsors links instead.
- Weekly delta is the text `N stars this week` (or `today` / `this month`); total stars live in the `/stargazers` link.
- On the developers page the dev's popular repo is not in any plain `href` near the name — extract the href that follows `click_target&quot;:&quot;REPOSITORY&quot;` in the hydro-click payload.

## 2. New repos this week (API — cleaner, use gh CLI)

Best source for 'repos created in the last N days, most starred':

```sh
gh api 'search/repositories?q=created:>YYYY-MM-DD&sort=stars&order=desc&per_page=15' \
  --jq '.items[] | "\(.full_name) | \(.language // "-") | \(.stargazers_count) | \(.description // "" | .[0:90])"'
```

Set the date to today minus the requested window.

## 3. Popular repos for a product/niche ('popular repos for X')

```sh
gh api -X GET search/repositories -f q='<keyword>' -f sort=stars -f order=desc -f per_page=20 \
  --jq '.items[] | "\(.full_name) | \(.language // "-") | \(.stargazers_count) | \(.updated_at[0:10]) | \(.description // "" | .[0:90])"'
```

- Search the product's OWN name/domain token first (`hh.ru`, `notion`) — paraphrased keyword queries ('hh auto apply') miss the top repos, whose descriptions use the product name itself.
- Run 2–3 queries in one go (plain keyword, keyword + native-language terms, `topic:<x>`) and merge; niche ceilings are real (~600★ for RU-market tools vs 75k★ international equivalents) — report the ceiling, don't keep digging.
- Filter noise rows (gibberish names) before presenting.

## Output

Present as a markdown table with clickable repo links, then a 1–2 line thematic read of the week (what's trending as a category). Offer follow-ups: per-language trend, trending developers, or a cron job for recurring digests.
