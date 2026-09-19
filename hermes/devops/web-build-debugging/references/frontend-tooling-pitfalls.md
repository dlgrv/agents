# Frontend Tooling Pitfalls

## Vite HMR breaks on structural refactoring

**Symptom:** White screen in browser after file moves, new file creation, or import path changes. `npx vite build` and `npx tsc --noEmit` pass, but browser shows blank page with 0 elements.

**Root cause:** Vite's HMR (Hot Module Replacement) can't track module graph changes when files are created, moved, or when import structures shift significantly. The dev server continues running and reports "connected" but React fails to render silently — console errors appear as empty-message exceptions.

**Fix:** Kill and restart the dev server:
```bash
pkill -f vite && npx vite --host 0.0.0.0
```

**Detection:** After any refactoring that involves file creation/moves, always do a browser navigation check, not just TypeScript + build verification.

## Docker white screen after code changes — check volume mounts first

**Symptom:** User runs `docker compose up -d` after you've changed 10+ frontend files. White screen on the Docker-served port (e.g., 5173).

**Step 1 — Check if `docker-compose.override.yml` mounts volumes:**

```bash
cat docker-compose.override.yml | grep -A2 'frontend:'
# If you see `volumes: - ./frontend:/app`, code IS synced live
```

**If volumes ARE mounted** (common in dev override files): the container's filesystem mirrors your local source. The code is NOT stale — the white screen is browser-side (cache, service worker, stale HMR in the user's browser tab). Verify by checking the page yourself:

```bash
curl -s http://localhost:5173/ | head -5   # If HTML is served, server is fine
# Or: browser_navigate to the Docker port — if it rendered, it's the user's browser
```

Fix: tell the user to hard-refresh (`Cmd+Shift+R`) or clear site data in DevTools. Do NOT tell them to rebuild the image — that's not the problem.

**If volumes are NOT mounted** (no override, or production-like setup): the Dockerfile's `COPY . .` copies source at build time. `docker compose up -d` WITHOUT `--build` reuses the old image with old code. Fix:

```bash
docker compose up -d --build frontend
```

**Key distinction:**
- Volumes mounted + white screen → browser cache / HMR (tell user to hard-refresh)
- No volumes + white screen after code changes → stale image (`--build`)
- HMR broke mid-session (no code changes) → `docker restart lowbid_frontend`

**Lesson learned:** In this project, `docker-compose.override.yml` mounts `./frontend:/app` with a separate `frontend_node_modules` volume. Code changes are live-synced. When the user reported white screen after token migration, the assumption was stale image — but the code was actually current. The real issue was the user's browser cache. Always check `docker-compose.override.yml` for volume mounts before assuming stale image.

## `vite build` rejected by terminal tool as "long-lived"

**Symptom:** `npx vite build` in foreground `terminal()` is rejected with: "This foreground command appears to start a long-lived server/watch process."

**Root cause:** The terminal tool's heuristic detects `vite` in the command and assumes it's a dev server (which never exits). `vite build` does exit, but the heuristic can't distinguish `build` from `dev`.

**Fix:** Run `vite build` with `background=true` + `notify_on_complete=true`, then `process(action='wait')`:
```bash
# In terminal(background=true, notify_on_complete=true):
npx vite build 2>&1 | tail -5
# Then process(action='wait') to get the result
```

`npx tsc --noEmit` runs fine in foreground — only `vite build` triggers the heuristic.

## `npx tsc --noEmit` + `npx vite build` combined in one command

Don't chain `tsc && vite build` in a single foreground `terminal()` call — `vite build` triggers the long-lived heuristic even when chained after `tsc`. Run them as separate calls:
1. `npx tsc --noEmit` (foreground, fast)
2. `npx vite build` (background + notify_on_complete, then wait)