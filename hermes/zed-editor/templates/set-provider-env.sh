#!/bin/sh
# Expose LLM provider API keys to GUI apps (Zed) via launchctl setenv.
# macOS GUI apps don't inherit shell env, so this runs at login (see
# ~/Library/LaunchAgents/app.dlgrv.zed-provider-keys.plist).
# Keys live in ~/.hermes/.env — single source of truth, not duplicated here.
#
# Zed names env vars for custom openai_compatible providers as <PROVIDER_ID>_API_KEY:
#   cometapi         -> COMETAPI_API_KEY
#   openrouter-free  -> OPENROUTER_FREE_API_KEY
#   opencode-zen     -> OPENCODE_ZEN_API_KEY

ENV_FILE="$HOME/.hermes/.env"

get_value() {
    grep -E "^${1}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//'
}

set_key() {
    key="$1"; src="$2"
    value=$(get_value "$src")
    if [ -n "$value" ]; then
        /bin/launchctl setenv "$key" "$value"
    fi
}

# COMETAPI_KEY is the real var name in .env; Zed wants COMETAPI_API_KEY
set_key COMETAPI_API_KEY COMETAPI_KEY
set_key COMETAPI_KEY COMETAPI_KEY
set_key OPENROUTER_API_KEY OPENROUTER_API_KEY
set_key OPENROUTER_FREE_API_KEY OPENROUTER_API_KEY
set_key OPENCODE_ZEN_API_KEY OPENCODE_ZEN_API_KEY
