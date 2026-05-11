# Stretch — Module 28 (Project Memory)

Optional extensions for students who finish early. Not graded.

- **Include `~/.config/agent/MEMORY.md`** at the end of the discovery chain — a global, per-user agent memory file.
- **Per-file budget**: allow each file family to declare a sub-budget so a runaway 200 KB `.cursorrules` can't crowd out a small CLAUDE.md.
- **Soft-link awareness**: if `AGENTS.md` is a symlink to `CLAUDE.md`, skip the second copy without reading and hashing.
- **`/memory ls`** slash command that lists all discovered files with their byte sizes, so the student can see what's being injected.
- Compare against pydantic-deepagents' context-file table (in the framework README) — what files are you missing?

Pick one or two; don't try to do all of them.
