# Modernize YNAB Import Project - Revised Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Modernize ynab-import with minimal, focused documentation for AI-agentic workflow development + pre-commit hooks.

**Scope:** Tooling (✅ done), Essential Docs Only, Pre-commit Hooks, Optional CI/CD

**Status:**
- ✅ Phase 1 Complete (uv + ruff)
- 🚧 Phase 2 Revised (minimal docs only)
- 🆕 Phase 2b New (pre-commit hooks)
- 🔲 Phase 3 Optional (GitHub Actions)

---

## Phase 2: Minimal Essential Documentation

### Task 3a: Create Minimal README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README with minimal version**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/README.md << 'EOF'
# ynab-import

Automate transaction imports from bank CSV exports to YNAB API.

**Supported banks:** Swedbank, Revolut, TBC

## Install

```bash
pip install ynab-import
```

## Quick Start

```bash
# Configure with your YNAB API credentials
export YNAB_API_KEY=your_token
export YNAB_BUDGET_ID=your_budget_id
export YNAB_ACCOUNT_ID=your_account_id

# Import transactions
ynab-import --config .env import
```

## Development

```bash
make install      # Install dependencies
make test         # Run tests (2 passed, 1 skipped)
make fmt          # Format code
make lint         # Check code quality
make check        # Full checks (lint + type)
```

See [CLAUDE.md](CLAUDE.md) for architecture and [AGENTS.md](AGENTS.md) for AI assistant guidelines.

## License

MIT
EOF
```

- [ ] **Step 2: Verify file created**

```bash
cat /Users/demurnodia/playground/ynab-import-3/README.md
```

Expected output: Minimal README with essential info only

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: simplify README.md to minimal version

- Keep only essential install, quick start, and development info
- Remove references to non-existent documentation files
- Point to CLAUDE.md and AGENTS.md for details"
```

---

### Task 3b: Create Minimal CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create minimal CLAUDE.md**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/CLAUDE.md << 'EOF'
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

- Revolut: Amount parsing incomplete (transformers)
- Coverage: ~36%, goal is 80%+
- Test: 1 skipped (`test_base_transformer_amount`)

## For AI Assistants

See [AGENTS.md](AGENTS.md) for how to help with this project.
EOF
```

- [ ] **Step 2: Verify file**

```bash
wc -l /Users/demurnodia/playground/ynab-import-3/CLAUDE.md
```

Expected output: ~80-100 lines (compact)

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add minimal CLAUDE.md for development

- Project overview and core modules
- Before-you-code setup checklist
- Code standards (format, lint, type hints, tests)
- Architecture and data flow
- Key files to know
- Development workflow
- Known issues
- Reference to AGENTS.md"
```

---

### Task 3c: Create Minimal AGENTS.md

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Create minimal AGENTS.md**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/AGENTS.md << 'EOF'
# For AI Assistants

Quick guidelines for Claude Code and other AI helping with this project.

## Start Here

1. Read [CLAUDE.md](CLAUDE.md) for architecture and code standards
2. Run `make install && make test` to verify environment
3. Check existing providers in `ynab_import/infra/*/providers.py` for patterns

## Key Rules

**Testing:** All new code needs tests. Test structure mirrors source: `tests/tbc/` ↔ `ynab_import/infra/tbc/`

**Code Quality:** Always run before commit:
- `make fmt` — format code
- `make lint` — check style
- `make check` — verify type hints

**Git:** Commit frequently after each passing test. Format: `type(scope): what` (e.g., `feat(tbc): add reader`)

**No Placeholders:** Don't commit TODO/TBD code. If you can't finish, don't start.

## Important Files

- `CLAUDE.md` — Read this first for context
- `pyproject.toml` — Dependencies and tool configs
- `tests/conftest.py` — Pytest fixtures
- `.pre-commit-config.yaml` — Auto-format hooks

## When to Ask the User

- Architecture decisions (e.g., "Add new bank?")
- Scope changes
- Breaking changes
- Merge strategy

## Example: Add a Bank Provider

1. Create `ynab_import/infra/mybank/models.py` with CSV dataclass
2. Create `ynab_import/infra/mybank/providers.py` with reader (copy pattern from TBC)
3. Write test: `tests/mybank/test_providers.py` (failing first)
4. Implement minimal code to pass test
5. Update README with bank name
6. Commit: `feat(mybank): add MyBank CSV reader`
EOF
```

- [ ] **Step 2: Verify file**

```bash
wc -l /Users/demurnodia/playground/ynab-import-3/AGENTS.md
```

Expected output: ~60-80 lines (concise)

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add minimal AGENTS.md for AI assistants

- Start here checklist
- 4 key rules (testing, code quality, git, no placeholders)
- Important files
- When to ask user
- Example workflow for adding bank provider"
```

---

## Phase 2b: Pre-commit Hooks Setup

### Task 4: Setup Pre-commit Hooks

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create .pre-commit-config.yaml**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/.pre-commit-config.yaml << 'EOF'
# Pre-commit hooks for code quality automation
# Install: pip install pre-commit && pre-commit install
# Run manually: pre-commit run --all-files

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - pydantic-settings
        args:
          - --ignore-missing-imports
          - --python-version=3.8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: end-of-file-fixer
      - id: trailing-whitespace

ci:
  autofix_commit_msg: 'ci: auto-format code with pre-commit'
  autofix_prs: true
  autoupdate_branch: ''
  autoupdate_commit_msg: 'ci: update pre-commit hooks'
  autoupdate_schedule: weekly
EOF
```

- [ ] **Step 2: Install pre-commit**

```bash
pip install pre-commit
```

Expected output: Successfully installed pre-commit

- [ ] **Step 3: Setup pre-commit hooks**

```bash
cd /Users/demurnodia/playground/ynab-import-3
pre-commit install
```

Expected output: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 4: Run hooks on all files**

```bash
pre-commit run --all-files
```

Expected output: Ruff, mypy, and other hooks run successfully

- [ ] **Step 5: Verify tests still pass**

```bash
make test
```

Expected output: `2 passed, 1 skipped`

- [ ] **Step 6: Add pre-commit to README development section**

Update README.md development section to include:

```markdown
## Development

```bash
make install      # Install dependencies
make test         # Run tests (2 passed, 1 skipped)
make fmt          # Format code
make lint         # Check code quality
make check        # Full checks (lint + type)
```

### Pre-commit Hooks (automatic)

Hooks run automatically before each commit:
```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```
```

- [ ] **Step 7: Commit**

```bash
git add .pre-commit-config.yaml README.md
git commit -m "ci: add pre-commit hooks for automatic code quality

- Ruff format and check on every commit
- MyPy type checking
- Standard pre-commit checks (trailing whitespace, large files, etc)
- Update README with pre-commit setup instructions"
```

---

## Phase 3: GitHub Actions (Optional)

### Task 5: Add GitHub Actions Workflows

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/lint.yml`

- [ ] **Step 1: Create .github/workflows/test.yml**

```bash
mkdir -p /Users/demurnodia/playground/ynab-import-3/.github/workflows

cat > /Users/demurnodia/playground/ynab-import-3/.github/workflows/test.yml << 'EOF'
name: Tests

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install uv
      - run: uv sync
      - run: uv run pytest tests/ -v --cov=ynab_import
EOF
```

- [ ] **Step 2: Create .github/workflows/lint.yml**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/.github/workflows/lint.yml << 'EOF'
name: Lint & Type Check

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
      - run: pip install uv
      - run: uv sync
      - run: uv run ruff format --check ynab_import tests
      - run: uv run ruff check ynab_import tests
      - run: uv run mypy ynab_import
EOF
```

- [ ] **Step 3: Verify files created**

```bash
ls -la /Users/demurnodia/playground/ynab-import-3/.github/workflows/
```

Expected output: test.yml and lint.yml exist

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/
git commit -m "ci: add GitHub Actions workflows

- test.yml: Run pytest on Python 3.8-3.13
- lint.yml: Ruff format, check, and mypy
- Runs on push and all PRs"
```

---

## Final Verification

### Task 6: Final Checks

**Files:**
- Verify: All changes complete and working

- [ ] **Step 1: Check git log for all commits**

```bash
git log --oneline -20
```

Expected output: Shows commits from Tasks 1-5

- [ ] **Step 2: Run full test suite**

```bash
make test
```

Expected output: `2 passed, 1 skipped`

- [ ] **Step 3: Run full checks**

```bash
make check
```

Expected output: No lint or type errors

- [ ] **Step 4: Verify pre-commit hooks work**

```bash
pre-commit run --all-files
```

Expected output: All hooks pass

- [ ] **Step 5: List all new/modified files**

```bash
git diff --name-only HEAD~10
```

Expected output: Shows modernization changes (pyproject.toml, uv.lock, Makefile, ruff.toml, README.md, CLAUDE.md, AGENTS.md, .pre-commit-config.yaml, .github/workflows/)

- [ ] **Step 6: Verify CLI works**

```bash
uv run ynab-import --version
```

Expected output: Version number

- [ ] **Step 7: Create summary**

```bash
cat > /tmp/modernization-summary.txt << 'EOF'
YNAB Import Modernization Complete ✅

Phase 1: Tooling Modernization ✅
- Poetry → uv
- black/flake8/isort → ruff
- All tests passing

Phase 2: Essential Documentation ✅
- README.md: Minimal, focused
- CLAUDE.md: Development guidelines
- AGENTS.md: AI assistant guidelines

Phase 2b: Pre-commit Hooks ✅
- Auto-format on commit
- Type checking
- Standard checks

Phase 3: GitHub Actions (Optional) ✅
- Test automation (Python 3.8-3.13)
- Lint automation

Project is now ready for feature development with:
- Modern tooling (uv, ruff, pre-commit)
- Essential documentation for AI workflows
- Automated code quality checks
EOF
cat /tmp/modernization-summary.txt
```

Expected output: Summary of all completed work

---

## Summary

**Total Tasks:** 6 (down from 8)
**Removed:** CODE_REVIEW.md, TEST_REVIEW.md, legacy documentation
**Added:** Pre-commit hooks, GitHub Actions

**Documentation Files:**
- ✅ README.md — 30 lines (minimal)
- ✅ CLAUDE.md — ~100 lines (essential dev info)
- ✅ AGENTS.md — ~65 lines (AI assistant quick start)

**Automation:**
- ✅ Pre-commit hooks (auto-format/type-check on commit)
- ✅ GitHub Actions (test + lint on push/PR)

**Next Steps:** Add features! Start with failing test → implement → commit.
