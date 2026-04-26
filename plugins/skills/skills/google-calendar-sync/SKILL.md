---
name: google-calendar-sync
description: Create or update events directly in Google Calendar so they sync to devices already connected to that Google account. Use when an agent should perform a real calendar update instead of emailing an `.ics` file.
---

# Google Calendar Sync

Use the bundled script to create or update a Google Calendar event through the Google Calendar API.

This is the direct-sync path:

- event is written into Google Calendar
- your phone updates through the normal Google Calendar sync for that account
- no `.ics` email step is required

## When to use this

Use this skill when the user wants a real calendar update written directly to Google Calendar.

## How phone sync works

If your phone is signed into the same Google account and calendar sync is enabled, events created by this skill should appear in Google Calendar on the phone automatically.

## Prerequisites

1. Enable the Google Calendar API in Google Cloud
2. Create an OAuth desktop app client
3. Download the OAuth client JSON
4. Install dependencies:

```bash
uv sync
```

The script stores a refreshable token locally after the first successful authorization.

For persistent repo-local setup, create `google-calendar-sync/.env.calendar` inside `skills/`. The script loads that file automatically, or you can override it with `--env-file`.

Use [SETUP.md](SETUP.md) for the one-time setup steps on a MacBook.

## Required inputs

- Summary
- Start datetime: `YYYY-MM-DD HH:MM`
- End datetime: `YYYY-MM-DD HH:MM`
- Timezone: IANA timezone such as `America/New_York`
- OAuth client secret JSON path

## Optional inputs

- Description
- Location
- Calendar ID
- Existing event ID for update
- Attendee emails
- Meet link creation

## Run

Create a new event in your primary calendar:

```bash
uv run skills/google-calendar-sync/scripts/upsert_google_calendar_event.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --client-secret /path/to/client_secret.json
```

Create a new event with attendees and Google Meet:

```bash
uv run skills/google-calendar-sync/scripts/upsert_google_calendar_event.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --description "Review current milestone and blockers." \
  --attendee "person@example.com" \
  --attendee "teammate@example.com" \
  --add-meet \
  --client-secret /path/to/client_secret.json
```

Update an existing event:

```bash
uv run skills/google-calendar-sync/scripts/upsert_google_calendar_event.py \
  --event-id "<existing event id>" \
  --summary "Project Review" \
  --start "2026-04-15 15:00" \
  --end "2026-04-15 15:30" \
  --tz "America/New_York" \
  --client-secret /path/to/client_secret.json
```

## Notes

- Default calendar is `primary`
- The first run triggers a local OAuth consent flow
- The token file defaults to `skills/google-calendar-sync/token.json`
