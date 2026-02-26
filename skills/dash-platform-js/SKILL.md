---
name: dash-platform-js
description: "JavaScript/TypeScript development with dash npm package, js-dash-sdk, wasm-dpp2, @dashevo/wasm-dpp, dapi-client. Use when writing JS/TS code that interacts with Dash Platform, browser apps, or Node.js services."
---

Assist with JS/TS development on Dash Platform using `dash` npm package and `@dashevo/wasm-dpp`.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

```bash
npm install dash
```

## Lexicon

`lexicon/` contains keyword lookup tables for Dash Platform APIs. To answer questions:
1. Grep the relevant `lexicon/*.md` file for keywords matching the user's query
2. Find the `Src` or `Docs` column link in matching rows
3. Expand the link prefix (see table below) to a full URL and WebFetch it for details

| File | Content |
|------|---------|
| `lexicon/contract.md` | data contract types, JSON Schema, DPP, document types |
| `lexicon/rust.md` | Rust SDK types, functions, patterns |
| `lexicon/js.md` | JS SDK types, functions, patterns |
| `lexicon/grpc.md` | gRPC services, messages, endpoints |

Primary: `lexicon/js.md`, `lexicon/grpc.md`. Link prefixes:

| Pre | URL |
|-----|-----|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `Y:` | `https://github.com/PastaPastaPasta/yappr/blob/master/` |
| `D:` | `https://github.com/PastaPastaPasta/dash-bridge/blob/master/` |
| `E:` | `https://github.com/dashpay/evo-sdk-website/blob/master/` |

## Client Init

```javascript
const client = new (require('dash')).Client({
  network: 'testnet',
  wallet: { mnemonic: '...' },
});
await client.connect();
```

## Operations

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

## WASM-DPP (Browser)

```javascript
import { DashPlatformProtocol } from '@dashevo/wasm-dpp';
const dpp = new DashPlatformProtocol();
```

Provides: contract/document validation, state transition creation/signing, identity key management.

## Security

**Pure JS SDK has NO client-side proof verification.** For security-critical apps use `wasm-sdk` (has proofs) or validate server-side with Rust SDK.

## Wallet

Built-in: HD derivation from mnemonic, UTXO management, tx creation/broadcasting, balance queries.

## Examples

- `PastaPastaPasta/yappr` — social app, document CRUD
- `PastaPastaPasta/dash-bridge` — bridge application
- `dashpay/evo-sdk-website` — SDK docs with examples
