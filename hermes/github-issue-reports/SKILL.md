---
name: github-issue-reports
description: "File upstream GitHub issues: dupes, mechanism, evidence."
license: MIT
metadata:
  hermes:
    tags: [github, issues, bug-reports, upstream, open-source]
---

# Filing upstream issues (bug reports)

Class: filing a NEW issue about a defect on someone's repo. Command mechanics (list/edit/label via gh) → `github-issues`; NousResearch/hermes-agent repo specifics → `hermes-agent-contributing`.

## Gate — before writing

1. Verified against the code the user actually runs (local checkout / editable install / built bundle), not memory or docs.
2. Root-caused at MECHANISM level: you can name file:line and the exact function/constant that misbehaves. Symptom-only reports earn needs-repro and get closed.
3. Dupe check twice: once by SYMPTOM (the user's words), once by MECHANISM (function name, constant, limit, file). Read any hit in full. Same root cause → comment there, don't file. Adjacent but different mechanism/layer → file new and add a "Relation to #N" section explaining why the fixes differ (fixing one must not imply fixing the other).

## Evidence standard

- A runnable probe beats a screenshot. If the repo is importable (venv, editable install), execute the failing path directly and paste verbatim output — counts, booleans, error text.
- Cite artifacts: `file.py:LINE`, the introducing commit SHA (find via `git log -S "<string>"`), version (`git describe --tags`), config facts.
- State in one line what you did NOT verify (other surfaces, other platforms, packaged builds).
- Environment section = real version facts only. Never fabricate debug-report/upload links; if the template demands them, say why they're absent and offer to run the uploader.

## Structure

Mirror the repo's `.github/ISSUE_TEMPLATE/` when it exists. Title = outcome ("X truncates/invisible when Y"), not activity ("Investigate X"). Sections: Summary (what + since when, one paragraph) → Environment → Steps to reproduce (minimal; embed the probe script) → Root cause (file:line story) → Expected → Acceptance criteria. Criteria are testable and mechanism-level: "empty-composer `/` lists `/goal`", not "goal works again".

## Publishing

- Submit with `gh issue create --body-file`, then verify by reading it back (`gh issue view N --json number,title,state,url`).
- Labels, assignees, milestones need triage rights — expect 403 as an outside contributor; triagers label on review. Don't retry.

## /sepia rule

When the user invokes /sepia for issue/PR text: load the sepia skill references (professional-pass; `domains/tickets.md` for reports, `domains/dev-replies.md` for follow-up comments), sample the venue (the repo's issue template + 2–3 recent issues), and self-review the draft (professional checklist 1–10 + style-pass §2–3) BEFORE posting. Known repeat miss: the repro depends on a version fact left out of Environment.
