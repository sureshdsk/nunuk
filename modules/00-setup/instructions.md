# Module 00 — Setup

> Track 0 — Setup
> Branch: `module/00-setup`

## What you'll build

A working development environment and an `./agent --doctor` command that verifies it. By the end of this module, the runner can sanity-check every other student's environment with one call.

## Why it matters

Half of "I'm stuck" in cohort programs is "my environment is wrong." This module catches that on day one. The doctor command also becomes a useful diagnostic later when something inexplicable breaks — your future self will thank you.

## Prerequisites

_(none — this is the first module)_

## Learning goals

By the end of this module you can:

- [ ] Run `uv` to manage Python versions and dependencies.
- [ ] Source a `.env` file and read its variables in Python.
- [ ] Detect missing requirements and report them clearly via exit code and stderr.
- [ ] Make `./agent --doctor` exit 0 on a healthy machine.

## What's already done for you

The starter branch contains:

- `pyproject.toml` declaring `python>=3.12`, `python-dotenv`, and `openai` as dependencies (the latter two used by future modules).
- `agent` (a thin shell wrapper) that runs `uv run python -m app.main "$@"`.
- `app/main.py` with an `argparse` skeleton that handles `--doctor` and `-p` flags.
- A `.env.example` showing the required keys.

You'll fill in the doctor logic.

## Your task

1. Implement the `doctor()` function in `app/main.py`.
2. It must check, in order:
    1. Python version is ≥3.12. Print `python: 3.X.Y OK` or `python: X.Y FAIL (need >=3.12)`.
    2. `uv` is on the PATH. Print `uv: <version> OK` or `uv: missing FAIL`.
    3. `OPENROUTER_API_KEY` is set (after loading `.env`). Print `OPENROUTER_API_KEY: set OK` or `OPENROUTER_API_KEY: missing FAIL`.
    4. `MODEL` is set, or default to `anthropic/claude-haiku-4.5` and print the default.
3. If any check fails, exit non-zero. If all pass, print `OK` on the last line and exit 0.

Helpers you'll likely use: `sys.version_info`, `shutil.which`, `os.environ.get`, `dotenv.load_dotenv`.

## Test contract

The runner runs:

```bash
./agent --doctor
```

Tests:

- **`doctor exits 0 on healthy env`**: with `OPENROUTER_API_KEY=test-key` set, exit code is 0 and stdout's final line is `OK`.
- **`doctor exits non-zero when key missing`**: with `OPENROUTER_API_KEY` unset, exit code is non-zero and stdout contains `OPENROUTER_API_KEY: missing FAIL`.
- **`doctor reports each check`**: stdout contains all four checks (python, uv, OPENROUTER_API_KEY, MODEL).

Run locally:

```bash
runner test --module 00
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
