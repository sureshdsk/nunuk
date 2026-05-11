# Module 09 — Bash Tool

> Track 2 — Tool Foundations
> Branch: `module/09-bash-tool`

## What you'll build

Implement `Bash` with timeout, captured stdout/stderr, and a basic command allowlist.

## Why it matters

Real coding agents (Claude Code, Cursor, Aider) all rely on this primitive. By the end of this module, the corresponding piece of your agent will work end-to-end and be tested against deterministic mock-LLM fixtures.

## Prerequisites

08-write-tool

Run `runner test --module 08` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Explain the core concept this module introduces.
- [ ] Implement the required behavior to pass `runner test --module 09`.
- [ ] Articulate at least one trade-off you encountered while building it.

## What's already done for you

The starter branch (`module/09-bash-tool`) contains all earlier modules' solved code. The skeleton for this module's new behavior is in place with `# TODO` markers; your job is to fill them in.

## Your task

1. Read the starter code and locate the `# TODO` markers introduced for this module.
2. Implement the behavior described in `## What you'll build`.
3. Run `runner test --module 09` until green.
4. Read `stretch.md` if you finished early.

## Test contract

Sample test:

- **Name:** `ls returns directory listing`
- **Prompt / setup:** `Run `ls` and tell me what you see`
- **Assertions (high-level):** stdout contains 'a.py'; tool_call_sequence contains Bash

See `test.yml` for the full set. Run locally:

```bash
runner test --module 09
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
