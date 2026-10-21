---
name: macos-proxy-ops
description: Use when a site won't load or Mac proxy/PAC is suspect.
---

# Local Mac proxy debugging

## When to Use
- A website won't load and DNS/direct access is unclear.
- Before/after editing a PAC file or any proxy-client config on this Mac (Clash Ghost/mihomo).
- "Added an exception but it still doesn't work" — browser PAC cache or served-artifact mismatch.

## Diagnose in layer order, before touching anything
1. DNS: `dig +short <domain>`.
2. Direct vs proxied: `curl -sv --noproxy '*' https://<domain>` vs `curl -x 127.0.0.1:17890 https://<domain>`. If direct works and proxied hangs → the proxy chain (PAC or proxy port) is the problem, not the site.
3. Find what the system actually uses: `scutil --proxy` (singular). On this macOS build `scutil --proxies` is not a valid flag. If `ProxyAutoConfigEnable: 1`, the PAC URL there is the source of truth — not any file you edited.
4. Find the listeners: `lsof -nP -iTCP -sTCP:LISTEN | grep -E '<ports|process names>'`.

## Never edit generated files of a running app
An app that stores its config in JSON and serves/renders derived artifacts (PAC, generated configs) will regenerate the artifact and silently revert hand edits to it. Editing the file at all is wasted work: find the source-of-truth field (e.g. Clash Ghost: `settings.json` → `pac_content`) and change that, via the app's own UI when it has one, or by quitting the app fully, editing the source file, and relaunching.

After any change, verify the SERVED artifact, not the file on disk — for Clash Ghost PAC: `curl -s http://127.0.0.1:17892/proxy.pac | grep <domain>`. Browsers cache PAC: browser restart or `chrome://net-internals/#proxy` → Re-apply settings is needed before the user sees the effect.

## Clash Ghost on this Mac — specifics
- Clash Ghost is sensitive territory (a past incident); never restart it without asking. A restart drops the proxy for all running chats and the WS-TLS NL profile does NOT auto-reconnect (`auto_connect: false`) — the user must click connect manually.
- When a fix needs an app restart, offer the user the GUI-edit path first; he prefers making UI changes to this app himself.
- Port map, PAC source of truth, and restart procedure: see `references/clash-ghost.md`.

## Testing PAC logic without a browser
`dnsDomainIs(host, "example.com")` is a suffix match, so one rule covers the domain and all subdomains (app., api., …). Verify a PAC evaluates correctly by loading it in node with global shims before/after editing:

```js
global.isPlainHostName = h => !h.includes('.');
global.dnsDomainIs = (h, s) => h === s.slice(1) || h.endsWith(s);
global.isInNet = () => false;
eval(require('fs').readFileSync('<pac-path-or-downloaded>', 'utf8'));
for (const h of ['example.com','api.example.com','google.com'])
  console.log(h, '=>', FindProxyForURL('https://' + h, h));
```
