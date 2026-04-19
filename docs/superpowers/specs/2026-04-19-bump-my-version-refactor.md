# Refactor Version Bumping to use bump-my-version - Design Specification

**Date:** 2026-04-19
**Status:** Approved
**Goal:** Refactor version management scripts to use `bump-my-version` internally, eliminating custom bash version arithmetic and sed compatibility issues while maintaining the same script-based abstraction layer.

---

## Executive Summary

The current implementation uses custom bash scripts (`scripts/bump-version.sh`) with manual semantic version arithmetic and sed-based file updates. This approach has proven fragile:
- sed compatibility issues between macOS and Linux (required fixes)
- Error-prone version parsing and arithmetic
- Custom tooling that reinvents published solutions

This design introduces `bump-my-version`, a mature, community-maintained Python package, as the internal implementation tool while keeping shell scripts as the stable abstraction layer. Scripts remain unchanged from the GitHub Actions workflow perspective, but internally delegate to `bump-my-version` for robust version handling.

Result: Cleaner, more maintainable, tool-agnostic version management with better error handling.

---

## Design

### 1. Configuration: `.bumpversion.toml`

**Purpose:** Configure `bump-my-version` behavior for the ynab-import project

**Implementation:**
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

**Behavior:**
- `current_version`: Synced with actual version in pyproject.toml
- `commit = true`: Auto-commits version change
- `tag = false`: Don't create git tags (manual release process only)
- `files`: Specifies where to find and update version

**Advantages:**
- Version location defined once, used by both scripts
- Auto-commit handled by tool, not script
- Configuration-driven, easy to extend

### 2. Version Detection Script: `scripts/check-version-changed.sh`

**Purpose:** Detect if version changed from previous commit (gates Test PyPI publishing)

**Implementation:**
```bash
#!/bin/bash
set -e

# Get current version using bump-my-version
CURRENT_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

# Handle first commit (no HEAD~1)
if ! git rev-parse HEAD~1 >/dev/null 2>&1; then
  echo "First commit detected, publishing version: $CURRENT_VERSION"
  exit 0
fi

# Get previous version from HEAD~1
PREV_VERSION=$(git show HEAD~1:pyproject.toml 2>/dev/null | python3 -c "import sys, tomllib; print(tomllib.loads(sys.stdin.read())['project']['version'])" || echo "")

if [ "$CURRENT_VERSION" = "$PREV_VERSION" ]; then
  echo "Version unchanged ($CURRENT_VERSION), skipping Test PyPI publish"
  exit 1
fi

echo "Version changed: $PREV_VERSION → $CURRENT_VERSION, proceeding with publish"
exit 0
```

**Alternative (simpler, using grep):**
```bash
#!/bin/bash
set -e

CURRENT_VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

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

**Notes:**
- Simpler approach (grep-based) preferred for reliability
- Optional: Could use `bump-my-version show current_version` instead of grep, but grep is sufficient and more portable
- Handles first commit edge case
- Exit codes: 0 (publish), 1 (skip)

### 3. Version Bumping Script: `scripts/bump-version.sh`

**Purpose:** Bump semantic version using bump-my-version

**Implementation:**
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
bump-my-version bump "$BUMP_TYPE"

# Get new version after bump
NEW=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

echo "Bumped: $CURRENT → $NEW"
```

**Behavior:**
- Accepts BUMP_TYPE (major/minor/patch), defaults to patch
- Validates bump type
- Calls `bump-my-version bump <type>`
- bump-my-version automatically:
  - Updates pyproject.toml with new version
  - Commits the change
- Script outputs confirmation with old/new versions
- Exit code 0 on success, non-zero on failure (via `set -e`)

**Error Handling:**
- `set -e` causes script to exit if `bump-my-version` fails
- Invalid bump type rejected with clear message
- If `.bumpversion.toml` missing or malformed, bump-my-version exits with error

### 4. Installation & Configuration

**Step 1: Add bump-my-version to dependencies**
```bash
uv add --group dev bump-my-version>=0.21.0
```

**Step 2: Create `.bumpversion.toml` in repo root**
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

**Step 3: Remove custom bash scripts** (old versions no longer needed)

**Step 4: Update GitHub Actions workflows**
- No changes needed to `.github/workflows/bump-version.yml` (calls `bash scripts/bump-version.sh` as before)
- No changes needed to `.github/workflows/publish-test.yml` (calls `bash scripts/check-version-changed.sh` as before)

### 5. Integration with Existing Workflows

**Unchanged from GitHub Actions perspective:**
- `bump-version.yml` still calls: `bash scripts/bump-version.sh ${{ inputs.bump_type }}`
- `publish-test.yml` still calls: `bash scripts/check-version-changed.sh`
- Scripts are black boxes to workflows

**Internal change:**
- Scripts delegate to `bump-my-version` instead of manual bash operations

### 6. Benefits

✅ **Robustness:** Version parsing handled by maintained tool, not custom regex
✅ **No sed issues:** Eliminates macOS/Linux sed compatibility problems
✅ **Auto-commit:** bump-my-version handles commit creation automatically
✅ **Configuration-driven:** Single source of truth in `.bumpversion.toml`
✅ **Tool-agnostic:** Can swap implementation tools without changing workflows
✅ **Community-maintained:** Leverages proven, widely-used package
✅ **Simpler scripts:** Fewer lines of custom bash code = fewer bugs

### 7. Testing Strategy

**Manual bumping:**
1. Manually edit `.bumpversion.toml` current_version to test value
2. Run: `bash scripts/bump-version.sh patch`
3. Verify: pyproject.toml updated, git commit created
4. Revert: `git reset --hard HEAD~1`

**GitHub Actions workflow dispatch:**
1. Go to Actions → Bump Version
2. Run with "major", "minor", "patch"
3. Verify: Commit created, workflows auto-trigger
4. Check: Test PyPI receives new version

**Version detection:**
1. Commit with version change
2. Run: `bash scripts/check-version-changed.sh`
3. Verify: Exit 0
4. Commit without version change
5. Run: `bash scripts/check-version-changed.sh`
6. Verify: Exit 1

### 8. Success Criteria

- ✅ `.bumpversion.toml` created and configured correctly
- ✅ `scripts/bump-version.sh` refactored to use `bump-my-version`
- ✅ `scripts/check-version-changed.sh` uses grep-based extraction (no custom parsing)
- ✅ bump-my-version added to dev dependencies
- ✅ Manual version bumps work (file updated, auto-committed)
- ✅ GitHub Actions workflow dispatch works (all bump types)
- ✅ Version detection correctly identifies changes/non-changes
- ✅ No sed compatibility issues
- ✅ All workflows unchanged from external perspective

---

## Files to Create/Modify

**Create:**
- `.bumpversion.toml` — bump-my-version configuration

**Modify:**
- `scripts/bump-version.sh` — Refactor to use bump-my-version
- `scripts/check-version-changed.sh` — Keep as-is (works well)
- `pyproject.toml` — Add bump-my-version to dev dependencies

**No changes:**
- `.github/workflows/bump-version.yml` (calls script as before)
- `.github/workflows/publish-test.yml` (calls script as before)

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| New dependency (bump-my-version) | Widely-used, active project, minimal additional size |
| Config mismatch | Version in `.bumpversion.toml` kept in sync with pyproject.toml |
| Auto-commit surprises | Workflows expect commits; bump-my-version behavior documented in scripts |
| Workflow compatibility | Scripts remain identical interface; only internal implementation changes |

---

## References

- Current versioning spec: `docs/superpowers/specs/2026-04-18-versioning-publishing-strategy.md`
- Current implementation plan: `docs/superpowers/plans/2026-04-18-versioning-publishing-strategy-implementation.md`
- bump-my-version docs: https://callowayproject.github.io/bump-my-version/
- bump-my-version GitHub: https://github.com/callowayproject/bump-my-version
