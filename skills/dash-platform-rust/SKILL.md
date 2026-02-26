---
name: dash-platform-rust
description: "Rust development with dash-sdk, dpp, rs-dapi-client, GroveDB, and Dash Platform. Use when writing Rust code that interacts with Dash Platform, identity management, data contracts, documents, or proof verification."
---

# Dash Platform Rust SDK

Assist with Rust development on Dash Platform using `dash-sdk`, `dpp`, `rs-dapi-client`, and related crates.

## Triggers

Activate when the user works with: `dash-sdk`, `dpp`, `rs-dapi-client`, `dapi-grpc`, GroveDB, Rust + Dash Platform, proof verification.

## Project Setup

When building or working in the `dashpay/platform` repo, run the environment setup first:

```bash
bash scripts/setup-ai-agent-environment.sh
```

This configures the build environment, installs dependencies, and prepares the workspace for development.

## Reference Index

Read `index/rust.md` and `index/grpc.md` for type/function/pattern lookups. Expand link prefixes to full URLs before web-fetching:

| Prefix | Expands to |
|--------|-----------|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `T:` | `https://github.com/dashpay/dash-evo-tool/blob/master/` |

When the index references a source or doc link, use WebFetch to retrieve the full content before answering.

## Knowledge

### SDK Setup

`dash-sdk` is not published to crates.io. Add it as a git dependency:

```toml
[dependencies]
dash-sdk = { git = "https://github.com/dashpay/platform", branch = "master" }
dpp = { git = "https://github.com/dashpay/platform", branch = "master" }
```

### Core Types

| Type | Crate | Purpose |
|------|-------|---------|
| `Sdk` | `dash-sdk` | Main entrypoint — holds connections, config |
| `SdkBuilder` | `dash-sdk` | Builder pattern for `Sdk` construction |
| `Identity` | `dpp` | Platform identity with cryptographic keys |
| `DataContract` | `dpp` | JSON Schema contract definition |
| `Document` | `dpp` | Data instance conforming to a contract |
| `Identifier` | `dpp` | 32-byte ID for platform objects |
| `AddressList` | `dash-sdk` | DAPI masternode addresses |

### CRUD Operations

All reads use the `Fetch` and `FetchMany` traits:

```rust
use dash_sdk::platform::{Fetch, FetchMany, Identifier};

// Fetch single object — returns Ok(None) if not found
let identity = Identity::fetch(&sdk, id).await?;

// Fetch multiple objects
let documents = Document::fetch_many(&sdk, query).await?;
```

### Proof Verification

All queries return cryptographic proofs by default. The SDK verifies proofs automatically — this is a key security advantage over the JS SDK.

### Query Patterns

Use `DriveQuery` for document searches:
- Specify contract ID and document type
- Add where clauses, order by, limit
- Convert to `DocumentQuery` for SDK consumption

### GroveDB

Platform's storage layer. Hierarchical authenticated data structure:
- Tree-based storage with Merkle proofs
- Used internally by Drive for state management
- Direct interaction rarely needed — SDK abstracts it

### Async Runtime

The SDK is fully async. Use `tokio`:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let sdk = SdkBuilder::new(addresses)?.build()?;
    // ...
}
```

### Error Handling

The SDK uses `dash_sdk::Error` enum. Common variants:
- Connection errors (DAPI unreachable)
- Proof verification failures
- State transition broadcast failures
- Query errors (invalid contract/document type)

### Real-World Examples

`dash-evo-tool` demonstrates:
- Identity registration and management
- DPNS username registration
- Data contract creation and updates
- Document CRUD operations
- Token creation and transfers
- Multi-network support (Mainnet, Testnet, Devnet)
