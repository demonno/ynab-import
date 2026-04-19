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

# Clean uv.lock if modified (from previous runs)
if git diff --quiet uv.lock; then
  :
else
  git checkout uv.lock
fi

# Get current version before bump
CURRENT=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

# Run bump-my-version (auto-commits)
uv run bump-my-version bump "$BUMP_TYPE"

# Get new version after bump
NEW=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

# Push the commit created by bump-my-version
git push origin master

echo "Bumped: $CURRENT → $NEW"
echo "Pushed to origin/master"
