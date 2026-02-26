---
name: dash-platform-js
description: "JavaScript/TypeScript development with dash npm package, js-dash-sdk, wasm-dpp2, @dashevo/wasm-dpp, dapi-client. Use when writing JS/TS code that interacts with Dash Platform, browser apps, or Node.js services."
---

# Dash Platform JavaScript SDK

Assist with JavaScript/TypeScript development on Dash Platform using the `dash` npm package, `@dashevo/wasm-dpp`, and related libraries.

## Triggers

Activate when the user works with: `dash` npm package, `js-dash-sdk`, `js-evo-sdk`, `wasm-dpp2`, `@dashevo/wasm-dpp`, `dapi-client`, JavaScript/TypeScript + Dash Platform.

## Project Setup

When building or working in the `dashpay/platform` repo, run the environment setup first:

```bash
bash scripts/setup-ai-agent-environment.sh
```

This configures the build environment, installs dependencies, and prepares the workspace for development.

## Reference Index

Read `index/js.md` and `index/grpc.md` for type/function/pattern lookups. Expand link prefixes to full URLs before web-fetching:

| Prefix | Expands to |
|--------|-----------|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `G:` | `https://dashpay.github.io/platform/api/grpc/` |
| `B:` | `https://dashpay.github.io/platform/` |
| `Y:` | `https://github.com/PastaPastaPasta/yappr/blob/master/` |
| `D:` | `https://github.com/PastaPastaPasta/dash-bridge/blob/master/` |
| `E:` | `https://github.com/dashpay/evo-sdk-website/blob/master/` |

When the index references a source or doc link, use WebFetch to retrieve the full content before answering.

## Knowledge

### SDK Setup

```bash
npm install dash
```

### Client Initialization

```javascript
const Dash = require('dash');

const client = new Dash.Client({
  network: 'testnet',
  wallet: {
    mnemonic: 'your twelve word mnemonic phrase here...',
  },
});

await client.connect();
```

### Identity Operations

```javascript
// Create identity
const identity = await client.platform.identities.register();

// Retrieve identity
const identity = await client.platform.identities.get(identityId);
```

### Data Contract Operations

```javascript
// Register a contract
const contractDocuments = {
  note: {
    type: 'object',
    properties: {
      message: { type: 'string', maxLength: 256 },
    },
    additionalProperties: false,
  },
};

const contract = await client.platform.contracts.create(contractDocuments, identity);
await client.platform.contracts.publish(contract, identity);
```

### Document Operations

```javascript
// Create document
const document = await client.platform.documents.create(
  'contractId.note',
  identity,
  { message: 'Hello Dash Platform' }
);
await client.platform.documents.broadcast({ create: [document] }, identity);

// Query documents
const documents = await client.platform.documents.get('contractId.note', {
  where: [['$ownerId', '==', identity.getId()]],
  orderBy: [['$createdAt', 'desc']],
});
```

### DPNS Name Registration

```javascript
await client.platform.names.register(
  'alice.dash',
  { dashUniqueIdentityId: identity.getId() },
  identity
);

const name = await client.platform.names.resolve('alice.dash');
```

### WASM-DPP (Browser Usage)

For browser environments, use `@dashevo/wasm-dpp`:

```javascript
import { DashPlatformProtocol } from '@dashevo/wasm-dpp';

const dpp = new DashPlatformProtocol();
// Use for client-side validation, state transition creation
```

The `wasm-dpp` package provides:
- Data contract validation
- Document validation
- State transition creation and signing
- Identity key management

### Security Caveats

**Important**: The pure JS SDK does NOT perform client-side proof verification like the Rust SDK does. For security-critical applications:
- Use the WASM SDK (`wasm-sdk`) which includes proof verification
- Or validate responses server-side using the Rust SDK
- Never trust unverified responses in high-value transactions

### Real-World Examples

- **yappr** (`PastaPastaPasta/yappr`) — Social app demonstrating document CRUD
- **dash-bridge** (`PastaPastaPasta/dash-bridge`) — Bridge application
- **evo-sdk-website** (`dashpay/evo-sdk-website`) — SDK documentation site with examples

### Wallet Integration

The JS SDK includes wallet functionality:
- HD wallet derivation from mnemonic
- UTXO management
- Transaction creation and broadcasting
- Balance queries
