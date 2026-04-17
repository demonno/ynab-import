# CI/CD Workflows Redesign - Design Specification

**Date:** 2026-04-17
**Status:** Approved
**Goal:** Modernize CI/CD to use uv + ruff, implement chained workflows for quality gates and automated publishing.

---

## Executive Summary

The ynab-import project currently has 5 GitHub Actions workflows with significant technical debt:
- 3 outdated workflows using Poetry, black, flake8, isort
- 2 new workflows using uv and ruff
- Duplicate testing logic
- No proper dependency caching or coverage tracking
- Outdated GitHub Actions versions (v2 → v4)

This redesign consolidates to **3 modern, focused workflows** with:
- Single quality gate (ci.yml) that blocks publishing
- Chained publishing workflows (no duplicate checks)
- Modern tooling (uv, ruff, mypy)
- Dependency caching for speed
- Coverage tracking and security scanning

---

## Design

### 1. Workflow Structure

**Three independent but chained workflows:**

#### ci.yml (Continuous Integration)
**Purpose:** Quality gate that must pass before any publishing
**Triggers:** Push to master, all PRs, manually
**Jobs:**
- `test` — Run pytest on Python 3.10-3.13 with coverage
- `lint` — Run ruff format check + ruff lint
- `type-check` — Run mypy
- `security` — Run pip-audit or safety check

**Key behavior:**
- Runs in parallel (all jobs at once)
- Fails fast (any job failure blocks downstream workflows)
- Caches pip/uv dependencies between runs
- Uploads coverage reports to codecov

#### publish-test.yml (Test PyPI Publishing)
**Purpose:** Publish to Test PyPI after quality checks pass
**Triggers:** `workflow_run` event when ci.yml succeeds on master branch commits
**Jobs:**
- `publish` — Build and publish to Test PyPI

**Key behavior:**
- **Only runs after ci.yml passes** (workflow_run trigger)
- Only runs on master branch (filtered by workflow_run)
- Uses PyPI token from GitHub secrets
- Tags release with commit SHA for traceability

#### publish.yml (Real PyPI Publishing)
**Purpose:** Publish to real PyPI on GitHub release
**Triggers:** `release` event (published action only)
**Jobs:**
- `publish` — Build and publish to PyPI

**Key behavior:**
- **Only runs after ci.yml passes on that commit** (implicit via GitHub release timing)
- Only on release published events
- Uses PyPI token from GitHub secrets
- Attaches build artifacts to release

### 2. Execution Flow

```
Developer pushes to master
        ↓
    ci.yml runs
    (test, lint, type-check, security all in parallel)
        ↓
    All checks pass?
        ├─ YES → publish-test.yml auto-triggers
        │        (builds, publishes to Test PyPI)
        │
        └─ NO → Stop (no publishing until fixed)

Developer creates GitHub release
        ↓
    (ci.yml must have passed on that commit)
        ↓
    publish.yml auto-triggers
        ↓
    Build & publish to real PyPI
```

### 3. Tool Stack

| Tool | Purpose | Status |
|------|---------|--------|
| uv | Package manager + build | Modern ✅ |
| ruff | Linting + formatting | Modern ✅ |
| mypy | Type checking | Modern ✅ |
| pytest | Testing | Current ✅ |
| pip-audit | Security scanning | New |

All workflows use:
- `actions/checkout@v4` (latest)
- `actions/setup-python@v4` (latest)
- `actions/upload-artifact@v4` (for coverage)

### 4. Configuration Details

#### ci.yml Configuration
```yaml
- Python versions: 3.10, 3.11, 3.12, 3.13
- Cache: pip dependencies (pip cache-dir)
- Coverage: Upload to codecov.io
- Timeouts: 10 minutes per job
- Continue on error: No (fail fast)
```

#### publish-test.yml Configuration
```yaml
- Trigger: workflow_run on ci.yml success + master branch
- Build: uv build (creates wheel + sdist)
- Publish: twine push to test.pypi.org
- Token: ${{ secrets.TEST_PYPI_API_KEY }}
- Retry: Yes (network resilience)
```

#### publish.yml Configuration
```yaml
- Trigger: GitHub release published
- Build: uv build (creates wheel + sdist)
- Publish: twine push to pypi.org
- Token: ${{ secrets.PYPI_API_KEY }}
- Artifacts: Attach .whl and .tar.gz to release
- Retry: Yes (network resilience)
```

### 5. Secrets Required

GitHub repository secrets needed:
- `TEST_PYPI_API_KEY` — Test PyPI token (from test.pypi.org)
- `PYPI_API_KEY` — Real PyPI token (from pypi.org)
- `CODECOV_TOKEN` — Codecov token (optional, for private repos)

### 6. Cleanup

**Delete (old/duplicate):**
- `.github/workflows/release.yml` (uses Poetry)
- `.github/workflows/pre_release.yml` (uses Poetry)
- `.github/workflows/test-suit.yml` (uses Poetry + old tools)
- `.github/workflows/test.yml` (duplicate of ci.yml logic)
- `.github/workflows/lint.yml` (separate, duplicate of ci.yml logic)

**Keep (new/correct):**
- `.github/workflows/ci.yml` (new, consolidated)
- `.github/workflows/publish-test.yml` (new)
- `.github/workflows/publish.yml` (new)

### 7. Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Testing | Outdated (v2 actions, Poetry) | Modern (v4, uv) |
| Publishing | Manual or broken (Poetry) | Automated (uv, chained) |
| Dependency caching | None | Yes (faster runs) |
| Coverage tracking | None | Yes (codecov) |
| Security scanning | Manual | Automated (pip-audit) |
| Python versions | 3.8-3.10 | 3.10-3.13 |
| Tool consistency | Mixed (isort/black/flake8) | Unified (ruff) |

---

## Quality Gates

All of these must pass before publishing:

1. **Tests:** `pytest tests/ -v --cov=ynab_import` — Coverage ≥ 38%
2. **Format:** `ruff format --check ynab_import tests` — No formatting violations
3. **Lint:** `ruff check ynab_import tests` — No style violations
4. **Type:** `mypy ynab_import` — No type errors
5. **Security:** `pip-audit` — No known vulnerabilities

Any failure stops the workflow and prevents publishing.

---

## Testing Strategy

**ci.yml tests on:**
- Python 3.10 (LTS)
- Python 3.11
- Python 3.12
- Python 3.13 (latest)

Matrix runs in parallel for fast feedback.

---

## Release Process

### For Test PyPI
```
1. Push code to master
2. CI checks run automatically
3. If all pass → Test PyPI publishes automatically
4. Verify in test.pypi.org/project/ynab-import/
5. Anyone can test: pip install -i https://test.pypi.org/simple/ ynab-import==0.0.11
```

### For Real PyPI
```
1. Create GitHub release (with tag matching version)
2. GitHub release publishes
3. publish.yml triggers automatically
4. Builds wheel + sdist with uv
5. Publishes to pypi.org
6. Available immediately: pip install ynab-import==0.0.11
```

---

## Implementation Tasks

1. Create ci.yml with all quality checks
2. Create publish-test.yml for Test PyPI
3. Create publish.yml for real PyPI
4. Delete old workflows (5 files)
5. Update pyproject.toml build-backend if needed (should be hatchling)
6. Test workflows locally or with dry-run
7. Configure GitHub secrets
8. Test publishing to Test PyPI manually
9. Document release process in README

---

## Success Criteria

- ✅ All old workflows deleted
- ✅ ci.yml runs on all commits/PRs, all checks pass
- ✅ publish-test.yml triggers on master commits, publishes to Test PyPI
- ✅ publish.yml triggers on releases, publishes to real PyPI
- ✅ Coverage reports uploaded and tracked
- ✅ No manual intervention needed for publishing
- ✅ All GitHub Actions v4 (latest)
- ✅ Secrets configured and working

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Publishing wrong version | GitHub release is manual step; tag must match pyproject.toml |
| Token leaked in logs | Never print secrets; use GitHub's masked logs |
| Test PyPI fills up | Cleanup old test versions manually or via PyPI UI |
| Publishing fails | Retry logic in workflow; manual fallback with `uv publish` |
| Python 3.10 drops support | Update matrix in ci.yml yearly |

---

## References

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [PyPI publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-to-pypi/)
- [uv documentation](https://docs.astral.sh/uv/)
- [ruff documentation](https://docs.astral.sh/ruff/)
