# Unity Batch-Mode Compilation Workflow

## Creating a project + compiling scripts headlessly

```bash
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
PROJECT="/Users/dlgrv/aezly/MyProject"

# Step 1: Create empty project (generates Library, ProjectSettings, Packages)
"$UNITY" -batchmode -nographics -createProject "$PROJECT" -logFile /tmp/unity-create.log

# Step 2: Copy scripts into Assets/Scripts/ (or write them there before creation)

# Step 3: Add missing packages to Packages/manifest.json (see below)

# Step 4: Re-open project to resolve packages + compile
"$UNITY" -batchmode -nographics -projectPath "$PROJECT" -logFile /tmp/unity-compile.log

# Step 5: Check results
grep -E "error CS|warning CS|Scripts have compiler|Compilation" /tmp/unity-compile.log
```

## Compilation error → fix reference

### CS0234 / CS0246: Missing namespace or type

Symptom:
```
error CS0234: The type or namespace name 'UI' does not exist in the namespace 'UnityEngine'
error CS0246: The type or namespace name 'TMPro' could not be found
error CS0246: The type or namespace name 'Button' could not be found
error CS0246: The type or namespace name 'TextMeshProUGUI' could not be found
```

Cause: Base project template omits UI packages.

Fix: Add to `Packages/manifest.json`:
```json
"com.unity.ugui": "2.0.0",
"com.unity.textmeshpro": "3.0.6",
```

### CS0122: Inaccessible due to protection level

Symptom:
```
error CS0122: 'InteractableZone.Update()' is inaccessible due to its protection level
```

Cause: Base class Unity lifecycle method is `private` (default), subclass tries `base.Update()`.

Fix: Change base to `protected virtual void Update()`, subclass to `protected override void Update()`.

### CS0246: NavMeshSurface / CollectObjects not found

Symptom:
```
error CS0246: The type or namespace name 'NavMeshSurface' could not be found
error CS0103: The name 'CollectObjects' does not exist in the current context
```

Cause: In Unity 6 (6000.x), `NavMeshSurface` and `CollectObjects` are in namespace `Unity.AI.Navigation` (from `com.unity.ai.navigation` package), not `UnityEngine.AI`.

Fix: Add `using Unity.AI.Navigation;` to the file. The package is included by default in Unity 6 projects.

### Warning CS0618: NavigationStatic deprecated

```
warning CS0618: 'StaticEditorFlags.NavigationStatic' is obsolete
```

This is a warning, not an error. In Unity 6, use `NavMeshBuilder.CollectSources()` instead, or ignore — it still works.

## Batchmode limitations

### -runScene does NOT start playmode

`-runScene "Assets/Scenes/GameScene.unity"` loads the scene in batchmode but does NOT start the game loop. `Update()` methods never fire, no physics, no spawning. To test gameplay:
- Open in Unity GUI and press Play, OR
- Build a standalone player and run it

### Batchmode may hang after compilation

After compilation succeeds, Unity may hang on `Created GICache directory` or `TrimDiskCacheJob`. The compilation result is already final — safe to `kill` the process. Verify via:
```bash
ls -lh ~/YourProject/Library/ScriptAssemblies/Assembly-CSharp.dll
```

### -executeMethod for scene building

Use `-executeMethod ClassName.MethodName` to run editor scripts in batchmode:
```bash
"$UNITY" -batchmode -nographics -projectPath "$PROJECT" \
  -executeMethod SceneBuilder.BuildScene \
  -logFile /tmp/unity-build.log
```

The method must be `public static`, in a class under `Assets/Editor/`, wrapped in `#if UNITY_EDITOR`.

## Package versions verified with Unity 6000.0.82f1

| Package | Version | Purpose |
|---------|---------|---------|
| `com.unity.ugui` | 2.0.0 | `UnityEngine.UI.Button`, `Image`, `Canvas` |
| `com.unity.textmeshpro` | 3.0.6 | `TMPro.TextMeshProUGUI`, text rendering |

## Key log file locations

- Create project: `/tmp/unity-create.log`
- Compilation: `/tmp/unity-compile.log`
- Editor logs: `~/Library/Logs/Unity/Editor.log`

## Checking compilation status from logs

```bash
# Success indicator — absence of "Scripts have compiler errors" + exit code 0
grep "Scripts have compiler errors" /tmp/unity-compile.log
# If found → compilation failed
# If not found + exit 0 → compilation succeeded

# All errors
grep -E "error CS" /tmp/unity-compile.log | sort -u

# All warnings
grep -E "warning CS" /tmp/unity-compile.log | sort -u
```
