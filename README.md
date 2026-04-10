# skills

Home for my AI agent skills.

## Python setup

This repo uses `uv` for Python dependency management and virtualenv execution.

```sh
cd /Users/ryanznie/Desktop/work/skills
uv sync
```

Run repo Python scripts with `uv run ...`.

## Layout
- Each skill lives in a top-level folder (e.g. `ai-scheduler/`) with a `SKILL.md`.
- System skills live in `.system/`.

## Summary
- `ai-scheduler`: Schedules Zoom meetings and emails `.ics` invites via AgentMail.
- `apple-calendar-sync`: Creates or updates iCloud/CalDAV events so Apple Calendar syncs them to your devices.
  Setup: see `apple-calendar-sync/SETUP.md`. Local credentials live in `apple-calendar-sync/.env.calendar`.
- `google-calendar-sync`: Creates or updates Google Calendar events directly so devices synced to that account get the update.
- `ics-sync`: Generates `.ics` calendar events and can email them, including to AgentMail inboxes.

## Point Codex at this repo
This repo is meant to back `~/.codex/skills`.

```sh
# backup current skills dir (if any)
mv ~/.codex/skills ~/.codex/skills.bak

# symlink Codex to this repo
ln -s ~/Desktop/work/skills ~/.codex/skills
```
