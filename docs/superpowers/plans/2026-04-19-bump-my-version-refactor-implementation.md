# bump-my-version Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor version management to use bump-my-version internally while keeping shell scripts as the abstraction layer, eliminating sed compatibility issues and custom version arithmetic.

**Architecture:** Scripts (check-version-changed.sh, bump-version.sh) remain the GitHub Actions interface. bump-my-version handles version parsing, file updates, and auto-commits internally. Configuration-driven via .bumpversion.toml.

**Tech Stack:** bump-my-version Python package, shell scripts, .bumpversion.toml configuration, pyproject.toml (PEP 621)

---

## Task 1: Add bump-my-version to dev dependencies

**Files:**
- Modify: `pyproject.toml` (dependency groups)
- Modify: `uv.lock` (auto-generated)

- [ ] **Step 1: Add bump-my-version to dev dependencies**

```bash
cd /Users/demurnodia/playground/ynab-import-3
uv add --group dev bump-my-version>=0.21.0
```

Expected: Command succeeds, uv.lock is updated

- [ ] **Step 2: Verify dependency is present**

```bash
grep "bump-my-version" pyproject.toml
```

Expected: Line shows `bump-my-version>=0.21.0` in dev dependencies section

- [ ] **Step 3: Verify bump-my-version is available**

```bash
uv run bump-my-version --version
```

Expected: Output shows bump-my-version version (e.g., "0.21.0")

- [ ] **Step 4: Commit the dependency addition**

```bash
git add pyproject.toml uv.lock
git commit -m "deps: add bump-my-version for version management"
```

---

## Task 2: Create .bumpversion.toml configuration

**Files:**
- Create: `.bumpversion.toml` (root of repo)

- [ ] **Step 1: Create .bumpversion.toml with exact content**

Create file at `/Users/demurnodia/playground/ynab-import-3/.bumpversion.toml`:

```toml
[tool:bumpversion]
current_version = "0.0.12"
commit = true
tag = false
tag_name = "v{new_version}"

[[tool:bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'
```

- [ ] **Step 2: Verify file was created**

```bash
cat .bumpversion.toml | head -10
```

Expected: File shows [tool:bumpversion] section with current_version = "0.0.12"

- [ ] **Step 3: Verify current_version matches pyproject.toml**

```bash
TOML_VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
echo "pyproject.toml version: $TOML_VERSION"
grep "current_version = " .bumpversion.toml
```

Expected: Both show version "0.0.12"

- [ ] **Step 4: Commit the configuration file**

```bash
git add .bumpversion.toml
git commit -m "config: add bump-my-version configuration"
```

---

## Task 3: Refactor scripts/bump-version.sh to use bump-my-version

**Files:**
- Modify: `scripts/bump-version.sh`

- [ ] **Step 1: Read the current script**

```bash
cat scripts/bump-version.sh
```

Expected: Shows the old custom bash script with manual arithmetic

- [ ] **Step 2: Replace with new implementation using bump-my-version**

Replace the entire content of `scripts/bump-version.sh` with:

```bash
#!/bin/bash
set -e

BUMP_TYPE="${1:-patch}"

# Validate bump type
case "$BUMP_TYPE" in
  major|minor|patch)
    ;;
  *)
    echo "Invalid bump type: $BUMP_TYPE (must be major, minor, or patch)"
    exit 1
    ;;
esac

# Get current version before bump
CURRENT=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

# Run bump-my-version (auto-commits)
uv run bump-my-version bump "$BUMP_TYPE"

# Get new version after bump
NEW=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

echo "Bumped: $CURRENT → $NEW"
```

- [ ] **Step 3: Verify script is executable**

```bash
chmod +x scripts/bump-version.sh
ls -la scripts/bump-version.sh
```

Expected: File shows `-rwxr-xr-x` (executable)

- [ ] **Step 4: Test the script with patch bump (without committing)**

```bash
# Show current version
echo "Before bump:"
grep "^version = " pyproject.toml

# Test patch bump
bash scripts/bump-version.sh patch

# Show new version
echo "After bump:"
grep "^version = " pyproject.toml

# Verify git commit was created
git log --oneline -1

# Revert the change for cleanup
git reset --hard HEAD~1
```

Expected:
- Version increments from 0.0.12 to 0.0.13
- New commit is created with message from bump-my-version
- After reset, version is back to 0.0.12

- [ ] **Step 5: Test the script with minor bump (without committing)**

```bash
bash scripts/bump-version.sh minor
grep "^version = " pyproject.toml
git log --oneline -1
git reset --hard HEAD~1
```

Expected: Version increments from 0.0.12 to 0.1.0, commit created, then reverted

- [ ] **Step 6: Test the script with major bump (without committing)**

```bash
bash scripts/bump-version.sh major
grep "^version = " pyproject.toml
git log --oneline -1
git reset --hard HEAD~1
```

Expected: Version increments from 0.0.12 to 1.0.0, commit created, then reverted

- [ ] **Step 7: Test invalid bump type**

```bash
bash scripts/bump-version.sh invalid 2>&1 || true
```

Expected: Error message "Invalid bump type: invalid (must be major, minor, or patch)"

- [ ] **Step 8: Commit the refactored script**

```bash
git add scripts/bump-version.sh
git commit -m "refactor: use bump-my-version for version bumping"
```

---

## Task 4: Review and test scripts/check-version-changed.sh

**Files:**
- Review: `scripts/check-version-changed.sh` (no changes needed)

- [ ] **Step 1: Review the current detection script**

```bash
cat scripts/check-version-changed.sh
```

Expected: Script uses grep/cut to extract versions and compares them

- [ ] **Step 2: Verify script is executable**

```bash
ls -la scripts/check-version-changed.sh
```

Expected: Shows `-rwxr-xr-x` (executable)

- [ ] **Step 3: Test on current commit (should show version unchanged)**

```bash
bash scripts/check-version-changed.sh
echo "Exit code: $?"
```

Expected: Output shows "Version unchanged" message, exit code 1

- [ ] **Step 4: Create a test commit with version bump**

```bash
# Manually edit version for testing
sed -i '' 's/version = "0.0.12"/version = "0.0.13"/' pyproject.toml
git add pyproject.toml
git commit -m "test: bump version"

# Now test detection (should show version changed)
bash scripts/check-version-changed.sh
echo "Exit code: $?"

# Revert for cleanup
git reset --hard HEAD~1
```

Expected: Output shows "Version changed: 0.0.12 → 0.0.13", exit code 0

- [ ] **Step 5: Confirm no changes needed to detection script**

The script works correctly with grep-based extraction. No refactoring needed.

```bash
git status
```

Expected: No unstaged changes to scripts/check-version-changed.sh

---

## Task 5: Verify GitHub Actions workflows still work with refactored scripts

**Files:**
- Review: `.github/workflows/bump-version.yml` (no changes)
- Review: `.github/workflows/publish-test.yml` (no changes)

- [ ] **Step 1: Review bump-version.yml workflow**

```bash
grep -A 5 "bash scripts/bump-version.sh" .github/workflows/bump-version.yml
```

Expected: Workflow calls `bash scripts/bump-version.sh ${{ inputs.bump_type }}`

- [ ] **Step 2: Review publish-test.yml workflow**

```bash
grep -A 5 "bash scripts/check-version-changed.sh" .github/workflows/publish-test.yml
```

Expected: Workflow calls `bash scripts/check-version-changed.sh` with condition on publish step

- [ ] **Step 3: Verify no workflow changes are needed**

The workflows call scripts as black boxes. Since scripts maintain the same interface (same commands, same exit codes), no workflow changes are required.

```bash
# Confirm workflows are unchanged since last commit
git diff HEAD .github/workflows/
```

Expected: No output (no changes needed)

- [ ] **Step 4: Document what changed**

From GitHub Actions perspective:
- Scripts still called the same way
- Exit codes still the same (0 for publish/changed, 1 for skip/unchanged)
- Auto-commit now handled by bump-my-version instead of shell script
- Internal tool changed, but interface remains stable

---

## Task 6: Manual end-to-end verification

**Files:**
- No files changed in this task (verification only)

- [ ] **Step 1: Simulate manual version bump via script**

```bash
# Show current version
echo "Current version:"
grep "^version = " pyproject.toml

# Bump patch
bash scripts/bump-version.sh patch

# Verify file updated
echo "After patch bump:"
grep "^version = " pyproject.toml

# Verify commit created
git log --oneline -1

# Clean up for next test
git reset --hard HEAD~1
```

Expected: Version 0.0.12 → 0.0.13, commit created with bump-my-version message

- [ ] **Step 2: Verify version detection gates publishing correctly**

```bash
# Case 1: Version unchanged (should skip)
bash scripts/check-version-changed.sh
RESULT=$?
echo "Version unchanged exit code: $RESULT"
test $RESULT -eq 1 && echo "✓ Correctly returns exit 1 (skip publish)"

# Case 2: Create commit with version change
sed -i '' 's/version = "0.0.12"/version = "0.0.13"/' pyproject.toml
git add pyproject.toml
git commit -m "test: bump version"

bash scripts/check-version-changed.sh
RESULT=$?
echo "Version changed exit code: $RESULT"
test $RESULT -eq 0 && echo "✓ Correctly returns exit 0 (publish)"

# Clean up
git reset --hard HEAD~1
```

Expected:
- Unchanged version: exit 1
- Changed version: exit 0

- [ ] **Step 3: Verify all script tests pass**

```bash
# Run all script tests in quick succession
echo "=== Test 1: Patch bump ==="
bash scripts/bump-version.sh patch && git reset --hard HEAD~1

echo "=== Test 2: Minor bump ==="
bash scripts/bump-version.sh minor && git reset --hard HEAD~1

echo "=== Test 3: Major bump ==="
bash scripts/bump-version.sh major && git reset --hard HEAD~1

echo "=== Test 4: Version detection (no change) ==="
bash scripts/check-version-changed.sh || true

echo "=== All tests completed ==="
```

Expected: All operations complete successfully

---

## Success Criteria

- ✅ bump-my-version added to dev dependencies
- ✅ .bumpversion.toml created with correct configuration
- ✅ current_version in .bumpversion.toml matches pyproject.toml
- ✅ scripts/bump-version.sh refactored to use bump-my-version
- ✅ Version bumping works for major/minor/patch
- ✅ Auto-commit created by bump-my-version
- ✅ scripts/check-version-changed.sh unchanged and working
- ✅ Version detection correctly identifies changed/unchanged versions
- ✅ GitHub Actions workflows unchanged (scripts are black boxes)
- ✅ No sed compatibility issues (bump-my-version handles file updates)
- ✅ All manual tests pass
- ✅ All files committed to git
