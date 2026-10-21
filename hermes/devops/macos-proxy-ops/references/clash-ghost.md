# Clash Ghost on this Mac (mihomo core)

## Where things live
- App support dir: `~/Library/Application Support/dev.clashghost.app/`
- SOURCE OF TRUTH for the PAC: `settings.json` → `pac_content` (a JSON string field; the editor in the app UI writes it).
- `proxy.pac` in the same dir is a GENERATED artifact — the app rewrites it (identical content restored, manual line gone, fresh mtime). Do not edit it.
- Config files here are rewritten from memory on app quit — edit `settings.json` only after the app is fully quit, then relaunch.

## Port map (mihomo listeners, all on 127.0.0.1)
- 17890 — HTTP proxy
- 17891 — SOCKS proxy (also bound on the Parallels host IP by a separate process — do not confuse)
- 17892 — PAC server run by the clash-ghost GUI process; macOS system proxy points here: `http://127.0.0.1:17892/proxy.pac` (check with `scutil --proxy`)
- 19090 — mihomo API

## PAC structure (custom "RU Direct, Others Proxy")
Sections in order: infra bypass (loopback/private/CGNAT, always enforced, prepended by the app) → 1 local networks → 2 RU TLDs (.ru/.su/.рф/.москва) → 3 RU services on international domains (vk, yandex CDNs…) → 4 user exceptions (volgatech.net, twitch + CDNs, …) → fallback `PROXY 127.0.0.1:17890`.

Adding a site to DIRECT = one line in section 4:
```js
        dnsDomainIs(host, "example.com") || // why
```
Suffix match covers all subdomains.

## Restart procedure (only with user approval — restarts drop proxy for all chats)
1. Ask; warn that the NL profile won't auto-reconnect (`auto_connect: false`) and the user must reconnect manually.
2. Quit app fully (`osascript -e 'quit app "Clash Ghost"'`; verify the mihomo process exited).
3. Edit `settings.json` `pac_content` (python json round-trip, not sed — it's one long escaped string).
4. Relaunch, wait for 17892 to listen, then `curl -s http://127.0.0.1:17892/proxy.pac | grep <domain>` to confirm the served PAC changed.
5. User reconnects the profile; browser PAC cache still needs a restart/Re-apply.
