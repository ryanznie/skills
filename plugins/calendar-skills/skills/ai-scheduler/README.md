# ai-scheduler

Schedules Zoom meetings and emails `.ics` invites via AgentMail.

## Documentation

- [Skill instructions](SKILL.md)
- [Developer setup and CLI reference](docs/DEV_SETUP.md)
- [Changelog](../../CHANGELOG.md)

## Components

- `scripts/schedule_zoom_and_send_invite.py` — creates Zoom meetings and sends invites
- `scripts/send_calendar_update.py` — updates existing `.ics` events, including in-person events
- `.env.scheduler.example` — credential configuration template
- `.event-log.jsonl` — local, gitignored event metadata log
