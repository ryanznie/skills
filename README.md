# skills

Home for my AI agent skills.

## Layout
- Each skill lives in a top-level folder (e.g. `ai-scheduler/`) with a `SKILL.md`.
- System skills live in `.system/`.

## Summary
- `ai-scheduler`: Schedules Zoom meetings and emails `.ics` invites via AgentMail.

## Point Codex at this repo
This repo is meant to back `~/.codex/skills`.

```sh
# backup current skills dir (if any)
mv ~/.codex/skills ~/.codex/skills.bak

# symlink Codex to this repo
ln -s ~/Desktop/work/skills ~/.codex/skills
```
