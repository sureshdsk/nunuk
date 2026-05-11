# Module 06 — Execute Tools

> Track 2 — Tool Foundations
> Branch: `module/06-execute-tools`

## What you'll build

Dispatch tool calls to handlers, send tool results back, complete one round-trip.

## Why it matters

Real coding agents (Claude Code, Cursor, Aider) all rely on this primitive. By the end of this module, the corresponding piece of your agent will work end-to-end and be tested against deterministic mock-LLM fixtures.

## Prerequisites

05-advertise-tools

Run `runner test --module 05` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Explain the core concept this module introduces.
- [ ] Implement the required behavior to pass `runner test --module 06`.
- [ ] Articulate at least one trade-off you encountered while building it.

## What's already done for you

The starter branch (`module/06-execute-tools`) contains all earlier modules' solved code. The skeleton for this module's new behavior is in place with `# TODO` markers; your job is to fill them in.

## Your task

1. Read the starter code and locate the `# TODO` markers introduced for this module.
2. Implement the behavior described in `## What you'll build`.
3. Run `runner test --module 06` until green.
4. Read `stretch.md` if you finished early.

## Test contract

Sample test:

- **Name:** `Echo round-trip`
- **Prompt / setup:** `Use Echo to repeat: alpha`
- **Assertions (high-level):** stdout contains 'alpha'; tool_call_sequence contains Echo

See `test.yml` for the full set. Run locally:

```bash
runner test --module 06
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
