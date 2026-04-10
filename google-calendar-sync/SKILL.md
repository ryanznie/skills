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

## When to use this instead of `.ics`

Use this skill when the user wants a real calendar update.

Use `ics-sync` only when:

- you need a portable invite file
- you want email-based delivery
- you do not have calendar API credentials

## How phone sync works

If your phone is signed into the same Google account and calendar sync is enabled, events created by this skill should appear in Google Calendar on the phone automatically.

## Prerequisites

1. Enable the Google Calendar API in Google Cloud
2. Create an OAuth desktop app client
3. Download the OAuth client JSON
4. Install dependencies:

```bash
python3 -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

The script stores a refreshable token locally after the first successful authorization.

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
python3 google-calendar-sync/scripts/upsert_google_calendar_event.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --client-secret /path/to/client_secret.json
```

Create a new event with attendees and Google Meet:

```bash
python3 google-calendar-sync/scripts/upsert_google_calendar_event.py \
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
python3 google-calendar-sync/scripts/upsert_google_calendar_event.py \
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
- The token file defaults to `google-calendar-sync/token.json`
- If you want an agent workflow with email fallback later, pair this skill with `ics-sync`
