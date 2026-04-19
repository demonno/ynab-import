# Fix Broken Core Paths — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dead/broken Revolut and Transformer code, fix the CLI so `Settings()` actually loads and the `import` command performs the import, and prevent silent YNAB dedup by making `import_id` unique for same-day same-amount transactions.

**Architecture:** Pure cleanup and bug-fix work. No new abstractions. One `Counter` field added to `YnabAPIBasedRepository`; everything else is deletion or signature simplification.

**Tech Stack:** Python 3.9+, Typer (CLI), pydantic-settings (config), pytest (tests), uv (package manager), ruff (lint/format), mypy (types).

Spec: `docs/superpowers/specs/2026-04-19-fix-broken-core-paths-design.md`

---

## File map

**Delete:**
- `ynab_import/infra/revolut/__init__.py`
- `ynab_import/infra/revolut/models.py`
- `ynab_import/infra/revolut/providers.py`
- `ynab_import/infra/revolut/transformers.py`
- `ynab_import/core/transformers.py`
- `tests/common/test_transformers.py` (imports the dead `Transformer`; only test in `tests/common/` — skipped)

**Modify:**
- `pyproject.toml` — remove Revolut from `tool.mypy.exclude`
- `ynab_import/runner/cli.py` — drop `--config`, fix `import` command body
- `ynab_import/infra/ynab.py` — add `Counter` field, use it in `_to_ynab`

**Create:**
- `tests/infra/__init__.py`
- `tests/infra/test_ynab.py` — counter test

---

## Task 1: Baseline verification

Confirm we start from a clean, known-good state so any regressions we introduce are visible.

**Files:** none modified.

- [ ] **Step 1: Verify working tree is clean**

Run:
```bash
git status
```
Expected: `nothing to commit, working tree clean`.

- [ ] **Step 2: Run the existing test suite**

Run:
```bash
make test
```
Expected: `2 passed, 1 skipped`. Coverage around 38%. Note the current pass/skip counts — regressions after our changes would show up as changes here.

- [ ] **Step 3: Run lint**

Run:
```bash
make lint
```
Expected: no issues reported.

- [ ] **Step 4: Run type check**

Run:
```bash
make check
```
Expected: no errors.

No commit for this task — it's a read-only baseline.

---

## Task 2: Delete the Revolut module

Delete all Revolut code and remove the now-unnecessary mypy exclude entry. Nothing in the codebase imports these files, so deletion is safe.

**Files:**
- Delete: `ynab_import/infra/revolut/__init__.py`
- Delete: `ynab_import/infra/revolut/models.py`
- Delete: `ynab_import/infra/revolut/providers.py`
- Delete: `ynab_import/infra/revolut/transformers.py`
- Modify: `pyproject.toml` (line ~80 — the `tool.mypy.exclude` array)

- [ ] **Step 1: Confirm nothing outside `infra/revolut/` references Revolut**

Run:
```bash
grep -rn "revolut\|Revolut" ynab_import/ tests/ --include="*.py" | grep -v "^ynab_import/infra/revolut/"
```
Expected: no output. If output appears, stop and investigate before deleting.

- [ ] **Step 2: Delete the Revolut directory**

Run:
```bash
rm -r ynab_import/infra/revolut
```

- [ ] **Step 3: Remove `ynab_import/infra/revolut` from mypy exclude**

Edit `pyproject.toml`. The current line (at line 79) is:

```toml
exclude = ["ynab_import/infra/revolut", "ynab_import/infra/http.py", "ynab_import/infra/ynab.py", "ynab_import/runner/cli.py", "ynab_import/setup.py"]
```

Change to:

```toml
exclude = ["ynab_import/infra/http.py", "ynab_import/infra/ynab.py", "ynab_import/runner/cli.py", "ynab_import/setup.py"]
```

Only remove the `"ynab_import/infra/revolut"` entry; leave the rest untouched. Verify with `grep -n 'exclude' pyproject.toml` — the first match on line 79 is the one to edit (the second match around line 89 is `exclude_lines` for coverage, unrelated).

- [ ] **Step 4: Run lint, type check, tests**

Run:
```bash
make lint && make check && make test
```
Expected: all pass; test counts unchanged (2 passed, 1 skipped).

- [ ] **Step 5: Commit**

```bash
git add -A ynab_import/infra/revolut pyproject.toml
git commit -m "refactor: remove dead Revolut provider module

The Revolut reader and transformer referenced fields that did not exist
on the CSV model and were never wired into the factory. Removing them
also drops the mypy exclude that was masking the broken signatures."
```

---

## Task 3: Delete the dead `Transformer` abstraction

The `Transformer` abstract base in `core/transformers.py` was only subclassed by Revolut. After Task 2 it has no subclasses. Its skipped unit test in `tests/common/test_transformers.py` goes with it.

**Files:**
- Delete: `ynab_import/core/transformers.py`
- Delete: `tests/common/test_transformers.py`
- Delete: `tests/common/__init__.py` (empty, no other tests in the dir)

- [ ] **Step 1: Confirm no references remain outside the files being deleted**

Run:
```bash
grep -rn "from ynab_import.core.transformers\|core\.transformers\|import Transformer" ynab_import/ tests/ --include="*.py"
```
Expected output is limited to the two files we're about to delete:
```
ynab_import/core/transformers.py: ...
tests/common/test_transformers.py: ...
```
If anything else appears, stop and investigate.

- [ ] **Step 2: Delete the files**

Run:
```bash
rm ynab_import/core/transformers.py
rm tests/common/test_transformers.py
rm tests/common/__init__.py
rmdir tests/common
```

- [ ] **Step 3: Confirm `core/__init__.py` does not re-export `Transformer`**

Run:
```bash
cat ynab_import/core/__init__.py
```
Expected: only `import_transactions` is exported. No change needed — just verify.

- [ ] **Step 4: Run lint, type check, tests**

Run:
```bash
make lint && make check && make test
```
Expected: `2 passed, 0 skipped` (the skipped test is now deleted). Lint and mypy pass.

- [ ] **Step 5: Commit**

```bash
git add -A ynab_import/core/transformers.py tests/common
git commit -m "refactor: remove dead Transformer abstract base

The Transformer class had no callers after the Revolut removal. Its
utility methods duplicate CSVReader's. Deletes the only (skipped) test
that exercised it."
```

---

## Task 4: Add the `import_id` collision counter (TDD)

YNAB's API deduplicates transactions by `import_id`. The current `_to_ynab` builds the id from `amount` and `date` only, so two same-day same-amount transactions (common case: paying a flat fee twice on the same day) share an id and one is silently dropped. Fix by maintaining a `Counter` keyed on `(account_id, amount, iso_date)` that appends `:0`, `:1`, `:2`, … as collisions occur.

**Files:**
- Create: `tests/infra/__init__.py` (empty)
- Create: `tests/infra/test_ynab.py`
- Modify: `ynab_import/infra/ynab.py`

- [ ] **Step 1: Create the test package**

Run:
```bash
mkdir -p tests/infra
touch tests/infra/__init__.py
```

- [ ] **Step 2: Write the failing counter test**

Create `tests/infra/test_ynab.py` with:

```python
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock

from ynab_import.core.interactions import Transaction
from ynab_import.infra.ynab import YnabAPIBasedRepository


class FakeHttpClient:
    def __init__(self) -> None:
        self.posted_bodies: List[Dict[str, Any]] = []

    def post(self, endpoint: str, *, json: Dict[str, Any]):
        self.posted_bodies.append(json)
        response = MagicMock()
        response.json.return_value = {}
        response.status_code = 200
        return response


def test_import_id_counter_suffixes_collisions():
    client = FakeHttpClient()
    repo = YnabAPIBasedRepository(
        http_client=client,
        budget_id="budget-1",
        account_id="account-1",
    )

    same_day = datetime(2026, 4, 19)
    transactions = [
        Transaction(date=same_day, amount=-1500, payee_name="Coffee", description="a"),
        Transaction(date=same_day, amount=-1500, payee_name="Coffee", description="b"),
        Transaction(date=same_day, amount=-2000, payee_name="Lunch", description="c"),
    ]

    repo.create_many(transactions)

    assert len(client.posted_bodies) == 1
    sent = client.posted_bodies[0]["transactions"]
    assert [t["import_id"] for t in sent] == [
        "YNAB:-1500:2026-04-19T00:00:00:0",
        "YNAB:-1500:2026-04-19T00:00:00:1",
        "YNAB:-2000:2026-04-19T00:00:00:0",
    ]
```

- [ ] **Step 3: Run the test to verify it fails**

Run:
```bash
uv run pytest tests/infra/test_ynab.py -v
```
Expected: FAIL. The current `_to_ynab` emits ids like `YNAB:-1500:2026-04-19T00:00:00` (no `:N` suffix), so the assertion on the full list will fail on the first element.

- [ ] **Step 4: Implement the counter in `YnabAPIBasedRepository`**

Edit `ynab_import/infra/ynab.py`. The current file starts with:

```python
from dataclasses import asdict, dataclass
from pprint import pprint
from typing import List

from requests import Response

from ynab_import.core.interactions import Transaction
from ynab_import.core.models import YnabTransaction
from ynab_import.infra.http import HttpClient


@dataclass
class YnabAPIBasedRepository:
    http_client: HttpClient[Response]
    budget_id: str
    account_id: str

    def create_many(self, transactions: List[Transaction]) -> int:
        ynab_transactions = [asdict(self._to_ynab(t)) for t in transactions]
        ...

    def _to_ynab(self, transaction: Transaction) -> YnabTransaction:
        import_id = f"YNAB:{transaction.amount}:{transaction.date.isoformat()}"
        ...
```

Change the imports and the class header to:

```python
from collections import Counter
from dataclasses import asdict, dataclass, field
from pprint import pprint
from typing import List

from requests import Response

from ynab_import.core.interactions import Transaction
from ynab_import.core.models import YnabTransaction
from ynab_import.infra.http import HttpClient


@dataclass
class YnabAPIBasedRepository:
    http_client: HttpClient[Response]
    budget_id: str
    account_id: str
    counter: Counter = field(default_factory=Counter)
```

And change `_to_ynab` so it uses the counter:

```python
    def _to_ynab(self, transaction: Transaction) -> YnabTransaction:
        iso_date = transaction.date.isoformat()
        key = (self.account_id, transaction.amount, iso_date)
        suffix = self.counter[key]
        self.counter[key] += 1
        import_id = f"YNAB:{transaction.amount}:{iso_date}:{suffix}"

        return YnabTransaction(
            account_id=self.account_id,
            date=iso_date,
            amount=str(transaction.amount),
            payee_name=transaction.payee_name,
            memo=transaction.description,
            cleared="cleared",
            approved=False,
            flag_color="red",
            import_id=import_id,
        )
```

Leave the `create_many` body unchanged — it already calls `self._to_ynab(t)` in order per transaction, which is exactly what the counter relies on.

- [ ] **Step 5: Run the test to verify it passes**

Run:
```bash
uv run pytest tests/infra/test_ynab.py -v
```
Expected: PASS.

- [ ] **Step 6: Run full checks**

Run:
```bash
make lint && make check && make test
```
Expected: lint and mypy pass; tests show `3 passed` (2 original + 1 new), `0 skipped`.

- [ ] **Step 7: Commit**

```bash
git add ynab_import/infra/ynab.py tests/infra
git commit -m "fix(ynab): make import_id unique for same-day same-amount txns

YNAB deduplicates by import_id. With only amount and date in the id,
two identical-amount same-day transactions collide and one is silently
dropped on import. Adds a per-repository Counter keyed on
(account_id, amount, iso_date) that appends :N to the id."
```

---

## Task 5: Clean up the CLI

Two changes:
1. Remove the `--config` Typer option. `Settings()` reads env / `.env` directly via pydantic-settings; the `--config` path argument was being passed positionally and raising `ValidationError` on every invocation. The existing error handler printed the error and fell through, leaving `state["config"]` unset.
2. Fix the `import` command so its body actually runs the import (currently just echoes a log line). Rename the Python-level function from `cli` to `run_import` to remove the name collision with `app`; keep Typer-level name `"import"`.

**Files:**
- Modify: `ynab_import/runner/cli.py`

- [ ] **Step 1: Replace `cli.py` with the corrected version**

Overwrite `ynab_import/runner/cli.py` with:

```python
from pprint import pprint
from typing import Optional

import typer

from ynab_import import __version__
from ynab_import.core import import_transactions
from ynab_import.settings import Settings
from ynab_import.setup import create_reader, create_writer

app = typer.Typer(name="Ynab Import CLI")
state: dict = {"verbose": False}


def version_callback(value: bool):
    if value:
        typer.echo(f"CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = False,
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback),
):
    """
    CLI for managing read/transform/import operations
    """
    if verbose:
        state["verbose"] = True
    state["config"] = Settings()


@app.command()
def check():
    """
    Print config to be used for importing
    """
    settings = state["config"]
    pprint(settings.dict())


@app.command()
def read() -> None:
    """
    Read transactions from a specified source and print in STD out
    """
    settings = state["config"]
    typer.echo(f"Reading transactions with config {settings.dict()}")
    typer.echo("Transactions loaded from reader")

    reader = create_reader(settings)
    typer.echo(reader.read_transactions())


@app.command()
def read_write() -> None:
    """
    Read transactions from a specified source and write to a specified destination
    """
    settings = state["config"]
    typer.echo("Importing transactions")

    reader = create_reader(settings)
    writer = create_writer(settings)

    import_transactions(reader, writer)


@app.command(name="import")
def run_import() -> None:
    """
    Read/Import transactions from source to destination
    """
    settings = state["config"]
    typer.echo(f"Import transactions with config {settings.dict()}")

    reader = create_reader(settings)
    writer = create_writer(settings)

    import_transactions(reader, writer)
```

Key diffs from the original:
- Removed `Path`, `ValidationError` imports (no longer needed).
- Removed `config: Path = typer.Option(...)` parameter from `main`.
- Removed the `try / except ValidationError` block.
- Renamed the `import`-command function from `cli` to `run_import`.
- `run_import` body now mirrors `read_write`.
- Fixed typo `conifg` → `config` in both `read` and `run_import` echo strings.
- Added type annotation `state: dict` to satisfy ruff/mypy.

- [ ] **Step 2: Verify `--help` output**

Run:
```bash
uv run ynab-import --help
```
Expected: no `--config` option; commands listed: `check`, `read`, `read-write`, `import`. No error during help invocation (previously `--help` might have worked but real commands would not).

- [ ] **Step 3: Run lint, type check, tests**

Run:
```bash
make lint && make check && make test
```
Expected: all pass; test counts unchanged (3 passed after Task 4).

- [ ] **Step 4: Commit**

```bash
git add ynab_import/runner/cli.py
git commit -m "fix(cli): drop broken --config flag and wire up import command

Settings() already loads from env / .env via pydantic-settings; the
--config Path option was passed positionally to Settings and raised
ValidationError on every run. The handler swallowed the error and
continued, so downstream commands crashed on an unset state['config'].

The 'import' command now calls import_transactions, matching
read-write. Renamed the Python-level function from cli to run_import
to avoid the collision with the Typer app variable."
```

---

## Task 6: Final verification

Smoke-test the full CLI and confirm everything is green.

**Files:** none modified.

- [ ] **Step 1: Clean sync**

Run:
```bash
make install
```
Expected: no errors. The `pydantic[dotenv]` warning from uv may still appear — it is not addressed by this spec.

- [ ] **Step 2: Full checks**

Run:
```bash
make lint && make check && make test
```
Expected: lint passes, mypy passes (no more Revolut exclude), tests show `3 passed, 0 skipped`.

- [ ] **Step 3: CLI smoke — `--help`**

Run:
```bash
uv run ynab-import --help
```
Expected: four commands listed (`check`, `read`, `read-write`, `import`); no `--config` option.

- [ ] **Step 4: CLI smoke — `check`**

Run:
```bash
uv run ynab-import check
```
Expected: prints the loaded `Settings` dict from `.env`. (If `.env` is invalid or missing required fields, pydantic-settings now raises a real error — this is the intended fix, and is still a "pass" for verification purposes: you should see a clear error, not a silent fallthrough.)

- [ ] **Step 5: Confirm git state**

Run:
```bash
git log --oneline -6
git status
```
Expected:
- Four new commits (one per Task 2, 3, 4, 5) on top of the spec commit.
- Working tree clean.

- [ ] **Step 6: Push**

Run:
```bash
git push origin master
```
Expected: push succeeds; CI workflow runs; publish-test workflow chains off it (per the project's existing CI setup).

No commit for this task — it is pure verification.

---

## Self-review notes

- **Spec coverage:**
  - Spec §Deletions → Tasks 2, 3.
  - Spec §`pyproject.toml` mypy exclude → Task 2 Step 3.
  - Spec §`runner/cli.py` (drop `--config`, fix `import`) → Task 5.
  - Spec §`infra/ynab.py` counter → Task 4.
  - Spec §Verify (no re-exports) → Task 3 Step 3 (core) and Task 2 Step 1 (confirms no external Revolut refs; `infra/__init__.py` was checked during planning and contains no Revolut symbols, so no edit needed).
  - Spec §Kept unchanged (`InMemoryBasedRepository`, `CSVReader`, command surface) → no tasks touch them.
  - Spec §Manual smoke test → Task 6.
  - Spec §New unit test → Task 4.
- **Placeholder scan:** none remaining.
- **Type consistency:** `Counter` field name and key tuple `(account_id, amount, iso_date)` used consistently between plan body and test assertions. `run_import` (Python function) vs `"import"` (Typer command name) distinction noted.
