---
name: macos-app-cleanup
description: "Systematically find and remove orphaned app artifacts on macOS — Application Support, Caches, Preferences, Containers, LaunchAgents/Daemons, system extensions, and stale brew casks. Use when the user asks to clean up Mac, remove leftover files from uninstalled apps, or audit disk usage."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [macos, cleanup, disk-cleanup, brew, system-extensions]
    related_skills: []
---

# macOS App Cleanup

Use this skill when the user asks to clean up their Mac, remove leftover files from uninstalled apps, find orphaned artifacts, or audit what's taking disk space.

## Approach

1. **Inventory installed apps** — know what's actually installed before declaring something orphaned.
2. **Scan all artifact locations** — Application Support, Caches, Preferences, Containers, LaunchAgents/Daemons.
3. **Cross-reference** — compare artifacts to installed apps; anything without a corresponding app is orphaned.
4. **Check system-level items** — system extensions, audio drivers, brew casks without apps.
5. **Generate cleanup commands** — group by safety level, provide copy-paste blocks.

## Step 1: Inventory Installed Apps

```bash
# All apps in /Applications
ls -d /Applications/*.app | sed 's|/Applications/||' | sort

# User-level apps
ls -d ~/Applications/*.app 2>/dev/null | sort

# Spotlight (most comprehensive — finds apps everywhere)
mdfind "kMDItemKind == 'Application'" | grep -v "^/System/" | sort

# Brew casks and formulae
brew list --cask
brew list --formula
```

## Step 2: Scan Artifact Locations

### Application Support (largest artifacts)

```bash
# All non-Apple Application Support dirs
ls ~/Library/Application\ Support/ | grep -v "^com\.apple\." | sort

# Get sizes — sort by size to find biggest orphans
for dir in ~/Library/Application\ Support/*/; do
  du -sh "$dir" 2>/dev/null
done | sort -rh | head -30
```

### Caches

```bash
ls ~/Library/Caches/ | grep -v "^com\.apple\." | sort
```

### Preferences (plist files)

```bash
# List non-Apple plists
for plist in ~/Library/Preferences/*.plist; do
  name=$(basename "$plist" .plist)
  [[ "$name" == com.apple.* ]] && continue
  echo "$name"
done | sort
```

### Containers (sandboxed apps)

```bash
ls ~/Library/Containers/ | grep -v "^com\.apple\." | sort
```

### LaunchAgents and Daemons

```bash
ls ~/Library/LaunchAgents/ 2>/dev/null    # User-level
ls /Library/LaunchAgents/ 2>/dev/null      # System-level user agents
ls /Library/LaunchDaemons/ 2>/dev/null     # System daemons
```

## Step 3: Check System-Level Items

### System Extensions (can get stuck)

```bash
systemextensionsctl list
```

Stuck extensions (from apps deleted without proper uninstallers) require either:
- **Reinstall + official uninstall** — download the .pkg, install, run the vendor's uninstall script
- **Recovery Mode** — `csrutil disable` → `systemextensionsctl uninstall <teamID> <bundleID>` → `csrutil enable`

### Audio drivers (Audio Hijack / ACE)

```bash
ls /Library/Audio/Plug-Ins/HAL/
# Remove orphaned drivers:
sudo rm -rf /Library/Audio/Plug-Ins/HAL/<DriverName>.driver
sudo killall coreaudiod
```

### Brew casks without apps

```bash
# For each cask, check if the app actually exists
for cask in $(brew list --cask); do
  app_path=$(brew info --cask "$cask" 2>/dev/null | grep -o '/Applications/[^ ]*\.app' | head -1)
  if [ -z "$app_path" ] || [ ! -d "$app_path" ]; then
    echo "ORPHAN: $cask"
  fi
done
```

Some casks fail to uninstall when the app's uninstaller script is missing. Force-remove:
```bash
brew uninstall --force --cask <name>
rm -rf /opt/homebrew/Caskroom/<name>
```

## Step 4: Cross-Reference and Classify

For each artifact found, classify:

| Safety | Criteria |
|--------|----------|
| ✅ Safe | App not in /Applications, not in brew list, not in Spotlight |
| ⚠️ Check | App exists but artifact looks like installer cache (e.g. `com.docker.install`) |
| ❌ Keep | App is installed and artifact is active data |

## Step 5: Generate Cleanup Commands

Group commands by category. Always use `rm -rf` for directories and `rm -f` for files. Provide a single copy-paste block.

### Common orphan patterns

- `~/Library/Application Support/<AppName>` — main data dir
- `~/Library/Caches/<bundleID>` — cache
- `~/Library/Preferences/<bundleID>.plist` — preferences
- `~/Library/Containers/<bundleID>` — sandboxed app container
- `~/Library/Logs/<AppName>` — logs
- `~/.<appname>` — dotfile config (e.g. `~/.codex`)

### Trash that won't delete

Apps in `~/.Trash/` with SIP-protected files (code signatures, frameworks) need:
```bash
sudo rm -rf ~/.Trash/<AppName>.app
# Or empty trash via Finder
```

## Full Uninstall of an Installed App (user asks "вычистить полностью" / remove app + all artifacts)

Work in passes and verify after each:

1. **Find everything first** — `mdfind "kMDItemFSName == '*<name>*'"` plus `find ~/Library -maxdepth 3 -iname "*<bundleid-or-name>*"`. Check: /Applications, ~/Applications (incl. VM-created dirs like `~/Applications (Parallels)`), /Library/<Vendor>, ~/Library/{Preferences,Containers,Group Containers,Application Scripts,Caches,HTTPStorages,Logs,Mobile Documents}, /Library/Application Support/<App> (can be GBs — e.g. GarageBand 907MB, Logic, Groove), /Library/Audio/Apple Loops.
2. **Pass 1 — user-writable data** (no sudo): Application Support, Caches, plists (incl. `ByHost/*.ShipIt.*`), HTTPStorages, Logs, Application Scripts, Group Containers, Mobile Documents (iCloud app data). Use plain `rm -rf` via terminal.
3. **Pass 2 — apps + /Library system content**: needs admin. In a non-interactive session `sudo -n` fails; use `osascript -e 'do shell script "..." with administrator privileges with prompt "..."'` — pops the native macOS auth dialog for the user. Check first for leftover daemons: `launchctl list | grep -i <name>`, /Library/LaunchDaemons, kextstat, /Library/PrivilegedHelperTools — bootout/uninstall before deleting.
4. **Pass 3 — sandbox containers**: `~/Library/Containers/<bundleID>` are protected by containermanagerd — `Operation not permitted` even as root. Delete what's inside works, the dir + `.com.apple.containermanagerd.metadata.plist` stay. Don't fight it: report them as ~KB inert leftovers that macOS reaps after a reboot (or user deletes via Finder).
5. **Shared-component guard**: apps in a family share plists/helpers — e.g. deleting Excel must NOT remove `com.microsoft.office.plist` or Microsoft AutoUpdate while Word stays. Inventory sibling apps before touching shared identifiers.
6. **Verify**: re-run the find commands; every remaining path should be explained (sandbox-protected / intentionally kept).

## Memory & disk audit technique ("what's eating RAM/disk", "which apps are stale")

- RAM by app (aggregate Chromium-style multi-process apps): `ps -Ao rss,comm | awk 'NR>1 {rss=$1; $1=""; key=$0; sub(/^ +/,"",key); split(key,p,"/"); app=p[3]; gsub(/\.app.*/,"",app); sum[app]+=rss} END {for (a in sum) printf "%6.0f MB  %s\n", sum[a]/1024, a}' | sort -rn | head -15` — top-level ps sorting hides Arc/Chrome/Cursor true totals.
- Real last-used date (not file mtime): `mdls -raw -name kMDItemLastUsedDate /Applications/X.app`; `(null)` means never launched (or not indexed) — pair with data-dir sizes to judge staleness. Session-based apps (browsers, editors) also leave per-app data: check `~/Library/Application Support/<App>` size before calling an app abandoned.
- Dev caches worth sweeping: `~/.cache/uv` (can be GBs), `~/.npm/_cacache`, `brew cleanup` (check with `-n` first), `docker system prune -af --volumes` (warn: -volumes drops DB data), Docker installer cache `~/Library/Application Support/com.docker.install` (safe vs real data in Group Containers), editor `state.vscdb.backup` duplicates (GBs), Xcode DerivedData.
- macOS `pmset` power tuning (`-c` = charger, `-b` = battery; verify with `pmset -g custom`). Changing system settings non-interactively: same osascript admin-privileges pattern.
- Replacing Docker Desktop with a lighter runtime (OrbStack/Colima) on macOS: see `references/macos-docker-runtimes.md` — comparison, OrbStack config keys (`orbctl config set machine.docker.*`), migration steps, volume-transfer command.
- Cursor/VSCode-specific housekeeping (extension audit, dead workspaceStorage, state.vscdb): see the "Editor/workspace housekeeping" section above.

## Editor/workspace housekeeping (Cursor/VSCode family)

When auditing a machine with Cursor/VSCode installed, these are the recurring wins:

- **Extension audit**: `ls ~/.cursor/extensions/` (12+ extensions is common bloat). Correlate with what the user actually works in: Go extension (`golang.go` pulls gopls, hundreds of MB RAM) only if Go projects exist; GitLens (`eamodio.gitlens`) is the heaviest git plugin and is redundant if the user has a separate git GUI (GitKraken CLI spawns its own `gk mcp` processes); `indent-rainbow` is pure cosmetics. Uninstall via `cursor --uninstall-extension <id>` (works even though the binary lives in the app), then **also clean `extensions.json`** in the same dir and the extension's `globalStorage/<id>` data dir — the CLI uninstall leaves the registry entry, which resurrects processes until edited.
- **Dead workspace storage**: `~/Library/Application Support/Cursor/User/workspaceStorage/` accumulates one dir per opened folder forever. Sweep: `find ... -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +`. ~2/3 of entries are typically stale.
- **AI-chat history DB**: `User/globalStorage/state.vscdb` grows unbounded (11+ GB seen). There is a `state.vscdb.backup` next to it (another GBs) — the backup is safe to delete outright. The live db can only be shrunk from the app UI (delete old AI chats), not by deleting the file.
- **Python/uv projects**: set in User `settings.json` — `"python.defaultInterpreterPath": ".venv/bin/python"`, `"python.venvFolders": [".venv", "venv"]`, `"python.terminal.activateEnvironment": true` — stops per-workspace env autodetection.
- **settings.json gotcha**: these settings files are JSONC (comments allowed) but the patch/write tooling validates strict JSON — a file with `//` comments or trailing commas will be refused. Cleanest fix is a full rewrite via write_file (comments dropped — they're usually dead code anyway).

## Pitfalls

- **Don't delete Apple system containers** — anything starting with `com.apple.` is system-level. Always filter these out.
- **Some artifacts belong to installed apps** — e.g. `BitTorrentHelper` belongs to Transmission. Cross-reference before deleting.
- **Brew cask uninstaller scripts may be missing** — when the app was deleted manually before `brew uninstall`, the cask's uninstaller.sh doesn't exist. Use `--force` and manual Caskroom cleanup.
- **System extensions are SIP-protected** — cannot be removed with `sudo rm` while SIP is enabled. Must use Recovery Mode or reinstall+uninstall approach.
- **`com.docker.install` is NOT Docker's data** — it's the installer cache. Docker's actual data is in `~/Library/Containers/com.docker.docker` and `~/Library/Group Containers/group.com.docker`. Safe to delete `com.docker.install` even when Docker is installed.
- **Empty Application Support dirs (0B)** — leftover from browser installs (Brave, Edge, Opera, Vivaldi, Chromium, CEF). Safe to delete.
