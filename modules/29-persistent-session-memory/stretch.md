# Stretch — Module 29 (Persistent Session Memory)

Optional extensions for students who finish early. Not graded.

- **Mid-session checkpoints & rewind**: implement `/checkpoint <name>` to snapshot the in-memory conversation history, and `/rewind <name>` to restore it. Distinct from this module's whole-session save/resume — checkpoints are mid-session and many-per-session. Reference: pydantic-deepagents' `include_checkpoints=True` capability. Useful when a tool call took the conversation in an unproductive direction and you want to back up without losing earlier context.
- **List sessions**: `/sessions ls` enumerates saved sessions for the current project with their last-modified timestamps.
- **Compact-on-save**: when serializing history to disk, drop redundant tool-result payloads (e.g. `Read` results whose file is still on disk and unchanged). Saves disk + reload time.
- **Cross-project resume**: `--resume <full-id>` accepts a session id from a *different* project root, with a clear warning that paths in the history may not be valid.

Pick one or two; don't try to do all of them.
