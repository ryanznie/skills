# skills

Canonical home for my Codex agent skills.

## Layout
- Each skill lives in a top-level folder (e.g. `review-target/`) with a `SKILL.md`.
- System skills live in `.system/`.

## Featured skill: `ai-scheduler`
Schedules Zoom meetings and emails `.ics` invites via AgentMail.

- Skill docs: `ai-scheduler/SKILL.md`
- Script: `ai-scheduler/scripts/schedule_zoom_and_send_invite.py`

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

## Point Codex at this repo
This repo is meant to back `~/.codex/skills`.

```sh
# backup current skills dir (if any)
mv ~/.codex/skills ~/.codex/skills.bak

# symlink Codex to this repo
ln -s ~/Desktop/work/skills ~/.codex/skills
```
