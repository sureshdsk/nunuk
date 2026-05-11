# Reference — Module 32 (Agent Teams)

Primary concepts, terminology, and external links.

## Concepts

Where Module 31's subagent is a single isolated worker spawned for one task and returning a single string, a team is a long-lived collection of workers sharing two pieces of explicit state — a TODO list and a message bus. The shape resembles a job queue with workers; the difference is that each worker is itself an LLM-driven agent loop, not a function. Teams are the natural fit when the unit of work is enumerable up front and the tasks are roughly independent. They're the wrong fit when tasks have rich dependencies between them — that's a workflow, not a team.

## Glossary terms used

See [`docs/glossary.md`](../../docs/glossary.md) for definitions of any unfamiliar terms.

## External reading

- [pydantic-deepagents — `include_teams=True`](https://github.com/vstorm-co/pydantic-deepagents) (search the README for "Teams").
- [Anthropic — Multi-agent research](https://www.anthropic.com/research) — design notes on parallel agents and shared scratch space.

## Implementation references

- Module 31's `Task` tool (`app/tools/task.py`) is the starting point; the `team=True` variant reuses most of its scaffolding.
- Module 24's `TodoWrite` tool established the in-memory TODO concept; this module generalizes it from "the model's notepad" to "shared state across workers."
- Module 19's cancellation handling matters here: a Ctrl-C must stop all workers, not just the parent.
