# Unity Hub Headless CLI Reference

## Binary path (macOS)

```
/Applications/Unity Hub.app/Contents/MacOS/Unity Hub
```

All commands require `-- --headless` prefix:

```bash
HUB="/Applications/Unity Hub.app/Contents/MacOS/Unity Hub"
"$HUB" -- --headless <command> [options]
```

## Commands

### editors (alias: e)

List releases and installed editors.

```bash
# All (installed + available)
"$HUB" -- --headless editors

# Only installed
"$HUB" -- --headless editors --installed

# Only available releases
"$HUB" -- --headless editors --releases

# JSON output
"$HUB" -- --headless editors --installed --json

# Filter by architecture
"$HUB" -- --headless editors -a arm64
```

### install (alias: i)

Install an editor version.

```bash
# ✅ CORRECT — pipe Y to auto-accept child module prompt
echo "Y" | "$HUB" -- --headless install \
  --version 6000.0.82f1 \
  --architecture arm64 \
  -m android documentation &
```

**Options:**
- `--version|-v <version>` — required, e.g. `6000.0.82f1`
- `--changeset|-c <changeset>` — required if version not in release list
- `--module|-m <moduleid>` — space-separated module IDs:
  - `android` — Android Build Support
  - `android-sdk-ndk-tools` — Android SDK & NDK
  - `android-open-jdk` — OpenJDK (child of android)
  - `ios` — iOS Build Support
  - `webgl` — WebGL Build Support
  - `documentation` — API docs
  - `visualstudio` — Visual Studio for Mac
  - `mac-il2cpp` — Mac Build Support (IL2CPP)
  - `windows-mono` — Windows Build Support (Mono)
  - `linux-mono` — Linux Build Support (Mono)
  - `linux-il2cpp` — Linux Build Support (IL2CPP)
- `--childModules` — auto-install child modules without prompting
- `--architecture|-a <arch>` — `arm64` or `x86_64`

### install-modules (alias: im)

Add modules to an existing editor install.

```bash
"$HUB" -- --headless install-modules --version 6000.0.82f1 -m ios
```

### install-path (alias: ip)

Get or set where editors are installed.

```bash
# Get
"$HUB" -- --headless install-path --get

# Set
"$HUB" -- --headless install-path --set /Applications/Unity/Hub/Editor/
```

Default: `/Applications/Unity/Hub/Editor`

## Pitfalls

### Interactive prompt hangs background processes

`install` prompts:
```
Would you also like to install the child module android-open-jdk-17.0.18+8 of the parent module android (Y/n)
```

**`--childModules` does NOT reliably suppress this.** The prompt still appeared and killed the process silently even with the flag. The reliable fix is piping `echo "Y"`:

```bash
# ✅ CORRECT — pipe Y to auto-accept, run in background
echo "Y" | "$HUB" -- --headless install --version 6000.0.82f1 --architecture arm64 -m android documentation &

# ❌ WRONG — hangs silently even with --childModules
"$HUB" -- --headless install --version 6000.0.82f1 --architecture arm64 -m android documentation --childModules &
```

Poll with `kill -0 $PID` since the Hub spawns child processes and the foreground call blocks.

### Paused downloads interfere with new installs

The Hub stores paused/partial downloads in `~/Library/Application Support/UnityHub/paused-downloads.json`. When starting a new install, the Hub may **resume old paused downloads for a different version**, wasting bandwidth and disk. Clear paused downloads before installing:

```bash
rm ~/Library/Application\ Support/UnityHub/paused-downloads.json
```

### Monitoring download progress

Downloads go to `~/Library/Application Support/UnityHub/downloads/`. Monitor with:

```bash
du -sh ~/Library/Application\ Support/UnityHub/downloads/
ls -lh ~/Library/Application\ Support/UnityHub/downloads/
```

The Editor `.pkg` is ~3-5 GB; with modules total can be 8+ GB. Install takes 10-20 min depending on network.

### GUI locks IndexedDB

If the Hub GUI is running, CLI commands fail:
```
Failed to open LevelDB database from .../IndexedDB/file__0.indexeddb.leveldb/LOCK
```
Fix: `osascript -e 'quit app "Unity Hub"'` then retry.

### Editor binary path

After installation, the Unity Editor binary is at:
```
/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity
```

Use this for batch-mode project creation and compilation:
```bash
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
"$UNITY" -batchmode -nographics -createProject ~/aezly/MyProject -quit
"$UNITY" -batchmode -nographics -projectPath ~/aezly/MyProject -quit -logFile /tmp/unity.log
```
