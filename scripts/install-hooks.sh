#!/usr/bin/env bash
# Installs the pre-push guard and turns on rerere for this clone.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cp "$root/scripts/pre-push" "$root/.git/hooks/pre-push"
chmod +x "$root/.git/hooks/pre-push"
git config rerere.enabled true
git config rerere.autoupdate true
echo "✔ pre-push hook installed, rerere enabled"
