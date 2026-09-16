---
name: apple-calendar
description: "Use when creating or reading Apple Calendar events."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [calendar, macos, eventkit, applescript, mcp]
---

# Apple Calendar on this Mac

## Standing approach

- EventKit MCP server is configured: `mcp_servers.apple-calendar` →
  `npx -y @redpop/apple-calendar-mcp` in ~/.hermes/config.yaml. Prefer its
  `mcp_apple-calendar_*` tools once Hermes has been restarted with them:
  correct recurrence expansion, full CRUD, faster and less brittle than
  AppleScript.
- **MCP tools load only at Hermes restart.** If tool_search finds no
  apple-calendar tools this session, don't stall and don't promise them —
  act now via Calendar.app AppleScript (below).
- User's personal calendar is **"Life"**. Everything else (Scheduled
  Reminders, Birthdays, Праздники России, Siri Suggestions) is
  service-generated — never write events there.
- Duration unspecified → 1 hour; the user states exceptions explicitly.

## Create events via osascript (fallback)

Send the script as `osascript <<'EOF' … EOF` — inline `-e` quoting breaks
on Cyrillic and nested quotes.

1. List calendars first, never assume a name:
   `osascript -e 'tell application "Calendar" to get name of every calendar'`
2. Build dates by setting fields on `current date`
   (year → month → day → hours → minutes → seconds). Parsing date strings
   misfires by locale.
3. One-off event:

```applescript
tell application "Calendar"
    set cal to calendar "Life"
    set startDate to current date
    set year of startDate to 2026
    set month of startDate to September
    set day of startDate to 21
    set hours of startDate to 19
    set minutes of startDate to 30
    set seconds of startDate to 0
    set endDate to startDate + (60 * 60) -- seconds
    set ev to make new event at end of events of cal with properties {summary:"Заголовок", start date:startDate, end date:endDate, location:"Адрес", description:"Детали"}
    return uid of ev
end tell
```

4. Recurring: after `make`, set a plain RRULE string on the event:
   `set recurrence of ev to "FREQ=WEEKLY;INTERVAL=1;BYDAY=WE,FR"`.
   Start the series at the first occurrence's date — not at "today"
   unless today is one.
5. **Verify by uid, not exit code.** Re-fetch the created event
   (`first event of cal whose uid is "<UID>"`) and print summary, start
   date, duration, recurrence. A write to the wrong calendar also exits 0.

## Pitfalls

- First Calendar automation may pop a macOS permission dialog; osascript
  error -1743 means it was denied before → user approves in System
  Settings → Privacy & Security → Automation (and Calendars: Full Access,
  not Add Only, or writes fail).
