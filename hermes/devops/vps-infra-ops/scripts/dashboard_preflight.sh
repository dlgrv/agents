#!/usr/bin/env bash
# Pre-flight the Hermes dashboard auth before connecting the Mac desktop via
# remote gateway. Runs from the Mac, no desktop app needed.
# Usage: dashboard_preflight.sh HOST [PORT] [USER] [PASSWORD]
#   USER/PASSWORD fall back to env HERMES_DASH_USER / HERMES_DASH_PASS
#   (prefer env over argv so secrets stay out of shell history).
set -uo pipefail
HOST=${1:?host}; PORT=${2:-9119}
USER=${3:-${HERMES_DASH_USER:-}}; PASS=${4:-${HERMES_DASH_PASS:-}}
[ -n "$USER" ] || { echo "need user (arg3 or HERMES_DASH_USER)" >&2; exit 2; }
[ -n "$PASS" ] || { echo "need password (arg4 or HERMES_DASH_PASS)" >&2; exit 2; }
BASE="http://$HOST:$PORT"; T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

title=$(curl -sm 10 "$BASE/" | grep -o '<title>[^<]*' | head -1 || true)
echo "1) GET / -> ${title:-<no title>}   (auth gate on = 'Sign in — Hermes Agent')"

code=$(curl -sm 10 -o /dev/null -w '%{http_code}' -u "$USER:$PASS" "$BASE/api/sessions")
echo "2) Basic-auth API probe -> HTTP $code   (401 expected: API is cookie-based, not Basic)"

body=$(python3 -c "import json,sys;print(json.dumps({'provider':'basic','username':sys.argv[1],'password':sys.argv[2]}))" "$USER" "$PASS")
code=$(curl -sm 10 -c "$T/c.txt" -X POST "$BASE/auth/password-login" -H 'Content-Type: application/json' -d "$body" -o "$T/login.json" -w '%{http_code}')
echo "3) POST /auth/password-login -> HTTP $code  $(cat "$T/login.json")  (200 = creds OK)"

code=$(curl -sm 10 -b "$T/c.txt" -o "$T/sess.json" -w '%{http_code}' "$BASE/api/sessions?limit=5")
n=$(python3 -c "import json,sys
try: print(len(json.load(open(sys.argv[1])).get('sessions',[])))
except Exception: print('?')" "$T/sess.json")
echo "4) Cookie auth /api/sessions -> HTTP $code, $n sessions   (200 + N>0 = desktop sign-in will work)"
