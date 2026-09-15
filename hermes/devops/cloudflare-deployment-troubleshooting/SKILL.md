---
name: cloudflare-deployment-troubleshooting
description: Fix Cloudflare Pages build failures and stale deployments.
---

# Cloudflare Pages deployment troubleshooting

Use this skill when a Cloudflare Pages deployment fails or the site is stuck on an old version despite pushing new commits.

## Common failure patterns and fixes

### Build failure due to npm version mismatch

**Symptom:** `npm ci` fails on Cloudflare (exit code 1, 'package-lock.json ... is not consistent with package.json')

**Root cause:** The lockfile contains optional dependencies (like `esbuild@0.28.2`) that are present in the local lock but missing in the Cloudflare environment (npm 10.9.2).

**Fix:**
1. Regenerate the lockfile using the CF npm version:
   ```bash
   npx npm@10.9.2 install --package-lock-only
   ```
2. Commit the updated lockfile:
   ```bash
git add package-lock.json
git commit -m "fix(deploy): regenerate lockfile for Cloudflare npm 10.9.2"
   ```
3. Test with the CF npm version to confirm it passes:
   ```bash
   npx npm@10.9.2 ci  # should exit 0
   ```
4. Push and wait for the new deployment

**Pitfall:** Never commit a lockfile that fails this test — Cloudflare deployment will fail otherwise.

### Accidental symlink to local paths

**Symptom:** Build succeeds but deployed files are old/incorrect; JS/CSS hashes don't match recent commits

**Root cause:** A symlink pointing to a local absolute path (e.g., `node_modules` → `/root/github/dlgrv.com/node_modules`) was committed to the repo. On Cloudflare's build environment, this path doesn't exist.

**Detection:**
```bash
git ls-files -s | grep "120000"  # mode 120000 = symlink
git cat-file -p <sha>  # shows the target path
```

**Fix:**
1. Remove the symlink from the index:
   ```bash
git rm --cached node_modules
   ```
2. Commit the removal:
   ```bash
git commit -m "fix(deploy): remove accidental symlink to local path"
   ```
3. Push to trigger a new deployment

**Pitfall:** Symlinks to local paths will break the build even if the target exists locally. Always verify symlinks point to relative paths or are committed as regular directories.

### Deployment not updating despite new commits

**Symptom:** Recent commits are pushed but the deployed site still shows old content

**Root cause:** The previous deployment may have failed silently, leaving the old version live. Cloudflare only updates when a build succeeds.

**Verification:**
1. Check the deployed files:
   ```bash
curl -s https://your-domain.com/some-file | wc -c
cd local-repo && wc -c public/some-file
   ```
2. If sizes differ significantly, the deployment is stale

**Fix:**
1. Make a trivial change (e.g., add a comment) and commit/push to force a new build
2. Monitor the deployment status (Cloudflare dashboard or `wrangler pages deployments list`)
3. If it fails again, check the build logs for errors

## Deployment verification workflow

After any fix, verify the deployment:

1. **Check file sizes** (quick check):
   ```bash
echo "=== prod index.json bytes ==="
curl -s --max-time 20 https://your-domain.com/blog/index.json | wc -c
echo "=== local dist/blog/index.json bytes ==="
cd local-repo && wc -c dist/blog/index.json
   ```
2. **Check specific endpoints**:
   ```bash
curl -s --max-time 20 -o /dev/null -w "blog/: %{http_code}\n" https://your-domain.com/blog/
curl -s --max-time 20 -o /dev/null -w "article: %{http_code}\n" https://your-domain.com/blog/article-slug/
   ```
3. **Wait for deployment completion** (typically 2.5-3.5 minutes for small sites)

## Build logs access

If the deployment fails and you need to see build logs:

- **Cloudflare Dashboard:** Pages project → Deployments → Click on the failed deployment → Logs
- **Wrangler CLI (if authenticated):**
  ```bash
  wrangler pages deployments list
  wrangler pages deployment logs <deployment-id>
  ```

## Prevention

- Always test `npm ci` with the same npm version as Cloudflare (npm 10.9.2) before committing
- Never commit symlinks to absolute local paths
- Use `.gitignore` to exclude local-only files/directories
- Regularly check that the deployed site matches your local build

## Related skills

- `dlgrv-desktop` — Contains site-specific deployment notes and git workflow
- `github-pr-workflow` — For creating PRs to trigger deployments
