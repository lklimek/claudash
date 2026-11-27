---
name: dash-dev
description: "Load before searching source or using RPC for dash-evo-tool (including its dash-cli) and Tenderdash. Use for plan-only CLI changes, active protocol version lookups, and Tenderdash peer counts, sync, or node status. Load for a one-field lookup too, including when a live RPC endpoint or a saved net_info or status response is already supplied. Use the Dash Platform (Evolution) lexicon for Rust dash-sdk/dpp/Drive, JS/TS @dashevo SDKs, Swift/Kotlin, DAPI gRPC, data contracts, documents, identities, tokens, DPNS, state transitions, credits, proofs, SDK compatibility, Tenderdash consensus, Drive ABCI, and node upgrades."
---

Assist with Dash Platform development: data contracts, Rust SDK, JS/TS SDK, identities, documents, queries, and Tenderdash integration.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

**Rust** — not on crates.io, use git dep pinned to a release tag (current stable and lexicon source: `v5.1.0`):
```toml
[dependencies]
dash-sdk = { git = "https://github.com/dashpay/platform", tag = "v5.1.0" }
dpp = { git = "https://github.com/dashpay/platform", tag = "v5.1.0" }
```

**JS/TS**:
```bash
npm install @dashevo/evo-sdk@5.1.0   # ESM-only, Node >= 22
```

## Lexicon

The `lexicon/` keyword tables ship **inside this plugin**, not in the working directory. Their absolute location is `${CLAUDE_PLUGIN_ROOT}/lexicon/`. Always use that absolute path: a relative `lexicon/rust.md` resolves against the working directory, which has no lexicon.

**Before answering any question about Dash Platform API names, types, methods, signatures or versions, you MUST grep the lexicon first — never answer from memory.** Pick the file from the table below.

To answer questions:
1. Grep the relevant file by absolute path, e.g. `grep -i "<keyword>" "${CLAUDE_PLUGIN_ROOT}/lexicon/rust.md"` (Bash grep or the Grep tool)
2. Find the `Src` or `Docs` column link in matching rows
3. Expand the link prefix (see table below) to a full URL and WebFetch it for details

| File (under `${CLAUDE_PLUGIN_ROOT}/lexicon/`) | Content |
|------|---------|
| `rust.md` | Rust SDK types, functions, patterns (5400+ entries, includes dapi-grpc bindings) |
| `js.md` | JS SDK types, functions, patterns |
| `contract.md` | data contract types, JSON Schema, DPP, document types |
| `grpc.md` | gRPC services, messages, endpoints |
| `explorers.md` | Insight API + Platform Explorer endpoints, instances |
| `changelog/platform/*.md` | per-release public-API diffs + migration guidance (breaking changes, added/removed symbols) |
| `changelog/tenderdash/*.md` | Tenderdash consensus, ABCI, RPC, and configuration migration |

For Insight (Core/L1) and Platform Explorer (L2), use `explorers.md` to select the mainnet or testnet **API base URL**. UI and documentation URLs are separate. Confirm the network with Insight `status?q=getInfo` (`info.network`) or Platform Explorer `status` (`network`) before using the instance; do not infer it from documentation examples.

### Version & migration questions

When the user asks "what changed in `<version>`", "is X a breaking change", "how do I migrate from A to B", or mentions upgrading SDK versions:
- For Platform, grep `${CLAUDE_PLUGIN_ROOT}/lexicon/changelog/platform/*.md` for the symbol or RPC. Read the Change and Migration columns in every file from after the current version through the target. An upgrade from 5.0.1 to 5.1.0 uses 5.0.2.md, 5.0.3.md, and 5.1.0.md. Expand and fetch the `Ref` links for details.
- For Tenderdash and its Drive integration, grep `${CLAUDE_PLUGIN_ROOT}/lexicon/changelog/tenderdash/*.md` and follow its links to tagged source and upgrade notes.

Stable Platform files are permanent. Keep only the newest prerelease file.

Link prefixes:

| Pre | URL |
|-----|-----|
| `P:` | `https://github.com/dashpay/platform/blob/v5.1.0/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `T:` | `https://github.com/dashpay/dash-evo-tool/blob/v1.0-dev/` |
| `Y:` | `https://github.com/PastaPastaPasta/yappr/blob/master/` |
| `D:` | `https://github.com/dashpay/dash-bridge/blob/main/` |
| `E:` | `https://github.com/dashpay/evo-sdk-website/blob/master/` |
| `PR:` | `https://github.com/dashpay/platform/pull/` |
| `C:` | `https://github.com/dashpay/platform/commit/` |

## Platform 5.1 and Tenderdash 2.0

- Check the target network's protocol version. SDK 5.1 reads protocol 14 and 15. Upgrade 5.0.x clients before activation to retain access to DPNS, DashPay, newly stored contracts, document history, and 128-bit sums. [App upgrade guide](https://github.com/dashpay/platform/blob/v5.1.0/book/src/sdk/protocol-version-15-upgrade.md)
- Protocol 15 adds private document types (`private.entrySize`), decision proposals, compiled contracts, and keep-history deletion and erasure (`canBeDeleted`, `canBeErased`). Read private entries with `getPrivateDocumentEntries` and submit them with `PrivateDocumentCreateFromShieldedPool`.
- Use `GetDocumentHistoryRequestV1` at protocol 15. Let the SDK negotiate the request version for older networks. Use `i128` in Rust or `Int128` in Swift for proved document sums, and keep FFI decimal strings exact.
- Upgrade Drive and Tenderdash together before activation. Platform protocol 15 sets Tenderdash consensus version 2, which requires Tenderdash 2.0+ on validators and full nodes. Tenderdash 2.0 also calls commit-level `VerifyVoteExtension` with an empty `validator_pro_tx_hash`. [Tenderdash migration](../../lexicon/changelog/tenderdash/2.0.0.md)
- For Dashmate upgrades, follow the pinned instructions for Core 24, Tenderdash 2.0 and the Core RPC whitelist. Restart the full node so Core loads the new whitelist. [Platform upgrade guide](https://github.com/dashpay/platform/releases/tag/v5.1.0#upgrading)

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
- `preorder`: salted commit-reveal below protocol 15. At protocol 15, DPNS v3 requires the owner's unsalted preorder from an earlier block and consumes it on registration.
- DPNS v3 generates labels with `homographSafeASCII`. Owners can delete uncontested names or permanently retire a name with a `tombstone`.

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
use dash_sdk::platform::{Document, Fetch, FetchMany, Identifier, Identity};

let identity = Identity::fetch(&sdk, id).await?;       // Ok(None) if missing
let docs = Document::fetch_many(&sdk, query).await?;
```

### Key Patterns

- **Proofs**: All queries return cryptographic proofs, verified automatically (same in JS SDK trusted mode)
- **Queries**: build `DocumentQuery::new(contract, "type")?` + `.with_where(..)`/`.with_order_by(..)`/`.with_limit(n)`; a `DriveDocumentQuery` converts via fallible `DocumentQuery::try_from(&drive_query)?` (no `From` in v5)
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

### JS Security

- Proof verification trusts the quorum keys `connect()` fetches over HTTPS from `quorums.<network>.networks.dash.org`; override with `quorumUrl` only to a source you trust.
- Use the `*Trusted()` factories: `new EvoSDK({...})` defaults to `trusted: false` (no quorum keys); never pass `proofs: false` for value-bearing reads.
- Load WIFs/mnemonics from a secret store or env var — never literals in source.

### Operations

Facades on the instance: `identities`, `documents`, `contracts`, `tokens`, `dpns`, `addresses`, `epoch`, `protocol`, `stateTransitions`, `system`, `group`, `contractGroups`, `voting`, `shielded`, `encryptedFor`, `moderationCharters`, `decisionProposals`. Reads return `undefined` when missing; `*WithProof` variants also return proof metadata. Writes take an options object with `identityKey` (`IdentityPublicKey`) + `signer` (`IdentitySigner`, `addKeyFromWif`).

```typescript
import { EvoSDK, Document, IdentitySigner } from '@dashevo/evo-sdk';

const identity = await sdk.identities.fetch(identityId);
if (!identity) throw new Error('identity not found');
const identityKey = identity.getPublicKeyById(keyId);
if (!identityKey) throw new Error('key not found');

const signer = new IdentitySigner();
signer.addKeyFromWif(wif); // wif from a secret store / env var, never a literal

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
- Contested creates pay a contest fund (doubles at 250 contenders, again per 50 more). `documents.create` / `dpns.registerName` read it automatically; `contestFund` (credits) only caps it. Preview with `sdk.documents.contestFundToJoin`; hand-built `DocumentCreateTransition`s pass it as `prefundedVotingBalance`.
- New query kinds: aggregate `count`/`sum`/`average`, `ranked`/`having`, `chained`, `composite`.
- New facades: `contractGroups`, `encryptedFor`, `moderationCharters`; contract moderation (`banUser`, `moderationStatus`, …) on `contracts`.

### Platform 5.1 JS changes

- `documents.history` returns `{ entries, lifecycle }` on every network. `documents.historyWithProof` wraps that result with proof metadata. `startAtMs` is inclusive. Drop `offset` and use `startAfter` for cursor pagination at protocol 15.
- Use `dpns.deleteName` or `dpns.tombstoneName` according to the desired name lifecycle. Use the `decisionProposals` facade for yes/no and multiple-choice proposals.
- The opt-in Core quorum proof provider verifies DIP 175 proofs from a trusted checkpoint. Check `js.md` for provider constructors and WASM features. Mainnet verified mode requires reachable proof relays supplied by the app.

### Low-level bindings

`@dashevo/evo-sdk` re-exports `@dashevo/wasm-sdk` (which bundles `wasm-dpp2` classes: `Document`, `DataContract`, `BatchTransition`, `DocumentCreateTransition`, …) — build/sign transitions by hand from these. Legacy `@dashevo/wasm-dpp` (`DashPlatformProtocol`) is a dev-only binding; prefer the re-exported `wasm-dpp2` classes.

### Wallet

`wallet` namespace export: BIP39 mnemonic generate/validate, BIP44/DIP9/DIP13 key derivation, `xprvToXpub`, `deriveChildPublicKey`, `generateKeyPair`, `keyPairFromWif`, address validation, message signing. No UTXO/L1 tx management — use `sdk.addresses` for Platform-address credits.

### JS Examples

- `PastaPastaPasta/yappr` — social app, document CRUD
- `dashpay/dash-bridge` — bridge application
- `dashpay/evo-sdk-website` — SDK docs with examples

---

## C++ / Swift / Kotlin SDKs

For C++ embedders, use `P:rs-sdk-cxx/`. The C++ binding expects host-provided DAPI endpoints, quorum keys and signing callbacks. Build the archive and generated headers together.

For Swift and Kotlin, read the tagged SDK source. `P:swift-sdk/` (iOS, SwiftPM `SwiftDashSDK` over the `DashSDKFFI` xcframework that `build_ios.sh` builds from `rs-unified-sdk-ffi`) and `P:kotlin-sdk/` (Android, JNI shim `rs-unified-sdk-jni`) — start with each package's `README.md` / `BUILD_GUIDE_FOR_AI.md`. Swift API changes: `## Swift` sections in `changelog/platform/*.md`; Kotlin is not in the changelogs.
