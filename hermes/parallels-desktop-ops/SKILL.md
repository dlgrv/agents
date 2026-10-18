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
- Mapped drive letters (Y:, Z: for Parallels shares) exist only in the user's logon session — `prlctl exec` (service session) cannot see them. Address shared folders by UNC `\\Mac\<share>` in exec commands; UNC works from any session.
- Cyrillic paths work fine through exec (robocopy/copy handle them) — just keep the mac-side double-backslash discipline.
- Double every backslash in cmd one-liners from the mac side (`\\\\Mac\\share`), or the mac shell eats them and the guest sees a mangled path. Verify reachability with `dir \\\\Mac\\<share>` first.
- For quoting-heavy work, write a .bat into a shared folder from the mac side, then run it: `prlctl exec ... cmd /c "\\\\Mac\\<share>\\file.bat"`. This sidesteps all quote-escaping between two shells.

## Guest shell / desktop / GUI apps
- prlctl exec runs in a service session with no interactive desktop. GUI apps launched from exec DO start — but they land in session 0 (tasklist shows `Services`), invisible to the user, eating RAM as zombie windows. Check the Session column in `tasklist /fi "IMAGENAME eq <name>.exe"`: `Console` = visible to the user, `Services` = invisible. If a session-0 duplicate appears while the user already has the app open, `taskkill /f /pid <Services-instance-pid>` — never kill the Console one.
- To apply shell/desktop-affecting changes (e.g. a desktop-folder registry redirect), reboot the guest instead: `shutdown /r /t 5` via exec — it auto-logs back in.
- When the user must launch a GUI app with specific arguments (e.g. a browser with a proxy flag), drop a .bat in the shared folder and have them double-click it — exec cannot put it on their desktop, and this avoids dictating steps over chat.

## Guest command output encoding
- Guest cmd output arrives through prlctl garbled (cp866, never converted). Don't fight it for yes/no facts (counts, task presence stay readable); for anything you must actually read back, redirect to a log in the shared folder and decode on the mac: Windows PowerShell `Out-File` defaults to UTF-16LE → `iconv -f UTF-16LE -t UTF-8 <log>`; cmd `>` writes cp866 → `iconv -f cp866 -t UTF-8`.

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

## Background service
The `com.parallels.desktop.launchdaemon` (system domain) keeps ~6 processes (prl_disp_service, prl_naptd, watchdog) alive whenever the mac boots, even with the app closed and all VMs stopped. To stop it and prevent autostart: `launchctl bootout system/com.parallels.desktop.launchdaemon` + `launchctl disable system/com.parallels.desktop.launchdaemon` (sudo — use the osascript admin-privileges pattern). Manual app/VM launch still works; the service relaunches on demand.

## Routing guest traffic through the mac's Clash proxy
Geo-blocked downloads (MathWorks blocks RU IPs, etc.) work from the guest if its traffic goes through the user's Clash proxy. Never edit Clash's config or ports (user's hard rule) — add a separate relay instead:
1. mihomo listens on localhost only, invisible from the guest. Run a small TCP forwarder on the mac bound to the Parallels host IP `10.211.55.2` on a free port (e.g. 17891), forwarding to the localhost Clash port (default 17890). Script lives at `~/Library/Scripts/clash_relay.sh`.
2. Persist it with a LaunchAgent (`~/Library/LaunchAgents/`, `RunAtLoad` + `KeepAlive`) — otherwise the relay dies with the agent session and the guest loses ALL internet (its only route is the proxy). Verify with `launchctl print` + a `curl -x` from the guest.
3. Enable the proxy in the guest via registry (`HKCU\...\Internet Settings`: `ProxyEnable=1`, `ProxyServer="10.211.55.2:17891"`) — survives guest reboots.
4. Leave the user an escape hatch: a `_proxy_off.bat` in the shared folder that sets `ProxyEnable=0`, for when Clash is off and direct internet is needed.
- Chromium browsers ignore a system proxy set after they started (background/Startup-boost processes survive window closes). Before testing, `taskkill /f /im msedge.exe`, then relaunch with the explicit flag: `msedge.exe --proxy-server="http://10.211.55.2:17891" <url>`.
- Verify the chain per hop before blaming the proxy: relay listening (`lsof -iTCP:<port> -sTCP:LISTEN` on the mac), then `curl -s -x http://10.211.55.2:17891 <url>` via `prlctl exec` from the guest.
