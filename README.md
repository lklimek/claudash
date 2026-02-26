# claudash

**Give Claude full knowledge of Dash Platform.** Data contracts, Rust SDK, JS/TS SDK, gRPC API — thousands of indexed entries so Claude can write correct code, answer API questions, and navigate the platform monorepo without hallucinating.

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code/plugins) for [Dash Platform](https://docs.dash.org/projects/platform/) developers.

## What is Dash Platform?

[Dash Platform](https://www.dash.org/platform/) is a decentralized application layer built on the Dash network. It provides decentralized data storage (Drive), a gRPC API layer (DAPI), user identities, data contracts (schema-defined documents stored on-chain), and a name service (DPNS). Developers build on it using the Rust SDK (`dash-sdk` + `dpp`) or the JS/TS SDK (`dash` npm package). The entire stack lives in the [dashpay/platform](https://github.com/dashpay/platform) monorepo — 30+ packages spanning Rust, JavaScript, and protobuf definitions.

## The Problem

Dash Platform has a rich API surface, but the developer experience has real friction:

- **Documentation is fragmented** across docs.dash.org, rustdoc, proto files, and multiple GitHub repos
- **The Rust SDK isn't on crates.io** or docs.rs — types are deeply nested across `dash-sdk`, `dpp`, `rs-dapi-client`, and `dapi-grpc`
- **The monorepo is massive** — finding the right type, trait, or query pattern means knowing which of 30+ packages to look in
- **API surface is large** — thousands of public Rust types/functions, hundreds of gRPC RPCs and messages, hundreds of JS SDK exports and contract types
- **Community resources are limited** — fewer tutorials, examples, and Stack Overflow answers compared to larger blockchain ecosystems

When you ask a vanilla LLM about Dash Platform, it guesses. Often wrong.

## The Solution

claudash ships a **lexicon** — pre-indexed lookup tables generated from actual source code — plus a skill that teaches Claude how to use them. When you ask about Dash Platform, Claude greps the lexicon for matching types and functions, then fetches the exact source file for details.

**What's indexed:**

| Lexicon | Entries | Coverage |
|---------|---------|----------|
| **Rust SDK** | ~2,900 | Every public type, function, and trait from `dash-sdk`, `dpp`, `rs-dapi-client`, `dapi-grpc` |
| **Rust Patterns** | ~40 | Real-world SDK usage patterns and examples from `dash-evo-tool`, `yappr`, `dash-bridge` |
| **JS/TS SDK** | ~500 | Types, options, facades, query interfaces from the `dash` npm package and `wasm-dpp` |
| **Data Contracts** | ~240 | Contract types, document schemas, state transitions, token config, groups, voting |
| **gRPC API** | ~320 | All 3 services, RPCs, request/response message types |

This means Claude can help you:

- **Write data contracts** with correct JSON Schema, indexes, and security settings
- **Use the Rust SDK** — `Fetch`/`FetchMany` traits, `DocumentQuery` builders, proof verification, state transitions, token operations
- **Use the JS SDK** — client initialization, identity/contract/document CRUD, DPNS registration, wallet management
- **Call gRPC endpoints** directly with correct message types
- **Navigate the monorepo** — find the right package, type, or function instantly

## Install

Add the marketplace, then install the plugin:

```
/plugin marketplace add lklimek/claudash
/plugin install dash-platform@claudash
```

Alternatively, install from a local clone:

```bash
claude plugin install /path/to/claudash

# Or load for a single session
claude --plugin-dir /path/to/claudash
```

## Usage

The `dash-platform` skill activates automatically when your conversation involves Dash Platform development. Just ask:

```
> How do I fetch a document by owner ID using the Rust SDK?
> Write a data contract for a social media app with posts and comments
> What gRPC endpoint do I use to query identities?
> Show me how to register a DPNS name in JavaScript
```

### Update the Lexicon

To regenerate lookup tables from the latest source code:

```
/dash-platform:update-lexicon
```

This clones the source repos, runs rustdoc, and spawns agents to re-index everything. Run this when Dash Platform releases a new version.

## How It Works

```
User asks about Dash Platform
        │
        ▼
┌─────────────────────┐
│  dash-platform skill │  ← activates on relevant context
└─────────┬───────────┘
          │ grep lexicon/*.md for keywords
          ▼
┌─────────────────────┐
│   Lexicon tables     │  ← ~4,000 entries with source links
│   rust.md            │
│   js.md              │
│   contract.md        │
│   grpc.md            │
└─────────┬───────────┘
          │ WebFetch source links for details
          ▼
┌─────────────────────┐
│  Accurate answer     │  ← grounded in real source code
│  with code examples  │
└─────────────────────┘
```

The lexicon files use **abbreviated link prefixes** to save tokens:

| Prefix | Points to |
|--------|-----------|
| `P:` | `github.com/dashpay/platform/blob/master/packages/…` |
| `R:` | `dashpay.github.io/platform/api/rust/…` |
| `G:` | `dashpay.github.io/platform/api/grpc/…` |
| `T:` | `github.com/dashpay/dash-evo-tool/blob/master/…` |

Skills expand these to full URLs before fetching.

## What's Covered

### Data Contracts
Contract structure, document types, JSON Schema properties, index design (compound, unique, range), DPNS name service, security best practices, versioning rules.

### Rust SDK (`dash-sdk` + `dpp`)
Core types (`Sdk`, `Identity`, `DataContract`, `Document`, `Identifier`), CRUD via `Fetch`/`FetchMany` traits, query builders (`DriveQuery`, `DocumentQuery`), cryptographic proof verification, state transitions, token operations (mint, burn, freeze, transfer), document marketplace, group actions, contested resource voting.

### JS/TS SDK (`dash` npm + `wasm-dpp`)
Client initialization, identity registration, contract creation and publishing, document CRUD, DPNS names, wallet (HD derivation, UTXO management), WASM-DPP for browser validation. Includes the critical note that **pure JS SDK lacks client-side proof verification** — use `wasm-sdk` for security-critical apps.

### gRPC API
Complete service definitions, all RPC endpoints, request/response message schemas, masternode voting, protocol upgrades, chain status, epoch info.

## Project Structure

```
claudash/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest
│   └── marketplace.json     # Marketplace listing
├── skills/
│   ├── dash-platform/       # Main development skill
│   └── update-lexicon/      # Lexicon regeneration skill
├── lexicon/                 # Auto-generated lookup tables (do not edit)
│   ├── rust.md              # Rust SDK entries
│   ├── rust-patterns.md     # SDK usage patterns & examples
│   ├── js.md                # JS/TS SDK types & patterns
│   ├── contract.md          # Data contract types
│   └── grpc.md              # gRPC services & RPCs
└── scripts/                 # Lexicon generation tooling
    ├── clone-repos.sh       # Clone source repos to .repos/
    ├── gen-rustdoc-json.sh  # Generate rustdoc JSON
    └── gen-rust-lexicon.py  # Parse rustdoc JSON → lexicon tables
```

## Development

```bash
# Validate the plugin
claude plugin validate .

# Test locally
claude --plugin-dir .

# Refresh lexicon from source
/dash-platform:update-lexicon
```

## Related

**[claudius](https://github.com/lklimek/claudius)** — opinionated dev lifecycle toolkit with agents and skills. claudash provides domain knowledge; claudius provides the workflow. They're better together.

## License

GPL-3.0. See [LICENSE](LICENSE).
