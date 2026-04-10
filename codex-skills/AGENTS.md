## Agent behavior notes (skills workspace)

### Python and environment policy

Always use `uv` for Python dependency management in this repo.

Rules:

- Create or refresh the repo environment with `uv sync`
- Run Python entrypoints with `uv run ...`
- If a command must target the repo virtualenv directly, use `.venv/bin/python` from this repo
- Do not use bare `python`, `python3`, or `pip` for repo tasks unless there is a specific reason you state first
- Keep installs inside the repo-managed virtual environment, not the system interpreter
- When adding Python dependencies, update `pyproject.toml` so `uv sync` remains the source of truth

### Network failures in sandbox mode

If a command that needs outbound network access fails with a DNS/network-style error (e.g. `httpx.ConnectError: [Errno 8] nodename nor servname provided, or not known`), immediately retry the same command with `sandbox_permissions="require_escalated"` (requesting approval via the tool call) without sending an extra assistant message to ask first.

Rationale: these failures are commonly caused by sandbox network restrictions, and the escalated retry is the fastest path to success. If the escalated retry also fails, treat it as a real environment/network/DNS issue and report the error.
