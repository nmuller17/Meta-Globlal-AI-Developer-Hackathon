<p><img src="docs/img/doubloon-logo.png" alt="Doubloon" width="240"></p>

# Doubloon

**We monetize the web for agentic traffic.**
*Any website. Any AI agent. Any piece of information. One payment.*

Meta Global AI Developer Hackathon 2026 · Startup track · Theme: Build for Your World · Maximilien Rambaud, Cosme de Ranieri, Aristote Pellissier, Nathanaël Muller

AI agents are the web's fastest-growing audience: about 1.7% of web activity in 2026, a quarter of web traffic expected by 2035 (DataDome, June 2026; Cisco, 2026). They read pages without seeing ads or paying, so websites earn almost nothing from them, and blocking agents is their only safe default. On the other side, an agent that needs one precise figure can only scrape public pages, or buy a whole report built for humans, which it cannot do on its own.

Doubloon makes every website **payable for all AI agent readers**. A content owner pastes its URL, and in about 60 seconds its content becomes data that any AI agent can discover, negotiate for and buy, with no code. For publishers, it is a **new revenue stream** from an audience that never sees an ad. For buyers, it is **access to information without buying the whole report**: one figure for 0.10 USDC, a small table for 0.50, a full section for 2.00, while the rest of the report stays protected.

**Meta's Muse Spark does the language work.** It writes the catalog that agents browse, turns prices written in plain words into a price table, negotiates with buyer agents as the publisher's sales agent, and decides for our buyer agent whether an offer fits its mission. Code then checks every one of its answers: **a language model may propose, but only code decides price, permission and money.**

Every sale runs on **x402**, the open protocol that finally puts HTTP's `402 Payment Required` to work. The agent receives an invoice, signs a payment and gets the data in seconds, settled in **USDC on the Base blockchain**. Every transaction is public and verifiable, and the publisher is paid before any data leaves.

| At a glance | |
| --- | --- |
| Meta model | Muse Spark (`muse-spark-1.3`) on the Meta Model API, in four roles: [how Doubloon uses it](#how-doubloon-uses-muse-spark) |
| Proof | 64 payments settled on-chain, 2 of them on Base mainnet with real USDC: [on-chain evidence](payments/docs/ONCHAIN_EVIDENCE.md) |
| Demo publisher | [velstrand-research.vercel.app](https://velstrand-research.vercel.app), a fictional research firm |
| Tests | 173 automated tests, with no API key and no funded wallet |

---

## Contents

1. [Proof it works](#proof-it-works)
2. [Who it is for](#who-it-is-for)
3. [How it works](#how-it-works)
4. [How Doubloon uses Muse Spark](#how-doubloon-uses-muse-spark)
5. [Why x402 and the blockchain](#why-x402-and-the-blockchain)
6. [Security and compliance](#security-and-compliance)
7. [The demo](#the-demo)
8. [Use your own AI assistant as a buyer](#use-your-own-ai-assistant-as-a-buyer)
9. [Deployment](#deployment)
10. [Test cases](#test-cases)
11. [Repository map and tech stack](#repository-map-and-tech-stack)
12. [Limits and roadmap](#limits-and-roadmap)

---

## Proof it works

Real payments, not mock-ups, verifiable by anyone on a public block explorer:

- **64 payments settled on-chain**: 62 on Base Sepolia (39.21 test USDC, 17 to 19 October 2026) and 2 on Base mainnet with real USDC.
- **A full product sale on Base mainnet**: agent identity check, sales agent negotiation, LLM decision, code guards, x402 payment, delivery after settlement, for 0.10 USDC: [transaction on basescan.org](https://basescan.org/tx/0xc70ea043716023f1e76ef26dac5e27c814d51ae0ca541d797ee249c949d36f8f).
- **A 2.00 USDC sale paid only after human approval**: [transaction on Base Sepolia](https://sepolia.basescan.org/tx/0xb59df8f6496f54d360c487d052cc10fa888a9cb6b97664d1fe2a8552050d80ea).
- **173 automated tests** across gateway, ingestion, payments, buyer agent and MCP connector.

The full list is read from the chain itself, not from our database: [payments/docs/ONCHAIN_EVIDENCE.md](payments/docs/ONCHAIN_EVIDENCE.md). These payments were recorded before the switch to Muse Spark; the payment code they exercise did not change in the switch.

The demo publisher is **Velstrand Research**, a fictional research firm whose company names and figures are invented: [velstrand-research.vercel.app](https://velstrand-research.vercel.app).

---

## Who it is for

Three types of content owners cannot get paid by AI agents today:

| Content owner | Earns from | Why agents don't pay | Order |
| --- | --- | --- | --- |
| **Research and data providers** (market studies, reports, datasets) | Reports sold for thousands of euros | Agents need one figure, not a whole report | **Now, initial focus** |
| Subscription publishers (news, magazines, professional databases) | Monthly or yearly subscriptions | Agents need one article, not a subscription | Next |
| Ad-funded websites (news, blogs, reviews) | Ads shown to human readers | Agents read the page but never see an ad | Then |

**Business model.** Publishers set their prices and keep them in full. Doubloon's planned revenue is a fixed fee of 0.01 USD per transaction, paid by the buyer on top of the publisher's price. The prototype does not charge this fee yet.

---

## How it works

### For the publisher: about 60 seconds, no code

1. **Paste the website URL.** Doubloon crawls it (respecting `robots.txt`), reads HTML pages and PDF reports, and splits them into sections.
2. **Review the catalog.** Muse Spark describes each section by topic, region, period and type of data, without any figure. Mark each section *Sell*, *Free* or *Private*. Pages that look internal are detected and kept private. Agents only ever see titles and topics, never a figure.
3. **Write prices in plain words**, such as "one figure at $0.10, a small table at $0.50, a full section at $2.00". Muse Spark turns them into a price table that the publisher confirms. From then on, every check uses that confirmed table.
4. **Connect a wallet and go live.** A signed manifest tells agents what is for sale and where to pay. USDC goes straight to the publisher's wallet, and a dashboard shows every sale with its audit trail.

### For the buyer agent: a sale in six steps

1. **Discover.** Read the publisher's signed manifest (`/.well-known/ai-data.json`) and check the signature.
2. **Identify (KYA, Know Your Agent).** Sign a one-time code with its wallet. The wallet is screened against the US sanctions list.
3. **Negotiate.** Explain the need to the publisher's sales agent, Muse Spark seeing only titles and topics, never the figures. Code checks every offer: price, tier, and that no paid figure leaks.
4. **Decide.** Muse Spark weighs the offer against the buyer's mission. Code checks the budget, the per-purchase cap and daily limits. Above 1.00 USDC, the owner must say yes.
5. **Pay (x402).** Receive a `402` invoice, sign a USDC transfer (EIP-3009); a facilitator settles it on Base and pays the gas.
6. **Deliver.** Only after settlement: the data, watermarked for the buyer, with a license receipt signed by the publisher.

### Architecture

```
   PUBLISHER WEBSITE              META MODEL API (MUSE SPARK)       BUYER AGENT
   pages, PDF reports             metadata, pricing rules,          our Muse Spark agent, or
                                  sales agent, buyer choice         any assistant through MCP
          | crawl                          | structured JSON                 | HTTP + x402
          v                                v                                 v
+------------------------------------------------------------------------------------------+
|                               DOUBLOON GATEWAY (FastAPI)                                  |
|   Ingestion                  Discovery and sales                 Payments                 |
|   crawler, catalog,          signed manifest, KYA, sales         x402 paid routes,        |
|   leak filter                agent, offer checks, live events    settle first, receipts   |
|   Compliance: sanctions screening, SHA-256 audit chain, signed receipts, watermark        |
|   Shared SQLite: catalog, offers, transactions, events                                    |
+------------------------------------------------------------------------------------------+
          | REST + live events             | balanceOf                       | /verify, /settle
          v                                v                                 v
   WEB APP (Next.js)              BASE (USDC contract)  <-----------  x402 FACILITATOR
   onboarding, live view,         public record of sales             submits the transfer,
   dashboard, MetaMask                                               pays the gas
```

Every step emits an event. The live view and the audit trail are built only from these events, so what the screen shows is what happened. The payment flow and its algorithms are in [payments/docs/PAYMENTS.md](payments/docs/PAYMENTS.md), the sales agent guarantees in [gateway/README.md](gateway/README.md).

---

## How Doubloon uses Muse Spark

Doubloon calls Muse Spark (`muse-spark-1.3`) through the Meta Model API's Chat Completions endpoint, with the OpenAI SDK. Every call asks for **structured output against a strict JSON schema** generated from a Pydantic model, so each answer arrives as a typed object that code checks field by field. Free text never sets a price, a permission or a payment.

| Role | Where | What Muse Spark does | What code checks next | Without the model |
| --- | --- | --- | --- | --- |
| Catalog writer | `ingestion/catalog.py` | Describes each section: topic, region, period, data types, sensitivity, suggested tier | The leak filter redacts any paid figure; internal pages stay private whatever the model says | Heuristic metadata |
| Pricing rules | `gateway/routers/rules.py` | Turns "one figure at $0.10, a small table at $0.50..." into a tier table | Each price must match a paid route; the publisher confirms the table | Deterministic parser |
| Sales agent | `gateway/sales_agent.py` | Talks with buyer agents from catalog metadata only, and proposes one offer | Exact tier price, tier floor, sellable content, daily limit, leak filter; one retry with the errors, else a safe refusal | Safe refusal, no sale |
| Buyer agent | `buyer-agent/agent.py` | Accepts, counters or refuses an offer against its owner's mission | Budget, per-purchase cap, human approval threshold, daily and hourly caps, every invoice field before signing | Rule-based decision; refusal if a call fails |

- **Reasoning effort per role**: low for the sales agent, the buyer agent and the catalog (many short calls), medium for the pricing rules (one call, confirmed by the publisher). Set with `SALES_AGENT_EFFORT` and `RULES_PARSER_EFFORT`.
- **One client for every role**: [shared/model_api.py](shared/model_api.py). `LLM_MODEL` picks the Muse Spark version, and `MODEL_API_BASE_URL` can point the same code at another OpenAI-compatible host serving Meta's open-weights models.
- **Tested without a key**: [gateway/tests/test_llm.py](gateway/tests/test_llm.py) runs the real SDK against a simulated Meta Model API. It checks the request, that every schema meets Meta's strict-mode rules, and that any unusable answer (error, invalid JSON, cut-off answer, refusal) is refused.

---

## Why x402 and the blockchain

- **x402 lets machines pay machines over plain HTTP.** One purchase is four messages: request, `402` invoice, retry with a signed payment, content with its receipt. No account, no card, no checkout page.
- **No fixed fee.** x402 has no protocol fee and settlement on Base costs a fraction of a cent, so a sale of a few cents stays profitable where card fees would eat it.
- **Instant, final settlement.** USDC reaches the publisher in seconds, with no monthly payouts and no chargebacks.
- **EIP-3009 signatures** authorise one exact transfer (amount, recipient, 120-second window, single-use nonce). The agent needs no gas: the facilitator submits the transfer.
- **The blockchain is the receipt.** Every sale is public and verifiable by the publisher, the buyer and any auditor, without trusting our database.
- **Same code on testnet and mainnet.** Moving from Base Sepolia to Base mainnet is configuration only, and has been done.

---

## Security and compliance

Code, not AI, decides every price, permission and payment.

| Question | Answer | How |
| --- | --- | --- |
| Can anyone get paid data without paying? | No | Content leaves only after on-chain settlement, to the paying wallet. The sales agent never sees paid content, and a leak filter checks every message |
| Can a wallet pay the wrong amount or party? | No | The invoice is fixed server-side, the buyer checks every field against the signed manifest, and each payment is unique (replay refused with 409) |
| Can an agent spend more than its owner allows? | No | Budget (5.00 USDC), per-purchase cap (2.50), daily and hourly caps are checked in code before signing. A human approves anything above 1.00 USDC |

Main controls:

| Risk | Control | Where |
| --- | --- | --- |
| Fake agent, sanctioned or blocked wallet | KYA signature on a single-use nonce, OFAC SDN screening (Chainalysis oracle), short session bound to the identity | `gateway/routers/kya.py`, `shared/sanctions.py` |
| Fake payment address | The publisher signs its manifest; the buyer pins the signer and refuses a changed or unsigned one | `shared/signing.py`, `buyer-agent/agent.py` |
| Sales agent leaks or misprices | It sees metadata only. Deterministic checks on tier, exact price, sellable content, daily limit and leaks before any offer reaches the buyer | `gateway/sales_agent.py`, `ingestion/leak_filter.py` |
| Prompt injection | Buyer text is untrusted data, flagged and logged; prices come from the confirmed table only | `gateway/sales_agent.py` |
| Client changes the amount, replays a payment | Invoice rebuilt server-side, payer must be the KYA wallet, unique nonce and offer | `payments/router.py`, `payments/store.py` |
| Data taken without paying, or paid but not delivered | Settlement before delivery; recovery from the chain after a crash; 24-hour re-download | `payments/router.py`, `payments/recovery.py` |
| Agent overspends or splits purchases | Spending limits in code, near-threshold splitting forces approval, signing ceiling in the x402 client | `buyer-agent/agent.py`, `buyer-mcp/server.py` |
| History rewritten, proof of sale, resale | SHA-256 audit chain, publisher-signed license receipt, per-buyer watermark | `shared/audit_chain.py`, `payments/watermark.py` |
| Personal data kept forever | Conversations erased after 30 days and on request; payment records kept (AML) | `shared/retention.py` |
| Setup, dashboards or buyer controls exposed | Owner only: a caller on the gateway's machine, or an owner token | `shared/owner.py`, `payments/buyer_router.py` |
| Secrets | `.env` (git-ignored) and encrypted keystores; confidential values masked in every logged event | `shared/events.py`, `scripts/encrypt_keys.py` |

Every control, with its code, its tests and the regulation behind it (OFAC, GDPR, AML record keeping, China PIPL): [docs/SECURITY_AND_COMPLIANCE.md](docs/SECURITY_AND_COMPLIANCE.md). Buyer permission tiers and the risk register: [payments/docs/SECURITY_P3.md](payments/docs/SECURITY_P3.md).

---

## The demo

Three minutes, on the web app's onboarding, live view and dashboard.

1. **A publisher goes live.** Paste the Velstrand URL. Muse Spark writes the catalog ("Internal notes" is already private), then turns prices written in plain words into a price table. Connect the wallet, go live.
2. **A Muse Spark buyer agent buys.** Its mission: "find the 2025 European market share of the leading battery manufacturer". It discovers the site, proves its identity, negotiates with the Muse Spark sales agent, gets an offer at 0.10 USDC, pays, and receives the figure with its transaction link. The live view shows each purchase as a conversation between the two agents.
3. **A bigger purchase needs the owner.** Mission: "get the full methodology section of the 2025 European battery market report". A full section at 2.00 USDC is above the 1.00 limit, so the agent waits until its owner clicks **Approve** in the live view.
4. **Security.** A prompt injection is caught on screen: no figure revealed, prices unchanged.
5. **The publisher gets paid.** The dashboard shows revenue, each sale with its audit trail, and the blockchain payment history.

Each mission starts from a button in the live view (**▶ Small purchase**, **▶ Big purchase**, **▶ Attack**), which runs the buyer agent inside the gateway (`POST /buyer/run`, owner only), so its steps reach the live view. One mission buys one section. Anyone's own AI assistant can play the buyer instead, through the [MCP connector](#use-your-own-ai-assistant-as-a-buyer). Run sheet: [frontend/DEMO.md](frontend/DEMO.md).

Backup: with mock data (`NEXT_PUBLIC_USE_MOCKS=true`), the same buttons replay the story without a gateway or a wallet.

---

## Use your own AI assistant as a buyer

`buyer-mcp/` is an MCP server. Add it to any MCP client and your own assistant becomes a buyer agent:

| Tool | What it does |
| --- | --- |
| `search_data(question)` | Reads the manifest and the free catalog summary |
| `ask_seller(message)` | Proves the wallet identity on first use, then talks to the sales agent and returns any offer with a budget verdict |
| `buy(offer_id, owner_approved)` | Checks the offer and the invoice, signs the x402 payment, returns the data and the explorer link |
| `wallet_status()` | Wallet, on-chain USDC balance, budget left, receipts |

Money is never left to the LLM: only offers the sales agent really made can be bought, the price comes from that offer, and budget, cap and invoice are checked in code with the same guards as our buyer agent. Setup: [buyer-mcp/README.md](buyer-mcp/README.md).

---

## Deployment

### 1. Local deployment (what the demo runs)

Requirements: Python 3.11+ (a native build for your CPU), Node 20+, a [Meta Model API](https://dev.meta.ai/docs/models) key, and test USDC on Base Sepolia for the buyer wallets ([faucet.circle.com](https://faucet.circle.com)).

```bash
# 1. Backend
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt -r payments/requirements.txt -r ingestion/requirements.txt -r buyer-mcp/requirements.txt
cp .env.example .env                        # set JWT_SECRET (32+ chars) and MODEL_API_KEY
.venv/bin/python scripts/create_wallets.py  # publisher + 4 buyer wallets, then fund the buyers
.venv/bin/python scripts/encrypt_keys.py --apply --rewrite-env   # move keys to encrypted keystores
.venv/bin/python scripts/check_funds.py
.venv/bin/uvicorn gateway.main:app --port 8000

# 2. Simulated publisher site (or use https://velstrand-research.vercel.app)
.venv/bin/python site-demo/serve.py --port 8001   # local scan needs SCAN_ALLOW_PRIVATE_HOSTS=1

# 3. Web app
cd frontend && npm install
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000 npm run dev   # http://localhost:3000

# 4. Before a demo
.venv/bin/python scripts/preflight.py       # config, gateway, catalog, facilitator, RPC, balances, audit chain
```

- `LLM_MODEL` (default `muse-spark-1.3`) and `MODEL_API_BASE_URL` (default `https://api.meta.ai/v1`) are optional.
- Without `NEXT_PUBLIC_GATEWAY_URL`, the web app runs on built-in mock data, with a "mock data" badge in the navigation.
- Interactive API docs of the running gateway: http://localhost:8000/docs.
- To let your own assistant buy, add the connector to an MCP client: [buyer-mcp/README.md](buyer-mcp/README.md).

### 2. Base mainnet, real USDC

Same code, configuration only. Create `.env.mainnet` with the mainnet values below and dedicated mainnet wallets (`scripts/create_wallets.py --env-file .env.mainnet --buyers 1`), then prefix every command with `scripts/mainnet.sh`, for example `scripts/mainnet.sh .venv/bin/uvicorn gateway.main:app --port 8000`.

| Setting | Testnet (default `.env`) | Mainnet (`.env.mainnet`) |
| --- | --- | --- |
| `NETWORK` | `eip155:84532` (Base Sepolia) | `eip155:8453` (Base) |
| `USDC_ADDRESS` | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| `FACILITATOR_URL` | `https://x402.org/facilitator` | `https://facilitator.payai.network` |
| `RPC_URL`, `EXPLORER_URL` | `https://sepolia.base.org`, `https://sepolia.basescan.org` | a Base mainnet RPC, `https://basescan.org` |

Sanctions screening fails closed on mainnet: keep `SANCTIONS_RPC_URL` pointing to a working Ethereum mainnet RPC.

### 3. Hosted deployment

| Component | Where | How |
| --- | --- | --- |
| Publisher site | Vercel | `python site-demo/deploy.py --gateway <public agent URL>` with `VERCEL_TOKEN` in `.env`. It deploys `site-demo/public` and proxies `/.well-known/ai-data.json` to the gateway |
| Gateway | A server or container you control | `uvicorn gateway.main:app --host 0.0.0.0 --port 8000` behind HTTPS, with its `.env`, its keystores and a persistent `DB_PATH` |
| Web app | The publisher's machine, next to the gateway | `npm run build && npm start` with `NEXT_PUBLIC_GATEWAY_URL` set to the gateway |

What changes when the gateway is reachable from the internet:

- **Only the agent routes should be public**: `/.well-known/ai-data.json`, `/discover`, `/kya/*`, `/session/message`, `/offer/accept`, `/query/*`, `/receipt/*`. Put a reverse proxy in front that forwards these and nothing else.
- **Owner routes stay private.** Publisher setup, dashboards, live events and buyer controls accept a caller on the gateway's machine, or the `X-Owner-Token` header matching `PUBLISHER_OWNER_TOKEN` or `BUYER_OWNER_TOKEN`. Set both tokens on a hosted gateway. The web app does not send these tokens, so run it on the gateway's machine.
- **Set** `GATEWAY_PUBLIC_URL` to the public agent URL (the manifest sends agents there), `CORS_ORIGINS` to the web app's origin, and a strong `JWT_SECRET`.

---

## Test cases

173 automated tests, all passing on a clean checkout, with no API key and no funded wallet (on macOS and Linux; on Windows, one keystore test fails because NTFS has no POSIX file modes):

```bash
.venv/bin/python -m pytest gateway/tests ingestion/tests payments/tests buyer-agent buyer-mcp/tests -q
cd frontend && npx tsc --noEmit && npm run lint
```

| Suite | Tests | What it checks |
| --- | --- | --- |
| `gateway/tests` | 65 | Human visitor redirected; KYA with wrong signer, replayed nonce, blocklisted and sanctioned wallets refused; session bound to the agent's identity; offer validation (exact price, tier floor, excluded content, leaked figure, daily limit per wallet); prompt injection logged and ignored; LLM outage gives a safe refusal; Meta Model API request and strict JSON schema, unusable answers refused; onboarding, rules and activation; owner-only routes; audit chain tamper detection; signed receipts; data retention; security headers |
| `ingestion/tests` | 52 | Crawl of the demo site, `robots.txt`, SSRF targets refused; PDF and HTML sections, data-rich HTML sold and boilerplate kept free, link following without a sitemap; internal page flagged and never sellable; leak filter on number formats and Unicode variants |
| `payments/tests` | 21 | Buyer controls owner-only (remote caller refused); recovery of a paid but undelivered sale from the chain; rate limit on paid routes; watermark traces a leak and cannot be forged; encrypted keystores |
| `buyer-agent` | 30 | Budget, per-purchase cap, approval threshold, daily and hourly caps, structuring detection; tampered invoice (amount, `payTo`, network, asset, scheme) refused before signing; manifest signer pinned; license receipt checked; LLM decision parsed, refusal when the model fails |
| `buyer-mcp/tests` | 5 | Connector: approval order, seller text sanitised, on-chain balance |

The tests replace Muse Spark with scripted outputs or a simulated Meta Model API, so they need no API key.

**End-to-end scripts on the blockchain.** They need funded wallets and spend test USDC on Base Sepolia. The four payment scripts run against the payment module with a simulated gateway (`.venv/bin/uvicorn payments.dev_app:app --port 4022`); the connector script runs against the full gateway with the publisher activated.

| Script | Checks | What it proves |
| --- | --- | --- |
| `payments/e2e_query.py` | 15 | Paid route: a wrong amount gets `402`, a replayed payment and a reused nonce get `409`, content only after settlement |
| `payments/e2e_buyer.py` | 22 | The buyer agent's full journey, from manifest to delivery, one wallet per scenario: a 0.10 sale and a 2.00 sale after approval |
| `payments/e2e_balances_stats.py` | 10 | Balances read on-chain move by the exact price, `balance_changed` events are emitted, publisher stats follow |
| `payments/e2e_recovery.py` | 7 | A crash between payment and delivery is recovered from the chain; paid routes are rate-limited |
| `buyer-mcp/e2e_mcp.py` | 13 | The MCP connector, driven over stdio like a desktop assistant, buys on Base Sepolia with live sanctions screening (13/13) |

Their real transactions are listed in [payments/docs/ONCHAIN_EVIDENCE.md](payments/docs/ONCHAIN_EVIDENCE.md).

---

## Repository map and tech stack

| Folder | What it is |
| --- | --- |
| `site-demo/` | Simulated publisher site (Velstrand Research), built from `truth.json`, deployed on Vercel |
| `ingestion/` | Crawler, splitting of PDF reports and data-rich HTML pages, catalog written by Muse Spark, leak filter, publisher scan endpoints ([README](ingestion/README.md)) |
| `gateway/`, `shared/` | FastAPI app: manifest, discovery, KYA, sales agent, offers, pricing rules, audit, live events; shared schemas, database, events, compliance modules and the Meta Model API client ([README](gateway/README.md)) |
| `payments/` | x402 paid routes, replay protection, receipts, watermark, recovery, on-chain balances, stats ([PAYMENTS](payments/docs/PAYMENTS.md)) |
| `buyer-agent/` | Autonomous buyer agent on Muse Spark, with budget, cap, approval, invoice and manifest checks |
| `buyer-mcp/` | MCP connector: anyone's own AI assistant becomes a buyer agent ([README](buyer-mcp/README.md)) |
| `frontend/` | Next.js web app: onboarding, live view, dashboard ([README](frontend/README.md)) |
| `scripts/` | Wallet creation, key encryption, funds check, pre-demo preflight, on-chain evidence, mainnet launcher |
| `docs/` | Security and compliance reference with regulations ([SECURITY_AND_COMPLIANCE.md](docs/SECURITY_AND_COMPLIANCE.md)), images |

| Layer | Tools |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic v2, SQLite |
| Crawling and parsing | httpx, BeautifulSoup, PyMuPDF, `robots.txt` via `urllib.robotparser` |
| LLM | Muse Spark (`muse-spark-1.3`) on the Meta Model API, through the OpenAI SDK, with strict JSON-schema structured output: catalog metadata, pricing rules, sales agent, buyer decisions |
| Payments | x402 v2 (official Python SDK), EIP-3009, x402 facilitator (x402.org on testnet, PayAI on mainnet) |
| Blockchain | Base Sepolia and Base mainnet, USDC, `eth_account`, `web3.py`, Chainalysis sanctions oracle |
| Agent connector | Model Context Protocol (MCP) Python SDK |
| Web app | Next.js, React, Tailwind, wagmi and viem (MetaMask), Server-Sent Events |
| Hosting | Vercel (publisher site) |


## Limits and roadmap

**Priority 1: sell from the publisher's own domain.** Today, agents find the publisher through its manifest, then negotiate and pay on the Doubloon gateway: for the demo, we chose not to expose our own computers through a public tunnel. Next, the `402` comes from the publisher's own URL, through an edge proxy that forwards only the agent routes, or a plugin on the publisher's server (WordPress, Next.js, Cloudflare Worker). Humans keep seeing the normal pages.

**Priority 2: price each fact, not each section.** Today, the smallest unit sold is a report section, so a 0.10 "one figure" sale delivers a paragraph with several figures. Next, Muse Spark splits each report into individual facts, each with its own price.

**Then:**

- **Agent identity.** Agents are recognised by the identity headers they send (`X-Agent-Id`, `X-Agent-Wallet`), so an undeclared bot is treated as a human visitor and can read public pages. KYA proves who pays, not whether the caller is a bot. Next: accept signed bot requests (Web Bot Auth, IETF draft) next to wallet KYA. The strongest protection is that premium content is not public at all.
- **Publisher onboarding.** Domain ownership is not verified yet, and the demo site's paid PDFs are public because the scan reads them there (the gateway itself never serves paid content before settlement). Next: verify domain ownership, and scan reports from an upload or a private URL.
- **Keys and compliance.** Move keys to a KMS or server wallet, add the EU, UN and UK sanctions lists, and anchor the audit trail on-chain.
- **Scale and uptime.** A second facilitator, with approvals and rate limits in a shared store.
- **Business model.** Charge the planned 0.01 USD per-transaction fee.

**Out of scope for now:** refunds and disputes, multi-publisher marketplace, protection against rebuilding a report from many wallets beyond the daily limit.

Each known risk and its status: [payments/docs/SECURITY_P3.md](payments/docs/SECURITY_P3.md) (risk register) and [docs/SECURITY_AND_COMPLIANCE.md](docs/SECURITY_AND_COMPLIANCE.md) (open items and honest limits).
