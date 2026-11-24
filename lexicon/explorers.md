# Explorers Lexicon
<!-- Manually curated. API base URLs and status networks verified: 2026-11-24. -->
<!-- Sources: https://github.com/dashpay/insight-api, https://platform-explorer.com/api, https://testnet.platform-explorer.com/api -->

## Instances

| Service | Network | API base URL | Web UI | API documentation | Observed status network |
|---------|---------|--------------|--------|-------------------|-------------------------|
| Insight (Core/L1) | Mainnet | `https://insight.dash.org/insight-api/` | `https://insight.dash.org/insight/` | [Insight API](https://github.com/dashpay/insight-api#api-http-endpoints) | `info.network: "livenet"` |
| Insight (Core/L1) | Testnet | `https://insight.testnet.networks.dash.org/insight-api/` | `https://insight.testnet.networks.dash.org/insight/` | [Insight API](https://github.com/dashpay/insight-api#api-http-endpoints) | `info.network: "testnet"` |
| Platform Explorer (L2) | Mainnet | `https://platform-explorer.pshenmic.dev/` | `https://platform-explorer.com/` | [Mainnet API docs](https://platform-explorer.com/api) | `network: "evo1"` |
| Platform Explorer (L2) | Testnet | `https://testnet.platform-explorer.pshenmic.dev/` | `https://testnet.platform-explorer.com/` | [Testnet API docs](https://testnet.platform-explorer.com/api) | `network: "dash-testnet-51"` |

Append the paths below to the selected network's **API base URL**, not its UI or documentation URL. Platform Explorer's `/api` is a documentation page, not an API prefix.

Before using an instance, read `status?q=getInfo` for Insight or `status` for Platform Explorer and confirm the returned network matches the task. The status values above were observed on the verification date; testnet chain IDs may change after resets. Do not infer the network from sample identifiers or a documentation page's network label: older testnet docs may point to the mainnet backend. Check the selected network's current documentation for endpoint availability and parameters.

## Insight API Endpoints
REST + WebSocket explorer for Dash L1 (blocks, transactions, addresses, UTXOs, governance). Append endpoint to base URL.

| Keyword | Method | Description |
|---------|--------|-------------|
| `block/{hash}` | GET | Block by hash |
| `block-index/{height}` | GET | Block hash by height |
| `rawblock/{hash}` | GET | Raw block hex |
| `blocks?limit=N&blockDate=YYYY-MM-DD` | GET | Paginated blocks by date |
| `tx/{txid}` | GET | Transaction details |
| `rawtx/{txid}` | GET | Raw transaction hex |
| `txs/?block={hash}` | GET | Transactions in block |
| `txs/?address={addr}` | GET | Transactions for address |
| `addr/{addr}` | GET | Address details (optional `?noTxList=1`, `?from=N&to=N`) |
| `addrs/{addr1,addr2}` | GET | Multiple address details |
| `addr/{addr}/balance` | GET | Balance (satoshis) |
| `addr/{addr}/totalReceived` | GET | Total received |
| `addr/{addr}/totalSent` | GET | Total sent |
| `addr/{addr}/unconfirmedBalance` | GET | Unconfirmed balance |
| `addr/{addr}/utxo` | GET | Unspent outputs |
| `addrs/{addr1,addr2}/utxo` | GET | UTXOs for multiple addresses |
| `addrs/utxo` | POST | UTXOs via POST (`addrs` param) |
| `tx/send` | POST | Broadcast transaction (`rawtx` param) |
| `tx/sendix` | POST | Broadcast InstantSend tx (`rawtx` param) |
| `status?q=getInfo` | GET | Network info (also: `getDifficulty`, `getBestBlockHash`, `getBestChainLock`, `getLastBlockHash`) |
| `sync` | GET | Blockchain sync status |
| `peer` | GET | P2P peer status |
| `sporks` | GET | Spork configuration |
| `utils/estimatefee?nbBlocks=N` | GET | Fee estimation |
| `gobject/info` | GET | Governance parameters |
| `gobject/count` | GET | Proposal statistics |
| `gobject/list/proposal` | GET | Budget proposals list |
| `gobject/list/trigger` | GET | Budget triggers list |
| `gobject/get/{hash}` | GET | Proposal details |
| `gobject/check/{hexData}` | GET | Validate proposal |
| `gobject/deserialize/{hexData}` | GET | Parse proposal data |
| `gobject/votes/current/{hash}` | GET | Current proposal votes |
| `gobject/submit` | POST | Submit proposal |
| `governance/budget/{blockIndex}` | GET | Budget allocation |
| `messages/verify` | POST | Verify signed message |

### WebSocket
Socket.io on base host. Rooms: `inv` (events: `tx`, `txlock`, `block`), `sync` (event: `status`), `{dashAddress}` (address-specific updates).

## Platform Explorer API Endpoints
REST API for Dash Platform L2: identities, data contracts, documents, tokens, validators, contested resources. Append endpoint to API base URL.

Pagination: `?page=N&limit=N` (max 100). Sorting: `?order=asc|desc&order_by=...`. Responses JSON with `resultSet` + `pagination`.

| Keyword | Method | Description |
|---------|--------|-------------|
| `status` | GET | Network stats, epoch, API version |
| `epoch/{number}` | GET | Epoch info (TPS, validators) |
| `blocks` | GET | List blocks (filter: epoch, height, validator) |
| `block/{hash}` | GET | Block details |
| `transactions` | GET | List transactions (extensive filters) |
| `transaction/{hash}` | GET | Transaction details |
| `transaction/decode` | POST | Decode base64 state transition |
| `transaction/broadcast` | POST | Submit signed transaction |
| `transaction/wait` | POST | Poll for state transition completion |
| `dataContracts` | GET | List data contracts |
| `dataContract/{id}` | GET | Contract details |
| `dataContract/{id}/raw` | GET | Raw contract (base64) |
| `dataContract/{id}/documents` | GET | Documents in contract |
| `dataContract/{id}/transactions` | GET | Contract transactions |
| `dataContracts/rating` | GET | Contracts ranked by activity |
| `document/{id}` | GET | Latest document revision |
| `document/{id}/raw` | GET | Raw document (base64) |
| `document/{id}/revisions` | GET | Document version history |
| `identities` | GET | List identities |
| `identity/{id}` | GET | Identity details + balance |
| `identity/{id}/nonce` | GET | Identity contract nonce |
| `identity/{id}/transactions` | GET | Identity transactions |
| `identity/{id}/transfers` | GET | Identity transfers |
| `identity/{id}/withdrawals` | GET | Identity withdrawals |
| `identities/{id}/documents` | GET | Documents by identity |
| `identities/{id}/dataContracts` | GET | Contracts by identity |
| `identities/history` | GET | Registration trends |
| `dpns/identity?dpns={alias}` | GET | Lookup identity by DPNS name |
| `validators` | GET | List validators |
| `validator/{proTxHash}` | GET | Validator details |
| `validator/identity/{identityId}` | GET | Validator by masternode identity |
| `validator/{proTxHash}/blocks` | GET | Blocks by validator |
| `validator/{proTxHash}/stats` | GET | Validator stats over time |
| `validator/{proTxHash}/rewards/stats` | GET | Reward stats |
| `tokens` | GET | List tokens |
| `token/{id}` | GET | Token details |
| `token/{id}/transitions` | GET | Token transfers |
| `tokens/rating` | GET | Tokens ranked by activity |
| `identities/{id}/tokens` | GET | Tokens by identity |
| `contestedResources` | GET | Contested resources list |
| `contestedResources/stats` | GET | Voting statistics |
| `contestedResource/{value}` | GET | Contested resource details |
| `contestedResource/{value}/votes` | GET | Votes on resource |
| `masternodes/votes` | GET | Masternode voting activity |
| `search?query={value}` | GET | Search all entities |
| `rate` | GET | DASH/USD exchange rate |
| `transactions/history` | GET | Transaction volume over time |
| `transactions/gas/history` | GET | Gas usage trends |
