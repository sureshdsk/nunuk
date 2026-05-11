# Module 16 — Diff Display

> Track 4 — Agent UX
> Branch: `module/16-diff-display`

## What you'll build

When the model returns Edit/Write tool calls, print a colored unified diff before executing.

## Why it matters

Real coding agents (Claude Code, Cursor, Aider) all rely on this primitive. By the end of this module, the corresponding piece of your agent will work end-to-end and be tested against deterministic mock-LLM fixtures.

## Prerequisites

15-markdown-render

Run `runner test --module 15` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Explain the core concept this module introduces.
- [ ] Implement the required behavior to pass `runner test --module 16`.
- [ ] Articulate at least one trade-off you encountered while building it.

## What's already done for you

The starter branch (`module/16-diff-display`) contains all earlier modules' solved code. The skeleton for this module's new behavior is in place with `# TODO` markers; your job is to fill them in.

## Your task

1. Read the starter code and locate the `# TODO` markers introduced for this module.
2. Implement the behavior described in `## What you'll build`.
3. Run `runner test --module 16` until green.
4. Read `stretch.md` if you finished early.

## Test contract

Sample test:

- **Name:** `diff shown before write`
- **Prompt / setup:** `Add a comment to the top of code.py`
- **Assertions (high-level):** stdout contains '+# ' and '---' before tool execution

See `test.yml` for the full set. Run locally:

```bash
runner test --module 16
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
