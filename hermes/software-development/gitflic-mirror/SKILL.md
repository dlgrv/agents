---
name: gitflic-mirror
description: Mirror/push code to self-hosted GitFlic (GitLab fork).
---

# GitFlic self-hosted mirror

GitFlic is a **GitLab fork** self-hosted by the user (often for Минцифры software-registry compliance). The main code remote is usually `primegit.ru`; GitFlic is a **second mirror** kept in sync for visibility (commits, tags/releases, green CI), not active development.

## Golden rule: never touch `origin`
Add GitFlic as a **second remote** (`gitflic`). Plain `git push` keeps going to `origin` (upstream unchanged). Only `git push gitflic` reaches GitFlic. Reassure the user: multiple remotes don't auto-fan-out, upstream stays on origin.

## Auth: SSH on port 2255, NOT HTTP basic-auth
- **Git push over HTTP(S) does NOT accept token/password as basic-auth.** GitFlic redirects unauthorized git to `/auth/login`; git fails with `fatal: unable to update url base from redirection`, even with a valid PAT in the URL. Don't waste time on token/password over http(s).
- **SSH works.** But the GitFlic SSH listener is on **port 2255**, NOT 22 (22 is the system `sshd`, which doesn't know GitFlic keys → `Permission denied (publickey)`).
- Remote URL form: `ssh://git@HOST:2255/GROUP/REPO.git`
- `ssh -T` success looks like a *rejection*: `GitFlic не поддерживает данный вид ssh взаимодействия с сервером` — that means auth **succeeded** (GitFlic just refuses an interactive shell). Proceed to push.
- Client needs `GIT_SSH_COMMAND="ssh -i ~/.ssh/id_gitflic -o StrictHostKeyChecking=no -p 2255"`. Use a **dedicated key** per GitFlic instance.

## GitFlic Runner (CI/CD) = binary, NOT a docker image
- `docker pull registry.gitflic.ru/company/gitflic/gitflic-runner:latest` → **not found**; `:4.12.2` → 404/401. No runner docker image in that registry for CE 4.12.x.
- Install via the **"Install GitFlic runner"** button on `/admin/ci-cd/runners` in the UI — it gives the exact binary download URL + registration command for your platform/version. Don't guess the image name.
- Registration token is on the same page (`/admin/ci-cd/runners` → "Add this registration token"). Runner type **Docker** is cleanest when docker is already present (your `.gitlab-ci.yml` using `image: node:20` then works); **Shell** requires node on the host OS.
- Until a runner is connected, pipelines sit `pending`/`stuck` even with a valid `.gitlab-ci.yml`.

## Self-signed TLS on a bare IP (no domain)
Publicly-trusted HTTPS needs a domain (Let's Encrypt won't issue for an IP). For a self-hosted IP:
- Issue cert with SAN = IP: `openssl req -x509 ... -subj "/CN=IP" -addext "subjectAltName=IP:1.2.3.4"`.
- Put **nginx** on the host as TLS-termination reverse proxy → `proxy_pass http://127.0.0.1:8080` (GitFlic container). Redirect 80→443. nginx is a 1-package addition, safe.
- Client: either `git config http.sslVerify false` (per-repo) or `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain gitflic.crt` (macOS, preferred).
- Validated: after setup `curl -k https://IP/` → 302, `curl http://IP/` → 301.

## Repo must exist before push
A pre-added remote does NOT mean the repo exists on the server. If `git push` returns `Could not read from remote repository` / `repository not found` after SSH auth succeeds → create the repo in the GitFlic UI (group → New project) first. The Clone pop-up shows the authoritative SSH URL.

## CI file hygiene for "visibility"
Keep `.gitlab-ci.yml` minimal and green without secrets: `npm ci && npm run build` (+ `npm test` if vitest exists). **Remove deploy stages** needing SSH keys / unknown hosts — they turn the pipeline red and defeat the visibility goal. Both `crbsit-site` and `primeconfigurator` have `build` + `test` (vitest) scripts.

## References
See `references/gitflic-recipes.md` for copy-paste command sequences (cert+nginx, SSH key, runner note, validated push).
