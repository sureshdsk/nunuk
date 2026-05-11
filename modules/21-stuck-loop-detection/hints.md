# Hints — Module 21 (Stuck-Loop Detection)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

The detector lives in `app/stuck.py` and is called from `app/agent.py` once per tool-call iteration. A `collections.deque(maxlen=N)` of `(tool_name, args_hash, noop)` triples is enough state. Hash the arguments with `json.dumps(args, sort_keys=True)` — comparing dicts directly is fragile.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
from collections import deque
from dataclasses import dataclass
from enum import Enum

class Verdict(str, Enum):
    OK = "ok"
    WARN = "warn"
    ABORT = "abort"

@dataclass
class _Call:
    name: str
    args_key: str
    noop: bool

class StuckDetector:
    def __init__(self, window: int = 6):
        self.recent: deque[_Call] = deque(maxlen=window)
        self.strikes = 0

    def record(self, name: str, args: dict, noop: bool) -> Verdict:
        key = json.dumps(args, sort_keys=True, default=str)
        self.recent.append(_Call(name, key, noop))
        if self._is_stuck():
            self.strikes += 1
            return Verdict.ABORT if self.strikes >= 2 else Verdict.WARN
        return Verdict.OK

    def _is_stuck(self) -> bool:
        # TODO: implement the three signals
        ...
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

```python
def _is_stuck(self) -> bool:
    if len(self.recent) >= 3:
        last3 = list(self.recent)[-3:]
        if all((c.name, c.args_key) == (last3[0].name, last3[0].args_key) for c in last3):
            return True
    if len(self.recent) >= 4:
        a, b, c, d = list(self.recent)[-4:]
        if (a.name, a.args_key) == (c.name, c.args_key) and \
           (b.name, b.args_key) == (d.name, d.args_key) and \
           (a.name, a.args_key) != (b.name, b.args_key):
            return True
    if len(self.recent) >= 4 and all(c.noop for c in list(self.recent)[-4:]):
        return True
    return False
```

The integration in `app/agent.py`:

```python
verdict = detector.record(call.name, call.arguments, noop=_is_noop(result))
if verdict is Verdict.WARN:
    messages.append({"role": "system", "content": STUCK_WARNING})
elif verdict is Verdict.ABORT:
    print("agent aborted: stuck loop detected", file=sys.stderr)
    sys.exit(2)
```

</details>
