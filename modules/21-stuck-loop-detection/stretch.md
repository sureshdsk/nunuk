# Stretch — Module 21 (Stuck-Loop Detection)

Optional extensions for students who finish early. Not graded.

- **Detector telemetry**: print a one-line stuck-loop diagnostic to stderr on `WARN` showing which signal fired (repeat / oscillation / no-op streak) and the offending tool name. Future you will thank present you.
- **Configurable thresholds**: read `STUCK_REPEAT_N`, `STUCK_NOOP_K`, and `STUCK_WINDOW` from env. Defaults stay 3/4/6.
- **Wider no-op classification**: `Write` of an existing file with identical content, `Bash` with `set -e` exit-zero but no observable side effect (creative ground — pick one extension).
- Compare against pydantic-deepagents' detector under `pydantic_deep/processors/` — what does theirs catch that yours doesn't?

Pick one or two; don't try to do all of them.
