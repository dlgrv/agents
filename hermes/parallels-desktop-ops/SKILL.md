---
name: parallels-desktop-ops
description: Use when managing Parallels Desktop VMs via prlctl on macOS.
---

# Parallels Desktop VM operations on macOS

## When to Use
Load when the task involves a Parallels Desktop VM on this Mac: controlling the VM, running commands inside the guest Windows, sharing mac folders into the guest, or isolating the guest desktop from mac files.

Manage Parallels VMs entirely from the mac terminal with `prlctl`; no GUI needed for control or guest commands.

## Control
- `prlctl` fails with «Failed to initialize Parallels Desktop in unattended mode» (inittool2 init hint) while the Parallels Desktop app is closed — `open -a "Parallels Desktop"` first, wait a few seconds, then prlctl works; no sudo init procedure needed.
- `prlctl list -a` — VMs and their state. Use the display name (e.g. `"Windows 11"`) everywhere; the UUID also works.
- `prlctl start|suspend|resume|stop "<vm>"`. `stop` is a hard power-off — prefer a guest-side `shutdown /s /t 0` via exec. A suspended VM must be resumed before exec works (`prlctl resume`, give it ~20 s).
- Run commands inside the guest: `prlctl exec "Windows 11" cmd /c "<command>"`. Works for cmd, reg, tasklist, shutdown, etc.
- Opening the guest console window can only be done in the Parallels Control Center GUI (double-click the VM card, or topbar View menu after focusing). prlctl cannot open it.

## Passing Windows paths from the mac shell
- Mapped drive letters (Y:, Z: for Parallels shares) exist only in the user's logon session — `prlctl exec` (service session) cannot see them. Address shared folders by UNC `\\Mac\<share>` in exec commands; UNC works from any session. An isolated VM may have no `\\Mac\Home` at all — list the shares the guest actually has (`net use` via exec) before assuming.
- Mac→guest bulk copy recipe: `ditto <src> <stage>` into the dedicated shared folder on the mac side, then `robocopy "\\\\Mac\\<share>\\stage" "C:\\dest" /MIR /NFL /NDL /NJH` via exec, then delete the stage. `robocopy /MIR` mirrors deletions too — use it to re-sync a whole tree, never against a folder with an app open in the guest (locks + rewrite on save).
- Guest-side `findstr` can fail to open a Cyrillic path that `dir` lists fine — don't debug guest-side search; `copy /Y` the file to the shared folder and grep it on the mac.
- Cyrillic paths work fine through exec (robocopy/copy handle them) — just keep the mac-side double-backslash discipline.
- Double every backslash in cmd one-liners from the mac side (`\\\\Mac\\share`), or the mac shell eats them and the guest sees a mangled path. Verify reachability with `dir \\\\Mac\\<share>` first.
- For quoting-heavy work, write a .bat into a shared folder from the mac side, then run it: `prlctl exec ... cmd /c "\\\\Mac\\<share>\\file.bat"`. This sidesteps all quote-escaping between two shells.
- Never pass PowerShell code inline (`powershell -Command "$ws = New-Object ..."`) or generate the .ps1 via double-quoted printf/echo from the mac shell: bash expands `$vars` into empty strings and the guest runs broken code. Write the .ps1 with a file-write tool (no shell interpolation), run it from the share, delete it after.

## Guest shell / desktop / GUI apps
- prlctl exec runs in a service session with no interactive desktop. GUI apps launched from exec DO start — but they land in session 0 (tasklist shows `Services`), invisible to the user, eating RAM as zombie windows. Check the Session column in `tasklist /fi "IMAGENAME eq <name>.exe"`: `Console` = visible to the user, `Services` = invisible. If a session-0 duplicate appears while the user already has the app open, `taskkill /f /pid <Services-instance-pid>` — never kill the Console one.
- To apply shell/desktop-affecting changes (e.g. a desktop-folder registry redirect), reboot the guest instead: `shutdown /r /t 5` via exec — it auto-logs back in.
- When the user must launch a GUI app with specific arguments (e.g. a browser with a proxy flag), drop a .bat in the shared folder and have them double-click it — exec cannot put it on their desktop, and this avoids dictating steps over chat.

## Guest command output encoding
- Guest cmd output arrives through prlctl garbled (cp866, never converted). Don't fight it for yes/no facts (counts, task presence stay readable); for anything you must actually read back, redirect to a log in the shared folder and decode on the mac: Windows PowerShell `Out-File` defaults to UTF-16LE → `iconv -f UTF-16LE -t UTF-8 <log>`; cmd `>` writes cp866 → `iconv -f cp866 -t UTF-8`.

## Long-running guest commands
- Never hold `prlctl exec` open across a long guest install (language packs, installers) — it stalls the mac-side terminal past its timeout and you lose the output anyway. Instead: write the .ps1 to the shared folder, have it redirect all output to a log file in that same folder, launch it detached (`start /b powershell -ExecutionPolicy Bypass -File \\Mac\<share>\x.ps1`), and poll the log file from the mac side. Even the detached-launch exec call can hang; treat any exec as fire-and-forget and verify via the log, not via exec's exit.
## Silent installs in the guest (MSI/installers)
- Verify by the binary, not the exit code: after a silent install, `Test-Path` the actual exe (e.g. `C:\Program Files\Google\Chrome\Application\chrome.exe`). msiexec exit 0 with no files on disk is a real failure mode (see next rule).
- A failed or half-finished silent install leaves the product REGISTERED with no files. Re-running the same MSI then enters maintenance mode — instant exit 0, nothing installed; the verbose log (`/l*v`) shows `Feature: Complete; Installed: Local; Request: Null` and "maintenance mode". Fix: `msiexec /x <same.msi> /qn` first (plus remove the leftover install dir), then `/i` fresh. Check for a registered entry (`HKLM:\...\Uninstall\*` DisplayName) before diagnosing anything else.
- Prefer downloading the installer on the MAC into the shared folder over downloading inside the guest — guest downloads stall easily (proxy/geo), and the share already bridges the two. Big installers (~160 MB Chrome enterprise MSI works fine) run detached per the long-running pattern above.
- If a silent install keeps failing after one clean-reinstall attempt, stop: copy the installer to the guest desktop (`copy /Y \\Mac\<share>\x.msi C:\Users\<user>\Desktop\`) and give the user the 2-step manual instruction (uninstall the phantom entry in Settings→Apps if one exists, then double-click). The user prefers finishing installs by hand over long automated debugging.
- Before diagnosing an installer that crashes on launch (access violation / "Runtime error 216"), list the app's own directory for an unexpected DLL — Windows loads same-dir DLLs first, and cracked Altium distros (1tors.ru-style) ship a fake `shfolder.dll` license emulator; one sitting in `\\Mac\<share>` crashed even Chrome's official installer run from that folder. "Runtime error 216" from a modified Installer.exe with no emulator next to it means the crack requires its `shfolder.dll` — do not help restore it; point the user at the official installer + student license instead. Also: a mounted ISO holds its files open — `Dismount-DiskImage` before deleting the distro folder.
- When the vendor's installer still crashes from a clean local copy with no suspicious DLLs, ship a portable build instead of debugging the crash. Validated for Chrome: zip from `https://storage.googleapis.com/chrome-for-testing-public/<ver>/win64/chrome-win64.zip` (get `<ver>` from `googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json`), extract on the mac with `ditto -x -k`, `robocopy \\Mac\<share>\dir C:\<dir> /E` into the guest, and create a `WScript.Shell` desktop shortcut — a full working app beats a broken installer.
- Removing Edge leaves http/https `UserChoice` pointing at the dead `MSEdgeHTM` ProgId — any installer's OAuth sign-in step (Altium-style browser redirect) then fails with a cryptic auth error. A portable browser is invisible to Settings until registered: create `HKCU:\Software\Classes\ChromeHTML\shell\open\command` (`"C:\Chrome\chrome.exe" --single-argument %1`) plus `HKCU:\Software\Clients\StartMenuInternet\GoogleChrome` with `Capabilities` (ApplicationName, ApplicationIcon, `URLAssociations` http/https → the ProgId) and `shell\open\command`; then have the user pick it once in Settings → Default apps — the UserChoice Hash cannot be scripted.
- Qt-based apps (Transmission) need the VC++ 2015–2022 x64 redistributable: download on the mac, install with `vc_redist.x64.exe /install /quiet /norestart`.
- Never hand-compute an MSI compressed product GUID by string-reversing the fields — the reversal is byte-wise per field, and a wrong compressed GUID silently deletes nothing, so the phantom registration survives and the maintenance-mode loop repeats. Read the GUID from the verbose log / registry and do the transformation programmatically.
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
Add a layout alone via `Get-WinUserLanguageList` / `.Add('ru-RU')` / `Set-WinUserLanguageList -Force`. Reboot the guest afterwards (`shutdown /r /t 5`) — UI language applies only at next logon. Adding just the layout often does not make typing work: after logon verify with `Get-WinUserLanguageList` that the language (ru-RU) is in the user's Languages list, not only a keyboard layout — if missing, add the language, not the layout, and sign out again. Substitute the tag/GeoId for other languages.

## Guest safe mode: exec is dead
Parallels Tools do not run in Windows safe mode, so `prlctl exec` fails with "Unable to open new session in this virtual machine" for as long as the guest stays in safe mode — shared folders die with it, so you cannot even run a recovery script from `\\Mac\...`. Recovery is manual, in the VM console window (Win+R → cmd): `bcdedit /deletevalue safeboot` then `shutdown /r /t 0`.
- Never `bcdedit /set safeboot` from exec just to make a one-off change (driver removal, service work): if the follow-up work cannot run, the VM is stranded in safe mode with no tool access. Only enter safe mode when something inside the next boot also exits it (see the self-exiting task pattern below).
- Before setting safeboot, warn the user the VM will be console-only for a while and exec will not answer.

## Hardening / disabling Windows Defender in the guest
- `Set-MpPreference` reverts unless Tamper Protection is off first (`Set-MpPreference -DisableTamperProtection 1`); check state via `Get-MpComputerStatus`.
- `Sense` (Defender ATP) and `SecurityHealthService` accept a direct `Start=4` via reg/Set-ItemProperty, even from exec's SYSTEM session. The core keys — `WinDefend`, `WdNisSvc`, `WdNisDrv`, `WdFilter`, `WdBoot` — do not: the running WdFilter kernel driver blocks SetAccessControl (ownership/ACL) on them with "unauthorized operation" even as SYSTEM. Registry edits only stick while that driver is not loaded — i.e. in safe mode.
- Pattern: from exec, copy a .ps1 to `C:\` (shared folders are unavailable in safe mode), register it as a SYSTEM onstart scheduled task (`schtasks /create /sc onstart /ru SYSTEM /rl HIGHEST`), set `bcdedit /set safeboot minimal`, reboot. The task must be self-exiting: disable the Wd* services, delete its own task, `bcdedit /deletevalue safeboot`, `shutdown /r /t 10` — otherwise the VM is stranded (see safe-mode section). Log everything to `C:\<name>_log.txt` and read it back via exec after the guest returns to normal mode to verify Start=4 took.
- Getting the guest into safe mode requires a reboot cycle where exec is dead; budget for the manual console recovery above when the task does not fire.

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
