#!/bin/bash
set -e

# Verify pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
  echo "Error: pyproject.toml not found" >&2
  exit 1
fi

CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed -n 's/^version = ["\x27]\([^"'"'"']*\)["\x27].*/\1/p')

if [ -z "$CURRENT_VERSION" ]; then
  echo "Error: Could not extract version from pyproject.toml" >&2
  exit 1
fi

# Handle first commit (no HEAD~1)
if ! git rev-parse HEAD~1 >/dev/null 2>&1; then
  echo "First commit detected, publishing version: $CURRENT_VERSION"
  exit 0
fi

PREV_VERSION=$(git show HEAD~1:pyproject.toml 2>/dev/null | grep "^version = " | sed -n 's/^version = ["\x27]\([^"'"'"']*\)["\x27].*/\1/p' || echo "")

if [ -z "$PREV_VERSION" ]; then
  echo "First commit or pyproject.toml didn't exist in HEAD~1, publishing as new version" >&2
  echo "Version: $CURRENT_VERSION"
  exit 0
fi

if [ "$CURRENT_VERSION" = "$PREV_VERSION" ]; then
  echo "Version unchanged ($CURRENT_VERSION), skipping Test PyPI publish"
  exit 1
fi

echo "Version changed: $PREV_VERSION → $CURRENT_VERSION, proceeding with publish"
exit 0
