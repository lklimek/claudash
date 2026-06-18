---
name: dash-platform
description: "Dash Platform development — data contracts, Rust SDK (dash-sdk, dpp), JS SDK (@dashevo/evo-sdk, wasm-dpp), gRPC, identities, documents. Use when working with Dash Platform in any language."
---

Assist with Dash Platform development: data contracts, Rust SDK, JS/TS SDK, identities, documents, and queries.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

**Rust** — not on crates.io, use git dep:
```toml
[dependencies]
dash-sdk = { git = "https://github.com/dashpay/platform", branch = "master" }
dpp = { git = "https://github.com/dashpay/platform", branch = "master" }
```

**JS/TS**:
```bash
npm install @dashevo/evo-sdk
```

## Lexicon

`lexicon/` contains keyword lookup tables for Dash Platform APIs. To answer questions:
1. Grep the relevant `lexicon/*.md` file for keywords matching the user's query
2. Find the `Src` or `Docs` column link in matching rows
3. Expand the link prefix (see table below) to a full URL and WebFetch it for details

| File | Content |
|------|---------|
| `lexicon/rust.md` | Rust SDK types, functions, patterns (2700+ entries, includes dapi-grpc bindings) |
| `lexicon/js.md` | JS SDK types, functions, patterns |
| `lexicon/contract.md` | data contract types, JSON Schema, DPP, document types |
| `lexicon/grpc.md` | gRPC services, messages, endpoints |
| `lexicon/explorers.md` | Insight API + Platform Explorer endpoints, instances |

Link prefixes:

| Pre | URL |
|-----|-----|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `T:` | `https://github.com/dashpay/dash-evo-tool/blob/master/` |
| `Y:` | `https://github.com/PastaPastaPasta/yappr/blob/master/` |
| `D:` | `https://github.com/PastaPastaPasta/dash-bridge/blob/master/` |
| `E:` | `https://github.com/dashpay/evo-sdk-website/blob/master/` |

---

## Data Contracts

### Structure

- Defines document types via JSON Schema; unique ID from owner identity + entropy
- Contains ≥1 document types with indexes for querying
- Versionable (owner can update; old versions remain queryable)

### Document Types

Each type defines:
- `type: "object"` + `properties` (JSON Schema)
- `indices` — index definitions for Platform queries
- `required` — required fields
- Optional: `additionalProperties: false`, `$comment`, `transient`, `documentsKeepHistoryContractDefault`

### Index Design

- `name` + `properties` array (each: `name` + `asc`/`desc`)
- `unique: true` for uniqueness constraints
- First property = range scan key in compound indexes
- Max 10 per document type
- System props: `$ownerId`, `$createdAt`, `$updatedAt`

### DPNS

Maps names → identities:
- `domain` type: `label`, `normalizedLabel`, `normalizedParentDomainName`, `records`
- `preorder` type: commit-reveal registration
- Normalized (lowercase) for uniqueness

### Contract Security

- Always set `additionalProperties: false`
- Validate schemas before submission
- Consider size limits and storage costs
- Contract updates must be backward-compatible (add props OK, remove/rename breaks)

---

## Rust SDK

### Core Types

| Type | Crate | Purpose |
|------|-------|---------|
| `Sdk` / `SdkBuilder` | `dash-sdk` | Entrypoint, builder pattern |
| `Identity` | `dpp` | Platform identity with keys |
| `DataContract` | `dpp` | JSON Schema contract def |
| `Document` | `dpp` | Data instance in contract |
| `Identifier` | `dpp` | 32-byte platform object ID |
| `AddressList` | `dash-sdk` | DAPI masternode addresses |

### CRUD via Fetch Traits

```rust
use dash_sdk::platform::{Fetch, FetchMany, Identifier};

let identity = Identity::fetch(&sdk, id).await?;       // Ok(None) if missing
let docs = Document::fetch_many(&sdk, query).await?;
```

### Key Patterns

- **Proofs**: All queries return cryptographic proofs, verified automatically (security advantage over JS SDK)
- **Queries**: `DriveQuery` → where clauses, order, limit → convert to `DocumentQuery`
- **GroveDB**: Hierarchical authenticated storage; SDK abstracts it — direct use rarely needed
- **Async**: Fully async, use `tokio`
- **Errors**: `dash_sdk::Error` — connection, proof failure, broadcast failure, query errors

### Rust Examples

`dash-evo-tool` demonstrates: identity registration, DPNS names, contract CRUD, document CRUD, tokens, multi-network support.

---

## JS/TS SDK

> **Deprecated: js-dash-sdk / `dash` npm package** — The `js-dash-sdk` (npm: `dash`) is deprecated and unsupported, replaced by `js-evo-sdk` (npm: `@dashevo/evo-sdk`). If you encounter `require('dash')`, `new Dash.Client()`, or `js-dash-sdk` imports: alert the user, recommend migrating to `@dashevo/evo-sdk`, and do NOT generate new code using the legacy package.

### Client Init

```javascript
import { EvoSDK } from '@dashevo/evo-sdk';

const client = new EvoSDK({
  network: 'testnet',
  wallet: { mnemonic: '...' },
});
await client.connect();
```

### Operations

```javascript
// Identity
const identity = await client.platform.identities.register();
await client.platform.identities.get(identityId);

// Contract
const contract = await client.platform.contracts.create({
  note: { type: 'object', properties: { message: { type: 'string', maxLength: 256 } }, additionalProperties: false }
}, identity);
await client.platform.contracts.publish(contract, identity);

// Document
const doc = await client.platform.documents.create('contractId.note', identity, { message: 'Hello' });
await client.platform.documents.broadcast({ create: [doc] }, identity);
const docs = await client.platform.documents.get('contractId.note', {
  where: [['$ownerId', '==', identity.getId()]], orderBy: [['$createdAt', 'desc']]
});

// DPNS
await client.platform.names.register('alice.dash', { dashUniqueIdentityId: identity.getId() }, identity);
const name = await client.platform.names.resolve('alice.dash');
```

### WASM-DPP (Browser)

```javascript
import { DashPlatformProtocol } from '@dashevo/wasm-dpp';
const dpp = new DashPlatformProtocol();
```

Provides: contract/document validation, state transition creation/signing, identity key management.

### JS Security

**Pure JS SDK has NO client-side proof verification.** For security-critical apps use `wasm-sdk` (has proofs) or validate server-side with Rust SDK.

### Wallet

Built-in: HD derivation from mnemonic, UTXO management, tx creation/broadcasting, balance queries.

### JS Examples

- `PastaPastaPasta/yappr` — social app, document CRUD
- `PastaPastaPasta/dash-bridge` — bridge application
- `dashpay/evo-sdk-website` — SDK docs with examples
