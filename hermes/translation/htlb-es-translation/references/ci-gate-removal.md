# CI gate removal (HTLB ES translation)

## Rule

If upstream CI workflows are specific to their README structure (e.g., epub-workflow tied to Chinese README), remove them from the fork's main branch to avoid failures. The fork's CI should only contain infrastructure needed for the English wrapper and translations.

## Why

Upstream workflows often assume their Chinese README structure and may reference tools (like epub-generation) that don't exist in the fork. Running these causes CI failures and blocks merges.

## Procedure

```bash
# Remove upstream-specific workflows
git rm .github/workflows/epub-workflow.yml  # or similar upstream-specific files
# Keep only fork-specific workflows: check-links.yml, build-pages.yml, etc.
git commit -m "chore: remove upstream-specific CI workflows"
```

## Pitfall

Never keep upstream workflows that reference Chinese-specific tools or assume their README structure — the fork's CI must match the fork's content structure (English wrapper + translations).
