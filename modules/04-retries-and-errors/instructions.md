# Module 04 — Retries And Errors

> Track 1 — LLM Plumbing
> Branch: `module/04-retries-and-errors`

## What you'll build

Wrap LLM calls in exponential backoff for 429/5xx; give up gracefully after a cap.

## Why it matters

Real coding agents (Claude Code, Cursor, Aider) all rely on this primitive. By the end of this module, the corresponding piece of your agent will work end-to-end and be tested against deterministic mock-LLM fixtures.

## Prerequisites

03-streaming

Run `runner test --module 03` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Explain the core concept this module introduces.
- [ ] Implement the required behavior to pass `runner test --module 04`.
- [ ] Articulate at least one trade-off you encountered while building it.

## What's already done for you

The starter branch (`module/04-retries-and-errors`) contains all earlier modules' solved code. The skeleton for this module's new behavior is in place with `# TODO` markers; your job is to fill them in.

## Your task

1. Read the starter code and locate the `# TODO` markers introduced for this module.
2. Implement the behavior described in `## What you'll build`.
3. Run `runner test --module 04` until green.
4. Read `stretch.md` if you finished early.

## Test contract

Sample test:

- **Name:** `retries on 429 then succeeds`
- **Prompt / setup:** `Hello`
- **Assertions (high-level):** exit 0; llm_call_count exactly 3 (mock returns 429, 429, 200)

See `test.yml` for the full set. Run locally:

```bash
runner test --module 04
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
