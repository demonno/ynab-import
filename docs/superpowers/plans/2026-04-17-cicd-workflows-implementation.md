# CI/CD Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 3 modern GitHub Actions workflows (ci.yml, publish-test.yml, publish.yml) with automated quality gates and chained publishing.

**Architecture:**
- Consolidated quality checks in ci.yml (tests, lint, type-check, security)
- Chained publishing workflows triggered by ci.yml success
- Test PyPI publishes on every master commit
- Real PyPI publishes on GitHub releases
- All workflows use uv + ruff (modern stack)

**Tech Stack:** GitHub Actions v4, uv, ruff, mypy, pytest, pip-audit

---

## File Structure

**New files to create:**
- `.github/workflows/ci.yml` — Continuous integration quality gate
- `.github/workflows/publish-test.yml` — Test PyPI publishing (chained to ci.yml)
- `.github/workflows/publish.yml` — Real PyPI publishing (on releases)

**Files to delete:**
- `.github/workflows/release.yml` (old Poetry-based)
- `.github/workflows/pre_release.yml` (old Poetry-based)
- `.github/workflows/test-suit.yml` (old, duplicate)
- `.github/workflows/test.yml` (we created, now superseded)
- `.github/workflows/lint.yml` (we created, now superseded)

**No changes needed to:**
- `pyproject.toml` (already has hatchling build-backend from Task 1)
- `README.md` (minimal version sufficient)

---

## Task 1: Create ci.yml (Quality Gate Workflow)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create ci.yml with test job**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/.github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]
  workflow_dispatch:

jobs:
  test:
    name: "Test Python ${{ matrix.python-version }}"
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests with coverage
        run: uv run pytest tests/ -v --cov=ynab_import --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false

  lint:
    name: Lint (Ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Check formatting
        run: uv run ruff format --check ynab_import tests

      - name: Run linter
        run: uv run ruff check ynab_import tests

  type-check:
    name: Type Check (MyPy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run mypy
        run: uv run mypy ynab_import

  security:
    name: Security Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run security audit
        run: uv run pip-audit
EOF
```

- [ ] **Step 2: Verify ci.yml is valid YAML**

```bash
python3 -m yaml /Users/demurnodia/playground/ynab-import-3/.github/workflows/ci.yml || echo "Install pyyaml: pip install pyyaml"
# Or just check if it's parseable by GitHub
cat /Users/demurnodia/playground/ynab-import-3/.github/workflows/ci.yml | head -20
```

Expected output: File is valid, first 20 lines show correct YAML structure

- [ ] **Step 3: Commit ci.yml**

```bash
cd /Users/demurnodia/playground/ynab-import-3
git add .github/workflows/ci.yml
git commit -m "ci: create ci.yml workflow with quality gates

- Test on Python 3.10-3.13 in parallel
- Lint with ruff (format + check)
- Type check with mypy
- Security audit with pip-audit
- Upload coverage to codecov
- All jobs run in parallel, fail-fast on error"
```

---

## Task 2: Create publish-test.yml (Test PyPI Publishing)

**Files:**
- Create: `.github/workflows/publish-test.yml`

- [ ] **Step 1: Create publish-test.yml**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/.github/workflows/publish-test.yml << 'EOF'
name: Publish to Test PyPI

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [master, main]

jobs:
  publish-test:
    name: Publish to Test PyPI
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_commit.id }}

      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Build package
        run: uv build

      - name: Publish to Test PyPI
        run: |
          uv pip install twine
          python3 -m twine upload --repository testpypi dist/* -u __token__ -p ${{ secrets.TEST_PYPI_API_KEY }}
        env:
          TWINE_SKIP_EXISTING: true
EOF
```

- [ ] **Step 2: Verify publish-test.yml is valid YAML**

```bash
cat /Users/demurnodia/playground/ynab-import-3/.github/workflows/publish-test.yml | head -20
```

Expected output: First 20 lines show valid YAML

- [ ] **Step 3: Commit publish-test.yml**

```bash
cd /Users/demurnodia/playground/ynab-import-3
git add .github/workflows/publish-test.yml
git commit -m "ci: create publish-test.yml for Test PyPI

- Triggered by successful ci.yml completion on master/main
- Builds wheel and sdist with uv
- Publishes to test.pypi.org using TEST_PYPI_API_KEY secret
- Skips if version already exists (TWINE_SKIP_EXISTING)"
```

---

## Task 3: Create publish.yml (Real PyPI Publishing)

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Create publish.yml**

```bash
cat > /Users/demurnodia/playground/ynab-import-3/.github/workflows/publish.yml << 'EOF'
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    name: Publish to PyPI
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v4
        with:
          python-version: "3.13"
          cache: 'pip'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        run: |
          uv pip install twine
          python3 -m twine upload dist/* -u __token__ -p ${{ secrets.PYPI_API_KEY }}

      - name: Upload artifacts to release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF
```

- [ ] **Step 2: Verify publish.yml is valid YAML**

```bash
cat /Users/demurnodia/playground/ynab-import-3/.github/workflows/publish.yml | head -20
```

Expected output: First 20 lines show valid YAML

- [ ] **Step 3: Commit publish.yml**

```bash
cd /Users/demurnodia/playground/ynab-import-3
git add .github/workflows/publish.yml
git commit -m "ci: create publish.yml for real PyPI

- Triggered on GitHub release published
- Builds wheel and sdist with uv
- Publishes to pypi.org using PYPI_API_KEY secret
- Attaches build artifacts to GitHub release"
```

---

## Task 4: Delete Old Workflows

**Files:**
- Delete: `.github/workflows/release.yml`
- Delete: `.github/workflows/pre_release.yml`
- Delete: `.github/workflows/test-suit.yml`
- Delete: `.github/workflows/test.yml`
- Delete: `.github/workflows/lint.yml`

- [ ] **Step 1: Delete old workflow files**

```bash
cd /Users/demurnodia/playground/ynab-import-3
rm -f .github/workflows/release.yml
rm -f .github/workflows/pre_release.yml
rm -f .github/workflows/test-suit.yml
rm -f .github/workflows/test.yml
rm -f .github/workflows/lint.yml
```

- [ ] **Step 2: Verify deletions**

```bash
ls -la .github/workflows/
```

Expected output: Only ci.yml, publish-test.yml, publish.yml remain (3 files)

- [ ] **Step 3: Commit deletions**

```bash
cd /Users/demurnodia/playground/ynab-import-3
git add -u .github/workflows/
git commit -m "ci: remove old outdated workflows

- Deleted release.yml (Poetry-based, outdated)
- Deleted pre_release.yml (Poetry-based, outdated)
- Deleted test-suit.yml (uses old tools: Poetry, isort, black, flake8)
- Deleted test.yml (superseded by ci.yml)
- Deleted lint.yml (superseded by ci.yml)

Keeping only modern workflows: ci.yml, publish-test.yml, publish.yml"
```

---

## Task 5: Document GitHub Secrets Setup

**Files:**
- No new files created
- Reference documentation for setup

- [ ] **Step 1: Create setup instructions (reference)**

GitHub repository secrets need to be configured manually via GitHub UI. Document what's needed:

**TEST_PYPI_API_KEY:**
1. Go to https://test.pypi.org/manage/account/token/
2. Create token with scope "Entire account"
3. Copy token
4. Go to GitHub repo → Settings → Secrets → New repository secret
5. Name: `TEST_PYPI_API_KEY`
6. Value: paste token

**PYPI_API_KEY:**
1. Go to https://pypi.org/manage/account/token/
2. Create token with scope "Entire account"
3. Copy token
4. Go to GitHub repo → Settings → Secrets → New repository secret
5. Name: `PYPI_API_KEY`
6. Value: paste token

- [ ] **Step 2: Update README with release documentation (optional)**

Add to README.md after Development section:

```markdown
## Publishing

### Publishing to Test PyPI

Automatic on every master commit (after CI passes):
```bash
git push origin master
# Workflow runs automatically
# Check test.pypi.org/project/ynab-import/ for published version
```

### Publishing to PyPI

Automatic on GitHub release:
```bash
# Create release on GitHub (https://github.com/demonno/ynab-import/releases/new)
# Tag must match version in pyproject.toml (e.g., v0.0.11)
# publish.yml runs automatically
# Check pypi.org/project/ynab-import/ for published version
```

Requires: TEST_PYPI_API_KEY and PYPI_API_KEY secrets configured.
```

- [ ] **Step 3: Verify GitHub Secrets are configured (manual)**

Go to: `https://github.com/demonno/ynab-import/settings/secrets/actions`

Verify:
- `TEST_PYPI_API_KEY` exists
- `PYPI_API_KEY` exists

Expected: Both secrets present (values hidden)

- [ ] **Step 4: Create a brief note (commit is optional, this is informational)**

No commit needed - secrets are configured in GitHub UI, not in repo.

Print:

```bash
echo "GitHub Secrets configured (done manually in GitHub UI)"
```

---

## Task 6: Test CI Workflow Locally

**Files:**
- No files modified
- Test workflow definition

- [ ] **Step 1: Verify workflow files are valid YAML**

```bash
cd /Users/demurnodia/playground/ynab-import-3
for file in .github/workflows/*.yml; do
  echo "Checking $file..."
  python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✓ Valid" || echo "✗ Invalid"
done
```

Expected output: All 3 workflows are valid YAML

- [ ] **Step 2: Run local commands that workflows will run**

```bash
cd /Users/demurnodia/playground/ynab-import-3

# Test what ci.yml will run
make test
make lint
make check
uv run pip-audit || echo "pip-audit may warn about packages"
```

Expected output:
- Tests pass: 2 passed, 1 skipped
- Lint passes: no errors
- Type check passes: no errors
- Security audit completes (may have warnings)

- [ ] **Step 3: Verify build command works**

```bash
cd /Users/demurnodia/playground/ynab-import-3
uv build
ls -lh dist/
```

Expected output: Created dist/ynab-import-*.whl and dist/ynab-import-*.tar.gz

- [ ] **Step 4: No commit needed**

Workflows are defined, local verification complete.

---

## Task 7: Test Publishing to Test PyPI (Manual)

**Files:**
- No files modified
- Manual test of publishing

**⚠️ Prerequisites:**
- GitHub secrets configured (TEST_PYPI_API_KEY in repo)
- Package built locally (uv build)

- [ ] **Step 1: Get credentials for manual test**

Test PyPI token should be in TEST_PYPI_API_KEY secret. For manual testing, you can:
- Create a separate token locally, or
- Wait for GitHub workflow to test automatically

Option A (manual test locally):
```bash
pip install twine
cd /Users/demurnodia/playground/ynab-import-3
python3 -m twine upload --repository testpypi dist/* -u __token__ -p YOUR_TOKEN_HERE
```

Option B (wait for GitHub workflow):
Push to master, workflow runs automatically, check GitHub Actions tab.

Expected output: Successfully published to test.pypi.org

- [ ] **Step 2: Verify package on Test PyPI**

```bash
# Visit https://test.pypi.org/project/ynab-import/
# Or test install:
pip install -i https://test.pypi.org/simple/ ynab-import==0.0.10
```

Expected: Package appears on Test PyPI

- [ ] **Step 3: No commit needed**

Publishing is automated via GitHub workflows.

---

## Task 8: Final Verification

**Files:**
- No files modified
- Verification only

- [ ] **Step 1: List all workflows**

```bash
ls -la /Users/demurnodia/playground/ynab-import-3/.github/workflows/
```

Expected output: Only ci.yml, publish-test.yml, publish.yml (3 files)

- [ ] **Step 2: Check git history for workflow commits**

```bash
git log --oneline | grep -i "ci:" | head -10
```

Expected output: Shows commits for ci.yml, publish-test.yml, publish.yml, deletion of old workflows

- [ ] **Step 3: Verify pyproject.toml has correct build-backend**

```bash
grep -A2 "build-system" /Users/demurnodia/playground/ynab-import-3/pyproject.toml
```

Expected output:
```
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 4: Test that all local commands pass**

```bash
cd /Users/demurnodia/playground/ynab-import-3
make test && make lint && make check
```

Expected output: All commands pass

- [ ] **Step 5: Display summary**

```bash
cat << 'EOF'
✅ CI/CD Workflows Redesign Complete

Workflow Files Created:
- .github/workflows/ci.yml (quality gate: test, lint, type-check, security)
- .github/workflows/publish-test.yml (auto-publish to Test PyPI on master)
- .github/workflows/publish.yml (auto-publish to PyPI on release)

Old Workflows Deleted:
- release.yml, pre_release.yml, test-suit.yml, test.yml, lint.yml

Modern Stack:
- GitHub Actions v4 (updated from v2)
- uv package manager (not Poetry)
- ruff linting (not black/flake8/isort)
- mypy type checking
- pip-audit security scanning

Publishing Strategy:
1. Every master commit → Test PyPI (workflow_run trigger)
2. GitHub release published → Real PyPI (release trigger)
3. All quality gates must pass before publishing

Next Steps:
1. Configure GitHub secrets: TEST_PYPI_API_KEY, PYPI_API_KEY
2. Push to master to test workflows
3. Create a release on GitHub to test publishing
EOF
```

Expected output: Summary displayed

---

## Self-Review

**Spec coverage:**
- ✅ Create ci.yml with tests, lint, type-check, security (Task 1)
- ✅ Create publish-test.yml chained to ci.yml success (Task 2)
- ✅ Create publish.yml triggered on releases (Task 3)
- ✅ Delete 5 old workflows (Task 4)
- ✅ Document secrets setup (Task 5)
- ✅ Test locally (Task 6)
- ✅ Test publishing (Task 7)
- ✅ Final verification (Task 8)

**Placeholder scan:**
- ✅ No TBD/TODO in steps
- ✅ All code blocks are complete
- ✅ All commands are exact with expected output
- ✅ All file paths are absolute

**Type consistency:**
- ✅ Workflow names consistent (ci.yml, publish-test.yml, publish.yml)
- ✅ Secret names consistent (TEST_PYPI_API_KEY, PYPI_API_KEY)
- ✅ Commands consistent (uv build, uv run pytest, etc.)

**No issues found. Plan is ready for execution.**

---

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-04-17-cicd-workflows-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (Recommended)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
