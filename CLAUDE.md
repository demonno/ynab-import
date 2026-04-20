# YNAB Import - Development Guidelines

## What This Is

CLI tool for automating bank transaction imports to YNAB budgeting app. Reads CSV from 3 banks, transforms to common format, writes to YNAB API.

**Core modules:**
- `ynab_import/core/` — Domain models, transformers
- `ynab_import/infra/` — Bank readers, YNAB API client
- `ynab_import/runner/` — CLI (Typer)

## Before You Code

```bash
# Setup
make install

# Verify baseline
make test        # Should show: 2 passed, 1 skipped
make lint        # Should show: no issues
make check       # Should show: no type errors
```

## Code Standards

- **Format:** `make fmt` (ruff) before commit
- **Lint:** `make lint` (ruff) must pass
- **Type hints:** All functions require type hints, `make check` (mypy) must pass
- **Tests:** New features need tests in `tests/{module}/test_{file}.py`
- **Commits:** Frequent, focused. Format: `type(scope): description` (e.g., `feat(tbc): fix amount parsing`)

## Architecture

### Provider Pattern (for new bank support)

Each bank has:
1. `models.py` — CSV dataclass (fields from CSV)
2. `providers.py` — Reader class implementing `BaseProvider`
3. Optional: `transformers.py` — Convert to common `Transaction` model

### Data Flow
```
CSV → Provider.read() → [Transaction, ...] → YNAB API
```

### Key Files to Know

- `ynab_import/core/models.py` — Common `Transaction` model
- `ynab_import/infra/*/providers.py` — Bank readers (copy pattern for new banks)
- `tests/conftest.py` — Test fixtures
- `pyproject.toml` — Dependencies, tool configs
- `.pre-commit-config.yaml` — Auto-format hooks (see setup)

## Development Workflow

```bash
# Make changes
git checkout -b feature/your-feature

# Format, lint, test
make fmt
make lint
make test

# Commit frequently
git commit -m "feat(module): what you did"

# Before PR
make check  # Full type checking
```

## Known Issues

- Coverage: ~36%, goal is 80%+
- Test: 1 skipped (`test_base_transformer_amount`)

## For AI Assistants

See [AGENTS.md](AGENTS.md) for how to help with this project.
