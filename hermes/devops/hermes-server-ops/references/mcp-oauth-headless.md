# Headless MCP OAuth login (VPS Hermes)

`hermes mcp login <provider>` on a headless server prints an authorize URL and
starts a one-shot callback listener on an EPHEMERAL localhost port. The browser
runs on the user's Mac, the listener on the server — the callback cannot land
by itself. Validated flow:

1. Run the login inside a tmux session with a WIDE panel. Long authorize URLs
   wrap, and a naive copy grabs a truncated URL (guaranteed consent-page
   error). Extract the URL programmatically instead:
   `tmux capture-pane -p -t <session>` then regex `https://\S*authorize\S*`,
   and open the full match in the user's local browser.
2. The provider's consent page is where the user picks the scope (full vs
   read-only) — a provider-side choice, Hermes has no flag for it.
3. After consent the browser redirects to `http://127.0.0.1:<port>/callback?code=…`
   ON THE MAC and shows "connection refused / reset" — that is expected; the
   code lives in the address bar. Have the user copy the FULL callback URL.
4. Land the callback on the server: pre-open an SSH remote forward for the
   port (`ssh -R <port>:127.0.0.1:<port> root@<server>`) BEFORE the user
   consents, and finish consent+callback within ~5 minutes — the listener
   exits on a ~300 s timeout, and "connection was reset" means it already
   died. If it expired: re-run login (new port + new URL) and redo consent;
   the old code is dead. The callback port CHANGES between attempts — never
   assume the previous port.
5. Verify: `cat ~/.hermes/mcp-tokens/<provider>.json` (access + refresh;
   refresh is automatic afterwards) and enumerate the MCP's tools after a
   gateway restart.

Pitfalls: truncated/wrapped URL paste is the #1 failure; reusing a dead
listener's port after the timeout is #2. Tunnel-first + fast consent beats URL
replay.
