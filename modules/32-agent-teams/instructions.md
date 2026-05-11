# Module 32 — Agent Teams

> Track 7 — Advanced
> Branch: `module/32-agent-teams`

## What you'll build

A step up from the one-shot subagent of Module 31: a long-lived "team" of agents sharing a single TODO list with atomic claim/release semantics and a message bus that the parent and children all post to. The `Task` tool gains a `team=true` variant that starts a worker which polls the shared TODO for unclaimed items, executes them, and posts results to the bus. Termination is by drain (no unclaimed TODOs remain) or by an explicit stop signal from the parent.

## Why it matters

Subagents (Module 31) are great for "go figure out X, come back with a string." Teams are for "here are 10 things to do; spread them across 3 workers and tell me when they're all done." The distinction is shared state vs. isolated context. Production agents (pydantic-deepagents' `include_teams=True`, multi-agent research patterns) lean on this for parallel research, parallel refactoring, and any workload where the unit of work is enumerated up front.

## Prerequisites

31-subagents-task-tool

Run `runner test --module 31` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Implement a shared TODO list with atomic claim/release using `threading.Lock`.
- [ ] Design a message bus that both parent and workers post to.
- [ ] Run multiple workers concurrently against the shared list without duplicating work.
- [ ] Aggregate worker results back into a single parent transcript.
- [ ] Reason about when a "team" is the right shape vs. one subagent vs. inline tool calls.

## What's already done for you

The starter branch contains:

- All of Modules 00-31 solved.
- A `app/team.py` stub with `SharedTodoList` and `MessageBus` skeletons.
- The `Task` tool gains a `team: bool = False` parameter slot in `app/tools/task.py`.
- Mock-LLM support for spawning multiple workers from a single `Task(team=True)` call.

## Your task

1. In `app/team.py`, implement `SharedTodoList`:
   - `add(item: str) -> str` (returns id)
   - `claim(worker_id: str) -> tuple[str, str] | None` — atomic; returns `(id, item)` or `None` if none unclaimed.
   - `complete(id: str, result: str)` — marks claimed-and-done; appends result to a results dict.
   - `drained() -> bool` — true when all items have a recorded result.
2. Implement `MessageBus.post(worker_id: str, msg: dict)` and `MessageBus.drain() -> list[dict]`.
3. In `app/tools/task.py`, when `team=True`:
   - Read the parent's TODO seed from arguments.
   - Spawn `n_workers` child agents (default 2; cap at 5).
   - Each worker polls `claim()`, executes the work (full agent loop), posts to the bus, calls `complete()`.
   - Parent waits for `drained()` (with a timeout), then assembles a final transcript from the bus.
4. Surface the bus contents back to the parent so the parent's transcript shows what each worker did.

## Test contract

- **`team drains TODOs without duplication`**: mock seeds 3 TODOs with 2 workers → each TODO has exactly one `claim` and one `complete`; final result aggregates all 3 outputs.
- **`worker count is bounded`**: requesting 10 workers caps at 5; the cap is logged to stderr.
- **`drain timeout aborts cleanly`**: a worker mock hangs; the parent times out → exit non-zero with a `team timed out` message; no zombie workers.

Run locally:

```bash
runner test --module 32
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
