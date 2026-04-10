---
name: ics-sync
description: Create `.ics` calendar events and optionally deliver them by email, including through an AgentMail inbox. Use when an agent needs a lightweight calendar invite flow without a direct Google/Outlook integration.
---

# ICS Sync

Use the bundled script to generate a single-event `.ics` file and either:

- write it to disk
- email it as an attachment

This skill is the lightweight option when you want calendar-compatible invites without depending on a calendar API.

## What this does

- Generates a standards-friendly `VCALENDAR` + `VEVENT`
- Converts local time plus IANA timezone into UTC event timestamps
- Supports organizer, attendees, location, description, URL, and reminders
- Can send the `.ics` as an email attachment through AgentMail

## Important limitation

An `.ics` file is an invitation payload, not a calendar backend.

- Sending to a normal mailbox can cause Google Calendar, Outlook, Apple Calendar, or another client to import/show the event
- Sending to an AgentMail inbox works as email delivery, and the inbox will receive the `.ics` attachment
- AgentMail itself is not a calendar store and does not automatically expose a synced calendar view

If you want true two-way calendar sync, use this skill for invite transport only, then pair it with a real calendar API or a worker that reads the agent inbox and writes events into Google/Outlook.

## Required inputs

- Summary
- Start datetime: `YYYY-MM-DD HH:MM`
- End datetime: `YYYY-MM-DD HH:MM`
- Timezone: IANA name such as `America/New_York`

## Optional inputs

- Description
- Location
- URL
- Organizer name + email
- One or more attendees
- Output path
- Email subject/body
- AgentMail credentials for delivery

## Run

Write an `.ics` file only:

```bash
python ics-sync/scripts/send_ics_invite.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --description "Review current milestone and blockers." \
  --location "Zoom" \
  --output /tmp/project-review.ics
```

Send the invite through AgentMail:

```bash
python ics-sync/scripts/send_ics_invite.py \
  --summary "Project Review" \
  --start "2026-04-15 14:00" \
  --end "2026-04-15 14:30" \
  --tz "America/New_York" \
  --description "Review current milestone and blockers." \
  --from-inbox "scheduler@agentmail.to" \
  --to "participant@example.com" \
  --output /tmp/project-review.ics \
  --agentmail-api-key "$AGENTMAIL_API_KEY"
```

Send to another agent inbox:

```bash
python ics-sync/scripts/send_ics_invite.py \
  --summary "Internal Agent Handoff" \
  --start "2026-04-15 16:00" \
  --end "2026-04-15 16:15" \
  --tz "America/New_York" \
  --from-inbox "scheduler@agentmail.to" \
  --to "calendar-bot@agentmail.to" \
  --agentmail-api-key "$AGENTMAIL_API_KEY"
```

## Delivery rules

- Before sending, always review the generated subject, recipients, and event times
- If using AgentMail, include the standard disclaimer as the first line of the email body
- Prefer sending both a readable email body and the `.ics` attachment

## Notes for agent inboxes

Use an AgentMail inbox when you want an agent to:

- receive an invite by email
- inspect or forward the `.ics`
- trigger downstream automation from the message

Do not treat the AgentMail inbox itself as the final synced calendar unless you also build the ingestion step that converts the attachment into calendar API writes.
