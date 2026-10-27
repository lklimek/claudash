#!/usr/bin/env bash
# Clone or update Dash Platform source repos into .repos/ for lexicon generation.
# Usage: [PLATFORM_REF=<tag-or-branch>] bash scripts/clone-repos.sh
#   PLATFORM_REF pins dashpay/platform to a release tag (e.g. v5.0.0); default: default branch.
#   Existing clones are re-fetched and checked out detached at the remote ref; fetch errors abort.
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
  ref="HEAD" # remote default branch
  if [ "$repo" = "dashpay/platform" ] && [ -n "$PLATFORM_REF" ]; then
    ref="$PLATFORM_REF"
  fi
  if [ ! -d "$dir" ]; then
    echo "clone $repo@$ref → $dir"
    if [ "$ref" = "HEAD" ]; then
      git clone --depth 1 "https://github.com/$repo.git" "$dir"
    else
      git clone --depth 1 --branch "$ref" "https://github.com/$repo.git" "$dir"
    fi
  else
    # Always check out exactly what the remote has now: a local branch/tag of the
    # same name may be stale, and a previous pinned run leaves HEAD detached.
    echo "update $dir@$ref"
    git -C "$dir" fetch --depth 1 origin "$ref"
    git -C "$dir" checkout --quiet --detach FETCH_HEAD
  fi
done

echo ""
echo "Commit SHAs:"
for dir in "$REPOS_DIR"/*/; do
  name=$(basename "$dir")
  sha=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
  echo "  $name@$sha"
done
