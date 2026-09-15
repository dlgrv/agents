# Removing a Cross-Cutting React Feature

When removing a feature that spans multiple components (e.g., removing all collapse/toggle functionality), you must trace the full dependency chain. Missing one link causes type errors that only surface at `tsc` time.

## Dependency chain to trace

```
Component props (expanded, onExpandedChange, collapsible)
  → Component type definition (BidAttemptsSectionProps)
    → State variables (useState for expanded)
      → prefsRef object (holds expanded for save/load)
        → Prefs type (BidRuntimePrefs.expanded)
          → defaultPrefs function
            → mergePrefs function
              → Hook file (useCampaignSectionsPrefs.ts) — may become orphan
                → Style constants (runtimeCollapsibleShellStyle) — may become orphan
                  → Caller props (sectionsPrefs={sectionsPrefs}, collapsible)
                    → Caller type/controller (CampaignSectionsPrefsController)
                      → Caller helper functions (sectionCollapseProps)
```

## Step-by-step

1. **Component itself** (`CollapsibleSection.tsx`): Remove `expanded`, `onExpandedChange`, `defaultExpanded` props, `useState`, toggle button, conditional render. Keep `title`, `children`, `headerExtra`, `style`.

2. **Wrapper components** (`BidAttemptsSection.tsx`, `PlaybackRuntimeSection.tsx`): Remove `collapsible` prop from type. Remove `expanded` state. Remove `expanded` from `prefsRef`. Remove from `useEffect` dep array. Remove conditional `if (collapsible) { return <CollapsibleSection expanded={...}> }` — always return `<CollapsibleSection>`.

3. **Prefs types** (`campaignDashboardPrefs.ts`): Remove `expanded` from `BidRuntimePrefs` and `PlaybackRuntimePrefs` types. Remove from `defaultBidRuntimePrefs()` / `defaultPlaybackRuntimePrefs()`. Remove from `mergeBidRuntimePrefs()` / `mergePlaybackRuntimePrefs()`.

4. **Caller page** (`CampaignsPage.tsx`): Remove `sectionsPrefs` state, `sectionCollapseProps` helper, `CampaignSectionsPrefsController` type, `sectionsPrefs` prop from `CampaignFormFields`, `{...sectionCollapseProps(...)}` from all `<FormSection>` elements (use `sed` for 3+ occurrences), `collapsible` prop from runtime section calls.

5. **Orphan cleanup**: Delete hook file (`useCampaignSectionsPrefs.ts`). Remove unused style constant (`runtimeCollapsibleShellStyle`). Remove unused imports (`useCampaignSectionsPrefs`, `CampaignDetailSection`, `CampaignSectionsPrefs`, `getSectionExpanded`, `loadCampaignSectionsPrefs`, `saveCampaignSectionsPrefs`).

6. **Verify**: `npx tsc --noEmit` after each major step to catch orphaned references early.

## Common orphan patterns

- **Hook file**: If a hook was only used for the removed feature, the entire file becomes orphan. Delete it.
- **Style constant**: `runtimeCollapsibleShellStyle` was only imported by components using `collapsible` mode. After removing collapsible, it's orphan.
- **Prefs type field**: `expanded: boolean` in prefs types. Must remove from type, default function, AND merge function — missing any one causes a type error.
- **Batch prop removal**: Use `sed -i '' "s/ pattern//g" file` for 3+ identical prop spreads, then `tsc` to catch orphans.
