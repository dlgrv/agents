---name: unity-game-development
description: "Unity/C# game project setup, scaffolding, and headless tooling — Unity Hub CLI, project structure for idle/arcade games, static verification without a compiler, batch-mode compilation."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [unity, csharp, game-development, scaffolding, cli]
    related_skills: [plan, core-coding-guidelines]
---

# Unity Game Development

Use this skill when creating, scaffolding, or verifying Unity/C# game projects — especially when setting up from scratch without an existing Editor install, or when verifying C# code before the Unity compiler is available.

## Unity Hub CLI

Unity Hub ships a headless CLI at `/Applications/Unity Hub.app/Contents/MacOS/Unity Hub` (macOS). Use it to install editors, list releases, and manage projects without the GUI.

See `references/unity-hub-cli.md` for the full command reference.
See `references/batch-mode-compilation.md` for the batch-mode compilation workflow and error→fix reference.

### Key commands

```bash
# List installed editors
"/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless editors --installed

# List available releases
"/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless editors -r

# Install an editor (ARM64 + Android + Docs)
# ⚠️ MUST pipe echo "Y" — --childModules does NOT suppress the interactive prompt
echo "Y" | "/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless install \
  --version 6000.0.82f1 --architecture arm64 -m android documentation &

# Get/set install path
"/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless install-path --get
```

### Pitfall: Interactive prompt on install

The `install` command prompts `"Would you also like to install the child module..."` interactively. In a background process or non-TTY context this **hangs silently**. `--childModules` flag does NOT reliably suppress this — the prompt still appeared and killed the process silently. The reliable fix is piping `echo "Y"`:

```bash
# ❌ WRONG — hangs silently even with --childModules
"/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless install \
  --version 6000.0.82f1 --architecture arm64 -m android documentation --childModules &

# ✅ CORRECT — pipe Y to auto-accept the prompt
echo "Y" | "/Applications/Unity Hub.app/Contents/MacOS/Unity Hub" -- --headless install \
  --version 6000.0.82f1 --architecture arm64 &
```

Run in background (`&`), then poll with `kill -0 $PID` since the Hub spawns child processes and the foreground call blocks.

### Pitfall: Paused downloads interfere with new installs

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

### Pitfall: Unity Hub GUI locks IndexedDB

If the Hub GUI is running, headless CLI commands may fail with `Failed to open LevelDB database...IO error: LOCK`. Quit the GUI first: `osascript -e 'quit app "Unity Hub"'` (macOS).

## Project Structure for Idle/Arcade Games

```
Assets/
├── Scripts/
│   ├── Core/          # GameManager singleton, enums, economy
│   ├── Player/        # Controller, inventory, interaction
│   ├── World/         # Zones: production, shelf, checkout
│   ├── Customer/      # AI state machine, spawner
│   ├── UI/            # Money display, upgrade buttons
│   └── Data/          # ScriptableObject definitions
├── Prefabs/           # Reusable GameObjects
├── ScriptableObjects/ # Data asset instances
├── Scenes/            # .unity scene files
└── Materials/         # Visual materials
```

### Architecture patterns

- **GameManager singleton**: central state (money, balance constants), events via `System.Action<T>`.
- **InteractableZone base class**: trigger collider + E-key interaction; subclasses override `OnInteract()`.
- **CustomerAI state machine**: `NavMeshAgent` + enum states (Seeking → Picking → CheckingOut → Leaving).
- **ScriptableObjects for data**: ItemDefinition, UpgradeDefinition — decoupled from logic.
- **GameManager holds balance constants**: all tuning values in one Inspector-accessible place.

## Static Verification Without a Compiler

When no C# compiler is available (no `dotnet`, `mono`, `csc`, or `mcs`), run the static verification script to check what's checkable:

```bash
python3 ~/.hermes/skills/software-development/unity-game-development/scripts/verify-cs-static.py <path-to-Scripts-folder>
```

Checks performed (ad-hoc, not a compiled build pass):
- Brace balance `{}` per file
- Paren balance `()` per file
- Quote balance `"` per file (flags potential unclosed strings)
- Class/enum/interface definitions found
- Inheritance hierarchy correctness
- Cross-file type references resolve to definitions

**This is explicitly NOT a compilation pass.** State this clearly to the user. Full compilation requires Unity Editor batch mode:

```bash
# Once Editor is installed, verify compilation:
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
"$UNITY" -batchmode -nographics -projectPath ~/aezly/MiniMarket -quit -logFile /tmp/unity-build.log
grep -E "error CS|Compilation failed" /tmp/unity-build.log
```

## Creating a Unity Project via CLI

```bash
# Create empty project (after Editor is installed)
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
"$UNITY" -batchmode -nographics -createProject ~/aezly/MiniMarket -quit
```

Then copy your pre-written `Assets/Scripts/` into the project folder and open in Editor to compile.

## Workflow: Scaffold Before Editor Is Ready

1. Write all C# scripts to `Assets/Scripts/` using `write_file` — Unity will import them when the project is opened.
2. Run `scripts/verify-cs-static.py` for ad-hoc static checks.
3. Create `.gitignore` (Unity template) and init git repo.
4. Commit the scripts before opening in Editor.
5. Once Editor is installed, create the `.unity` project and open it — Unity auto-compiles scripts on import.
6. Assemble the scene (camera, lights, primitives, NavMesh bake) in Editor.

## Programmatic Scene Assembly (No GUI)

When you can't use the Unity Editor GUI, build scenes via C# editor scripts run in batchmode. This is the **only viable approach** for headless/CLI workflows.

### Pattern: SceneBuilder editor script

Create `Assets/Editor/SceneBuilder.cs` with a static method decorated `[MenuItem("Tools/Build Game Scene")]`. Use `EditorSceneManager.NewScene()`, `GameObject.CreatePrimitive()`, `AddComponent()`, `PrefabUtility.SaveAsPrefabAsset()`, and `EditorSceneManager.SaveScene()`.

Run it via:
```bash
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
"$UNITY" -batchmode -nographics -projectPath "$PROJECT" \
  -executeMethod SceneBuilder.BuildScene \
  -logFile /tmp/unity-build-scene.log
```

See `references/programmatic-scene-assembly.md` for the full pattern with code examples.

### Pitfall: NavMeshSurface namespace in Unity 6

In Unity 6 (6000.x), `NavMeshSurface` and `CollectObjects` moved to namespace `Unity.AI.Navigation` (from the `com.unity.ai.navigation` package), **not** `UnityEngine.AI`. The package is included by default but the namespace must be imported explicitly:

```csharp
using Unity.AI.Navigation; // ← required for NavMeshSurface, CollectObjects

// Usage:
var surface = ground.AddComponent<NavMeshSurface>();
surface.collectObjects = CollectObjects.All;
surface.BuildNavMesh();
```

Without this `using`, you get:
```
error CS0246: The type or namespace name 'NavMeshSurface' could not be found
error CS0103: The name 'CollectObjects' does not exist in the current context
```

Also: `StaticEditorFlags.NavigationStatic` is deprecated in Unity 6 — use `NavMeshBuilder.CollectSources()` instead, or just ignore the warning.

### Pitfall: -runScene does NOT start playmode

In batchmode, `-runScene "Assets/Scenes/GameScene.unity"` **loads** the scene but does NOT start the playmode game loop. `Update()` methods don't fire, no physics, no spawning. To actually test gameplay:
- Open in Unity GUI and press Play, OR
- Build a standalone player (`-buildTarget`) and run it

### Pitfall: Batchmode may hang on GICache/asset import after compilation

After compilation succeeds, Unity may hang on `Created GICache directory` or `TrimDiskCacheJob` in batchmode. The compilation result is already final at that point — safe to `kill` the process. Verify via `Assembly-CSharp.dll` existence:
```bash
ls -lh ~/YourProject/Library/ScriptAssemblies/Assembly-CSharp.dll
```

### Pitfall: TMP_Settings.defaultFontAsset is null in batchmode

When creating TextMeshPro components programmatically in batchmode (editor scripts via `-executeMethod`), `TMP_Settings.defaultFontAsset` throws `NullReferenceException`. TMP Essentials may not be initialized in the headless context.

**Fix:** Do NOT set `tmp.font = TMP_Settings.defaultFontAsset`. Just omit the font assignment — TextMeshPro uses its default font automatically when one is available:

```csharp
// ❌ WRONG — NullReferenceException in batchmode
tmp.font = TMP_Settings.defaultFontAsset;

// ✅ CORRECT — omit font assignment
var tmp = labelObj.AddComponent<TextMeshPro>();
tmp.text = text;
tmp.fontSize = fontSize;
// don't touch tmp.font
```

### Pitfall: -executeMethod without -quit hangs after completion

When running `-executeMethod SceneBuilder.BuildScene`, Unity may hang after the method completes on asset import, GICache creation, or `TrimDiskCacheJob`. The actual work (scene creation, compilation) is already done — safe to kill the process.

**Fix:** Kill the process after confirming success in the log file. Check for the success marker or `Assembly-CSharp.dll` existence:

```bash
# Run in background, then kill after success marker appears
"$UNITY" -batchmode -nographics -projectPath "$PROJECT" \
  -executeMethod SceneBuilder.BuildScene \
  -logFile /tmp/unity-build.log &

# Poll for completion
grep "GameScene built and saved" /tmp/unity-build.log && kill $!
```

### Pitfall: Multiple Unity instances cannot open the same project

If a Unity process is already running with a project open (even in batchmode), a second batchmode call will abort:

```
Aborting batchmode due to fatal error:
It looks like another Unity instance is running with this project open.
```

**Fix:** Kill all Unity Editor processes before starting a new batchmode run:

```bash
pkill -f "Unity.app/Contents/MacOS/Unity"
sleep 2
rm -f "$PROJECT/Temp/UnityLockfile"
```

## Pitfalls

- **write_file overwrites entire files** — always use `patch` for partial edits to existing C# files.
- **write_file can corrupt files** if a previous write was interrupted — always verify file content with `read_file` before patching, and if a file looks wrong (contains line numbers from a previous read), rewrite it completely with `write_file`.
- **FindFirstObjectByType** (Unity 6) replaces `FindObjectByType` — use the correct API for the Unity version.
- **NavMesh requires baking** — Window → AI → Navigation → Bake. Static plane marked as NavMesh Static.
- **Tag "Player"** must be set on the player GameObject for trigger detection to work.
- **CharacterController + gravity** — must manually apply `Physics.gravity * Time.deltaTime` each frame.

### Missing UI packages in base project template

Unity's default project template (created via `-createProject`) does **not** include `com.unity.ugui` or `com.unity.textmeshpro`. Any script using `UnityEngine.UI.Button`, `TMPro.TextMeshProUGUI`, or `TMPro` will fail with:

```
error CS0234: The type or namespace name 'UI' does not exist in the namespace 'UnityEngine'
error CS0246: The type or namespace name 'TMPro' could not be found
error CS0246: The type or namespace name 'Button' could not be found
error CS0246: The type or namespace name 'TextMeshProUGUI' could not be found
```

**Fix:** Add these packages to `Packages/manifest.json` before first compilation:

```json
"dependencies": {
    "com.unity.ugui": "2.0.0",
    "com.unity.textmeshpro": "3.0.6",
    ...
}
```

Then re-open the project in Unity (batch mode) to trigger package resolution + recompilation.

### Unity message methods need `protected virtual` for `base.` calls

Unity's lifecycle methods (`Update`, `Start`, `Awake`, etc.) are `private` by convention. If a base class implements `Update()` and a subclass calls `base.Update()`, the compiler throws:

```
error CS0122: 'InteractableZone.Update()' is inaccessible due to its protection level
```

**Fix:** Declare the base method as `protected virtual` and the subclass as `protected override`:

```csharp
// Base class
protected virtual void Update()
{
    if (_playerInRange && Input.GetKeyDown(KeyCode.E))
        OnInteract();
}

// Subclass
protected override void Update()
{
    // custom logic...
    base.Update(); // now accessible
}
```

This applies to any Unity lifecycle method where a subclass needs to extend (not replace) the base behavior.
