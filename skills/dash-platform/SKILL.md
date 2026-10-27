---
name: dash-platform
description: "Dash Platform development — data contracts, Rust SDK (dash-sdk, dpp), JS SDK (@dashevo/evo-sdk, wasm-dpp), gRPC, identities, documents. Use when working with Dash Platform in any language."
---

Assist with Dash Platform development: data contracts, Rust SDK, JS/TS SDK, identities, documents, and queries.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

**Rust** — not on crates.io, use git dep pinned to a release tag (current stable: `v5.0.0`):
```toml
[dependencies]
dash-sdk = { git = "https://github.com/dashpay/platform", tag = "v5.0.0" }
dpp = { git = "https://github.com/dashpay/platform", tag = "v5.0.0" }
```

**JS/TS**:
```bash
npm install @dashevo/evo-sdk   # 5.0.0; ESM-only, Node >= 18.18
```

## Lexicon

The `lexicon/` keyword tables ship **inside this plugin**, not in the working directory. They live under `$CLAUDE_PLUGIN_ROOT/lexicon/`, and `$CLAUDE_PLUGIN_ROOT` is expanded **only by the shell** — so you MUST read them with a **Bash** `grep`/`rg` command. A bare path like `lexicon/rust.md`, or the Grep tool, resolves against the working directory (which has no lexicon) and makes the tables wrongly appear empty.

To answer questions:
1. Bash-grep the relevant file, e.g. `grep -i "<keyword>" "$CLAUDE_PLUGIN_ROOT/lexicon/rust.md"`
2. Find the `Src` or `Docs` column link in matching rows
3. Expand the link prefix (see table below) to a full URL and WebFetch it for details

| File (under `$CLAUDE_PLUGIN_ROOT/lexicon/`) | Content |
|------|---------|
| `rust.md` | Rust SDK types, functions, patterns (4600+ entries, includes dapi-grpc bindings) |
| `js.md` | JS SDK types, functions, patterns |
| `contract.md` | data contract types, JSON Schema, DPP, document types |
| `grpc.md` | gRPC services, messages, endpoints |
| `explorers.md` | Insight API + Platform Explorer endpoints, instances |
| `changelog/platform/*.md` | per-release public-API diffs + migration guidance (breaking changes, added/removed symbols) |

### Version & migration questions

When the user asks "what changed in `<version>`", "is X a breaking change", "how do I migrate from A to B", or mentions upgrading SDK versions:
1. Bash-grep `$CLAUDE_PLUGIN_ROOT/lexicon/changelog/platform/*.md` for the symbol/RPC keyword (same grep-first flow as the lexicon).
2. Pick the file for the target version (newer release); read the matching row's Change + Migration columns.
3. Expand the `Ref` link (`PR:` → `https://github.com/dashpay/platform/pull/`, `C:` → `https://github.com/dashpay/platform/commit/`) and WebFetch for the full rationale.

Stable files are permanent; only the single most-recent prerelease file is kept.

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
| `PR:` | `https://github.com/dashpay/platform/pull/` |
| `C:` | `https://github.com/dashpay/platform/commit/` |

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
- **Queries**: `DriveDocumentQuery` → where clauses, order, limit → convert to `DocumentQuery` via `From`
- **GroveDB**: Hierarchical authenticated storage; SDK abstracts it — direct use rarely needed
- **Async**: Fully async, use `tokio`
- **Errors**: `dash_sdk::Error` — connection, proof failure, broadcast failure, query errors

### Rust Examples

`dash-evo-tool` demonstrates: identity registration, DPNS names, contract CRUD, document CRUD, tokens, multi-network support.

---

## JS/TS SDK

> **Deprecated: js-dash-sdk / `dash` npm package** — The `js-dash-sdk` (npm: `dash`) is deprecated and unsupported, replaced by `js-evo-sdk` (npm: `@dashevo/evo-sdk`). If you encounter `require('dash')`, `new Dash.Client()`, or `js-dash-sdk` imports: alert the user, recommend migrating to `@dashevo/evo-sdk`, and do NOT generate new code using the legacy package.

### Client Init

```typescript
import { EvoSDK } from '@dashevo/evo-sdk';

const sdk = EvoSDK.testnetTrusted(); // or mainnetTrusted(), localTrusted(), devnetTrusted(name)
await sdk.connect();                  // trusted mode pre-fetches quorum keys → proofs verified
```

### Operations

Facades on the instance: `identities`, `documents`, `contracts`, `tokens`, `dpns`, `addresses`, `epoch`, `protocol`, `stateTransitions`, `system`, `group`, `voting`, `shielded`, `encryptedFor`, `moderationCharters`. Reads return `undefined` when missing; `*WithProof` variants also return proof metadata. Writes take an options object with `identityKey` (`IdentityPublicKey`) + `signer` (`IdentitySigner`, `addKeyFromWif`).

```typescript
import { EvoSDK, Document, IdentitySigner } from '@dashevo/evo-sdk';

const identity = await sdk.identities.fetch(identityId);
const contract = await sdk.contracts.fetch(contractId);

const signer = new IdentitySigner();
signer.addKeyFromWif(wif);
const identityKey = identity.getPublicKeyById(keyId);

// Document create: fetches nonce, builds, signs, broadcasts, returns confirmed document
const document = new Document({ properties: { message: 'Hello' }, documentTypeName: 'note', dataContractId: contractId, ownerId: identityId });
await sdk.documents.create({ document, identityKey, signer });

const docs = await sdk.documents.query({
  dataContractId: contractId, documentTypeName: 'note',
  where: [['$ownerId', '==', identityId]], orderBy: [['$createdAt', 'desc']], limit: 10,
});

// DPNS
await sdk.dpns.registerName({ label: 'alice', identity, identityKey, signer });
const ownerId = await sdk.dpns.resolveName('alice.dash');
```

Grep `js.md` for exact option types (`ContractPublishOptions`, `IdentityCreateOptions`, …) before writing calls.

### Protocol v14 (Platform 5.0) notes

- Document IDs commit to the identity contract nonce of the create transition — `new Document({...})` without `identityContractNonce` has a placeholder id until the create transition derives it.
- Contested documents must state a contest fund (`contestFund`, `sdk.documents.contestFundToJoin`).
- New query kinds: aggregate `count`/`sum`/`average`, `ranked`/`having`, `chained`, `composite`.
- New facades: `encryptedFor`, `moderationCharters`; contract moderation (`banUser`, `moderationStatus`, …) on `contracts`.

### Low-level bindings

`@dashevo/evo-sdk` re-exports `@dashevo/wasm-sdk` (which bundles `wasm-dpp2` classes: `Document`, `DataContract`, `BatchTransition`, `DocumentCreateTransition`, …) — build/sign transitions by hand from these. Legacy `@dashevo/wasm-dpp` (`DashPlatformProtocol`) is a dev-only binding; prefer the re-exported `wasm-dpp2` classes.

### Wallet

`wallet` namespace export: BIP39 mnemonic generate/validate, BIP44/DIP9/DIP13 key derivation, `xprvToXpub`, `deriveChildPublicKey`, `generateKeyPair`, `keyPairFromWif`, address validation, message signing. No UTXO/L1 tx management — use `sdk.addresses` for Platform-address credits.

### JS Examples

- `PastaPastaPasta/yappr` — social app, document CRUD
- `PastaPastaPasta/dash-bridge` — bridge application
- `dashpay/evo-sdk-website` — SDK docs with examples
