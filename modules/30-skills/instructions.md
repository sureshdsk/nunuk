# Module 30 — Skills

> Track 6 — Planning & Memory
> Branch: `module/30-skills`

## What you'll build

A `skills/` discovery primitive. Each skill is a directory under `./skills/<name>/` containing a `SKILL.md` (frontmatter: `name`, `description`, `tools`, `triggers`) and optional resource files. On startup, the agent enumerates skills and registers each as a virtual tool whose schema is `{"prompt": string}` and whose description carries the SKILL.md description. When the model calls the skill, the agent prepends the skill's SKILL.md body to the conversation for that turn and (optionally) restricts the active tool palette to the skill's whitelisted tools.

## Why it matters

Skills are how you ship reusable agent behavior without bloating the system prompt. A `summarize-pr` skill, a `migrate-to-pydantic-v2` skill, a `write-unit-tests` skill — each is a small package: instructions + tool whitelist + maybe a few example files. Production agents (Anthropic Claude Code, pydantic-deepagents' `bundled_skills/`) lean on this pattern; without it your agent is locked into one omnibus system prompt.

## Prerequisites

29-persistent-session-memory

Run `runner test --module 29` to confirm the prior module is green before starting (if applicable).

## Learning goals

By the end of this module you can:

- [ ] Parse YAML frontmatter from a Markdown file.
- [ ] Register a "virtual tool" backed by a skill manifest, not a Python function.
- [ ] Inject skill body text into the conversation just-in-time on invocation.
- [ ] Restrict the active tool palette per-turn based on a whitelist.

## What's already done for you

The starter branch contains:

- All of Modules 00-29 solved.
- A `skills/` directory at the repo root with two example skills: `skills/summarize-pr/` and `skills/write-changelog/`.
- A YAML frontmatter parser stub at `app/skills.py` with `# TODO` markers.
- The tool-registry abstraction extended to support tool-source provenance ("builtin" vs "skill") — relevant for the per-turn palette filter.

## Your task

1. In `app/skills.py`, implement `discover_skills(root: Path) -> list[Skill]`:
   - Walk `root/*/SKILL.md`. Parse YAML frontmatter (`---` ... `---`) with `name`, `description`, `tools: [Read, Write, ...]`, optional `triggers: [...]`.
   - Body is whatever comes after the frontmatter.
2. Register each `Skill` as a tool named `skill_<name>` with description from the frontmatter. Schema: `{"prompt": string}`.
3. When the model calls `skill_<name>`:
   - Append a system message containing the skill body.
   - Set the per-turn allowed-tool whitelist to the skill's `tools` field (plus the skill tool itself, so the model can complete normally).
   - Run the inner tool-call loop until completion.
   - Return a brief summary to the parent as the skill tool's result.
4. Add a `--list-skills` CLI flag that prints discovered skills and exits.

## Test contract

- **`discovered skill is listed`**: with `skills/summarize-pr/SKILL.md` present, `--list-skills` exits 0 and stdout contains `summarize-pr`.
- **`model invokes skill, body is injected`**: mock returns a `skill_summarize-pr` tool call → next mock-LLM request to the provider includes the skill body text in messages.
- **`whitelisted tools only`**: mock invokes the skill, then tries `Bash` (not in the skill's whitelist) → the agent rejects with a clear error and the tool call is not executed.

Run locally:

```bash
runner test --module 30
```

## Hints

Try for at least 30 minutes before peeking. Hints are progressive — see [`hints.md`](./hints.md).

## Stretch

Optional extensions for finishers — see [`stretch.md`](./stretch.md).

## Reference

External reading and concept primers — see [`reference.md`](./reference.md).
