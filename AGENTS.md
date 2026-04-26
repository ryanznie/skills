# Calendar Skills Plugin

This repository is structured as a Claude Code plugin (see `plugins/calendar-skills/`), but the skills follow the open [Agent Skills specification](https://agentskills.io) format.

## Keep updated

When modifying or adding skills, keep these files in sync:

- `plugins/calendar-skills/.claude-plugin/plugin.json` - plugin version using semver
- `README.md` - installation instructions, available skills table, and repository structure
- `CHANGELOG.md` - add an entry under `[Unreleased]` describing what changed
- skill-local setup docs and examples when paths or invocation change

### Changelog conventions

`CHANGELOG.md` is updated manually alongside code changes. The GitHub release workflow (`.github/workflows/release.yml`) generates release notes independently from `git log` and does not read `CHANGELOG.md`.

When bumping the plugin version for a release, move the `[Unreleased]` entries under a new versioned heading (for example `## [0.2.0] - 2026-04-26`) before merging. Use the same category headings the release workflow uses:

- `### Skills & Features` - new skills, new arguments, behavior changes
- `### Bug Fixes` - correctness fixes
- `### Documentation` - README, AGENTS.md, setup guides
- `### Maintenance` - CI, dependencies, refactors with no user-visible change

## Structure

```text
plugins/calendar-skills/skills/<skill-name>/SKILL.md
```

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown instructions. Supporting materials should stay next to the skill they belong to.

Recommended layout:

```text
plugins/calendar-skills/skills/<skill-name>/
|- SKILL.md
|- scripts/
|- references/
|- assets/
|- templates/
|- agents/
```

## Creating or updating a skill

1. Create or edit `plugins/calendar-skills/skills/<skill-name>/SKILL.md`
2. Keep YAML frontmatter accurate
3. Update any supporting scripts or references in the same skill directory
4. Update `README.md` if the available skills list changed
5. Add a short note to `CHANGELOG.md`

## Repo policy

- Use `uv` for Python dependency management and execution in this repo
- Run Python entrypoints with `uv run ...` unless a skill explicitly requires a separate environment
- Do not commit live credentials, refresh tokens, or local OAuth artifacts
- Keep path examples pointed at `plugins/calendar-skills/skills/...` so they work without any repo-root symlinks.
