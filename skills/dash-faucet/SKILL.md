---
name: dash-faucet
description: "Use when the user wants testnet DASH/tDASH from a Dash testnet faucet for a Dash testnet address."
user-invocable: true
---

Request testnet DASH from a funded faucet. Primary: `https://faucet.thepasta.org`. Fallback (if Pasta is down): `https://faucet.testnet.networks.dash.org` — same backend (`PastaPastaPasta/dash-faucet`) and API, but additionally sits behind an Anubis anti-bot PoW gate (see below).

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

Use the `capEndpoint` from `/api/status` to get the CAP token (see PoW below). If the faucet responds with HTTP `429` and asks for hard captcha, use `hardCapEndpoint` and retry once with:

```json
{"address":"TESTNET_DASH_ADDRESS","capToken":"CAP_TOKEN","hardCapToken":"HARD_CAP_TOKEN"}
```

Each successful `/api/core-faucet` request sends the live `coreFaucetAmount` from `/api/status` (currently 1 tDASH). For larger amounts, repeat normal requests until the target is reached or the faucet rate-limits/refuses (`rateLimitPerHour`).

Do not bypass rate limits, rotate IPs, fabricate captcha tokens, or use unsupported request fields such as `amount` or `promoCode`; the faucet API ignores/does not expose those for `/api/core-faucet`.

## Solving the CAP.js v4 proof-of-work (`capToken`)

`capEndpoint` gates the faucet behind a proof-of-work captcha, not a plain token:

1. `POST {capEndpoint}challenge` (use a browser `User-Agent` — plain curl UAs get 403) → `{challenge:{c,s,d}, token}` (`c` = challenge count, `s` = salt length, `d` = target length).
2. For `i` in `1..=c`: `salt = prng(f"{token}{i}", s)`, `target = prng(f"{token}{i}d", d)`; brute-force `nonce` (int, from 0) where `sha256(salt + str(nonce)).hexdigest()` starts with `target`.
3. `POST {capEndpoint}redeem {"token": token, "solutions": [nonces...]}` → `{"token": capToken}`.

`prng(seed, len)`: seed an xorshift32 generator with `fnv1a(seed)` (standard 32-bit FNV-1a), then repeatedly step (`x ^= x<<13; x ^= x>>>17; x ^= x<<5`, 32-bit wraparound each op) emitting each state as an 8-hex-char word; concatenate words and truncate to `len`. Typically `c=80-100, d=4` — a few seconds single-threaded.

## Anubis anti-bot gate (fallback faucet only)

`faucet.testnet.networks.dash.org` additionally proxies through [Techaro Anubis](https://github.com/TecharoHQ/anubis). A `POST /api/core-faucet` without a valid Anubis session returns a 200 HTML challenge page (not JSON) plus a `techaro.lol-anubis-cookie-verification` cookie — keep a cookie jar for the whole flow:

1. Parse the `<script id="anubis_challenge" type="application/json">` block from that HTML page: `rules.difficulty`, `challenge.id`, `challenge.randomData`.
2. Brute-force `nonce = 0, 1, 2, ...` where `sha256(randomData + str(nonce))`'s digest bytes start with `difficulty // 2` zero bytes (plus, if `difficulty` is odd, the following byte's top nibble must also be zero).
3. `GET /.within.website/x/cmd/anubis/api/pass-challenge?id=<id>&response=<hex_digest>&nonce=<nonce>&elapsedTime=<ms>&redir=%2F`, same cookie jar. `redir` is required — omitting it 400s with "Invalid redirect". The 302 response sets the real `techaro.lol-anubis-auth` JWT cookie (~24h validity).
4. Retry the original `/api/core-faucet` POST with that cookie jar attached.

If the target's Anubis version differs, confirm the hash/target logic against its own `/.within.website/x/cmd/anubis/static/js/worker/sha256-<algo>.mjs` before trusting the above.
