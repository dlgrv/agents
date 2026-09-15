# Programmatic Scene Assembly via Editor Scripts

When the Unity GUI is unavailable, build entire scenes via C# editor scripts executed in batchmode. This covers the full pattern.

## Core Pattern

### 1. Create the editor script

File: `Assets/Editor/SceneBuilder.cs`

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.UI;
using TMPro;
using UnityEngine.EventSystems;
using Unity.AI.Navigation; // NavMeshSurface in Unity 6

public static class SceneBuilder
{
    const string SCENE_PATH = "Assets/Scenes/GameScene.unity";

    [MenuItem("Tools/Build Game Scene")]
    public static void BuildScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        // Create GameObjects with CreatePrimitive, AddComponent, etc.
        // ...

        // Save scene
        EditorSceneManager.SaveScene(scene, SCENE_PATH);
        AssetDatabase.SaveAssets();
        Debug.Log("GameScene built and saved to " + SCENE_PATH);
    }

    static Material CreateMaterial(string name, Color color)
    {
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null) shader = Shader.Find("Standard");
        var mat = new Material(shader);
        mat.name = name;
        mat.color = color;
        AssetDatabase.CreateAsset(mat, $"Assets/Materials/{name}.mat");
        return mat;
    }
}
#endif
```

### 2. Run in batchmode

```bash
UNITY="/Applications/Unity/Hub/Editor/6000.0.82f1/Unity.app/Contents/MacOS/Unity"
PROJECT="/path/to/YourProject"

"$UNITY" -batchmode -nographics -projectPath "$PROJECT" \
  -executeMethod SceneBuilder.BuildScene \
  -logFile /tmp/unity-build-scene.log
```

### 3. Verify

```bash
# Scene file exists
ls -la "$PROJECT/Assets/Scenes/GameScene.unity"

# No errors
grep "error CS" /tmp/unity-build-scene.log | sort -u

# Success marker
grep "GameScene built and saved" /tmp/unity-build-scene.log
```

## Key APIs for Programmatic Scene Building

| API | Purpose |
|-----|---------|
| `EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single)` | Create empty scene |
| `GameObject.CreatePrimitive(PrimitiveType.Cube)` | Create primitive with collider + renderer |
| `Object.DestroyImmediate(obj.GetComponent<CapsuleCollider>())` | Remove default collider before adding CharacterController |
| `obj.AddComponent<T>()` | Attach component with default values |
| `PrefabUtility.SaveAsPrefabAsset(obj, "Assets/Prefabs/X.prefab")` | Save as reusable prefab |
| `AssetDatabase.LoadAssetAtPath<GameObject>(path)` | Load prefab reference |
| `AssetDatabase.CreateAsset(mat, path)` | Save material as .mat asset |
| `EditorSceneManager.SaveScene(scene, path)` | Save scene file |
| `EditorBuildSettingsScene` | Add scene to Build Settings |
| `NavMeshSurface.BuildNavMesh()` | Bake NavMesh at build time |

## Gotchas

### CharacterController replaces CapsuleCollider
When adding `CharacterController` to a capsule, first destroy the default `CapsuleCollider`:
```csharp
Object.DestroyImmediate(player.GetComponent<CapsuleCollider>());
var cc = player.AddComponent<CharacterController>();
```

### NavMeshAgent replaces CapsuleCollider
Same for customer prefabs with NavMeshAgent — remove the default collider to avoid conflicts.

### Trigger colliders for interaction zones
Set `isTrigger = true` on BoxCollider for zones where player interaction is needed:
```csharp
garden.GetComponent<BoxCollider>().isTrigger = true;
```

### UI requires EventSystem
Canvas + GraphicRaycaster need an EventSystem GameObject:
```csharp
var es = new GameObject("EventSystem");
es.AddComponent<EventSystem>();
es.AddComponent<StandaloneInputModule>();
```

### TextMeshProUGUI needs Canvas
TMP text elements must be children of a Canvas. Set up Canvas with CanvasScaler before adding text:
```csharp
var canvas = canvasObj.AddComponent<Canvas>();
canvas.renderMode = RenderMode.ScreenSpaceOverlay;
var scaler = canvasObj.AddComponent<CanvasScaler>();
scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
scaler.referenceResolution = new Vector2(1920f, 1080f);
canvasObj.AddComponent<GraphicRaycaster>();
```

### RectTransform anchoring for UI
Use anchorMin/anchorMax/pivot/anchoredPosition/sizeDelta for precise UI placement:
```csharp
var rect = obj.GetComponent<RectTransform>();
rect.anchorMin = new Vector2(0.5f, 1f);  // top-center
rect.anchorMax = new Vector2(0.5f, 1f);
rect.pivot = new Vector2(0.5f, 1f);
rect.anchoredPosition = new Vector2(0f, -20f);
rect.sizeDelta = new Vector2(300f, 60f);
```

### Add scene to Build Settings
```csharp
var buildScenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
if (!buildScenes.Exists(s => s.path == SCENE_PATH))
{
    buildScenes.Add(new EditorBuildSettingsScene(SCENE_PATH, true));
    EditorBuildSettings.scenes = buildScenes.ToArray();
}
```

### Shader.Find may return null
URP shader name is `"Universal Render Pipeline/Lit"`. If URP is not active, fall back:
```csharp
var shader = Shader.Find("Universal Render Pipeline/Lit");
if (shader == null) shader = Shader.Find("Standard");
```

### NavMeshSurface in Unity 6
Must use `using Unity.AI.Navigation;` namespace (not `UnityEngine.AI`). Bake via:
```csharp
var surface = ground.AddComponent<NavMeshSurface>();
surface.collectObjects = CollectObjects.All;
surface.BuildNavMesh();
```
