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
- `codex-skills/`: Codex-facing skill tree for your own Codex skills and `AGENTS.md`.
- `claude-skills/`: Claude-facing skill tree. Empty placeholder for now.
- Repo tooling such as `pyproject.toml` and `uv.lock` stays at the repo root.

## Available Actions
| Skill | Action | Notes |
| --- | --- | --- |
| `ai-scheduler` | Schedule Zoom meetings and send `.ics` invites via AgentMail | Uses `codex-skills/ai-scheduler/` |
| `apple-calendar-sync` | Create or update iCloud/CalDAV events that sync into Apple Calendar | Setup: `codex-skills/apple-calendar-sync/SETUP.md`. Local credentials: `codex-skills/apple-calendar-sync/.env.calendar` |
| `google-calendar-sync` | Create or update Google Calendar events directly | Uses `codex-skills/google-calendar-sync/` |

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
