# Agent guide — implementing a new module

This file is for coding agents (Claude, etc.) working in this repo. It is **not** student-facing and **not** the same as `CONTRIBUTING.md` (which is about authoring curriculum prose) or `docs/instructor-guide.md` (which is about running a cohort).

## What you are doing when you "implement a module"

You are writing the **solved code** that satisfies the behavioral test contract in `modules/NN-slug/test.yml`. The curriculum prose, fixtures, and test specs already exist — your job is to make them green.

## Workflow (current — overrides the docs)

> ⚠️ This workflow **deliberately contradicts** `docs/architecture/branch-strategy.md`. The doc describes the original starter-branch + private-solutions-repo model. The current owner has chosen a simpler workflow described below. Until that doc is updated, **prefer this file**.

The contract is:

1. `main` holds the **cumulative working agent** — after module N is merged, `./agent` on `main` does everything modules 00..N support.
2. **One branch per module.** Name it exactly `module/NN-slug` matching the folder under `modules/`.
3. **One focused commit** per branch. The commit body should explain *why*, not just *what*.
4. **Merge with `--no-ff`** so each module appears as a visible bubble in `git log --graph main`.
5. **Do not delete the module branch** after merge — keep the ref around so `git diff main..module/NN-slug` and `git log module/NN-slug` keep working.

### Step-by-step

```bash
# 1. Confirm you're on main and clean (modulo pre-existing untracked curriculum files)
git status

# 2. Branch
git checkout -b module/NN-slug

# 3. Implement. Read instructions.md, test.yml, hints.md in that order.
#    hints.md Level 3 is usually a reasonable scaffold; treat it as a hint not gospel.

# 4. Validate locally (see "Validating without the runner" below)

# 5. Commit only the files this module touches. Do NOT stage:
#    - the pending readme.md -> README.md rename (pre-existing, not your work)
#    - the untracked CURRICULUM.md, modules/, docs/, fixtures/, runner/, tools/,
#      CONTRIBUTING.md, LICENSE, course-definition.yml (pre-existing curriculum drop)
git add <module-specific files only>
git commit -m "module/NN-slug: <one-line summary>

<body explaining why, key decisions, smoke-test result>"

# 6. Merge
git checkout main
git merge --no-ff module/NN-slug -m "Merge branch 'module/NN-slug'

<short paragraph on what landed>"
```

### Commit message style (matches commits already on main)

Subject: `module/NN-slug: <imperative one-liner>`, ≤72 chars. Body wrapped at ~72, bullets allowed. Explain *why* and any non-obvious choice (e.g., "stderr not stdout because test asserts stderr_contains"). Mention the smoke test you ran.

No `Co-Authored-By` / `Generated with` trailers unless explicitly requested.

## How to read a module before coding

Read in this order:

1. **`modules/NN-slug/instructions.md`** — what to build, prerequisites, the explicit "Your task" list.
2. **`modules/NN-slug/test.yml`** — the actual behavioral contract. Every assertion is something your code must satisfy. Match exact string shapes (e.g., `python: X.Y.Z OK`).
3. **`modules/NN-slug/hints.md`** — three progressive levels. Level 3 is near-complete reference code; cross-check your design against it.
4. **`modules/NN-slug/fixtures/llm/*.json`** — the mock responses tests will play back. Your agent's request/response shape must work against these.
5. **`docs/architecture/mock-llm.md`** — fixture matching rules. Match on **conversation state**, never on call index.
6. **`docs/architecture/runner.md`** — the test types and full assertion vocabulary.

## Files you will typically touch

| Where | When |
|---|---|
| `pyproject.toml` | new dependency the module needs |
| `app/main.py` | virtually every early module touches this |
| `app/<new module>.py` | when adding a substantive new component (tools, streaming, etc.) |
| `agent` | almost never — leave the shell wrapper alone |
| `.env.example` | when adding a new env var students need |

You should not need to edit anything under `modules/`, `docs/`, `runner/`, `tools/`, `fixtures/`, `CURRICULUM.md`, `course-definition.yml`, or `CONTRIBUTING.md` when implementing a module — those are curriculum infrastructure.

## Validating without the runner

The runner (`nunuk-runner`) is not implemented yet (`runner/README.md` Status: "Not implemented"). Until it ships, **manually translate `test.yml` assertions into shell checks**:

- `exit_code: {equals: 0}` → run the command, `echo $?`.
- `stdout_contains: {text: "..."}` → `... | grep -q '...'`.
- `stderr_contains: {text: "..."}` → `... 2>&1 1>/dev/null | grep -q '...'`.
- `llm_call_count`, `tool_call_sequence` → spin up a tiny inline HTTP server that speaks OpenAI Chat Completions and counts requests. There is a working pattern for this in the module 01 implementation commit's message (search `git log --grep "inline HTTP mock"`).
- `no_network` → trust the mock; verify by setting `MOCK_LLM_BASE_URL=http://127.0.0.1:UNUSED_PORT` and ensuring the agent fails fast rather than hitting OpenRouter.

For modules that need a real `MOCK_LLM_FIXTURE`, you can write a ~30-line `http.server` shim that reads the fixture JSON and serves the first matching `responses[*]` entry. Don't build a real fixture engine — that's the runner's job; just unblock the smoke test.

## Coding conventions in this codebase

- **Python ≥3.12.** Pinned in `pyproject.toml`.
- **stdout = data, stderr = diagnostics.** The runner asserts separately on each. When a test asserts `stderr_contains: "X"`, use `print("...X...", file=sys.stderr); sys.exit(1)`, not a bare `raise SystemExit("X")` (it works but is less explicit).
- **Defensive `or ""` on `response.choices[0].message.content`.** `content` is legitimately `None` when the assistant returns only tool calls (module 05+). Cheap to handle now.
- **Read env at call time, not import time.** Tests use `env_overrides` per-test. Don't cache env in module-level globals.
- **`load_dotenv()` inside each public entry function** (`doctor()`, `chat()`, etc.) rather than at import. Same reason — keeps tests with non-default env honest.
- **No comments that explain *what* the code does.** Add a one-line comment only when the *why* is non-obvious (e.g., the `or ""` line might warrant one).
- **No new top-level helper modules until a module's instructions actually call for one.** Don't pre-factor.

## What not to do

- Do not edit `main` directly. Branch first.
- Do not delete a `module/NN-slug` branch after merge.
- Do not stage the pre-existing `readme.md → README.md` rename in your module commit — it predates module work.
- Do not stage the untracked curriculum bulk (CURRICULUM.md, docs/, modules/, etc.) — that is a separate phase-0 commit the owner will handle.
- Do not modify another module's `instructions.md`, `test.yml`, or fixtures to make your code pass. If a test seems wrong, surface it as a question; do not silently rewrite it.
- Do not skip the smoke test. "It type-checks" is not a green test.
- Do not introduce a new dependency without adding it to `pyproject.toml` and noting it in the commit message.
- Do not regenerate `CURRICULUM.md` unless `course-definition.yml` changed (it shouldn't, in a module implementation).

## When to ask vs proceed

Default to proceeding for routine decisions (variable names, where a helper lives, etc.). **Ask** before:

- Touching files outside the module's scope.
- Adding a new dependency.
- Designing around an ambiguous assertion in `test.yml`.
- Changing the merge style or branch naming.
- Anything that would force a rewrite of an already-merged module.

## Reference: completed modules

Look at the `module/NN-slug` branches and the merge commits on `main` for examples:

- `module/00-setup` — minimum-scaffold pattern: `pyproject.toml`, `agent`, `app/__init__.py`, `app/main.py`, `.env.example`, `.gitignore`.
- `module/01-first-llm-call` — single-file modification pattern: extend `app/main.py` to add a function + wire it into `main()`.

```bash
git log --graph --oneline main
git show <module-merge-commit>
git diff main^^..module/00-setup    # exact delta a module landed
```
