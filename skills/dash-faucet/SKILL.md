---
name: dash-faucet
description: "Use when the user wants testnet DASH/tDASH from Pasta's faucet for a Dash testnet address."
user-invocable: true
---

Request testnet DASH from Pasta's funded faucet at `https://faucet.thepasta.org`.

First check the live faucet settings:

```bash
curl https://faucet.thepasta.org/api/status
```

Then request one faucet payout:

```bash
curl -X POST https://faucet.thepasta.org/api/core-faucet \
  -H 'Content-Type: application/json' \
  -d '{"address":"TESTNET_DASH_ADDRESS","capToken":"CAP_TOKEN"}'
```

Use the `capEndpoint` from `/api/status` to get the CAP token. If the faucet responds with HTTP `429` and asks for hard captcha, use `hardCapEndpoint` and retry once with:

```json
{"address":"TESTNET_DASH_ADDRESS","capToken":"CAP_TOKEN","hardCapToken":"HARD_CAP_TOKEN"}
```

Each successful `/api/core-faucet` request sends the live `coreFaucetAmount` from `/api/status` (currently 1 tDASH). For larger amounts, repeat normal requests until the target is reached or the faucet rate-limits/refuses.

Do not bypass rate limits, rotate IPs, fabricate captcha tokens, or use unsupported request fields such as `amount` or `promoCode`; Pasta's live faucet API ignores/does not expose those for `/api/core-faucet`.
