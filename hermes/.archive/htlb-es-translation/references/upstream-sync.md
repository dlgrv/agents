# Upstream synchronization (HTLB ES translation)

## Rule

When pulling upstream/main (e.g. to sync with new infrastructure), use `git merge --allow-unrelated-histories origin/main`. Resolve conflicts in wrapper files (README.md, index.html, og.png) by preferring the fork's version (EN wrapper), but adopt upstream's EPUB link and Spanish language addition if present. Never merge upstream's Chinese content into the fork's English wrapper.

## Why

Upstream rewrites history (different root SHA), so standard merge fails. The fork's main branch is an English wrapper over Chinese content; upstream main is the Chinese original plus new infrastructure (EPUB, ads). The fork's wrapper must remain the single source of truth for English readers.

## Procedure

```bash
git fetch upstream main
git merge --allow-unrelated-histories origin/main
# Resolve conflicts:
# - README.md: Keep fork version (EN wrapper), add EPUB link and Spanish if missing
git add README.md && git status --short | grep -E "^(UU|AA)"
# - index.html: Keep fork version (EN site)
# - og.png: Keep fork version (EN banner)
# Commit and push
git commit -m "chore: sync upstream infrastructure"
```

## Pitfall

Never merge upstream's Chinese content into the fork's English wrapper — the fork's main branch is an English wrapper, not a translation of upstream. The Chinese content is already byte-identical; the merge is only for infrastructure sync.