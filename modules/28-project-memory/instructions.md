# Module 28 — Project Memory

> Track 6 — Planning & Memory
> Branch: `module/28-project-memory`

## What you'll build

A context-file auto-discovery primitive: scan the current directory and walk parent directories for a known family of agent-context files, concatenate their contents (with per-file dividers) into the system prompt, and add a `/memory <file>` slash command to edit any of them. Files to discover, in order: `CLAUDE.md`, `AGENTS.md`, `SOUL.md`, `CONVENTIONS.md`, `.cursorrules`, `.github/copilot-instructions.md`. Same list, walking up parents. Identical content is de-duplicated. Total injected size is capped at a configurable byte budget.

## Why it matters

Every coding agent ships with a context-files convention. Cursor reads `.cursorrules`, Claude Code reads `CLAUDE.md`, OpenAI Codex reads `AGENTS.md`, GitHub Copilot reads `.github/copilot-instructions.md`. Production agents (pydantic-deepagents auto-discovers six file types out of the box) treat this as a *family* — one project may have all of them present because different team members use different tools. Reading only one file means your agent ignores half of the project's documented behavior. Reading them all without de-dup means you waste tokens. This module gets it right.

## Prerequisites

27-plan-mode

Run `runner test --module 27` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Walk the directory tree from `cwd` to `/` looking for a list of well-known filenames.
- [ ] Concatenate found content with per-file dividers (`# === path ===`).
- [ ] De-duplicate identical content across files.
- [ ] Cap total injected size at a configurable byte budget (`AGENT_MEMORY_BUDGET_BYTES`, default 32 KB).
- [ ] Implement a `/memory <file>` slash command that opens the named context file in `$EDITOR`.

## What's already done for you

The starter branch (`module/28-project-memory`) contains all earlier modules' solved code. A stub `app/memory.py` is in place with a discovery scaffold and `# TODO` markers. The fixture project `fixtures/projects/multi-context-files/` already contains `CLAUDE.md`, `AGENTS.md`, `SOUL.md`, and `.cursorrules` for testing.

## Your task

1. In `app/memory.py`, implement `discover_context_files(cwd: Path) -> list[Path]`:
   - For each name in `["CLAUDE.md", "AGENTS.md", "SOUL.md", "CONVENTIONS.md", ".cursorrules", ".github/copilot-instructions.md"]`, check `cwd / name`. If found, add to list.
   - Then walk `cwd.parent`, `cwd.parent.parent`, ..., up to `/` (or filesystem root), repeating.
2. In `app/memory.py`, implement `build_system_prompt_addition(files: list[Path], budget: int) -> str`:
   - Read each file's content; skip identical-content duplicates (compare by `sha256`).
   - Format: `# === {relative_path} ===\n{content}\n\n` per file.
   - Cap at `budget` bytes — truncate the LAST file rather than dropping it (a partial CLAUDE.md is better than no CLAUDE.md).
3. Wire this into `app/agent.py::build_system_prompt`: append the discovered content after the static system prompt.
4. Implement `/memory <file>` slash command in `app/repl.py`:
   - `/memory CLAUDE.md` → opens `./CLAUDE.md` in `$EDITOR` (default `vi`).
   - `/memory` (no arg) → defaults to `CLAUDE.md`.
   - After save, reloads the system prompt for subsequent turns.

## Test contract

- **`single CLAUDE.md is found`**: fixture has only `CLAUDE.md` → system prompt contains its content.
- **`multiple files discovered and dividered`**: fixture has `CLAUDE.md` + `AGENTS.md` → system prompt contains both, separated by `# === CLAUDE.md ===` and `# === AGENTS.md ===` dividers.
- **`identical content is de-duplicated`**: fixture has `CLAUDE.md` and `AGENTS.md` with byte-identical content → only one copy is injected.
- **`parent dir walk works`**: fixture has `./sub/` as cwd with `CLAUDE.md` at `./` → system prompt finds it.
- **`byte budget caps injection`**: fixture has a 100 KB CLAUDE.md; with `AGENT_MEMORY_BUDGET_BYTES=4096` → system prompt addition is ≤4096 bytes.
- **`/memory edits then reloads`**: REPL session: `/memory` (mock editor appends "new note"), next turn → system prompt contains "new note".

Run locally:

```bash
runner test --module 28
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
