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
