# Reference — Module 21 (Stuck-Loop Detection)

Primary concepts, terminology, and external links.

## Concepts

A "stuck loop" is a degenerate agent state where the model keeps issuing the same (or nearly the same) tool call without making progress. The most common shapes are: (a) repeated identical calls, (b) two-step oscillation (A-B-A-B), and (c) a streak of tool calls that succeed but produce no useful information (no-ops). All three are recoverable by injecting a recovery hint into the conversation; if the hint is ignored, abort the turn rather than burn budget.

## Glossary terms used

See [`docs/glossary.md`](../../docs/glossary.md) for definitions of any unfamiliar terms.

## External reading

- [pydantic-deepagents — stuck-loop processor](https://github.com/vstorm-co/pydantic-deepagents) (see `pydantic_deep/processors/` for the production implementation).
- ["Why agents get stuck" — Anthropic engineering blog](https://www.anthropic.com/engineering) (search "agent loops" / "tool errors").

## Implementation references

- The seed POC at `/Users/dsk/Developer/byocc/codecrafters-claude-code-python/app/main.py` ran an unbounded loop and was the motivating example: a missing-file `Read` would burn through the iteration cap before this module landed.
