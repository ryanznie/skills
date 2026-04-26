---
name: apple-calendar-sync
description: Create or update events in an iCloud or other CalDAV calendar so Apple Calendar on iPhone, iPad, or Mac syncs the change automatically. Use when the user prefers Apple Calendar over email-based `.ics` invites.
---

# Apple Calendar Sync

Use the bundled script to create or update events in a CalDAV calendar, including iCloud Calendar.

This is the direct-sync path for Apple Calendar when your devices are using iCloud or another CalDAV account:

- the event is written into the CalDAV calendar backend
- Apple Calendar syncs it to iPhone, iPad, and Mac
- no `.ics` email step is required

## How this works on iPhone

Apple Calendar is the client. The actual synced data source is typically one of:

- iCloud Calendar
- Google Calendar
- Exchange
- another CalDAV account

If you use iCloud Calendar and your phone is signed into the same Apple Account with calendar sync enabled, events created by this skill should appear in the Calendar app automatically.

## iCloud credentials

For iCloud, use:

- your Apple Account email as the username
- an app-specific password, not your normal Apple Account password

Apple documents app-specific passwords for third-party access to iCloud Mail, Calendar, and Contacts.

## Dependencies

```bash
uv sync
```

## Required inputs

- Summary
- Start datetime: `YYYY-MM-DD HH:MM`
- End datetime: `YYYY-MM-DD HH:MM`
- Timezone: IANA timezone such as `America/New_York`
- CalDAV URL
- Username
- Password

## Optional inputs

- Calendar name filter
- Existing event UID for update
- Description
- Location
- URL

## Reasonable estimates for missing details

- If the user gives a start time but no end time, use a reasonable default duration based on the event type.
- For appointment-style events such as `appt`, `apt`, or `appointment`, default to `30 minutes` unless the user indicates otherwise.
- State the assumption briefly when confirming or reporting the created event.
- If the missing detail would materially change the scheduling outcome, ask instead of guessing.

You can provide the CalDAV connection settings either as flags or environment variables:

```bash
export APPLE_CALENDAR_CALDAV_URL="https://caldav.icloud.com"
export APPLE_CALENDAR_USERNAME="you@example.com"
export APPLE_CALENDAR_PASSWORD="app-specific-password"
export APPLE_CALENDAR_NAME="Home"
export APPLE_CALENDAR_TZ="America/New_York"
```

For persistent repo-local setup, create `.env.calendar` in this skill directory. The script loads that file automatically, or you can override it with `--env-file`.

Use [SETUP.md](SETUP.md) for the one-time setup steps on a MacBook.

## Run

Create a new event in iCloud Calendar. Run from this skill directory:

```bash
uv run scripts/upsert_caldav_event.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --caldav-url "https://caldav.icloud.com" \
  --username "you@example.com" \
  --password "$ICLOUD_APP_PASSWORD" \
  --calendar-name "Home"
```

Update an existing event. Run from this skill directory:

```bash
uv run scripts/upsert_caldav_event.py \
  --uid "<existing uid>" \
  --summary "Project Review" \
  --start "2026-04-15 15:00" \
  --end "2026-04-15 15:30" \
  --tz "America/New_York" \
  --caldav-url "https://caldav.icloud.com" \
  --username "you@example.com" \
  --password "$ICLOUD_APP_PASSWORD" \
  --calendar-name "Home"
```

## Selection rules

- If `--calendar-name` is provided, the script chooses the first matching writable calendar
- If omitted and exactly one calendar is available, it uses that calendar
- If multiple calendars are available and no name is given, the script exits and shows the available calendars

## Notes

- iCloud support is done through standard CalDAV, not a separate Apple-only API
- For iCloud, create an app-specific password at `account.apple.com`
