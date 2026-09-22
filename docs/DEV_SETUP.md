# Developer setup

## Clone and run locally

```bash
git clone git@github.com:ryanznie/skills.git
cd skills
claude --plugin-dir ./plugins/calendar-skills
```

To work on another plugin, point `claude --plugin-dir` at its directory under `plugins/`.

## Python setup

This repository uses `uv` for Python dependency management and execution:

```bash
uv sync
uv run <entrypoint>
```

The `calendar-skills` AI scheduler uses a dedicated environment for AgentMail and Zoom. See its [developer setup](../plugins/calendar-skills/skills/ai-scheduler/docs/DEV_SETUP.md) for integration-specific instructions.

Keep credentials, OAuth files, and generated event logs local; they are gitignored.

## Testing changes

Run targeted checks from the repository root, for example:

```bash
python3 -m py_compile plugins/calendar-skills/skills/ai-scheduler/scripts/*.py
git diff --check
```

## Releases

Run the [release workflow](../.github/workflows/release.yml) with the target plugin and semver bump. It updates `plugin.json`, creates immutable patch and mutable minor tags, and publishes the GitHub release.

Release tags use this format:

- `vX.Y.Z+<plugin>` — immutable patch release
- `vX.Y+<plugin>` — mutable minor release line
