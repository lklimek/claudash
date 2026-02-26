---
name: dash-platform-contract
description: "Dash Platform data contracts, JSON Schema, DPP, document types, DPNS, indexing strategies, contract versioning. Use when designing or debugging data contracts."
---

# Dash Platform Data Contracts

Assist with designing, creating, and managing Dash Platform data contracts.

## Triggers

Activate when the user works with: data contracts, JSON Schema, DPP, document types, DPNS, contract versioning, document indexing.

## Project Setup

When building or working in the `dashpay/platform` repo, run the environment setup first:

```bash
bash scripts/setup-ai-agent-environment.sh
```

This configures the build environment, installs dependencies, and prepares the workspace for development.

## Reference Index

Read `index/contract.md` for type/function/pattern lookups. Expand link prefixes to full URLs before web-fetching:

| Prefix | Expands to |
|--------|-----------|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `B:` | `https://dashpay.github.io/platform/` |

When the index references a source or doc link, use WebFetch to retrieve the full content before answering.

## Knowledge

### Contract Structure

A data contract defines document types using JSON Schema. Each contract:
- Has a unique ID derived from the owner's identity and entropy
- Contains one or more document types
- Specifies indexes for efficient querying
- Can be versioned (contract updates)

### Document Types

Each document type in a contract defines:
- `type: "object"` with `properties` (JSON Schema)
- `indices` — array of index definitions for Platform queries
- `required` — required properties
- Optional: `additionalProperties: false`, `$comment`, `transient`, `documentsKeepHistoryContractDefault`

### Index Design

Indexes enable efficient queries on Platform. Rules:
- Each index has a `name` and `properties` array
- Properties specify `name` and sort order (`asc`/`desc`)
- `unique: true` enforces uniqueness
- First property in a compound index is the range scan key
- Maximum 10 indexes per document type
- System properties available: `$ownerId`, `$createdAt`, `$updatedAt`

### DPNS (Dash Platform Name Service)

DPNS maps human-readable names to identities:
- `domain` document type with `label`, `normalizedLabel`, `normalizedParentDomainName`, `records`
- `preorder` document type for commit-reveal registration
- Names are normalized (lowercase) for uniqueness

### Security Considerations

- Validate all contract schemas before submission
- Use `additionalProperties: false` to prevent data injection
- Consider document size limits and storage costs
- Index design affects query performance and cost
- Contract updates must be backward-compatible

### Versioning

- Contracts can be updated by the owner identity
- Updates create new versions; old versions remain queryable
- Adding properties is safe; removing/renaming is breaking
- Index changes may require migration strategies
