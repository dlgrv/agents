---
name: llm-provider-key-validation
description: "Verify LLM API keys work; avoid OpenRouter false positives."
version: 1.0.0
author: hermes-session
---

# LLM Provider Key Validation

Use when you add, configure, or troubleshoot an LLM provider key in Hermes
(`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `COMETAPI_KEY`,
etc.) and need to prove the key is LIVE — not just that the file was edited.

## Class workflow
1. Write the secret into `~/.hermes/.env` (secrets ONLY here, never config.yaml).
   NOTE: `.env` cannot be read via `read_file` (credential-store guard) — edit it
   with terminal `sed`/`patch`/`grep`, never read-then-write (you can't read it back).
2. Register the credential pool: `hermes auth add <provider>`. In non-TTY shells
   the interactive prompt may fail to read input — that's OK; Hermes reads the
   `.env` var at request time. Confirm with `hermes auth list`.
3. VALIDATE with a real authenticated request (see Pitfall). Do NOT skip this step.

## Pitfall — OpenRouter false positive (the big one)
`GET https://openrouter.ai/api/v1/models` is a PUBLIC endpoint. It returns
`HTTP 200` even with an EMPTY or INVALID `OPENROUTER_API_KEY`. Testing the key
with `/models` falsely reports success ("HTTP 200, models returned").

CORRECT validation — make a real chat completion:
```bash
ORK=$(grep '^OPENROUTER_API_KEY=' ~/.hermes/.env | cut -d= -f2)
curl -s --max-time 30 https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $ORK" \
  -H "Content-Type: application/json" \
  -d '{"model":"z-ai/glm-5.2:free","messages":[{"role":"user","content":"hi"}]}'
```
- Valid key → a completion object (or a model-specific error, NOT 401).
- `401 {"error":{"message":"User not found."}}` → the key string is fine but is
  NOT attached to any live OpenRouter account (wrong key, deleted/blocked
  account, or unconfirmed account). Fix: a fresh key from the logged-in
  account at https://openrouter.ai/keys, not a Hermes config change.

General rule: never validate a credential with a public/unauthenticated
endpoint. Always exercise the authenticated code path you actually depend on.

See references/openrouter.md for the full false-positive transcript and free-model notes.
