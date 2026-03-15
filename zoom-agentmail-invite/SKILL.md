---
name: zoom-agentmail-invite
description: Schedule Zoom meetings via the Zoom API (Server-to-Server OAuth) or reuse an existing Zoom join URL, then email calendar invites (.ics) via AgentMail with a standardized “Zoom Meeting Invitation” body (topic, participants, date/time, join link, meeting ID, passcode, disclaimer). Use when an agent needs to create/send Zoom calendar invites, CC participants, or automate meeting scheduling + invite delivery.
---

# Zoom + AgentMail Meeting Invites

Use the bundled script to (a) create a Zoom meeting via API, and/or (b) send an AgentMail email with an `.ics` invite attachment and the standard invitation body.

## Style + confirmation rules

- Keep the email professional and minimal.
- Always show a full email preview (subject + body) before sending, then confirm (before sending) the host email (From), meeting time (with timezone), and participants (To/CC). The script prints a full email body preview before sending (even with `--yes`).
- Subject rule: if there is exactly 1 `--to` recipient, use `<PREFIX> <TO_NAME>: <TOPIC>` (prefer the display name if provided). `<PREFIX>` must be provided via `AGENTMAIL_SUBJECT_PREFIX` or `--subject-prefix`. The script compacts `<TOPIC>` to at most 5 words.
- Zoom meeting title rule: most punctuation is stripped/simplified for the Zoom meeting title sent to the Zoom API (email subject/body keep your original punctuation).

## Required inputs

- Topic (used for the Zoom meeting title and email subject)
- Optional chat topic (used in the body as the meeting topic)
- Start date/time + timezone (e.g. `2026-03-15 19:00`, `America/New_York`)
- Duration in minutes
- Participants (`--to` and optional `--cc`, comma-separated). You can use either:
  - plain emails: `--to "person@example.com"`
  - display name + email: `--to "Ry <person@example.com>"`
- Host display name (default: `Ryan Z. Nie`)

## Credentials (do not paste secrets into chat)

- Zoom Server-to-Server OAuth:
  - `ZOOM_ACCOUNT_ID`
  - `ZOOM_CLIENT_ID`
  - `ZOOM_CLIENT_SECRET`
- AgentMail:
  - `AGENTMAIL_API_KEY`
  - `AGENTMAIL_INBOX_ID` (required; used as the From/host email)

Preferred: set env vars in the environment running the script.

Optional: put env vars in a local `.env.zoom` file in the working directory (the script reads it and only fills missing env vars):

```bash
ZOOM_ACCOUNT_ID=...
ZOOM_CLIENT_ID=...
ZOOM_CLIENT_SECRET=...
AGENTMAIL_API_KEY=...
AGENTMAIL_INBOX_ID=ryanznie@agentmail.to
AGENTMAIL_INBOX_DISPLAY_NAME=Ryan Nie's AI Agent
AGENTMAIL_HOST_NAME=Ryan Nie's AI Agent
AGENTMAIL_ALWAYS_CC=ryanznie@gatech.edu
AGENTMAIL_SUBJECT_PREFIX=Ryan +
```

## Run

Create a meeting via Zoom API, then email an invite:

```bash
. .venv_agentmail/bin/activate
.venv_agentmail/bin/python zoom-agentmail-invite/scripts/schedule_zoom_and_send_invite.py \
  --topic "AgentMail" \
  --chat-topic "<Topic>" \
  --to "participant1@example.com" \
  --cc "participant2@example.com" \
  --start "2026-03-15 19:00" \
  --tz "America/New_York" \
  --duration 30
```

Reuse an existing Zoom meeting (skip Zoom API) and just send the invite email:

```bash
. .venv_agentmail/bin/activate
.venv_agentmail/bin/python zoom-agentmail-invite/scripts/schedule_zoom_and_send_invite.py \
  --topic "AgentMail" \
  --chat-topic "<Topic>" \
  --to "participant1@example.com" \
  --cc "participant2@example.com" \
  --start "2026-03-15 19:00" \
  --tz "America/New_York" \
  --duration 30 \
  --existing-join-url "<zoom join url>" \
  --existing-meeting-id <zoom meeting id> \
  --existing-passcode "<passcode>"
```

## Standard body template

The invite email body must not be hardcoded. The script renders the email body by reading `references/body-template.md` and filling placeholders with your inputs (topic, host, participants, when, join URL, meeting ID, passcode, disclaimer).

- See `references/body-template.md` for the exact text template.
