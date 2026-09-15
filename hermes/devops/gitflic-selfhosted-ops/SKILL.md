---
name: gitflic-selfhosted-ops
description: "Operate self-hosted GitFlic CE: push code, runner, fix CI."
---

# GitFlic Self-Hosted Operations

GitFlic is a Russian GitLab fork (gitflic.ru). Self-hosted CE behaves like GitLab
but with sharp differences. This skill captures the non-obvious parts that cost
many debugging turns to discover.

## When to use
- User has a GitFlic URL (`http(s)://<host>[:port]/<group>/<repo>`).
- Mirror/push code from a local repo into GitFlic "for visibility" / registry (e.g. Минцифры).
- GitFlic CI/CD pipeline shows "config file not found" or YAML parse errors.
- GitFlic runner will not connect or jobs stay pending.

## Hard-won facts (all verified this session)

### 1. Repo URLs and ports
- Web UI runs on the port GitFlic listens on (e.g. `:8080`). The repo clone URLs
  shown in UI are authoritative — copy them, do not guess.
- **SSH is on port 2255, NOT 22.** Port 22 is the host's system `sshd`, which does
  NOT know GitFlic SSH keys → `Permission denied (publickey)`.
- The docker container `gitflic-server` publishes `2255->2255` and `8080->8080`.
  So SSH git access = `ssh://git@<host>:2255/<group>/<repo>.git`.

### 2. Pushing code — basic-auth does NOT work for git
- `git push https://user:token@host/...` fails with
  `fatal: unable to update url base from redirection ... redirect: /auth/login`.
  GitFlic redirects unauthenticated (and token-in-URL) git requests to the login
  page instead of doing HTTP Basic. **Basic auth for git-over-HTTP is not accepted.**
- Password-in-URL also fails the same way.
- **USE SSH.** Generate a dedicated key, add pubkey in UI (Profile → SSH Keys),
  push via `ssh://git@<host>:2255/<group>/<repo>.git`.
- Keep the primary `origin` (e.g. primegit.ru) untouched: add GitFlic as a
  SECOND remote named `gitflic`; never `git remote rename origin`, never
  `git push --mirror`. `git push` (no args) still goes to `origin`.

### 3. Self-signed TLS on a bare IP (no domain)
- Let's Encrypt needs a domain; with only an IP you cannot get a public cert.
- Working setup used here: nginx on the host as TLS-termination reverse proxy.
  GitFlic itself serves plain HTTP on :8080 (inside docker). nginx listens 443,
  terminates a self-signed cert (SAN `IP:<ip>`), proxies `/` → `http://127.0.0.1:8080`.
  Git over HTTPS then works; client uses `git -c http.sslVerify=false` or adds the
  cert to the OS trust store. (Self-signed cert is fine for an internal contour.)
- Alternative without nginx: push over SSH (no cert needed at all) — preferred.

### 4. CI/CD configuration filename is `gitflic-ci.yaml`, NOT `.gitlab-ci.yml`
- Project Settings → CI/CD has a field **"CI/CD configuration file path"**
  (default often `gitflic-ci.yaml`). GitFlic looks for THAT name. A file named
  `.gitlab-ci.yml` in the repo root is NOT picked up → "config file not found".
- If a project already has working gitlab CI expecting `gitflic-ci.yaml`, DO NOT
  change the setting (you'd break the existing pipeline). Instead name your file
  `gitflic-ci.yaml`.
- Existing gitlab config is untouched by simply adding/renaming *your* file.

### 5. GitFlic CI YAML schema is STRICTER than GitLab's
- A `default:` block with `interruptible` / `image` / `cache` / `variables` /
  `rules` triggers: `yaml parsing : ... default can contain only the following fields:`
- Working minimal file:
  ```yaml
  stages:
    - build
    - test
  build:
    stage: build
    image: node:20-bookworm
    script:
      - npm ci
      - npm run build
    artifacts:
      paths:
        - dist/
  test:
    stage: test
    image: node:20-bookworm
    script:
      - npm ci
      - npm test
  ```
  Put `image:` per-job, drop `default:`, `interruptible`, `cache`, `variables`,
  `rules` until you confirm they're supported. Add them back one at a time.

### 6. Runner (agent) setup
- Runner image is **`registry.gitflic.ru/company/gitflic/runner:latest`**
  (NOT `gitflic-runner`). The doc "latest" page suggests docker, but the actual
  image is `runner`, not `gitflic-runner`.
- Install via docker compose (recommended). Template: `templates/gitflic-runner-compose.yaml`.
- Registration token: Admin → CI/CD → Runners → "Add this registration token".
  REG_URL = `http(s)://<host>[:port]/-/runner/registration`.
- `network_mode: host` is recommended by GitFlic docs to dodge self-signed-cert
  issues (runner reaches GitFlic directly, bypassing nginx/TLS).
- Runner type Docker: set `DIDENABLE: false` (uses host docker.sock, mounted).
- Jobs run as `node:20-bookworm` containers on the host — needs Docker Engine.
- If jobs stay `pending`: check runner TAGS vs job `tags:`. Easiest: leave
  runner `TAGS: ""` (no tags) unless you deliberately tag jobs.

### 7. Resource reality check
Official minimums (docs.gitflic.ru, verified 2026-09-02): GitFlic server
2 CPU / 4GB RAM / 25GB; runner 1 CPU / 2GB / 25GB.
- GitFlic CE is heavy: Java app + postgres + redis (rabbitmq for EE), dockerd.
  On a **4 GB RAM** box with ONE instance, a Java runner + node builds can OOM →
  server unreachable. If the server dies after enabling CI: `docker compose
  -p gitflic-runner down` to relieve memory. For "visibility" purposes, code +
  tags + releases suffice WITHOUT a live runner.
- **TWO instances + 1 shared runner on 8GB works for light load** (verified
  in user's migration plan): JVM heap cap 1–1.5G per instance (compose mem
  limits everywhere), runner CONCURRENCY=1 via shared docker.sock, swap 4G.
  Sizing rationale: devops/vps-infra-ops SKILL.md §Sizing philosophy.
- Disk sizing: light load → сетевой HDD fine; `docker system prune` по cron
  обязателен, иначе сборки съедают диск.

## Verification checklist
- [ ] Repo exists in GitFlic UI (create it if push says "repository not found").
- [ ] SSH key added to Profile → SSH Keys; `ssh -i <key> -p 2255 -T git@<host>` returns GitFlic banner (not "Permission denied").
- [ ] Remote `gitflic` = `ssh://git@<host>:2255/<group>/<repo>.git`; `origin` untouched.
- [ ] CI file named exactly per project setting (usually `gitflic-ci.yaml`).
- [ ] `gitflic-ci.yaml` parses (no `default:` block).
- [ ] Runner container `Up`; UI shows connected runner.

## References
- Official docs: https://docs.gitflic.ru (RU/EN) — min reqs:
  setup/gitflic_app/min_req; runner in docker: setup/runner/docker/docker_run.
- `references/gitflic-runner-compose.md` — full docker-compose.yaml with creds placeholders.
- `templates/gitflic-runner-compose.yaml` — starter compose (copy & edit).
