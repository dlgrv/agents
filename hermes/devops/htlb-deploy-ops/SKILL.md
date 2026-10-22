---
name: htlb-deploy-ops
description: Use when deploying or debugging HowToLiveBetter CI/CD.
---

# HTLB Deploy Ops

CI/CD and deploy operations for `dlgrv/HowToLiveBetter` (api = Go + PocketBase, book = static site, ebooks = EPUB/PDF × 7 langs).

## Pipelines (all in `.github/workflows/`)

| Workflow | Trigger | Does |
|---|---|---|
| `deploy-api` | push to main touching `api/**` | lint+test Go → build binary → stop service → backup `pb_data` → rsync binary → activate symlink → perms → start → health-check (auto-rollback on failure) |
| `deploy-book` | push touching `book/**` | build static site → generate sitemap.xml (532 urls) + llms-full.txt (22MB, 245 sections) + copy IndexNow key into `.publish/` → rsync to `/var/www/book.dlgrv.com/releases/<stamp>` → flip `current` symlink → IndexNow ping (changed urls; **first ping after adding the key may 403 — retry manually, later deploys are 200**; jq filter MUST precede positional `--args` args) |
| `ebooks` | push touching `book|docs|forge/ebook` | build EPUB+PDF per lang (matrix) → replace assets on fixed `ebooks-latest` release (must be exactly 14 assets, `gh release upload --clobber`) |
| `pages` | push touching `deploy/pages-redirect/**` | deploy a permanent redirect site to GH Pages (mirror removed 2026-10-20): `index.html` + `404.html` JS map `/HowToLiveBetter/<path>` → `book.dlgrv.com/<path>`. GH Pages serves 404.html for unknown paths (HTTP 404 is expected) — verify redirect content, not status code |

Deploy secrets (`DEPLOY_SSH_KEY`/`DEPLOY_HOST`/`DEPLOY_USER`) live in the **production environment**, not repo-level secrets — check there first when a deploy fails with empty/missing creds.

## Verify / trigger manually

```bash
gh api repos/dlgrv/HowToLiveBetter/actions/permissions          # Actions enabled?
gh workflow run deploy-api -R dlgrv/HowToLiveBetter --ref main  # dispatch needs --ref main
gh run watch <id> -R dlgrv/HowToLiveBetter --exit-status --interval 15
curl -sS https://api.dlgrv.com/api/htlb/v1/health               # {"ok":true,"version":"<sha>"}
```

## Git hooks (local gates)

`.githooks/` via `core.hooksPath`. pre-commit = `make lint` + `make check-content` + `forge/ops/check_links.py`; pre-push = full `make test`. A broken link blocks `git commit` (exit 1) naming the file — most CI test failures are therefore catchable before any push. Keep the hook list and the CI `test` workflow steps in sync: CI runs `make test`, which must include every node/pytest file.

To verify a hook end-to-end: commit (or stash) your hook edits FIRST, then plant the bad fixture (e.g. a broken relative link), run the real `git commit`, and clean up with `git checkout -- <fixture>` or `git reset --hard` — a reset done while the hook edits are still uncommitted wipes them and you ship stale hooks.

## Pitfalls

- **Check `sudo -l -U deployer` on the server BEFORE the first deploy run.** The deploy script ssh's as `deployer` and runs restricted sudo; any unlisted command aborts mid-deploy. Required NOPASSWD set lives in `/etc/sudoers.d/` on hermes-vm: exact `systemctl {stop,start,restart,status} htlb-api.service`, plus `ln`, `chown`, `mkdir`, `tar`, `rm`, and **exact** `chmod 755 /opt/htlb-api` + `chmod 755 /opt/htlb-api/releases` (arg-exact entries — bare `/usr/bin/chmod` is more privilege than needed).
- **`deploy-api` stops the service BEFORE the risky steps** (perms, start). Any failure between stop and start leaves prod 502 — the rollback logic only covers health-check failures. Recovery: finish the perm block manually as root (`chown root:htlb /opt/htlb-api; chmod 755 …; chown -R htlb:htlb pb_data; chown -R deployer:deployer releases; chown -h htlb:htlb htlb-api`), `systemctl start htlb-api`, curl health, then fix the root cause and re-run the workflow green.
- **A sudo denial inside the deploy script surfaces as the sudo insult message** («I'm sorry … I can't do that»), not a plain permission error — read `gh run view <id> --log-failed` and map the last `==>` step to the missing sudoers entry.
- **Run `python3 forge/ops/check_links.py` locally before pushing any book/docs edit.** It is the only `test`-workflow step that fails on content (Go lint/tests pass anyway), and it resolves relative links from each file's OWN directory — a translated chapter in `book/ru/…` linking to a repo-root file needs `../` depth counted from `book/ru/`, not from the root. Fix all reported links, don't guess depths.
- **A matrix job hanging far beyond its normal duration with job logs returning Azure `BlobNotFound` is lost runner state, not a code bug** — other matrix jobs on the same run succeeding confirms it. Fix: `gh run cancel <id>`, wait for `completed/cancelled`, then `gh run rerun <id> --failed` (rerun refuses while the run is still in progress).
- **Don't block on one long `gh run watch` inside a single terminal call** — it can exceed the tool timeout even when the run finishes fine. Poll instead: `gh run view <id> --json status,conclusion` between bounded sleeps.
- **`ebooks-latest` release `published_at` stays at its creation date** — assets are replaced in place, so verify freshness via asset `updated_at`, not the release date.
- Version in health response = git short SHA of the deployed binary; compare against `git rev-parse --short origin/main` to confirm what's live.
