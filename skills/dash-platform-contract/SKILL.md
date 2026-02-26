---
name: dash-platform-contract
description: "Dash Platform data contracts, JSON Schema, DPP, document types, DPNS, indexing strategies, contract versioning. Use when designing or debugging data contracts."
---

Assist with Dash Platform data contract design, creation, and management.

## Setup

In `dashpay/platform` repo: `bash scripts/setup-ai-agent-environment.sh`

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

Primary: `lexicon/contract.md`. Link prefixes:

| Pre | URL |
|-----|-----|
| `P:` | `https://github.com/dashpay/platform/blob/master/packages/` |
| `R:` | `https://dashpay.github.io/platform/api/rust/` |
| `B:` | `https://dashpay.github.io/platform/` |

## Contract Structure

- Defines document types via JSON Schema; unique ID from owner identity + entropy
- Contains ≥1 document types with indexes for querying
- Versionable (owner can update; old versions remain queryable)

## Document Types

Each type defines:
- `type: "object"` + `properties` (JSON Schema)
- `indices` — index definitions for Platform queries
- `required` — required fields
- Optional: `additionalProperties: false`, `$comment`, `transient`, `documentsKeepHistoryContractDefault`

## Document Index Design

- `name` + `properties` array (each: `name` + `asc`/`desc`)
- `unique: true` for uniqueness constraints
- First property = range scan key in compound indexes
- Max 10 per document type
- System props: `$ownerId`, `$createdAt`, `$updatedAt`

## DPNS

Maps names → identities:
- `domain` type: `label`, `normalizedLabel`, `normalizedParentDomainName`, `records`
- `preorder` type: commit-reveal registration
- Normalized (lowercase) for uniqueness

## Security

- Always set `additionalProperties: false`
- Validate schemas before submission
- Consider size limits and storage costs
- Contract updates must be backward-compatible (add props OK, remove/rename breaks)
