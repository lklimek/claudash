#!/usr/bin/env bash
# Generate rustdoc JSON for Dash Platform Rust crates.
# Requires: cargo +nightly
# Usage: bash scripts/gen-rustdoc-json.sh
set -euo pipefail

PLATFORM_DIR=".repos/platform"

if [ ! -d "$PLATFORM_DIR" ]; then
  echo "ERROR: $PLATFORM_DIR not found. Run scripts/clone-repos.sh first." >&2
  exit 1
fi

echo "Generating rustdoc JSON (nightly)..."
cd "$PLATFORM_DIR"
RUSTDOCFLAGS="-Z unstable-options --output-format json" \
  cargo +nightly doc --no-deps -p dash-sdk -p dpp -p rs-dapi-client -p dapi-grpc 2>&1 | tail -5

# Print doc dir for downstream scripts
DOC_DIR=$(cargo metadata --format-version 1 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['target_directory'])")/doc
echo ""
echo "DOC_DIR=$DOC_DIR"
