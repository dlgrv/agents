---
name: homebrew-maintenance
description: "Use for Homebrew upkeep on the user's Mac — upgrades, casks."
---

# Homebrew maintenance (user's Mac — Apple Silicon, /opt/homebrew)

## Always-on rules
- Never mass-upgrade without an explicit go-ahead — enumerate and present first. The user often runs large upgrades themselves; when they say "I updated something", VERIFY instead of re-running: `brew outdated --verbose`, then confirm actual versions with `brew list --versions` (formulae) and `brew list --cask --versions` (casks).
- Query formulae and casks with SEPARATE `brew list` calls — a cask name passed to plain `brew list --versions` looks "missing" (exit 1) even though it is installed.
- After any bulk upgrade, re-run `brew outdated` and read the "Deprecated or disabled package" warnings: `brew upgrade` silently SKIPS disabled casks — a package can survive an upgrade round without any failure.

## Procedure
1. State check: `brew outdated --verbose`. Output marks formulae with `<` and casks with `!=` — handle both.
2. Present the list grouped by significance: security/network libs (openssl, krb5, libssh, curl-stack…) → major version jumps (flag as break-risk) → main CLI tools → minor patch bumps.
3. Offer `brew vulns` as a follow-up — checks installed packages against OSV (new in Homebrew 7).
4. Upgrade on request, then verify per the always-on rules.

## Homebrew 7+ pitfalls
- Disabled casks: a cask whose build is unsigned/unnotarized fails the macOS Gatekeeper check and gets DISABLED upstream; `brew upgrade` skips it with only a warning. Do NOT force-install it and do NOT suggest an `xattr -cr` bypass — Homebrew 7 removed Gatekeeper bypass on principle. Diagnose with `brew info --cask <name>` (reason + date), confirm with `codesign -dv <app>` (`Signature=adhoc` = unsigned) and `spctl -a -vv <app>` (rejected). Leave the installed version running; it revives automatically once upstream ships signed builds.
- Tap trust: installing from a third-party tap requires trusting it first — `brew trust <tap>` (whole tap) or `brew trust --formula <user>/<tap>/<name>`; `brew untap <tap>` to remove. `brew install` prints guidance listing which installed taps need trust.

## BrewUI
Official native GUI for brew: `brew install homebrew-app` → `/Applications/Homebrew.app`. Requires macOS Tahoe 26+. Good offer for users who like browsing/updating packages visually.