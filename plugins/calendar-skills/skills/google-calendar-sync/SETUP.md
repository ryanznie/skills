# Google Calendar Setup

This skill writes events directly into Google Calendar so they sync to devices using that Google account.

## One-time setup

1. Create or refresh the repo virtual environment and install dependencies:

```bash
cd /path/to/skills
uv sync
```

2. In Google Cloud:

- enable the Google Calendar API
- create an OAuth client of type `Desktop app`
- download the OAuth client JSON

3. Create the skill config file:

```bash
cp plugins/calendar-skills/skills/google-calendar-sync/.env.calendar.example \
  plugins/calendar-skills/skills/google-calendar-sync/.env.calendar
```

4. Edit `plugins/calendar-skills/skills/google-calendar-sync/.env.calendar` and fill in:

- `GOOGLE_CALENDAR_TZ`
- `GOOGLE_CALENDAR_CLIENT_SECRET`
- optional `GOOGLE_CALENDAR_ID`
- optional `GOOGLE_CALENDAR_TOKEN_PATH`

Default calendar is `primary`.

## First live run

The first live run opens a local browser-based Google OAuth flow and writes the refreshable token to `GOOGLE_CALENDAR_TOKEN_PATH`.

Create a test event:

```bash
uv run plugins/calendar-skills/skills/google-calendar-sync/scripts/upsert_google_calendar_event.py \
  --summary "Google Calendar Test" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30"
```

## How to invoke from Codex

Mention the skill by name in your prompt:

```text
Use google-calendar-sync to create an event called Google Calendar Test tomorrow at 2:00 PM.
```

With `plugins/calendar-skills/skills/google-calendar-sync/.env.calendar` in place, you do not need to resend the client secret path every time.
