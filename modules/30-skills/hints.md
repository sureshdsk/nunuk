# Hints — Module 30 (Skills)

Three levels. Try for 30 minutes between peeks.

<details>
<summary><strong>Level 1 — a nudge</strong></summary>

Frontmatter parsing: split on `\n---\n` and use `yaml.safe_load` on the middle section. The tool registry already has a way to add new tools at runtime — Module 28's project-memory loader uses the same hook. Look at `app/tools/__init__.py::register_tool`.

</details>

<details>
<summary><strong>Level 2 — partial code</strong></summary>

```python
# app/skills.py
import re, yaml
from dataclasses import dataclass
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)\Z", re.DOTALL)

@dataclass
class Skill:
    name: str
    description: str
    tools: list[str]
    triggers: list[str]
    body: str
    path: Path

def discover_skills(root: Path) -> list[Skill]:
    skills = []
    for p in sorted(root.glob("*/SKILL.md")):
        m = FRONTMATTER_RE.match(p.read_text())
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        skills.append(Skill(
            name=meta["name"],
            description=meta.get("description", ""),
            tools=list(meta.get("tools", [])),
            triggers=list(meta.get("triggers", [])),
            body=m.group(2),
            path=p,
        ))
    return skills
```

</details>

<details>
<summary><strong>Level 3 — near-complete</strong></summary>

Wiring (`app/agent.py`):

```python
def handle_skill_call(skill: Skill, prompt: str, messages: list[dict]) -> str:
    # 1. Append skill body so the model has the playbook.
    messages.append({"role": "system",
                     "content": f"--- skill: {skill.name} ---\n{skill.body}"})
    # 2. Filter tool palette for this sub-loop.
    allowed = set(skill.tools) | {f"skill_{skill.name}"}
    with restricted_tools(allowed):
        result = inner_loop(prompt, messages)
    return result

def restricted_tools(allowed: set[str]) -> ContextManager:
    """Context manager that temporarily filters the tool registry."""
    ...
```

</details>
