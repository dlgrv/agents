# Screenshots and Visual Evidence in Issues

## When to Include Screenshots

- **Visual bugs:** UI rendering issues, layout problems, color mismatches
- **UX problems:** confusing workflows, missing elements, broken navigation
- **Accessibility issues:** text overlap, unreadable fonts, contrast problems
- **Mobile/desktop differences:** responsive design failures
- **Comparison requests:** "before/after" or "current vs expected" visual proofs

## Screenshot Best Practices

### Technical Specs
- Use consistent resolution (e.g., 1280×800 @2x for desktop previews)
- Capture full context — include surrounding UI elements
- Use system screenshot tools, not browser devtools (captures actual rendering)
- Save in PNG format for lossless quality
- Name systematically: `01-en-light.png`, `02-ru-dark.png`, etc.

### Content Guidelines
- **Annotate minimally:** Use circles/arrows only if absolutely necessary
- **Show the problem:** Don't crop out error messages or broken elements
- **Include state indicators:** Show version numbers, branch names, or environment labels
- **Multiple angles:** Provide both expanded and collapsed UI states when relevant
- **Mobile/desktop pairs:** Show responsive behavior across screen sizes

### Upload and Reference
- Attach directly to the issue (GitHub supports image uploads)
- Use relative links in issue body: `![alt](docs/screens/01.png)`
- Reference by filename for clarity: "See screenshot 01-en-light.png"

## Pitfalls to Avoid

- **Never edit screenshots:** Photoshop cropping or color correction hides real rendering
- **Don't use mockups:** Real screenshots only — mockups may not reproduce the bug
- **Avoid compression artifacts:** PNG format preserves pixel-perfect detail
- **Don't hide the UI:** Full context helps diagnose the root cause
- **Don't assume screen size:** Specify resolution if responsive behavior is key

## Example Issue Structure with Screenshots

```
**Title:** Sidebar scroll phantom in collapsed state

**Summary:** When the sidebar is collapsed, a phantom scrollbar appears in the empty area above the navigation.

**Environment:**
- Browser: Chrome 120.0.6099.130
- OS: macOS Sonoma 14.2.1
- Resolution: 1280×800 @2x
- Branch: visual-report-branch

**Screenshots:**
- [01-en-light-collapsed.png](docs/screens/01-en-light-collapsed.png) — Shows phantom scrollbar in light theme
- [02-en-dark-collapsed.png](docs/screens/02-en-dark-collapsed.png) — Same issue in dark theme

**Steps to reproduce:**
1. Navigate to any page
2. Click the hamburger menu to collapse sidebar
3. Observe phantom scrollbar in the empty left area

**Expected:** No scrollbar should appear when sidebar is collapsed

**Acceptance criteria:**
- [ ] Phantom scrollbar eliminated in collapsed state
- [ ] No regression in expanded sidebar behavior
- [ ] Works across all themes (light/dark)
```