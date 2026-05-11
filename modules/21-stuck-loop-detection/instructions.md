# Module 21 — Stuck-Loop Detection

> Track 5 — Robustness
> Branch: `module/21-stuck-loop-detection`

## What you'll build

A defensive layer wrapped around the agent loop that watches the recent tool-call sequence and short-circuits when the model is stuck. Three signals to detect: the same `(tool_name, arguments)` repeated `N` times in a row; an A-B-A-B oscillation across the last four calls; and `>K` consecutive tool calls that return no-op results (e.g. `Read` of a missing path, `Grep` with zero hits). On the first strike the agent injects a synthetic system message describing the loop and lets the model try once more; on a second strike the turn aborts with a clear error.

## Why it matters

Real agents get stuck. A model that decides `Read missing.txt` once will often decide it again — and again — until you run out of budget. Production systems (Claude Code, pydantic-deepagents, Aider) all detect repetition and break out. Without this layer, you've built a billing tool, not an agent.

## Prerequisites

20-history-truncation

Run `runner test --module 20` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Detect repeated `(tool_name, arguments)` calls within a sliding window.
- [ ] Detect A-B-A-B oscillation in the last four tool calls.
- [ ] Classify a tool result as a no-op (missing path, empty match, etc.) for loop-counting purposes.
- [ ] Inject a one-shot recovery system message before aborting the turn.

## What's already done for you

The starter branch (`module/21-stuck-loop-detection`) contains all earlier modules' solved code. `app/agent.py` exposes the tool-call list per turn. A `app/stuck.py` stub with `# TODO` markers is in place for the detector.

## Your task

1. In `app/stuck.py`, implement `StuckDetector` with three methods:
   - `record(tool_name: str, arguments: dict, result_was_noop: bool) -> Verdict`
   - The detector tracks a deque of the last N tool calls (N = 6 default).
   - Return `Verdict.OK`, `Verdict.WARN` (first strike — inject hint), or `Verdict.ABORT` (second strike — abort turn).
2. The three signals (any one triggers a strike):
   - **Repeat**: same `(name, args)` 3 times in a row.
   - **Oscillation**: last four are `A, B, A, B`.
   - **No-op streak**: 4 consecutive `result_was_noop=True`.
3. In `app/agent.py`, wire the detector into the loop. On `WARN`, append a system message like `"You appear to be repeating the same tool call. Try a different approach or stop."` and continue. On `ABORT`, print an explanatory error to stderr and exit non-zero.
4. Classify no-ops: `Read` returns "file not found", `Grep` returns empty results, `Glob` returns empty list.

## Test contract

- **`repeat triggers warn then abort`**: mock script returns `Read("nope.txt")` four times → on call 3 stderr/stdout contains `stuck loop`; on call 4 the agent aborts (`exit_code != 0`).
- **`oscillation detected`**: mock alternates `Read(a)` / `Read(b)` for six calls → detection fires by the 5th call.
- **`useful work is not a false positive`**: mock issues six distinct tool calls, each with non-empty results → no detector warning; `exit_code == 0`.

Run locally:

```bash
runner test --module 21
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
