---
name: account-recovery-appeals
description: "Use when an account is suspended, deactivated, or banned."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Support, Appeals, Recovery, Account, Deactivation, Ban]
    related_skills: [blocked-page-recovery]
---

# Account Recovery Appeals

A service has locked the user out: "account deleted or deactivated", "suspended",
"banned", "sign-in not found". The agent rarely holds the user's credentials, so
the deliverable is **diagnosis + a ready-to-send letter + the exact channel** —
not a completed send. Do the legwork; let the user press Send from their own
authenticated client.

Scope: suspensions, deactivations, bans, deletions, lockouts across services
(OpenAI, Google, GitHub, LinkedIn, hosts). If the page is merely blocked for
reading (403/paywall/WAF), that is `blocked-page-recovery`, not this.

## Procedure

### 1. Capture the exact error and the account identity
Get the verbatim error text and the email/username the account is registered
under. Do not attempt password resets or new sign-ups before the state is
known — creating a new account on the same email or re-requesting deletion can
be irreversible.

### 2. Diagnose: deleted vs deactivated vs banned
These have different remedies — name which one applies before writing anything:
- **Deactivated/suspended by the service** — usually appealable.
- **Deleted at the user's own request** — typically irreversible per ToS; the
  letter should ask for confirmation plus new-account cooldown terms, not
  restoration.
- **Unknown** — ask the user directly, one question, early: did they recently
  request deletion (settings page, DELETE endpoint)? The answer changes the
  entire letter. "I deleted it by mistake" and "I never asked for this" are
  different appeals.

### 3. Find the official guidance before drafting
Search the service's official help center for the exact error string, quoted.
Vendor articles name the canonical appeal channel and often pre-answer the
likely cause (e.g. "check your email, including spam, for a message from us").
Public help-center pages are usually reachable even when login flows are not —
read them with whatever browsing path works.

### 4. Inbox check BEFORE the letter
The service almost always emailed the reason (deactivation notice, failed
verification, policy flag). Have the user check inbox **and spam** of the
registered address. If a cause email is found, the letter quotes the real cause
and answers it — this materially speeds up Support's response.

### 5. Pick a channel that needs no agent-held credentials
In order of preference:
1. Public web/contact form (no auth). Cap: if required fields are CUSTOM
   dropdowns (Radix/headless-UI select look-alikes — common on modern vendor
   forms), programmatic selection often does not register even when the click
   reports success. Map the fields, pre-choose the right options, verify
   state via the page's visible TEXT (element inventories can disagree with
   actual form state), and if a dropdown won't take the value, hand the
   ~30-second fill + submit to the user in their own browser instead of
   grinding on it.
2. Support email the user sends from their own mail client — agent prepares
   the text, user hits send. Must be sent FROM the registered address (Support
   matches identity by sender).
3. On-site chat widget — often a separate iframe automation cannot reach;
   treat it as a user action with the letter pasted in.
4. Login-gated paths are a hard stop for the agent: hand the login to the user
   (their own browser, their hands on the keyboard). Never guess credentials.
   Don't burn turns fighting bot-walled sign-in forms (OAuth, Google sign-in) —
   route around them to 1–3 instead.

### 6. Draft the letter

```
Subject: Appeal: <state> — <account email>

1. The exact error, quoted verbatim.
2. Account identifier (registered email/username).
3. Facts: did the user request deletion? notification received or explicitly
   not received (spam checked). ToS/usage-policy standing, if clean — say so,
   calmly.
4. The ask: restore access, or state the reason and the steps to resolve.
5. Sign-off with the registered email address repeated.
```

- English for international services unless the service is local-language.
- Short, factual, no indignation, no invented commitments — every sentence
  checkable against known facts.
- If a cause email WAS found, quote it and respond to it directly.

### 7. Expectations and follow-up
Support responses typically take a few days to a week. Offer a follow-up
reminder. When support replies routing the user to a specific appeal/report
form, that form becomes the primary channel: record its URL and field map in
the case reference, note which choices fit the case, and decide whether it
automates or is a user-handoff. If the first channel is silent after ~a week, escalate through a
second channel (form vs email vs chat vs official support handle on social).
If the account was truly deleted, set expectations honestly: restoration is
usually off the table; pivot the ask to confirmation + new-account cooldown.

## Pitfalls

- Drafting before knowing whether the user requested deletion themselves.
- Sending from an address other than the account's registration — Support
  cannot match identity and the appeal stalls.
- Burning turns on login-gated flows instead of handing the login to the user.
- Presenting a chat widget as a usable channel without noting it may be an
  iframe the tooling cannot open.
- Grinding on a styled non-native dropdown: clicks and arrow keys report
  success but the choice never registers (required-field validation
  persists). Cap it early and hand the final fill to the user.
- Trusting the element inventory as proof of form state — confirm via page
  text.
- Promising restoration when the state may be deletion.

## Verification

- [ ] State (deleted / deactivated / banned) named; user asked the
      deletion question.
- [ ] Official help-center article for the exact error consulted.
- [ ] User pointed at inbox + spam before sending.
- [ ] Letter sends from the registered address; the chosen channel needs no
      agent-held credentials.
- [ ] Follow-up/escalation plan stated.

## Session references

- `references/openai-deactivation.md` — OpenAI-specific channels, article,
  ready letter template, and the 2026-09 case state.
