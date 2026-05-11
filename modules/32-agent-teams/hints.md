# Hints — Module 32 (Agent Teams)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

Atomic claim is the only hard part. Wrap a dict + a `threading.Lock` and you're 90% there. Don't over-engineer with `asyncio` if Module 31's subagent ran synchronously — keep the concurrency model consistent. The timeout is just `time.monotonic()` plus a budget.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
# app/team.py
import threading, time, uuid
from dataclasses import dataclass

@dataclass
class _TodoItem:
    id: str
    description: str
    worker: str | None = None
    result: str | None = None

class SharedTodoList:
    def __init__(self):
        self._lock = threading.Lock()
        self._items: dict[str, _TodoItem] = {}

    def add(self, description: str) -> str:
        tid = uuid.uuid4().hex[:8]
        with self._lock:
            self._items[tid] = _TodoItem(tid, description)
        return tid

    def claim(self, worker_id: str) -> tuple[str, str] | None:
        with self._lock:
            for item in self._items.values():
                if item.worker is None and item.result is None:
                    item.worker = worker_id
                    return item.id, item.description
        return None

    def complete(self, tid: str, result: str) -> None:
        with self._lock:
            self._items[tid].result = result

    def drained(self) -> bool:
        with self._lock:
            return all(it.result is not None for it in self._items.values())
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

```python
def run_team(parent_messages, seed_todos: list[str], n_workers: int = 2):
    n_workers = min(n_workers, 5)
    todos = SharedTodoList()
    bus = MessageBus()
    for t in seed_todos:
        todos.add(t)
    threads = []
    for i in range(n_workers):
        wid = f"w{i}"
        t = threading.Thread(target=_worker, args=(wid, todos, bus), daemon=True)
        t.start()
        threads.append(t)
    deadline = time.monotonic() + int(os.environ.get("TEAM_DRAIN_TIMEOUT_S", "60"))
    while not todos.drained() and time.monotonic() < deadline:
        time.sleep(0.05)
    if not todos.drained():
        sys.stderr.write("team timed out before draining\n")
        sys.exit(3)
    return bus.drain()
```

</details>
