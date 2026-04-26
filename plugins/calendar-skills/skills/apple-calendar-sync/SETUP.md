# Apple Calendar Setup

This skill writes events directly into iCloud Calendar over CalDAV so they sync into Apple Calendar on your MacBook and iPhone.

## One-time setup

1. Create or refresh the repo virtual environment and install dependencies:

```bash
cd /path/to/skills
uv sync
cd plugins/calendar-skills/skills/apple-calendar-sync
```

2. Generate an Apple app-specific password:

- Go to `account.apple.com`
- Sign in with your Apple Account
- Open `Sign-In and Security`
- Open `App-Specific Passwords`
- Create a password for this scheduling workflow

3. Create the skill config file:

```bash
cp .env.calendar.example .env.calendar
```

4. Edit `.env.calendar` and fill in:

- `APPLE_CALENDAR_USERNAME`
- `APPLE_CALENDAR_PASSWORD`
- `APPLE_CALENDAR_NAME`
- `APPLE_CALENDAR_TZ`

For iCloud, keep:

- `APPLE_CALENDAR_CALDAV_URL=https://caldav.icloud.com`

## Useful commands

List your available calendars:

```bash
uv run scripts/upsert_caldav_event.py \
  --list-calendars
```

Create a new iCloud calendar:

```bash
uv run scripts/upsert_caldav_event.py \
  --create-calendar "AI-sync"
```

Create an event:

```bash
uv run scripts/upsert_caldav_event.py \
  --summary "Dinner with Eric" \
  --start "2026-04-13 19:30" \
  --end "2026-04-13 21:00" \
  --description "Dinner with Eric."
```

Update an event when you already know the UID:

```bash
uv run scripts/upsert_caldav_event.py \
  --uid "<existing uid>" \
  --summary "Dinner with Eric" \
  --start "2026-04-13 20:00" \
  --end "2026-04-13 22:00"
```

## How to invoke from Codex

Mention the skill by name in your prompt:

```text
Use apple-calendar-sync to create an event called Dinner with Eric on Monday at 7:30 PM.
```

With `.env.calendar` in place, you do not need to resend credentials each time.
