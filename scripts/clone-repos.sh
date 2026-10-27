#!/usr/bin/env bash
# Clone or update Dash Platform source repos into .repos/ for lexicon generation.
# Usage: [PLATFORM_REF=<tag-or-branch>] bash scripts/clone-repos.sh
#   PLATFORM_REF pins dashpay/platform to a release tag (e.g. v5.0.0); default: default branch.
set -euo pipefail

PLATFORM_REF="${PLATFORM_REF:-}"

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
  if [ "$repo" = "dashpay/platform" ] && [ -n "$PLATFORM_REF" ]; then
    if [ ! -d "$dir" ]; then
      echo "clone $repo@$PLATFORM_REF → $dir"
      git clone --depth 1 --branch "$PLATFORM_REF" "https://github.com/$repo.git" "$dir"
    else
      echo "checkout $dir@$PLATFORM_REF"
      git -C "$dir" fetch --depth 1 origin "refs/tags/$PLATFORM_REF:refs/tags/$PLATFORM_REF" 2>/dev/null \
        || git -C "$dir" fetch --depth 1 origin "$PLATFORM_REF"
      git -C "$dir" checkout --detach "$PLATFORM_REF" 2>/dev/null || git -C "$dir" checkout --detach FETCH_HEAD
    fi
  elif [ -d "$dir" ]; then
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
