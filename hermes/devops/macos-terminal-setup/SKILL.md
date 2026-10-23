---
name: macos-terminal-setup
description: Use when auditing or editing the Mac's zsh/terminal config.
---

# macOS terminal (zsh) config work

## Layout of the user's shell

- Shell: zsh + oh-my-zsh (`~/.oh-my-zsh`), theme robbyrussell. `~/.zshenv` is (kept) empty; all config lives in `~/.zshrc`.
- Custom plugins in `~/.oh-my-zsh/custom/plugins`: zsh-autocomplete, zsh-autosuggestions, zsh-syntax-highlighting, zsh-history-substring-search.
- Tools managed by **mise** (`eval "$(mise activate zsh)"`) — do not hardcode tool paths that mise provides via shims.
- Completion dirs go into `fpath` BEFORE `source $ZSH/oh-my-zsh.sh`; omz runs compinit itself, so never add a second `autoload -Uz compinit` — duplicate compinit doubles shell startup cost.
- PATH additions are plain `export PATH=...` lines; `$HOME/go/bin` (static, not `$(go env GOPATH)`) to avoid spawning go at every shell start.

## Audit procedure

1. Read `~/.zshrc` and `~/.zshenv` in full; list `~/.oh-my-zsh/custom/plugins`.
2. Verify every PATH entry actually exists (`ls -d` each dir) — macOS accumulates dead Intel-era `/usr/local/opt/...` entries and tooling leftovers (e.g. a `~/.cargo/env` source with no `~/.cargo`); each one is either an error or a no-op on every shell start.
3. Verify plugin ordering: `zsh-syntax-highlighting` near-last, `zsh-history-substring-search` after it. Also check the plugin name matches the cloned directory name — omz's built-in plugin of a similar name silently loads instead of the custom clone if the name differs.
4. Check for one-shot commands executed at startup (e.g. `$(go env GOPATH)`) — replace with the static equivalent.
5. Check for plaintext secrets (`export *_TOKEN=`, passwords). Rule: no secrets in dotfiles — they land in dotfile backups and are exported into every process. Remove entirely if the user no longer needs it in the shell; if needed, propose `~/.secrets.env` with chmod 600 or keychain, but only after asking.
6. Apply edits with `patch` (targeted), then **verify by loading**: `zsh -i -c 'echo OK; echo $plugins'` and compare PATH before/after. A cleanup that isn't load-tested is not done.
7. After removing a secret, `grep -c TOKEN ~/.zshrc` to confirm zero; remind the user to rotate it if it ever appeared in backups or open sessions.

## Pitfalls

- Present findings as a short findings list split into artifacts vs improvements, and WAIT for approval before editing — the user approves in batch with a short «ок».
- Edit only what was agreed; keep harmless guards (e.g. a conditional mysql-client prefix) — clean without over-pruning.
- zsh-autocomplete emits a harmless `terminfo[kcbt]` warning on macOS — do not 'fix' it by reordering plugins.

## Recommended-but-not-installed tooling (proposed, awaiting user go-ahead)

fzf (history/file search), zoxide (repo jumping for ~/aezly + ~/github projects), SSH ControlMaster multiplexing for the A–F fleet, bat, eza, lazygit, direnv (per-project .env). The user installs binaries himself; the agent may prepare config edits once the tools exist.
