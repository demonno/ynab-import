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
