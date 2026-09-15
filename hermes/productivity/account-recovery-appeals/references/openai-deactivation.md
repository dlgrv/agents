# OpenAI account deactivation — case notes & template (2026-09)

## Case state

- User: Leonid. Account email: dolgirevleonid@gmail.com.
- Sign-in returns verbatim: "You do not have an account because it has been
  deleted or deactivated. If you believe this was an error, please contact us
  through our help center at help.openai.com."
- User confirmed he did NOT request deletion → treated as service-side
  deactivation, appealable.
- Status 2026-09-04 (morning): appeal letter sent via support@openai.com;
  OpenAI's AI-assisted support replied the same day and routed the case to
  the official appeal form: https://openai.com/form/appeal/ (field map
  below).
- Status 2026-09-04 (form): agent filled Email + radio in the Hermes preview
  pane, but the two custom dropdowns (product, reason) never registered a
  programmatic selection — page text kept showing placeholders ("Select an
  option…", "Select Reason...") after click/keyboard attempts. Form NOT
  submitted by the agent. Handed to the user: fill in own browser (~30 s)
  with the case choices below; OpenAI promises "follow up by email after
  review" → watch dolgirevleonid@gmail.com incl. spam.
- Next: after the user submits, expect a reply within days; if silent ~1
  week, escalate via the help.openai.com chat widget (user action, letter
  pasted in).

## Official guidance (help.openai.com)

- Help-center article for this exact error: "Oops! You do not have an account
  because it has been deleted or deactivated". Its two operative points:
  1. Check email inbox AND spam for a message from OpenAI — the reason is
     usually there (incomplete verification, policy flag, etc.).
  2. If the account was deactivated (not deleted by the user), contact Support
     via the help center.
- Channels:
  - `support@openai.com` — send FROM the registered address (identity match).
  - Chat widget on help.openai.com, bottom-right "Open chat" — Intercom-based,
    lives in a separate iframe; browser automation in the Hermes preview pane
    could not open it. Treat as a user action with the letter pasted in.
- If the account turns out to be deleted (not deactivated): restoration is not
  offered per ToS; ask Support about any new-account cooldown for the same
  email instead.

## Appeal letter (as delivered; reuse as template)

Subject: `Appeal: account deactivated without request — <account email>`

```
Hello OpenAI Support Team,

When I try to sign in to my account, I receive the message:

"You do not have an account because it has been deleted or deactivated."

Account email: <account email>

I did NOT request deletion of my account, and I have not received any
notification explaining a deactivation (I have checked my inbox and
spam folder). To my knowledge I have not violated the Terms of Use
or Usage Policies.

This deactivation appears to be an error. Please review my account
status and restore access, or let me know the reason for the
deactivation and what steps I can take to resolve it.

Thank you for your help.

Best regards,
<name>
<account email>
```

If a cause email IS found in spam first: quote it in the letter and answer it
directly — materially faster turnaround.

## Appeal form — https://openai.com/form/appeal/ (field map, 2026-09)

1. **Account Email** * — native input; automates fine.
2. **What would you like to do?** * — radios: "Appeal a warning or account
   deactivation" | "Report unauthorized activity involving my account";
   radio clicks register.
3. **Which OpenAI product is affected?** * — custom dropdown: ChatGPT |
   API Platform | Codex | ChatGPT Business, Enterprise, or Edu workspace |
   Other.
4. **Why are you appealing?** * — custom dropdown: "My usage did not violate
   OpenAI's Usage Policies or Terms of Use" | "My account was hacked or
   accessed without my permission" | "My API key or other credentials were
   compromised".
5. **Submit Appeal** — promises a follow-up by email after review.

Fields 3–4 are non-native (Radix-style) selects: clicks/keys report success
in the Hermes preview pane but no option registers; placeholders persist in
page text. Don't grind — hand the fill to the user's own browser.

Choices for this case: (2) appeal deactivation · (3) ChatGPT · (4) "usage did
not violate" — deactivation arrived with no notification email.

## Expectations

- Response time: typically a few days up to ~a week.
- If silent after a week: escalate via the second channel (chat if email was
  used, and vice versa).
