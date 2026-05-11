# Reference — Module 28 (Project Memory)

Primary concepts, terminology, and external links.

## Concepts

Project memory is the "instructions that travel with the codebase" pattern. The agent reads a known set of filenames from the working tree on startup and prepends their content to its system prompt. Different agents converged on different filenames — `CLAUDE.md` (Claude Code), `AGENTS.md` (Codex), `.cursorrules` (Cursor), `.github/copilot-instructions.md` (Copilot). A pragmatic agent discovers them all so it stays useful across tooling preferences. The two design knobs that matter: a byte budget (so a runaway file can't fill the context) and de-duplication (so a project mirroring its conventions across three filenames doesn't burn tokens three times).

## Glossary terms used

See [`docs/glossary.md`](../../docs/glossary.md) for definitions of any unfamiliar terms.

## External reading

- [pydantic-deepagents — context-file auto-discovery](https://github.com/vstorm-co/pydantic-deepagents) (the README table of file → purpose → scope).
- [Cursor — `.cursorrules`](https://docs.cursor.com/context/rules-for-ai).
- [GitHub Copilot — custom instructions](https://docs.github.com/copilot/customizing-copilot/about-customizing-github-copilot-chat-responses).
- [Anthropic — `CLAUDE.md` best practices](https://docs.anthropic.com/en/docs/claude-code) (search "CLAUDE.md").

## Implementation references

- Module 26's `TodoWrite` tool established in-memory state that survives across turns; project memory is the static-content analogue.
- Module 27's `--plan` mode also adds content to the system prompt; combine carefully so plan-mode preamble + memory contents don't blow the budget together.
