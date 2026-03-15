# ai-scheduler

Schedules Zoom meetings and emails `.ics` invites via AgentMail.

## Quick Start
- Skill docs: `ai-scheduler/SKILL.md`
- Script: `ai-scheduler/scripts/schedule_zoom_and_send_invite.py`
- Env file: `ai-scheduler/.env.scheduler` (copy from `ai-scheduler/.env.scheduler.example`)

Example:

```sh
. .venv_agentmail/bin/activate
.venv_agentmail/bin/python ai-scheduler/scripts/schedule_zoom_and_send_invite.py \
  --topic "Fundraising" \
  --chat-topic "$5M startup fundraising" \
  --to "Ry <ryanznie@bu.edu>" \
  --cc "ryanznie@gatech.edu" \
  --start "2026-03-15 21:00" \
  --tz "America/New_York" \
  --duration 20
```

## Zoom Credentials
To obtain `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, and `ZOOM_CLIENT_SECRET`, create a Zoom Server-to-Server OAuth app:

1. Sign in to the Zoom App Marketplace.
2. Create a new app of type "Server-to-Server OAuth".
3. In the app's "App Credentials" page, copy the Account ID, Client ID, and Client Secret.
4. Ensure the app has the required meeting scopes (at least `meeting:write` and `meeting:read`) and is activated.

## AgentMail Credentials
To obtain `AGENTMAIL_API_KEY` and an inbox for `AGENTMAIL_INBOX_ID`:

1. Go to AgentMail at `agentmail.to` and sign up.
2. Create an inbox from the dashboard.
3. Copy the inbox ID and API key into `ai-scheduler/.env.scheduler`.
