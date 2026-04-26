# Skills Marketplace

Plugin marketplace repo for Claude Code and other skill-compatible agents.

This repository can host multiple plugins. Right now it contains `calendar-skills`.

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
cd <repo-dir>
claude --plugin-dir ./plugins/calendar-skills
```

To work on a different plugin in this repo, point `claude --plugin-dir` at that plugin's directory under `plugins/`.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| `calendar-skills` | Zoom scheduling, Apple Calendar sync, and Google Calendar sync |

## Calendar Skills

The current `calendar-skills` plugin includes:

| Skill | Domain | Description |
|-------|--------|-------------|
| [ai-scheduler](plugins/calendar-skills/skills/ai-scheduler/SKILL.md) | Scheduling | Schedule Zoom meetings and send calendar invites via AgentMail |
| [apple-calendar-sync](plugins/calendar-skills/skills/apple-calendar-sync/SKILL.md) | Calendar | Create or update CalDAV and iCloud calendar events |
| [google-calendar-sync](plugins/calendar-skills/skills/google-calendar-sync/SKILL.md) | Calendar | Create or update Google Calendar events directly |

## Repository Structure

```text
.claude-plugin/marketplace.json
plugins/<plugin-name>/.claude-plugin/plugin.json
plugins/<plugin-name>/skills/<skill-name>/SKILL.md
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

Each plugin keeps its own semver in its `plugin.json`. GitHub releases are created by [release.yml](.github/workflows/release.yml), which lets you choose the target plugin from a dropdown, bumps that plugin version, commits it on a release branch, creates the matching `<plugin>@<version>` tag, publishes the release from that exact version, and opens a PR back to `main`.
