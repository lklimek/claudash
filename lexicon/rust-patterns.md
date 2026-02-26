## Patterns
| Keyword | Description | Example |
|---------|-------------|---------|
| `Fetch trait` | `T::fetch(&sdk, query).await?` → `Option<T>` with proof verification | [P:rs-sdk/src/platform/fetch.rs] |
| `FetchMany trait` | `T::fetch_many(&sdk, query).await?` → collection with proofs | [P:rs-sdk/src/platform/fetch_many.rs] |
| `Put traits` | `PutIdentity`, `PutContract`, `PutDocument` — broadcast state transitions | [P:rs-sdk/src/platform/] |
| `Query trait` | Types implementing `Query<R>` convert to gRPC requests; `Identifier`, `DocumentQuery`, etc. | [P:rs-sdk/src/platform/query.rs] |
| `Document transitions` | Builders for create, delete, replace, purchase, set_price, transfer | [P:rs-sdk/src/platform/documents/transitions/] |
| `Token builders` | Builders: mint, burn, transfer, freeze, unfreeze, destroy, purchase, set_price, claim | [P:rs-sdk/src/platform/tokens/builders/] |
| `DPNS usernames` | Query and register DPNS names, handle contested names | [P:rs-sdk/src/platform/dpns_usernames/] |
| `Proof verification` | All Fetch/FetchMany verify GroveDB proofs by default (security advantage over JS) | [P:rs-sdk/src/platform/fetch.rs] |
| `Mock testing` | `Sdk::new_mock()` with `MockResponse` trait for deterministic tests | [P:rs-sdk/src/mock/] |
| `Async runtime` | Fully async, requires `tokio` runtime | [P:rs-sdk/src/sdk.rs] |

## Examples
| Keyword | Description | File |
|---------|-------------|------|
| `read_contract` | Fetch a data contract by ID | [P:rs-sdk/examples/read_contract.rs] |
| `contested_names_with_contenders` | Query contested DPNS names and their contenders | [P:rs-sdk/examples/contested_names_with_contenders.rs] |
| `identity_contested_names` | Query contested names for an identity | [P:rs-sdk/examples/identity_contested_names.rs] |
| `dash-evo-tool` | Full GUI: identities, contracts, documents, tokens, voting, DPNS | [T:src/] |
