# Reference — Module 30 (Skills)

Primary concepts, terminology, and external links.

## Concepts

A skill is a unit of packaged agent behavior — instructions, a tool whitelist, optional supporting files — that the agent can load on demand rather than always carrying in its system prompt. Skills decouple "what your agent knows how to do" from "what your agent ships with by default." A team can author skills as a sibling-repo collection, version them independently of the agent, and even share skills across multiple agent frameworks. The cost of a skill is a folder and a Markdown file with YAML frontmatter; the payoff is a clean separation between the runtime and the workflows it supports.

## Glossary terms used

See [`docs/glossary.md`](../../docs/glossary.md) for definitions of any unfamiliar terms.

## External reading

- [Anthropic — Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code) (search "skills" / "agent skills").
- [pydantic-deepagents — `bundled_skills/`](https://github.com/vstorm-co/pydantic-deepagents/tree/main/pydantic_deep/bundled_skills) — production skill packaging.
- [Frontmatter convention](https://jekyllrb.com/docs/front-matter/) — the YAML-between-`---`-lines idiom borrowed from static-site generators.

## Implementation references

- Module 28's context auto-discovery (`app/memory.py`) reads multiple files from a search path; the skill discovery follows the same shape.
- The tool registry's per-turn whitelist hook (added in Module 17 for `--yolo`/allowlist) is the same hook a skill uses to restrict its sub-loop.
