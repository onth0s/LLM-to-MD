# Rich CLI Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace raw print statements with `rich` for colored, polished CLI output.

**Architecture:** Add `rich` as a dependency and use its `Console` for all user-facing output in `cli.py`. Errors get red styling, success messages get green, and markdown output prints as-is.

**Tech Stack:** Python, `rich`

---

### Task 1: Add `rich` dependency

**Files:**
- Modify: `pyproject.toml:10-12`

- [x] **Step 1: Add rich to dependencies**

```toml
dependencies = [
    "beautifulsoup4>=4.12",
    "rich>=13",
]
```

- [x] **Step 2: Install updated dependencies**

Run: `pip install -e .`
Expected: Successfully installed llmd (with rich)

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add rich dependency"
```

---

### Task 2: Update cli.py with rich output

**Files:**
- Modify: `llmd/cli.py:1-48`

- [x] **Step 1: Replace imports and add Console**

```python
import argparse
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from rich.console import Console

from .message import Message
from .parsers import get_parser

console = Console()
```

- [x] **Step 2: Replace error message**

```python
console.print(f"[red]Error:[/] input file not found: {args.input}")
```

- [x] **Step 3: Replace success message**

```python
console.print(f"[green]Done[/] — {len(messages)} messages written to {args.output}")
```

- [x] **Step 4: Replace output print**

```python
console.print(output)
```

- [x] **Step 5: Run verification**

Run: `llmd examples/grok/grok-conversation.html -p grok`
Expected: Colored "Done" message, markdown output displays correctly

Run: `llmd nonexistent.html -p grok`
Expected: Red "Error:" message

- [ ] **Step 6: Commit**

```bash
git add llmd/cli.py
git commit -m "feat: add rich colored output to CLI"
```
