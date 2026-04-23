# Fix broken core paths

**Date:** 2026-04-19
**Status:** Approved

## Problem

A project review surfaced several defects in the core import path. Four are in scope for this spec:

1. **Revolut provider is broken and unreachable.** `infra/revolut/providers.py` references fields (`.amount`, `.debit_credit`, `.payee`, `.date`) that do not exist on `RevolutTransaction`. The factory (`setup.py`) never wires it in, and `ReaderKind` has no `revolut_csv` entry. `pyproject.toml` excludes the whole directory from mypy. It is dead-and-broken code.
2. **`core/transformers.py` is dead code.** The `Transformer` abstract base is only subclassed by Revolut. With Revolut removed, it has no callers. Its utility methods duplicate those on `CSVReader` in `core/providers.py`.
3. **CLI `--config` option does nothing and the `import` command does nothing.**
   - `runner/cli.py:44` calls `Settings(config)` — passing a `Path` positionally to pydantic-settings. This raises `ValidationError` on every run; the handler prints the error and falls through, leaving `state["config"]` unset.
   - `@app.command(name="import")` decorates a function whose body only echoes. The actual working command is `read-write`.
4. **`import_id` collisions silently drop transactions.** `YnabAPIBasedRepository._to_ynab` builds `import_id = f"YNAB:{amount}:{date}"`. Two same-day same-amount transactions produce the same id, and YNAB's dedup drops one on import.

## Goals

- Delete dead/broken code so the codebase reflects reality.
- Make the CLI actually runnable (`Settings()` loads from env / `.env`; `import` command imports).
- Prevent same-day same-amount transactions from being silently deduplicated by YNAB.

## Non-goals

- Raising test coverage toward the 80% target.
- Dependency / security cleanup (Dependabot, `pydantic[dotenv]` warning).
- CI/release polish.
- Tooling config consolidation (`ruff.toml` vs `[tool.ruff]`, `.flake8`, `mypy.python_version` vs `requires-python`).

Each of these is a separate future spec.

## Architecture after changes

No new abstractions; the transform step (`Transaction` → `YnabTransaction`) stays in `YnabAPIBasedRepository` where it already lives.

```
CSV → CSVReader subclass (swedbank | tbc) → List[Transaction]
                                                 ↓
                                   YnabAPIBasedRepository.create_many
                                                 ↓
                                   _to_ynab (with counter) → YnabTransaction
                                                 ↓
                                         POST /transactions
```

## File-level changes

### Deletions

- `ynab_import/infra/revolut/__init__.py`
- `ynab_import/infra/revolut/models.py`
- `ynab_import/infra/revolut/providers.py`
- `ynab_import/infra/revolut/transformers.py`
- `ynab_import/core/transformers.py`

### `pyproject.toml`

Remove `"ynab_import/infra/revolut"` from `tool.mypy.exclude`.

### `ynab_import/runner/cli.py`

- Drop the `config: Path = typer.Option(...)` parameter on `main`.
- Drop the `try / except ValidationError` block. Replace with a direct call:
  ```python
  state["config"] = Settings()
  ```
  If env/`.env` is invalid, pydantic-settings raises and Typer surfaces a real error — better than the current half-initialized state.
- Rename the `import`-command function from `cli` to `run_import`. The Typer-level name stays `"import"`. Body mirrors `read_write`:
  ```python
  @app.command(name="import")
  def run_import() -> None:
      settings = state["config"]
      reader = create_reader(settings)
      writer = create_writer(settings)
      import_transactions(reader, writer)
  ```

### `ynab_import/infra/ynab.py`

Add a `Counter` field on `YnabAPIBasedRepository` and use it in `_to_ynab`:

```python
from collections import Counter
from dataclasses import asdict, dataclass, field

@dataclass
class YnabAPIBasedRepository:
    http_client: HttpClient[Response]
    budget_id: str
    account_id: str
    counter: Counter = field(default_factory=Counter)

    def _to_ynab(self, transaction: Transaction) -> YnabTransaction:
        iso_date = transaction.date.isoformat()
        key = (self.account_id, transaction.amount, iso_date)
        suffix = self.counter[key]
        self.counter[key] += 1
        import_id = f"YNAB:{transaction.amount}:{iso_date}:{suffix}"
        ...
```

### Verify (not expected to need changes)

- `ynab_import/infra/__init__.py` — confirm no Revolut re-exports; remove if present.
- `ynab_import/core/__init__.py` — confirm no `Transformer` re-export; remove if present.

## Kept unchanged

- `InMemoryBasedRepository` in `infra/ynab.py` — small, no cost to keep; useful when test coverage work lands.
- `CSVReader` base in `core/providers.py` — still used by swedbank and tbc.
- All existing commands (`check`, `read`, `read-write`, `import`) — only `import`'s body changes.

## Verification

### Manual smoke test

1. `make install` — clean sync.
2. `make lint` — passes; fix any unused-import warnings surfaced by deletions.
3. `make check` — mypy passes with Revolut exclude removed.
4. `make test` — 2 pass, 1 skipped, plus the new counter test below.
5. `uv run ynab-import --help` — `--config` is gone; four commands listed.
6. `uv run ynab-import check` — prints settings loaded from env / `.env`.
7. `uv run ynab-import read` — prints transactions given a valid swedbank/tbc CSV path.

### New unit test

`tests/infra/test_ynab.py::test_import_id_counter_suffixes_collisions`

- Build two `Transaction` objects with identical `(amount, date)`.
- Pass them through `YnabAPIBasedRepository.create_many` with a fake `HttpClient` that captures the posted JSON.
- Assert the posted transactions have `import_id` ending in `:0` and `:1` respectively.

### Rollback

All changes are local repo edits. `git revert` on the commit restores prior state.

## Risks

- **Removing the `ValidationError` swallow** changes behavior: users with an invalid `.env` will now see a traceback instead of a silent fallthrough. This is the intended fix — the silent fallthrough masked real config errors.
- **Counter reset semantics:** the counter resets per `YnabAPIBasedRepository` instance. The factory (`setup.py`) creates a fresh instance per CLI invocation, so import_ids are stable within a single import run and re-runs with the same input produce the same suffixes (which is what YNAB's dedup expects).
