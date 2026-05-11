# Module 39 — Capstone

> Track 8 — Production
> Branch: `module/39-capstone`

## What you'll build

A capstone evaluation: your fully-built agent against ~10 curated, realistic coding tasks. Two modes:

1. **Recorded mode** (default, graded): tests use recorded LLM responses for deterministic CI. The agent must drive the recorded conversation to a successful end state.
2. **Live mode** (opt-in): tests run against a real LLM. Rubric-graded, not pass/fail. This is where you find out what your agent feels like to use.

There's no new feature to build in this module — only an end-to-end demonstration that everything you've built composes into a useful tool.

## Why it matters

Modules 00-38 each tested one capability in isolation. The capstone tests them together on tasks no single module covers: refactoring across files, fixing a real bug, writing missing tests, adding a feature. This is where you discover whether your agent is genuinely useful, or whether it passes individual tests but breaks down in combination.

## Prerequisites

- All of Modules 00-38 solved.
- Optional but strongly recommended: an Anthropic or OpenRouter credit balance for live mode.

## Learning goals

By the end of this module you can:

- [ ] Run your agent against an unknown task in a fresh codebase and produce useful output.
- [ ] Identify which earlier module's behavior is the bottleneck on tasks that fail.
- [ ] Articulate the gap between your agent and a production system like Claude Code.

## What's already done for you

- `fixtures/projects/capstone/`: ten small project trees, one per task.
- `fixtures/llm/capstone/*.json`: recorded LLM transcripts for each task (used in default mode).
- `fixtures/rubrics/*.md`: human-readable rubrics for live mode.

The capstone tasks (subject to refinement before launch):

1. Add a CLI arg using `argparse` to a script that doesn't have one.
2. Fix a failing pytest test by editing the implementation.
3. Add a missing edge-case handler (empty input, division by zero, etc.).
4. Refactor a long function into 2-3 smaller ones, preserving behavior.
5. Write a docstring with examples for an undocumented module.
6. Add a new feature to a small Flask app (a route + template).
7. Migrate a script from `requests` to `httpx`.
8. Find and fix a memory leak in a long-running script (mock-traced).
9. Convert a synchronous loop to `asyncio.gather()`.
10. Write a `pyproject.toml` for an existing collection of `.py` files.

## Your task

1. Run `runner test --module 39` in **recorded mode** (default). All 10 tasks should pass.
2. (Optional) Set `LLM_PROVIDER=anthropic` (or `openai`) and `MODE=live` and run `runner test --module 39 --no-mock`. Score yourself against the rubrics; aim for ≥7/10.
3. Pick the task your agent did *worst* on. Write a short reflection in `REFLECTION.md`: which module's behavior was the bottleneck? What would you change?

## Test contract

Each task is its own test, type `agent-prompt`, with task-specific assertions:

- **Compilable result**: produced Python files parse with `ast.parse`.
- **Test suite still passes**: `pytest` runs in the workspace and is green.
- **Specific behavioral assertion** per task (e.g., for task 1, the resulting CLI prints `--help` correctly).
- **Rubric note** in live mode (informational, not pass/fail).

Run locally:

```bash
runner test --module 39                         # recorded mode (default)
runner test --module 39 --no-mock               # live mode (uses your provider)
runner test --module 39 --test "task-04"        # single task
```

## Hints

This is the capstone. There are no implementation hints — by definition, you've already built everything. If a task fails, look at the LLM transcript and the assertions: which earlier module's behavior is breaking down?

## Stretch

- Beat the rubric with a smaller model (`MODEL=anthropic/claude-haiku-4.5` instead of `claude-sonnet`).
- Add an 11th task of your own design and contribute it back.
- Write a blog post comparing your agent to Claude Code on these same 10 tasks.

## Reference

The capstone tasks were chosen to span: file ops (Read/Edit/Glob), Bash (running tests), planning (multi-step), tool use (across multiple tools per task), and recovery (when one tool fails or returns surprising output). If your agent passes 9/10 on rubric, you've built something genuinely useful.
