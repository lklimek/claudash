#!/usr/bin/env bash
# Clone or update Dash Platform source repos into .repos/ for lexicon generation.
# Usage: bash scripts/clone-repos.sh
set -euo pipefail

REPOS=(
  dashpay/platform
  dashpay/dash-evo-tool
  PastaPastaPasta/yappr
  PastaPastaPasta/dash-bridge
  dashpay/evo-sdk-website
)

REPOS_DIR=".repos"
mkdir -p "$REPOS_DIR"

for repo in "${REPOS[@]}"; do
  dir="$REPOS_DIR/$(basename "$repo")"
  if [ -d "$dir" ]; then
    echo "pull $dir"
    git -C "$dir" pull --ff-only 2>/dev/null || echo "  (pull failed, using existing)"
  else
    echo "clone $repo → $dir"
    git clone --depth 1 "https://github.com/$repo.git" "$dir"
  fi
done

echo ""
echo "Commit SHAs:"
for dir in "$REPOS_DIR"/*/; do
  name=$(basename "$dir")
  sha=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
  echo "  $name@$sha"
done
