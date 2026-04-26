# Calendar Skills Plugin

Agent skills for scheduling and calendar sync for Claude Code and other skill-compatible agents.

## Installation

### Claude Code

```bash
claude plugin marketplace add ryanznie/skills
claude plugin install calendar-skills@skills
```

Restart Claude Code after installation. Skills activate automatically when relevant.

**Update:**

```bash
claude plugin marketplace update
claude plugin update calendar-skills@skills
```

Or run `/plugin` to open the plugin manager.

### Other agents

For agents supporting the [skills.sh](https://skills.sh) ecosystem:

```bash
npx skills add ryanznie/skills
```

### Local development

```bash
git clone git@github.com:ryanznie/skills.git
cd skills
claude --plugin-dir ./plugins/calendar-skills
```

## Available Skills

| Skill | Domain | Description |
|-------|--------|-------------|
| [ai-scheduler](plugins/calendar-skills/skills/ai-scheduler/SKILL.md) | Scheduling | Schedule Zoom meetings and send calendar invites via AgentMail |
| [apple-calendar-sync](plugins/calendar-skills/skills/apple-calendar-sync/SKILL.md) | Calendar | Create or update CalDAV and iCloud calendar events |
| [google-calendar-sync](plugins/calendar-skills/skills/google-calendar-sync/SKILL.md) | Calendar | Create or update Google Calendar events directly |

## Repository Structure

```text
.claude-plugin/marketplace.json
plugins/calendar-skills/.claude-plugin/plugin.json
plugins/calendar-skills/skills/<skill-name>/SKILL.md
```

Each skill can include its own `scripts/`, `references/`, `assets/`, `templates/`, or `agents/` directories as needed.

## Python Setup

This repo uses `uv` for Python dependency management and execution.

```bash
cd /path/to/skills
uv sync
```

Run repo Python entrypoints with `uv run ...`.

## Tested Setup

- `apple-calendar-sync`: uses the repo `uv` environment plus `plugins/calendar-skills/skills/apple-calendar-sync/.env.calendar`
- `google-calendar-sync`: uses the repo `uv` environment plus `plugins/calendar-skills/skills/google-calendar-sync/.env.calendar`
- `ai-scheduler`: uses `plugins/calendar-skills/skills/ai-scheduler/.env.scheduler` and the local `.venv_agentmail` environment

## Releases

Plugin versioning is tracked in [plugins/calendar-skills/.claude-plugin/plugin.json](plugins/calendar-skills/.claude-plugin/plugin.json). GitHub releases are created by [release.yml](.github/workflows/release.yml) and use semver tags in the form `vX.Y.Z`.

See [CHANGELOG.md](CHANGELOG.md) for the human-maintained change log.
