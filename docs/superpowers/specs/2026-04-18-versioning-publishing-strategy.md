# Versioning & Publishing Strategy - Design Specification

**Date:** 2026-04-18
**Status:** Approved
**Goal:** Design optimal versioning strategy with manual bumps or GitHub Action automation, publish to Test PyPI only when version changes.

---

## Executive Summary

The current publishing workflow publishes to Test PyPI on every master commit, causing failures when the version hasn't changed (e.g., "File already exists" error).

This design introduces:
1. **Version Detection** — Only publishes to Test PyPI when `version` in `pyproject.toml` changes
2. **Manual Bumping** — Edit `pyproject.toml`, commit, auto-publish (patch bumps)
3. **Automated Bumping** — GitHub Action workflow with dropdown to choose major/minor/patch, auto-commit, auto-publish

Result: Clean, controlled versioning that prevents duplicate uploads while supporting both manual and automated workflows.

---

## Design

### 1. Version Detection in publish-test.yml

**Purpose:** Only run if version actually changed from previous commit

**Implementation:**
- Add step before publishing: Compare `version` from current commit vs previous commit
- Extract version from `pyproject.toml`: `grep "^version =" pyproject.toml`
- Compare with previous: `git show HEAD~1:pyproject.toml | grep "^version ="`
- If versions match: Skip publishing (exit 0, no error)
- If versions differ: Proceed with publishing

**Pseudo-code:**
```bash
CURRENT_VERSION=$(grep "^version =" pyproject.toml | cut -d'"' -f2)
PREV_VERSION=$(git show HEAD~1:pyproject.toml | grep "^version =" | cut -d'"' -f2)

if [ "$CURRENT_VERSION" = "$PREV_VERSION" ]; then
  echo "Version unchanged ($CURRENT_VERSION), skipping Test PyPI publish"
  exit 0
fi

# Continue with publish...
```

### 2. Manual Version Bumping

**Workflow:**
1. Developer edits `pyproject.toml`, changes `version = "0.0.10"` to `version = "0.0.11"`
2. Commits with message like `chore: bump version to 0.0.11`
3. Push to master
4. ci.yml runs all checks
5. ci.yml succeeds
6. publish-test.yml triggers, detects version change, publishes to Test PyPI

**No special workflow needed** — Just edit and commit.

### 3. GitHub Action: Automated Bumping

**Workflow File:** `.github/workflows/bump-version.yml`

**Trigger:** Manual dispatch (`workflow_dispatch`) with inputs

**Inputs:**
```yaml
bump_type:
  type: choice
  description: "Version bump type"
  options:
    - patch    # 0.0.10 → 0.0.11
    - minor    # 0.0.10 → 0.1.0
    - major    # 0.0.10 → 1.0.0
```

**Actions:**
1. Checkout code
2. Extract current version from `pyproject.toml`
3. Bump version based on selection (patch/minor/major)
4. Update `pyproject.toml` with new version
5. Commit with message: `chore: bump version to X.Y.Z`
6. Push to master
7. Workflow completes, ci.yml auto-triggers
8. ci.yml passes, publish-test.yml auto-triggers
9. publish-test.yml detects version change, publishes to Test PyPI

**Example:**
- Current: `version = "0.0.10"`
- User selects: `minor`
- Result: `version = "0.1.0"`
- Auto-committed and published

### 4. Release to Real PyPI

**Unchanged** — Still triggered by GitHub release published event

**Process:**
1. Create GitHub release (manual)
2. Tag must match version in `pyproject.toml` (e.g., `v0.1.0`)
3. publish.yml triggers, publishes to PyPI

### 5. Error Handling

**Version Detection Failures:**
- If `pyproject.toml` not found: Fail (indicates repo problem)
- If version extraction fails: Fail (indicates malformed toml)
- If git show fails: Fail (first commit? Use version detection with error handling)

**First Commit Special Case:**
- On first commit, `HEAD~1` doesn't exist
- Handle with: `if git rev-parse HEAD~1 >/dev/null 2>&1`
- If it fails (first commit), always publish (version is "new")

---

## Workflow Comparison

| Action | Method | Steps | Auto-Publish? |
|--------|--------|-------|---------------|
| Bump patch | Manual edit | Edit → commit → push | ✅ Yes (if version changed) |
| Bump minor | GitHub Action | Click → select minor → done | ✅ Yes (auto-commit) |
| Bump major | GitHub Action | Click → select major → done | ✅ Yes (auto-commit) |
| Release to PyPI | Manual release | Create GitHub release | ✅ Yes (on publish) |

---

## Version Scheme

**Format:** Semantic versioning (MAJOR.MINOR.PATCH)

**Current:** 0.0.10
**Examples:**
- Patch: 0.0.11, 0.0.12 (bug fixes, small improvements)
- Minor: 0.1.0, 0.2.0 (new features, backwards compatible)
- Major: 1.0.0, 2.0.0 (breaking changes)

---

## Files to Create/Modify

**Create:**
- `.github/workflows/bump-version.yml` — GitHub Action for automated version bumping

**Modify:**
- `.github/workflows/publish-test.yml` — Add version detection logic

**No changes:**
- `pyproject.toml` — Version stays, just updated by workflows
- `README.md` — Already documents publishing
- Other workflows — Unchanged

---

## Benefits

✅ **No duplicate uploads** — Prevents "File already exists" errors on Test PyPI
✅ **Flexible** — Manual OR automated bumping based on preference
✅ **Simple** — Manual is just edit + commit, automatic is one click
✅ **Safe** — GitHub Action auto-commits with clear message
✅ **Transparent** — Version changes are tracked in git history
✅ **Production-ready** — Works with both Test PyPI and real PyPI

---

## Testing Strategy

**Manual Bump:**
1. Edit `pyproject.toml` → `version = "0.0.11"`
2. Commit → ci.yml runs
3. Verify publish-test.yml publishes to Test PyPI
4. Check: https://test.pypi.org/project/ynab-import/

**GitHub Action:**
1. Go to Actions tab
2. Run "Bump Version" workflow
3. Select "patch"
4. Workflow auto-bumps, commits, publishes
5. Verify: Git log shows new commit, Test PyPI has new version

**Skip (Unchanged):**
1. Push without changing version
2. ci.yml runs
3. publish-test.yml detects no change, skips publishing
4. No error, no duplicate upload

---

## Success Criteria

- ✅ Version detection works (skips publish if no change)
- ✅ Manual bump triggers publish (edit → commit → publish)
- ✅ GitHub Action creates commit and auto-publishes
- ✅ Dropdown selection (major/minor/patch) works
- ✅ No duplicate Test PyPI uploads
- ✅ Real PyPI releases still work
- ✅ Git history clean (each version bump is a commit)

---

## Implementation Notes

**Version Detection Script:**
```bash
#!/bin/bash
set -e

CURRENT_VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

# Handle first commit (no HEAD~1)
if ! git rev-parse HEAD~1 >/dev/null 2>&1; then
  echo "First commit detected, publishing version: $CURRENT_VERSION"
  exit 0
fi

PREV_VERSION=$(git show HEAD~1:pyproject.toml 2>/dev/null | grep "^version = " | cut -d'"' -f2 || echo "")

if [ "$CURRENT_VERSION" = "$PREV_VERSION" ]; then
  echo "Version unchanged ($CURRENT_VERSION), skipping Test PyPI publish"
  exit 0
fi

echo "Version changed: $PREV_VERSION → $CURRENT_VERSION, proceeding with publish"
exit 1  # Non-zero tells workflow to continue (counterintuitive but clear in context)
```

**Bump Version Script (for GitHub Action):**
```bash
#!/bin/bash
set -e

CURRENT=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP_TYPE" in
  major) NEW="$((MAJOR+1)).0.0" ;;
  minor) NEW="$MAJOR.$((MINOR+1)).0" ;;
  patch) NEW="$MAJOR.$MINOR.$((PATCH+1))" ;;
esac

sed -i "s/^version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml
echo "Bumped: $CURRENT → $NEW"
```

---

## References

- Current publish-test.yml: `.github/workflows/publish-test.yml`
- Current publish.yml: `.github/workflows/publish.yml`
- pyproject.toml: Version field at top level
- GitHub Actions documentation: workflow_dispatch inputs
