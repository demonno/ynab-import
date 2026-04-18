# Versioning & Publishing Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement automated version detection and semantic version bumping with GitHub Actions, enabling conditional Test PyPI publishing and manual/automated version management.

**Architecture:** Two shell scripts handle version logic (detection, bumping), one new GitHub Actions workflow provides dropdown-based manual bumping, and one existing workflow integrates version detection to gate publishing.

**Tech Stack:** Bash scripting, GitHub Actions (workflow_dispatch), semantic versioning (MAJOR.MINOR.PATCH), pyproject.toml (PEP 621)

---

## File Structure

**Create:**
- `scripts/check-version-changed.sh` — Version detection script, exit code gates publishing
- `scripts/bump-version.sh` — Semantic version bumping script
- `.github/workflows/bump-version.yml` — Manual version bumping workflow with dropdown

**Modify:**
- `.github/workflows/publish-test.yml` — Integrate version detection step

---

## Task 1: Create version detection script

**Files:**
- Create: `scripts/check-version-changed.sh`

- [ ] **Step 1: Create scripts directory and file**

```bash
mkdir -p scripts
touch scripts/check-version-changed.sh
chmod +x scripts/check-version-changed.sh
```

- [ ] **Step 2: Write the version detection script**

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
  exit 1
fi

echo "Version changed: $PREV_VERSION → $CURRENT_VERSION, proceeding with publish"
exit 0
```

- [ ] **Step 3: Verify script is executable**

```bash
ls -la scripts/check-version-changed.sh
```

Expected: File shows executable bit (-rwxr-xr-x)

- [ ] **Step 4: Test the script locally**

```bash
cd /Users/demurnodia/playground/ynab-import-3
bash scripts/check-version-changed.sh
```

Expected: Script runs without error, outputs version message

- [ ] **Step 5: Commit the script**

```bash
git add scripts/check-version-changed.sh
git commit -m "feat: add version change detection script"
```

---

## Task 2: Create version bumping script

**Files:**
- Create: `scripts/bump-version.sh`

- [ ] **Step 1: Write the version bumping script**

```bash
#!/bin/bash
set -e

BUMP_TYPE="${1:-patch}"
CURRENT=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP_TYPE" in
  major) NEW="$((MAJOR+1)).0.0" ;;
  minor) NEW="$MAJOR.$((MINOR+1)).0" ;;
  patch) NEW="$MAJOR.$MINOR.$((PATCH+1))" ;;
  *) echo "Invalid bump type: $BUMP_TYPE"; exit 1 ;;
esac

sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml
echo "Bumped: $CURRENT → $NEW"
```

- [ ] **Step 2: Make script executable**

```bash
chmod +x scripts/bump-version.sh
```

- [ ] **Step 3: Test the script with patch bump**

```bash
# First, check current version
grep "^version = " pyproject.toml

# Run the script (don't commit yet, just test)
bash scripts/bump-version.sh patch

# Verify the change
grep "^version = " pyproject.toml

# Revert for real testing in workflow
git checkout pyproject.toml
```

Expected: Version incremented for PATCH component only

- [ ] **Step 4: Test the script with minor bump**

```bash
bash scripts/bump-version.sh minor
grep "^version = " pyproject.toml
git checkout pyproject.toml
```

Expected: Version incremented for MINOR component, PATCH reset to 0

- [ ] **Step 5: Test the script with major bump**

```bash
bash scripts/bump-version.sh major
grep "^version = " pyproject.toml
git checkout pyproject.toml
```

Expected: Version incremented for MAJOR component, MINOR and PATCH reset to 0

- [ ] **Step 6: Commit the script**

```bash
git add scripts/bump-version.sh
git commit -m "feat: add semantic version bumping script"
```

---

## Task 3: Create automated version bumping workflow

**Files:**
- Create: `.github/workflows/bump-version.yml`

- [ ] **Step 1: Write the bump-version workflow**

```yaml
name: Bump Version

on:
  workflow_dispatch:
    inputs:
      bump_type:
        type: choice
        description: "Version bump type"
        options:
          - patch
          - minor
          - major
        required: true

jobs:
  bump:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure git
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"

      - name: Extract current version
        id: current
        run: |
          VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Bump version
        run: bash scripts/bump-version.sh ${{ inputs.bump_type }}

      - name: Extract new version
        id: new
        run: |
          VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Commit and push
        run: |
          git add pyproject.toml
          git commit -m "chore: bump version to ${{ steps.new.outputs.version }}"
          git push origin master

      - name: Summary
        run: |
          echo "Version bumped: ${{ steps.current.outputs.version }} → ${{ steps.new.outputs.version }}"
          echo "Commit pushed to master"
          echo "ci.yml will auto-trigger, followed by publish-test.yml if checks pass"
```

- [ ] **Step 2: Verify workflow syntax**

```bash
# Check the file exists and is valid YAML
cat .github/workflows/bump-version.yml | head -20
```

Expected: Valid YAML structure, workflow_dispatch trigger visible

- [ ] **Step 3: Commit the workflow**

```bash
git add .github/workflows/bump-version.yml
git commit -m "feat: add GitHub Actions workflow for automated version bumping"
```

---

## Task 4: Integrate version detection in publish-test workflow

**Files:**
- Modify: `.github/workflows/publish-test.yml`

- [ ] **Step 1: Read the current publish-test workflow**

```bash
cat .github/workflows/publish-test.yml
```

Expected: Current workflow with publish step

- [ ] **Step 2: Add version detection step before publish**

Locate the publish step (looks like `- name: Publish to Test PyPI` or similar).

Insert this step BEFORE the publish step:

```yaml
      - name: Check if version changed
        id: version
        run: bash scripts/check-version-changed.sh
        continue-on-error: true
```

Then modify the publish step to add a condition:

```yaml
      - name: Publish to Test PyPI
        if: steps.version.outcome == 'success'
        run: uv run twine upload --repository testpypi dist/* --verbose
```

The complete modified section should look like:

```yaml
      - name: Check if version changed
        id: version
        run: bash scripts/check-version-changed.sh
        continue-on-error: true

      - name: Publish to Test PyPI
        if: steps.version.outcome == 'success'
        run: uv run twine upload --repository testpypi dist/* --verbose
```

- [ ] **Step 3: Verify the workflow is valid YAML**

```bash
cat .github/workflows/publish-test.yml | grep -A 10 "Check if version changed"
```

Expected: Both steps present, condition on publish step

- [ ] **Step 4: Commit the workflow modification**

```bash
git add .github/workflows/publish-test.yml
git commit -m "feat: add version detection gate to Test PyPI publishing"
```

---

## Task 5: Test the versioning strategy - manual version bump

**Files:**
- Modify: `pyproject.toml` (temporary, for testing)

- [ ] **Step 1: Manually bump version in pyproject.toml**

Edit `pyproject.toml` and change the version line. Current version is 0.0.11. Change to 0.0.12:

```toml
version = "0.0.12"
```

- [ ] **Step 2: Commit the version bump**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.0.12"
```

- [ ] **Step 3: Verify ci.yml will trigger**

```bash
# Check recent commits
git log --oneline -3
```

Expected: New commit on master with version bump message

- [ ] **Step 4: Verify publish-test.yml would detect the change**

```bash
# Simulate the version check script
bash scripts/check-version-changed.sh
```

Expected: Output "Version changed: 0.0.11 → 0.0.12" and exit code 0

- [ ] **Step 5: Push to remote and monitor GitHub Actions**

```bash
git push origin master
```

Then visit: https://github.com/demonno/ynab-import/actions

Expected: ci.yml runs, then publish-test.yml auto-triggers and publishes to Test PyPI (no "File already exists" error)

---

## Task 6: Test the versioning strategy - no version change skip

**Files:**
- No file changes (testing skip logic)

- [ ] **Step 1: Push a non-version-changing commit**

```bash
# Make a minor code change (add a comment, whitespace, etc.)
echo "# Test commit without version bump" >> README.md
git add README.md
git commit -m "docs: add test comment"
git push origin master
```

- [ ] **Step 2: Verify version detection skips publish**

```bash
# Simulate the version check (should fail because version unchanged)
bash scripts/check-version-changed.sh
echo "Exit code: $?"
```

Expected: Output "Version unchanged" and exit code 1

- [ ] **Step 3: Monitor GitHub Actions**

Visit: https://github.com/demonno/ynab-import/actions

Expected: ci.yml runs, publish-test.yml auto-triggers, version check exits with code 1, publish step skipped (does not attempt upload)

- [ ] **Step 4: Revert the test commit**

```bash
git revert HEAD --no-edit
git push origin master
```

---

## Task 7: Test the versioning strategy - GitHub Action workflow dispatch

**Files:**
- No files created/modified (testing the existing bump-version.yml)

- [ ] **Step 1: Navigate to GitHub Actions**

Visit: https://github.com/demonno/ynab-import/actions

- [ ] **Step 2: Find the "Bump Version" workflow**

Search for `.github/workflows/bump-version.yml` or "Bump Version" in the actions list

- [ ] **Step 3: Click "Run workflow"**

A dropdown appears for `bump_type`. You should see options: patch, minor, major

- [ ] **Step 4: Select "patch" and run**

The workflow runs with the following steps:
- Checkout code
- Configure git user
- Extract current version
- Run bump-version.sh with "patch"
- Extract new version
- Commit and push
- Display summary

- [ ] **Step 5: Verify commit was created**

```bash
git pull origin master
git log --oneline -2
```

Expected: New commit with message "chore: bump version to 0.0.X" where X is incremented

- [ ] **Step 6: Verify version in pyproject.toml**

```bash
grep "^version = " pyproject.toml
```

Expected: Version incremented by one patch level

- [ ] **Step 7: Monitor ci.yml and publish-test.yml**

Visit: https://github.com/demonno/ynab-import/actions

Expected: ci.yml auto-triggers after push, then publish-test.yml auto-triggers if ci.yml passes, and publishes to Test PyPI (version check passes because version changed)

- [ ] **Step 8: Test minor bump via workflow dispatch**

Repeat steps 1-7 but select "minor" instead of "patch"

Expected: MINOR component increments, PATCH resets to 0

- [ ] **Step 9: Test major bump via workflow dispatch**

Repeat steps 1-7 but select "major" instead of "patch"

Expected: MAJOR component increments, MINOR and PATCH reset to 0

---

## Task 8: Verify Test PyPI contains all bumped versions

**Files:**
- No files (verification only)

- [ ] **Step 1: Visit Test PyPI project page**

Navigate to: https://test.pypi.org/project/ynab-import/

- [ ] **Step 2: Check release history**

Look at the "Release history" section

Expected: Versions 0.0.11, 0.0.12, 0.0.13 (or similar incrementing versions) visible in Test PyPI, each corresponding to a version bump

- [ ] **Step 3: Verify no duplicate versions**

Expected: No duplicate version entries (no "File already exists" errors in history)

- [ ] **Step 4: Verify each version is installable**

```bash
# Test installing one of the new versions (optional, for thoroughness)
pip install --index-url https://test.pypi.org/simple/ ynab-import==0.0.12
```

Expected: Installation succeeds without errors

---

## Success Criteria

- ✅ Version detection script detects version changes and skips on no-change
- ✅ Version bumping script correctly increments semantic versions
- ✅ GitHub Actions bump-version.yml allows manual bumping via dropdown
- ✅ publish-test.yml only publishes when version changes
- ✅ No duplicate Test PyPI uploads (no "File already exists" errors)
- ✅ Manual version bump triggers ci.yml and publish-test.yml chain
- ✅ GitHub Action version bump (major/minor/patch) triggers full chain
- ✅ First commit edge case handled (always publishes)
- ✅ Test PyPI contains incrementing versions without duplicates
