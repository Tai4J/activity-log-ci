#!/usr/bin/env bash
# Prints the history evidence for the report.
# Usage: ./scripts/history.sh [N]   (default 25 commits)
git fetch --quiet origin
git log origin/main --graph --oneline --decorate --date=short \
  --format='%h %ad %<(12,trunc)%an %s%d' -n "${1:-25}"
