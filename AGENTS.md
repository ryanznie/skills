# Skills Marketplace

This repository is a Claude Code plugin marketplace. Each plugin lives under `plugins/<plugin-name>/`, and each plugin's skills follow the open [Agent Skills specification](https://agentskills.io) format.

Current plugins in this repo: `calendar-skills` and `productivity`.

## Keep updated

When modifying or adding skills, keep these files in sync:

- `plugins/<plugin-name>/.claude-plugin/plugin.json` - plugin version using semver
- `README.md` - installation instructions, available plugins section, and repository structure
- skill-local setup docs and examples when paths or invocation change

### Release conventions

The release flow uses a single workflow file:

- `.github/workflows/release.yml` publishes tags and performs the GitHub release for the selected plugin

The GitHub release body is generated from plugin-scoped `git log` output and is the source of truth for published release notes in this repo.

When cutting a release, the workflow must:

- select the target plugin from the workflow dropdown
- choose a semver bump from the workflow dropdown
- update that plugin's `plugin.json`
- create the immutable patch tag `vX.Y.Z+<plugin>`
- move the mutable minor tag `vX.Y+<plugin>` to the latest patch release for that minor line
- check out the immutable patch tag in the release job
- publish the GitHub release from the immutable patch tag

Preferred practice is to bump `plugin.json` as part of the normal edit that changes the plugin, rather than creating a separate release PR just to record the version. The release workflow should never create a PR for version bookkeeping.

The workflows expect a `RELEASE_TOKEN` secret with permission to create tags and GitHub releases.

## Structure

```text
plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown instructions. Supporting materials should stay next to the skill they belong to.

Recommended layout:

```text
plugins/<plugin-name>/skills/<skill-name>/
|- SKILL.md
|- scripts/
|- references/
|- assets/
|- templates/
|- agents/
```

## Creating or updating a skill

1. Create or edit `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
2. Keep YAML frontmatter accurate
3. Update any supporting scripts or references in the same skill directory
4. Update `README.md` if the available plugins or user-facing docs changed

## Repo policy

- Use `uv` for Python dependency management and execution in this repo
- Run Python entrypoints with `uv run ...` unless a skill explicitly requires a separate environment
- Do not commit live credentials, refresh tokens, or local OAuth artifacts
- Keep path examples pointed at the canonical plugin path for the specific plugin being documented.
