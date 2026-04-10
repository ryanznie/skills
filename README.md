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
- `codex-skills/`: Codex-facing skill tree, including `AGENTS.md`, skill folders, and `.system/`.
- `claude-skills/`: Claude-facing skill tree. Empty placeholder for now.
- Repo tooling such as `pyproject.toml` and `uv.lock` stays at the repo root.

## Summary
- `ai-scheduler`: Schedules Zoom meetings and emails `.ics` invites via AgentMail.
- `apple-calendar-sync`: Creates or updates iCloud/CalDAV events so Apple Calendar syncs them to your devices.
  Setup: see `codex-skills/apple-calendar-sync/SETUP.md`. Local credentials live in `codex-skills/apple-calendar-sync/.env.calendar`.
- `google-calendar-sync`: Creates or updates Google Calendar events directly so devices synced to that account get the update.

## Point Codex at this repo
Codex should point at the `codex-skills/` subtree, not the repo root.

```sh
# backup current skills dir (if any)
mv ~/.codex/skills ~/.codex/skills.bak

# symlink Codex to the Codex-specific subtree
ln -s ~/Desktop/work/skills/codex-skills ~/.codex/skills
```

## Claude

`claude-skills/` is intentionally empty right now. The reusable implementations still live in this repo, but Claude-specific wrappers have not been added yet.
