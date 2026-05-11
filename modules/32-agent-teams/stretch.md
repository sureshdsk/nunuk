# Stretch — Module 32 (Agent Teams)

Optional extensions for students who finish early. Not graded.

- **Worker telemetry**: include per-worker token spend and elapsed time in the assembled transcript. Sets up Module 37 (cost tracking) for multi-worker totals.
- **Heterogeneous workers**: let the parent pass a per-worker config (model, system prompt, tool whitelist) so one worker uses Haiku for cheap research while another uses Sonnet for synthesis.
- **Adaptive worker count**: if the TODO list grows mid-run (a worker discovers a new task), spawn an additional worker up to the cap.
- **Backpressure on the bus**: if the bus depth exceeds K, pause new claims. Realistic when workers post large diffs.

Pick one or two; don't try to do all of them.
