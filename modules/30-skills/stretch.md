# Stretch — Module 30 (Skills)

Optional extensions for students who finish early. Not graded.

- **Trigger-based auto-invocation**: when the user prompt matches one of a skill's `triggers` (e.g. "summarize PR"), pre-load the skill body without the model needing to call the skill tool explicitly. Mirror's Claude Code's behavior.
- **Skill discovery up the tree**: search `./skills/`, then parent dirs, then `~/.config/agent/skills/`. Same shape as Module 28's memory discovery.
- **Skill argument schema**: instead of every skill taking `{"prompt": string}`, let each skill declare its own input schema in frontmatter (`inputs: {target: string, mode: enum}`). Now skills are typed.
- **Skill packaging**: a `./agent skill new <name>` subcommand that scaffolds a SKILL.md with the right frontmatter.

Pick one or two; don't try to do all of them.
