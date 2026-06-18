#!/usr/bin/env python3
"""
changelog-plan.py — Release enumeration, pairing, idempotency, and drift detection.

Computes which lexicon/changelog/platform/<ver>.md files need to be (re)generated,
using GitHub Releases as the authoritative source of truth.

Usage:
    python3 scripts/changelog-plan.py [--repo <owner/repo>] [--bootstrap]
                                       [--output-dir <path>] [--surfaces <path>]

Output: JSON to stdout with shape:
    {
      "worklist": [{"version", "base_tag", "head_tag", "output_path", "action"}],
      "prune":    ["path/to/old-pre.md", ...]
    }

"action" is "generate" or "skip" (idempotent: skip if file already exists).
"prune"   lists stale prerelease files to delete (only current LATEST_PRE is kept).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_REPO = "dashpay/platform"
FLOOR = (3, 0, 0)                    # baseline anchor — no file for 3.0.0 itself
DEFAULT_OUTPUT_DIR = "lexicon/changelog/platform"
DEFAULT_SURFACES = "skills/api-changelog/surfaces.platform.json"

# Patterns that look like SDK/client surface packages (drift detector).
# Longest alternatives first to avoid regex shadowing.
_SDK_ISH_PAT = re.compile(
    r"^(?:"
    r"rs-sdk[a-z0-9-]*"          # rs-sdk, rs-sdk-ffi, …
    r"|rs-unified-sdk[a-z0-9-]*" # rs-unified-sdk-ffi
    r"|rs-dapi-client[a-z0-9-]*" # rs-dapi-client
    r"|rs-platform-wallet[a-z0-9-]*"  # rs-platform-wallet, rs-platform-wallet-ffi
    r"|rs-drive-proof-verifier[a-z0-9-]*"
    r"|dapi-grpc[a-z0-9-]*"      # dapi-grpc
    r"|wasm-[a-z0-9-]+"          # wasm-*
    r"|js-[a-z0-9-]+"            # js-*
    r"|swift-[a-z0-9-]+"         # swift-*
    r"|[a-z0-9-]+-client"        # *-client
    r"|[a-z0-9-]+-sdk"           # *-sdk (catch-all last)
    r")$"
)

# Allow-list for tag/version strings used in shell/URL calls (safety fence).
_SAFE_TAG_RE = re.compile(r"^[a-zA-Z0-9._/-]+$")


# ── Semver (inline, §3.2 — no external deps) ─────────────────────────────────

def _parse_semver(tag: str):
    """
    Parse vMAJOR.MINOR.PATCH[-pre] → (major, minor, patch, pre_parts) or None.

    pre_parts is a tuple of (kind, value) where:
        kind=0 → numeric identifier (compared numerically, lower rank)
        kind=1 → alphanumeric identifier (compared lexically, higher rank than numeric)

    Empty pre_parts → stable release (highest for a given core).

    SemVer §11: pre-release versions have lower precedence than the associated
    normal version.  E.g. 1.0.0-alpha < 1.0.0.
    """
    raw = tag.lstrip("v")
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-(.+))?", raw)
    if not m:
        return None
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    pre_str = m.group(4)
    if pre_str is None:
        return (major, minor, patch, ())
    parts = []
    for p in pre_str.split("."):
        try:
            parts.append((0, int(p)))   # numeric
        except ValueError:
            parts.append((1, p))        # alphanumeric
    return (major, minor, patch, tuple(parts))


def _semver_key(tag: str):
    """
    Comparison key suitable for sorted()/max() — implements SemVer §11 ordering.

    Key shape: (major, minor, patch, stability, *pre_parts)
        stability=1 → no prerelease (stable, highest for given core)
        stability=0 → prerelease (lower than stable with same core)
    """
    parsed = _parse_semver(tag)
    if parsed is None:
        return (0, 0, 0, 0)         # unparseable → bottom
    major, minor, patch, pre_parts = parsed
    if not pre_parts:               # stable
        return (major, minor, patch, 1)
    return (major, minor, patch, 0) + pre_parts


def _ver_str(tag: str) -> str:
    """Strip leading 'v' → filename-safe version string."""
    return tag.lstrip("v")


def _validate_tag(tag: str) -> str:
    """Raise if tag contains chars unsafe for shell/URLs. Returns tag unchanged."""
    if not _SAFE_TAG_RE.match(tag):
        raise ValueError(f"Unsafe characters in tag {tag!r} — refusing to continue")
    return tag


# ── GitHub helpers ────────────────────────────────────────────────────────────

def _gh(*args: str, check: bool = True) -> str:
    """Run a gh command and return stdout."""
    try:
        result = subprocess.run(
            ["gh", *args],
            capture_output=True, text=True, check=check,
        )
        return result.stdout
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: gh {' '.join(args)} failed:\n{exc.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: `gh` CLI not found — install GitHub CLI.", file=sys.stderr)
        sys.exit(1)


def fetch_releases(repo: str) -> list:
    """Fetch release list from GitHub (gh CLI). Returns raw list of dicts."""
    raw = _gh(
        "release", "list",
        "--repo", repo,
        "--json", "tagName,isPrerelease,isLatest,publishedAt",
        "--limit", "200",
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse gh output: {exc}", file=sys.stderr)
        sys.exit(1)


def fetch_packages_at(repo: str, tag: str) -> list:
    """
    List immediate children of packages/ at the given tag.
    Best-effort — returns [] on any failure (drift detection is non-fatal).
    """
    try:
        _validate_tag(tag)
        raw = subprocess.run(
            ["gh", "api", f"repos/{repo}/contents/packages?ref={tag}",
             "--jq", ".[].name"],
            capture_output=True, text=True, check=False,
        )
        if raw.returncode != 0:
            return []
        names = raw.stdout.strip().split("\n")
        return [n for n in names if n]
    except Exception:           # noqa: BLE001  — drift detection must not die
        return []


# ── Core algorithm ────────────────────────────────────────────────────────────

def compute_plan(
    releases: list,
    output_dir: Path,
    bootstrap: bool,
) -> tuple:
    """
    Implement §3 pairing algorithm.

    Returns:
        worklist — list of dicts (version, base_tag, head_tag, output_path, action)
        latest_stable — str tag or None
        latest_pre    — str tag or None
    """
    stable: list = []
    prerelease: list = []

    for r in releases:
        parsed = _parse_semver(r["tagName"])
        if parsed is None:
            continue                # skip unparseable tags (e.g. "1.0.0-pr.1694.7")
        major, minor, patch, pre_parts = parsed
        if r["isPrerelease"]:
            prerelease.append(r["tagName"])
        else:
            if (major, minor, patch) >= FLOOR:
                stable.append(r["tagName"])

    stable_sorted = sorted(stable, key=_semver_key)        # ascending
    latest_stable = stable_sorted[-1] if stable_sorted else None

    # Cross-check isLatest flag from GitHub
    is_latest_tags = [r["tagName"] for r in releases if r.get("isLatest")]
    if latest_stable and is_latest_tags and latest_stable not in is_latest_tags:
        print(
            f"WARNING: semver picks latest-stable={latest_stable!r} "
            f"but GitHub isLatest={is_latest_tags!r} — trusting semver.",
            file=sys.stderr,
        )

    # LATEST_PRE: highest prerelease strictly ahead of latest stable
    latest_pre = None
    if latest_stable:
        ls_key = _semver_key(latest_stable)
        candidates = [t for t in prerelease if _semver_key(t) > ls_key]
        if candidates:
            latest_pre = max(candidates, key=_semver_key)

    floor_tag = "v" + ".".join(str(x) for x in FLOOR)

    # §3.4 — target set
    targets: dict = {}
    for tag in stable_sorted:
        if _semver_key(tag) <= _semver_key(floor_tag):
            continue            # 3.0.0 itself = anchor, no file (locked decision)
        predecessors = [s for s in stable_sorted if _semver_key(s) < _semver_key(tag)]
        base = max(predecessors, key=_semver_key)
        targets[_ver_str(tag)] = (base, tag)

    if latest_pre:
        targets[_ver_str(latest_pre)] = (latest_stable, latest_pre)

    # §3.5 — bootstrap override
    if bootstrap:
        if not latest_pre or not latest_stable:
            print(
                "ERROR: --bootstrap requires both a latest stable and a latest prerelease.",
                file=sys.stderr,
            )
            sys.exit(1)
        targets = {_ver_str(latest_pre): (latest_stable, latest_pre)}

    # Idempotency: mark existing files as skip
    worklist = []
    for version, (base_tag, head_tag) in sorted(
        targets.items(), key=lambda kv: _semver_key("v" + kv[0])
    ):
        out_path = output_dir / f"{version}.md"
        action = "skip" if out_path.exists() else "generate"
        worklist.append({
            "version": version,
            "base_tag": base_tag,
            "head_tag": head_tag,
            "output_path": str(out_path),
            "action": action,
        })

    return worklist, latest_stable, latest_pre


def compute_prune(output_dir: Path, latest_pre) -> list:
    """
    §3.6 — list stale prerelease files: prerelease files that are NOT the current
    LATEST_PRE.  Stable files are permanent, never pruned.
    """
    if not output_dir.exists():
        return []

    current_ver = _ver_str(latest_pre) if latest_pre else None
    prune = []
    for f in sorted(output_dir.glob("*.md")):
        ver = f.stem
        parsed = _parse_semver("v" + ver)
        if parsed is None:
            continue
        _, _, _, pre_parts = parsed
        if pre_parts and ver != current_ver:
            prune.append(str(f))
    return prune


def run_drift_detector(repo: str, check_tag: str, surfaces_path: Path) -> None:
    """
    §4 drift detector — warn on unclassified SDK-ish packages at head tag.
    Non-fatal; all findings go to stderr as WARNING lines.
    """
    packages = fetch_packages_at(repo, check_tag)
    if not packages:
        print(
            f"WARNING: drift detector could not list packages/ at {check_tag!r} "
            "(check gh auth).",
            file=sys.stderr,
        )
        return

    known: set = set()
    excluded: set = set()

    if surfaces_path.exists():
        with surfaces_path.open() as fh:
            surfaces = json.load(fh)
        for lang, items in surfaces.items():
            if lang == "exclude_reason":
                excluded.update(items.keys())
                # Also handle glob excludes like "*-contract"
                for pat in items:
                    if pat.startswith("*"):
                        suffix = pat[1:]
                        for pkg in packages:
                            if pkg.endswith(suffix):
                                excluded.add(pkg)
            else:
                for item in (items if isinstance(items, list) else []):
                    if isinstance(item, dict):
                        known.add(item.get("pkg", ""))

    for pkg in packages:
        if pkg in known or pkg in excluded:
            continue
        if _SDK_ISH_PAT.match(pkg):
            print(
                f"WARNING: packages/{pkg} looks like a client surface but is unclassified "
                f"— add to or exclude in surfaces.platform.json",
                file=sys.stderr,
            )


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute API changelog worklist from GitHub releases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help="GitHub repo (owner/repo)")
    parser.add_argument("--bootstrap", action="store_true",
                        help="Emit exactly one target: latest-stable-3.0.x → latest prerelease")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output .md directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--surfaces", default=DEFAULT_SURFACES,
                        help=f"surfaces allow-list JSON (default: {DEFAULT_SURFACES})")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    surfaces_path = Path(args.surfaces)

    releases = fetch_releases(args.repo)
    worklist, latest_stable, latest_pre = compute_plan(releases, output_dir, args.bootstrap)
    prune = compute_prune(output_dir, latest_pre)

    # Drift detection (best-effort, warnings only)
    check_tag = latest_pre or latest_stable
    if check_tag:
        run_drift_detector(args.repo, check_tag, surfaces_path)

    result = {"worklist": worklist, "prune": prune}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
