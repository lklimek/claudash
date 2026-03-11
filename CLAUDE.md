# CLAUDE.md

Guidance for Claude Code working in this repository.

## Project Overview

**claudash** — a Claude Code plugin at [github.com/lklimek/claudash](https://github.com/lklimek/claudash). Skills and lexicon for Dash Platform developers. GPL-3.0.

## Repository Structure

```
.claude-plugin/
  plugin.json       # Plugin manifest (only `name` required; skills/ auto-discovered)
skills/             # Skill definitions (directories with SKILL.md)
lexicon/            # Auto-generated keyword lookup tables (do not edit manually)
scripts/            # Helper scripts for lexicon generation
```

## Skills

| Skill | Purpose |
|-------|---------|
| `dash-platform` | Data contracts, Rust SDK, JS/TS SDK, identities, documents, queries |
| `update-lexicon` | Regenerate lexicon/ from source repos (user-invocable) |

## Lexicon

Auto-generated keyword lookup tables in `lexicon/`. Skills grep these to find types, functions, and patterns, then WebFetch source links for details.

| File | Source | Method |
|------|--------|--------|
| `rust.md` | dash-sdk, dpp, rs-dapi-client, dapi-grpc | `cargo +nightly doc` → rustdoc JSON → `scripts/gen-rust-lexicon.py` |
| `rust-patterns.md` | rs-sdk examples, dash-evo-tool | Agent-generated, appended to rust.md by script |
| `contract.md` | rs-dpp, wasm-dpp, yappr, dash-bridge | Agent-generated |
| `js.md` | js-evo-sdk, wasm-sdk, yappr | Agent-generated |
| `grpc.md` | dapi-grpc protos | Agent-generated |

**Do not edit lexicon files manually.** Run `/update-lexicon` to regenerate.

### Link Prefixes

Lexicon tables use short prefixes in Src/Docs columns:

| Pre | Expands to |
|-----|-----------|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `T:` | `https://github.com/dashpay/dash-evo-tool/blob/master/` |
| `Y:` | `https://github.com/PastaPastaPasta/yappr/blob/master/` |
| `D:` | `https://github.com/PastaPastaPasta/dash-bridge/blob/master/` |
| `E:` | `https://github.com/dashpay/evo-sdk-website/blob/master/` |

## Scripts

| Script | Purpose | Requirements |
|--------|---------|--------------|
| `scripts/clone-repos.sh` | Clone/update source repos to `.repos/` | git |
| `scripts/gen-rustdoc-json.sh` | Generate rustdoc JSON for Rust crates | `cargo +nightly` |
| `scripts/gen-rust-lexicon.py` | Parse rustdoc JSON → `lexicon/rust.md` | Python 3 |

## Conventions

- Skill names: lowercase kebab-case
- Frontmatter `description`: single-line, state **when** to use
- Keep instructions concise — fewer tokens, same signal
- `.repos/` is gitignored — local clones for lexicon generation only

## Development

```bash
claude --plugin-dir /home/ubuntu/git/claudash   # local testing
claude plugin validate .                         # validate manifest
```

## Versioning

Bump version in `plugin.json`. Follow SemVer 2.

Pre-1.0: minor (0.x.0) for new skills or behavior changes, patch (0.0.x) for fixes.
