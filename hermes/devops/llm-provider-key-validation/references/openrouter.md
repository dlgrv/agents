# OpenRouter key validation — reference notes

## The false-positive trap (observed 2026-08-24)
- `GET https://openrouter.ai/api/v1/models` returns `HTTP 200` with NO valid
  key. It is a public catalog endpoint. Using it to "confirm" a key gives a
  false PASS.
- Real test must hit `POST https://openrouter.ai/api/v1/chat/completions` with
  `Authorization: Bearer <key>` and a `:free` model.

## Observed failure transcript (invalid key)
```
$ curl .../chat/completions -d '{"model":"z-ai/glm-5.2:free",...}'
{"error":{"message":"User not found.","code":401}}
HTTP 401
```
Meaning: the key STRING is well-formed (`sk-or-v1-` + 64 hex) but is NOT
attached to any live OpenRouter account. Causes: wrong/copied-from-elsewhere
key, deleted or blocked account, or unconfirmed (e-mail/payment) account.
Fix: generate a fresh key from the LOGGED-IN account at https://openrouter.ai/keys.

## Free models (catalog snapshot, 2026-08-24)
`/api/v1/models` grepped for `"id":"...:free"` returned 15 entries, incl.:
- z-ai/glm-5.2:free
- google/gemma-4-26b-a4b-it:free, google/gemma-4-31b-it:free
- nvidia/nemotron-3-super-120b-a12b:free, nvidia/nemotron-3-ultra-550b-a55b:free
- cohere/north-mini-code:free
OpenRouter may require a payment method (even $0) attached for some `:free`
models — that is OpenRouter policy, independent of Hermes.
