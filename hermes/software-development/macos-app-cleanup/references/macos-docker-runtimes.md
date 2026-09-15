# macOS Docker runtimes: Docker Desktop vs OrbStack vs Colima

Session-tested 2026-09 (macOS 26, Apple Silicon M5). Context: user's containers ≈ 2× Postgres, several Vite frontends, FastAPI/Python APIs, Redis, MinIO, Mailpit → real need ~4.5 GB, ~8 GB with an optional llama.cpp profile.

## Why macOS always needs a VM

Linux containers need a Linux kernel; macOS can't run them natively. Every Docker-on-macOS option = Linux VM + dockerd inside. On Ubuntu there is no VM layer — that's why "docker was only in the terminal" there.

## Comparison (2026 benchmarks + session observation)

| | Docker Desktop | OrbStack | Colima |
|---|---|---|---|
| Idle RAM | 1.8–4.2 GB | 0.5–0.8 GB | ~0.35–2 GB |
| Memory model | VM holds allocation | dynamic (ballooning, gives RAM back in seconds) | VM holds, needs `colima stop` |
| Compose cold start | ~9 s | ~4 s | fast container start |
| Bind-mount fs (vite HMR) | baseline 800–1200 ms reload | 2–3× faster (200–400 ms) | slower than OrbStack |
| Image builds | fastest | 2nd | — |
| GUI | full app | optional (menu-bar icon on `orb start`; window only if opened) | none |
| License | paid for corp | free personal, $96/yr commercial | MIT free |
| CLI-first usage | awkward | documented headless mode | native |

## OrbStack session notes

- Install: `brew install --cask orbstack`, then `open -a OrbStack` (first run does setup). CLI: `orb status/start/stop`, `orb top`, `orb restart docker`.
- Docker context auto-switches to `orbstack` (`docker context ls` to verify). The old `/usr/local/bin/docker` symlink into Docker.app keeps working — context decides which daemon answers.
- **Resource limits**: `orbctl config set machine.docker.cpu 4` and `orbctl config set machine.docker.memory_mib 8192`. These are CEILINGS, not reservations — with ballooning, idle usage stays ~0.5 GB. The settings only fully apply after quitting + reopening the app (`osascript -e 'tell application "OrbStack" to quit'`, then reopen). `docker info` may still show global values (16 GB/18 CPU) — that's OrbStack's dynamic reporting, not the cap being ignored.
- Config lives in `~/.orbstack/` (vmconfig.json was empty in practice; authoritative state via `orbctl config show`).
- `orb config set ...` (without `ctl`) fails for these keys — use `orbctl config set`.
- Auto-update doesn't work without GUI use — update manually via `brew upgrade orbstack`.

## Migration Docker Desktop → OrbStack

1. `docker compose down` in projects; quit Docker Desktop.
2. Containers/images do NOT migrate (and usually don't need to — recreate from compose). Volumes do not migrate either; for dev data either recreate (alembic/`npm install` refills them) or tar-backup: `docker run --rm -v <vol>:/data -v $(pwd):/backup alpine tar czf /backup/vol.tgz /data` (works on any engine).
3. Start OrbStack, `docker compose up -d` — images re-pull (~1–2 GB), volumes recreate.
4. Verify `docker compose ps` + healthchecks before uninstalling Desktop.
5. Docker Desktop removal is a standard app-cleanup pass (app + `/usr/local/bin/docker` symlink + `~/Library/Group Containers/group.com.docker`, `~/Library/Containers/com.docker.docker`, `com.docker.vmnetd` privileged helper + LaunchDaemon, `~/Library/Application Support/com.docker.install` = 2 GB installer cache, NOT data).

## Sizing heuristic discussed with user

Set the VM ceiling from the *worst simultaneous compose stack*, not per-service sums + fear. Docker Desktop's 8 GB was correct for their projects including an optional 3.2 GB llama.cpp service (compose `profiles:` — doesn't start on plain `up`). Desktop allocates lazily too; the real waste was running the Desktop app+daemons with zero containers, not the limit itself.

## Migration OrbStack → Docker Desktop (обратная, session-tested 2026-09)

1. `docker compose down -v` во всех запущенных проектах — данные внутри VM OrbStack (5 GB Group Containers) пропадут; спросить про pgdata заранее.
2. Quit app → `brew uninstall --cask orbstack --force` (uninstall script снимает app сам).
3. Данные: `rm -rf ~/.orbstack ~/OrbStack "~/Library/Group Containers/HUAQ24HBR6.dev.orbstack" "~/Library/Application Scripts/HUAQ24HBR6.dev.orbstack"`. Папка `~/OrbStack` создаётся read-only (r-xr-xr-x) — сначала `chmod -R u+rwx`.
4. Privileged helper (нужен админ, неинтерактивно — osascript with administrator privileges): `launchctl bootout system /Library/LaunchDaemons/dev.orbstack.OrbStack.privhelper.plist; rm -f <plist> /Library/PrivilegedHelperTools/dev.orbstack.OrbStack.privhelper`.
5. Симлинки в /usr/local/bin (root) OrbStack перезаписывает своими — вернуть на Docker.app: `docker`, `docker-credential-osxkeychain` → `/Applications/Docker.app/Contents/Resources/bin/…`; `docker-compose` НЕ восстанавливать (compose = cli-plugin, `docker compose`); убрать `orb`, `orbctl`, `kubectl`.
6. Убрать `source ~/.orbstack/shell/init.zsh` из ~/.zprofile; `docker context rm orbstack`.
7. Docker Hub из VM Docker Desktop может отдавать EOF при рабочем host-`curl` (VPN/троттлинг): в settings-store.json (Group Containers/group.com.docker) поставить ProxyHttpMode=manual + OverrideProxyHttp(s)=http://127.0.0.1:<порт clash/mihomo> (порты: `lsof -nP -iTCP -sTCP:LISTEN | grep mihomo`). Пуллы всё равно флакие — ретраить 2-3 раза.
8. Диагностика: `pgrep -x Docker` НЕ видит приложение (процесс называется "Docker Desktop"); живость движка — `curl --unix-socket ~/.docker/run/docker.sock http://localhost/_ping`.
