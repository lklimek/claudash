---
name: dash-platform-rust
description: "Rust development with dash-sdk, dpp, rs-dapi-client, GroveDB, and Dash Platform. Use when writing Rust code that interacts with Dash Platform, identity management, data contracts, documents, or proof verification."
---

Assist with Rust development on Dash Platform using `dash-sdk`, `dpp`, and related crates.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

Not on crates.io — use git dep:
```toml
[dependencies]
dash-sdk = { git = "https://github.com/dashpay/platform", branch = "master" }
dpp = { git = "https://github.com/dashpay/platform", branch = "master" }
```

## Lexicon

`lexicon/` has keyword lookup tables (auto-generated, 1000+ entries for Rust). To answer questions:
1. Grep `lexicon/rust.md` (or `grpc.md`, `contract.md`) for keywords
2. Find the `Src` link in the matching row
3. Expand the link prefix to a full URL → WebFetch for details

Primary: `lexicon/rust.md` (2700+ entries: Types, Functions, Patterns, Examples — includes dapi-grpc Rust bindings). Also: `lexicon/grpc.md` for proto definitions. Link prefixes:

| Pre | URL |
|-----|-----|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `T:` | `https://github.com/dashpay/dash-evo-tool/blob/master/` |

## Core Types

| Type | Crate | Purpose |
|------|-------|---------|
| `Sdk` / `SdkBuilder` | `dash-sdk` | Entrypoint, builder pattern |
| `Identity` | `dpp` | Platform identity with keys |
| `DataContract` | `dpp` | JSON Schema contract def |
| `Document` | `dpp` | Data instance in contract |
| `Identifier` | `dpp` | 32-byte platform object ID |
| `AddressList` | `dash-sdk` | DAPI masternode addresses |

## CRUD via Fetch Traits

```rust
use dash_sdk::platform::{Fetch, FetchMany, Identifier};

let identity = Identity::fetch(&sdk, id).await?;       // Ok(None) if missing
let docs = Document::fetch_many(&sdk, query).await?;
```

## Key Patterns

- **Proofs**: All queries return cryptographic proofs, verified automatically (security advantage over JS SDK)
- **Queries**: `DriveQuery` → where clauses, order, limit → convert to `DocumentQuery`
- **GroveDB**: Hierarchical authenticated storage; SDK abstracts it — direct use rarely needed
- **Async**: Fully async, use `tokio`
- **Errors**: `dash_sdk::Error` — connection, proof failure, broadcast failure, query errors

## Examples

`dash-evo-tool` demonstrates: identity registration, DPNS names, contract CRUD, document CRUD, tokens, multi-network support.
