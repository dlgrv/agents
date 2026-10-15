---
name: parallels-desktop-ops
description: Use when managing Parallels Desktop VMs via prlctl on macOS.
---

# Parallels Desktop VM operations on macOS

## When to Use
Load when the task involves a Parallels Desktop VM on this Mac: controlling the VM, running commands inside the guest Windows, sharing mac folders into the guest, or isolating the guest desktop from mac files.

Manage Parallels VMs entirely from the mac terminal with `prlctl`; no GUI needed for control or guest commands.

## Control
- `prlctl list -a` — VMs and their state. Use the display name (e.g. `"Windows 11"`) everywhere; the UUID also works.
- `prlctl start|suspend|resume|stop "<vm>"`. `stop` is a hard power-off — prefer a guest-side `shutdown /s /t 0` via exec.
- Run commands inside the guest: `prlctl exec "Windows 11" cmd /c "<command>"`. Works for cmd, reg, tasklist, shutdown, etc.
- Opening the guest console window can only be done in the Parallels Control Center GUI (double-click the VM card, or topbar View menu after focusing). prlctl cannot open it.

## Passing Windows paths from the mac shell
- Double every backslash in cmd one-liners from the mac side (`\\\\Mac\\share`), or the mac shell eats them and the guest sees a mangled path. Verify reachability with `dir \\\\Mac\\<share>` first.
- For quoting-heavy work, write a .bat into a shared folder from the mac side, then run it: `prlctl exec ... cmd /c "\\\\Mac\\<share>\\file.bat"`. This sidesteps all quote-escaping between two shells.

## Guest shell / desktop changes
- prlctl exec runs in a service session with no interactive desktop: launching the guest shell (`start explorer.exe`) silently does nothing — verify with `tasklist /fi "IMAGENAME eq explorer.exe"`. To apply shell/desktop-affecting changes (e.g. a desktop-folder registry redirect), reboot the guest instead: `shutdown /r /t 5` via exec — it auto-logs back in.

## Long-running guest commands
- Never hold `prlctl exec` open across a long guest install (language packs, installers) — it stalls the mac-side terminal past its timeout and you lose the output anyway. Instead: write the .ps1 to the shared folder, have it redirect all output to a log file in that same folder, launch it detached (`start /b powershell -ExecutionPolicy Bypass -File \\Mac\<share>\x.ps1`), and poll the log file from the mac side. Even the detached-launch exec call can hang; treat any exec as fire-and-forget and verify via the log, not via exec's exit.
- Delete the .ps1/_log files from the shared (desktop!) folder when done — the user sees that folder on both desktops.

## Guest language / localization
Set UI language + layout in one PowerShell script (run detached per the section above — the language-pack download takes minutes):
```powershell
Install-Language ru-RU -CopyToSettings   # downloads + installs the pack
Set-WinUILanguageOverride -Language ru-RU
Set-WinSystemLocale ru-RU
Set-Culture ru-RU
Set-WinHomeLocation -GeoId 203           # 203 = Russia
```
Add a layout alone via `Get-WinUserLanguageList` / `.Add('ru-RU')` / `Set-WinUserLanguageList -Force`. Reboot the guest afterwards (`shutdown /r /t 5`) — UI language applies only at next logon. Substitute the tag/GeoId for other languages.

## reg add pitfalls
- Never end a quoted `/d` value with a backslash (`"Y:\"`): reg.exe's parser eats the closing quote, drops `/f`, and reg loops forever on the overwrite prompt — flooding gigabytes of output under prlctl. Use `"Y:"`; Windows accepts a drive root without the trailing slash in these values.
- Redirect the guest desktop via both registry keys, then reboot:
  - `reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop /t REG_EXPAND_SZ /d "Y:" /f`
  - same path under `...\Explorer\Shell Folders` with `/t REG_SZ`
  - verify with `reg query` on User Shell Folders.

## Isolating a guest from mac files
Fresh Parallels VMs mirror mac Desktop/Documents/Downloads into the guest (Shared Profile). To isolate the guest:
1. Disable Shared Profile (VM Configuration → Options → Sharing).
2. Also disable **Shared Applications** in both directions (same Options → Sharing pane) — otherwise Windows apps keep publishing into macOS Spotlight/Launchpad, and mac apps into the guest Start menu. Parallels may already have created one shortcut per Windows app under `~/Applications` on the mac — delete those.
3. Create one dedicated mac folder and share only it into the guest; it appears at `\\Mac\<sharename>` in the guest and can be redirected to or mounted as a drive letter.
4. Result: files dropped in that mac folder appear on the guest desktop and vice versa; all other mac files stay invisible to the guest (remaining mac home still reachable via `\\Mac\Home` if needed).

VM config changes (`prlctl set`) only apply on a stopped VM — resume a suspended VM, shut it down cleanly, edit config, then start again.
