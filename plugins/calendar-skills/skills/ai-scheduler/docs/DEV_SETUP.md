# Developer setup

This skill uses a dedicated virtual environment for the AgentMail and Zoom integrations.

## Install

From this directory:

```sh
cd plugins/calendar-skills/skills/ai-scheduler
python3 -m venv .venv_agentmail
.venv_agentmail/bin/python -m pip install httpx agentmail
```

Copy `.env.scheduler.example` to `.env.scheduler` and fill in the Zoom and AgentMail credentials. Keep `.env.scheduler` local; it is gitignored.

## Create an invite

```sh
.venv_agentmail/bin/python scripts/schedule_zoom_and_send_invite.py \
  --topic "Project Sync" \
  --chat-topic "Bi-weekly project update and roadmap discussion" \
  --to "Jane Doe <jane.doe@example.com>" \
  --start "2026-03-15 14:00" \
  --tz "America/New_York" \
  --duration 30
```

The script generates the Zoom meeting, sends the `.ics` invite, and records the event UID in `.event-log.jsonl`.

## Update an invite

Use the original UID and increment the sequence number for each update:

```sh
.venv_agentmail/bin/python scripts/send_calendar_update.py \
  --uid "<original-uid>" \
  --to "person@example.com" \
  --subject "Ryan + Person: Coffee chat" \
  --topic "Agents and software factory" \
  --start "2026-03-15 16:00" \
  --previous-start "2026-03-15 14:00" \
  --tz "America/New_York" \
  --duration 30 \
  --location "Cafe" \
  --sequence 1
```

The email shows the previous time struck through and the new time below it. The `.ics` uses the same UID, `METHOD:REQUEST`, and a higher `SEQUENCE`, allowing calendar clients to update the existing event.

## Credentials

The Zoom integration requires a Server-to-Server OAuth app with meeting read/write scopes:

- `ZOOM_ACCOUNT_ID`
- `ZOOM_CLIENT_ID`
- `ZOOM_CLIENT_SECRET`

AgentMail requires:

- `AGENTMAIL_API_KEY`
- `AGENTMAIL_INBOX_ID`
- `AGENTMAIL_HOST` (optional organizer address)
- `AGENTMAIL_SUBJECT_PREFIX` (for example, `Ryan +`)

Never commit credentials, OAuth tokens, or generated event logs.
