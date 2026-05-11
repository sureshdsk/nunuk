# Hints — Module 00 (Setup)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

The doctor function lives in `app/main.py`. It runs four independent checks and tracks whether any failed. The checks themselves don't share state — each is a small block that prints one line.

For the API key check: `dotenv.load_dotenv()` reads `.env` into `os.environ`. Call it before checking.

For uv: `shutil.which("uv")` returns the path or `None`.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
import shutil
import sys
import os
import subprocess
from dotenv import load_dotenv

def doctor() -> int:
    load_dotenv()
    failed = 0

    # Python check
    py = sys.version_info
    if (py.major, py.minor) >= (3, 12):
        print(f"python: {py.major}.{py.minor}.{py.micro} OK")
    else:
        print(f"python: {py.major}.{py.minor} FAIL (need >=3.12)")
        failed += 1

    # TODO: uv check (use shutil.which; if found, run `uv --version` to get the version)
    # TODO: OPENROUTER_API_KEY check
    # TODO: MODEL check (default to anthropic/claude-haiku-4.5)

    if failed == 0:
        print("OK")
        return 0
    return 1
```

Wire `doctor()` into the `--doctor` branch of your argparse handler in `main()`.

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

```python
def doctor() -> int:
    load_dotenv()
    failed = 0

    py = sys.version_info
    if (py.major, py.minor) >= (3, 12):
        print(f"python: {py.major}.{py.minor}.{py.micro} OK")
    else:
        print(f"python: {py.major}.{py.minor} FAIL (need >=3.12)")
        failed += 1

    uv_path = shutil.which("uv")
    if uv_path:
        ver = subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip()
        print(f"uv: {ver} OK")
    else:
        print("uv: missing FAIL")
        failed += 1

    if os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY: set OK")
    else:
        print("OPENROUTER_API_KEY: missing FAIL")
        failed += 1

    model = os.environ.get("MODEL", "anthropic/claude-haiku-4.5")
    print(f"MODEL: {model}")

    if failed == 0:
        print("OK")
        return 0
    return 1
```

The remaining gap: how do you wire this into `main()` so `--doctor` calls it and propagates the exit code? (Hint: `sys.exit(doctor())`.)

</details>
