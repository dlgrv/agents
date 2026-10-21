# Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `python -c "import pm; pm.sync_venv(['stt-whisper'], explicit=True)"` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth` — re-authenticate OAuth providers (or `hermes auth add <provider>`)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.
5. **Surprise "copilot" provider in credential pool / quota widgets**: Hermes
   auto-imports an ambient `gh` CLI token into `auth.json` credential_pool
   (entry source `gh_cli`). A plain gh token CAN pass a bearer probe against
   `api.githubcopilot.com` (HTTP 200) without any Copilot subscription — a
   successful curl there proves nothing about an actual plan. Identify the
   source from the pool entry's label/source fields, never print tokens.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### web_extract shows a stale page (result caching)
`web_search`/`web_extract` cache results for 20 minutes (PR #94618) — a
repeat fetch of the same URL within the TTL is served from cache, which
can look like "my website changes aren't showing up."

Automatic carveouts (always fetched live, never cached):
- localhost / 127.0.0.1 / `*.local` / `*.localhost` / single-label LAN
  hostnames / private + link-local IP ranges (dev servers, hot-reload
  builds, chat-GUI artifact previews)
- URLs matched by `security.website_blocklist`
- failed responses and keyless-rescue-served responses

Developing a site tested over the PUBLIC internet (Vercel/Netlify
preview, ngrok/cloudflared tunnel, staging domain)? Public DNS isn't
auto-carved-out — list the host in config.yaml:

```yaml
web:
  cache_exempt_hosts:      # always fetched live; effective immediately
    - mysite.vercel.app
    - "*.ngrok-free.app"
    - mysite.dev           # suffix match: also covers preview.mysite.dev
```

Blunt instruments: `web.cache_ttl_minutes: 1` (min) or
`web.cache_enabled: false` disables both caches entirely.

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `hermes -s name` (or the skill's own `/<name>` slash command)

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows-specific issues** (`Alt+Enter` newline, WinError 10106, UTF-8 BOM config, line endings): see `references/windows-quirks.md`.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

**vision_analyze errors with a "text only / not supported" accept-code:** the configured
aux vision model is not vision-capable *on that endpoint* — the same model name can be
text-only on a coding endpoint while vision models live elsewhere. Don't swap flash↔full
of the same family; pick a model the endpoint actually serves with images (for z.ai's
coding endpoint that is `glm-4.6v`; the 5.3 family there is text-only). Smoke-test the
endpoint directly (chat/completions with a base64 image, key from `.env`) before blaming
the tool or the key.

Pitfalls once a vision model works:
- **Disable thinking for vision requests** (`"thinking": {"type": "disabled"}`) — image
  queries otherwise burn the whole token budget on reasoning before emitting a single line
  of description, and the answer comes back empty or truncated.
- **Config changes apply to NEW sessions only** — the live session keeps its old routing;
  verify fixes via direct API calls, not by re-calling the tool in-session.
- **Never downscale a dense image (schematic, document scan) before recognition** — the
  model hallucinates unreadable detail at low resolution. Tile the ORIGINAL resolution
  into crops and query each tile, then merge.
- **Find the primary source before transcribing**: photos of published material (magazine
  schematics, articles) often exist digitized in web archives; text from the source plus
  datasheet-standard topology (e.g. К155ИЕ2=7490, ИЕ4=7492) beats pixel-guessing values.
  Old Russian sites are usually koi8-r or cp1251 — decode by trial, mojibake patterns tell
  you which.

### Desktop native notifications never appear (macOS)
Diagnostics, cheapest first:
1. **App-level pref** — desktop notification kinds (approval, turnDone, turnError, backgroundDone) default to ON. The toggle is stored as `hermes:native-notifications` in Electron localStorage (`~/Library/Application Support/Hermes/Local Storage/leveldb/`). `grep -c "hermes:native-notifications" .../leveldb/*.ldb` returning 0 means defaults are in effect — do NOT conclude notifications are disabled.
2. **OS-level permission** — grep the app's bundle id in `~/Library/Preferences/com.apple.ncprefs.plist` (`plutil -convert xml1 -o /tmp/nc.plist <file>` first). Absent = the app never triggered the macOS permission prompt, and macOS silently drops notifications — this is the usual root cause, not an app setting.

Enabling the OS permission is user-interactive and cannot be done programmatically:
- Have the user click **Settings → Notifications → Test** in the desktop app (`sendTestNativeNotification`); the first send fires macOS's "Allow notifications?" dialog which the user must click.
- Fallback: open System Settings → Notifications directly (`open 'x-apple.systempreferences:com.apple.Notifications-Settings.extension'` via terminal — the browser tool cannot read a native Settings window) and have the user toggle the app there.

### "Reset permissions" / auto-approving everything
See `references/security-privacy.md` — wipe the "Always allow" stores, don't touch yolo mode.

