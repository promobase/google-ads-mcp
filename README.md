<div align="center">

<a href="https://openpromo.app">
  <img src="https://openpromo.app/logo.svg" width="80" alt="OpenPromo" />
</a>

# google-ads-mcp

**A typed MCP server for letting AI agents operate Google Ads.**

Built by [**Promobase**](https://openpromo.app) for [**OpenPromo**](https://openpromo.app), the AI-native workspace for creating, publishing, and managing ads.

[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB.svg)](https://www.python.org/)
[![Google Ads API](https://img.shields.io/badge/Google%20Ads%20API-v20-4285F4.svg)](https://developers.google.com/google-ads/api/docs/start)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-111827.svg)](https://github.com/jlowin/fastmcp)
[![CI](https://github.com/promobase/google-ads-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/promobase/google-ads-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

</div>

---

## What

`google-ads-mcp` wraps the official Google Ads Python SDK in a Model Context Protocol server. It exposes Google Ads API v24 services as typed MCP tools, so LLMs and agent runtimes can safely inspect accounts, create campaigns, manage budgets, upload conversions, work with assets, and run GAQL search.

This repo is the Google Ads execution layer behind OpenPromo's agent workflows. For application-facing, multi-platform ad publishing and inbox automation, use the companion SDK:

**[`@promobase/ad-platforms`](https://www.npmjs.com/package/@promobase/ad-platforms)** - one TypeScript SDK for Meta, TikTok, and soon Google Ads, with AI SDK tools and production clients for ad platform automation.

## Why

Google Ads has a large, typed API surface, but it is hard for agents to use directly. This server keeps the reliability of the official Python SDK while giving agents a structured tool interface:

- **Official SDK foundation** - built on `google-ads`, including its auth, retries, paging, and protobuf types.
- **Typed service wrappers** - implementations use Google Ads API v24 generated service, resource, enum, and operation types.
- **Agent-ready MCP tools** - FastMCP servers grouped by workflow: core, assets, targeting, bidding, planning, reporting, conversions, account management, and more.
- **GAQL access** - search and metadata tools for reporting, discovery, and account inspection.
- **Production-oriented scope** - designed for OpenPromo's ads loop: generate creative, build campaigns, publish, measure, and iterate.

## Coverage

Current tracker status:

| Area | Status |
|------|--------|
| Google Ads API version | `v20` |
| Implemented services | `90 / 103` |
| Coverage model | 1:1 service mapping where implemented |
| Type policy | Generated Google Ads protobuf types |
| Feature parity | [`docs/FEATURE_PARITY.md`](./docs/FEATURE_PARITY.md) |
| Detailed audit | [`TRACKER.md`](./TRACKER.md) |

Core campaign, ad group, ad, budget, keyword, conversion, asset, audience, recommendation, account, billing, and reporting workflows are implemented. The scannable parity table lives in [`docs/FEATURE_PARITY.md`](./docs/FEATURE_PARITY.md); detailed implementation notes live in [`TRACKER.md`](./TRACKER.md).

## Install

```bash
git clone https://github.com/promobase/google-ads-mcp.git
cd google-ads-mcp
uv sync
```

Create a `.env` file or export the required Google Ads credentials:

```bash
GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
GOOGLE_ADS_CLIENT_ID="your_client_id"
GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
GOOGLE_ADS_LOGIN_CUSTOMER_ID="optional_manager_customer_id"
```

See [`.env.example`](./.env.example) for the full credential template.

## Run

Run the default core tool group:

```bash
uv run main.py
```

Run every registered service group:

```bash
uv run main.py --groups all
```

Run a focused subset:

```bash
uv run main.py --groups core,assets,targeting,conversion
```

Available groups:

| Group | Includes |
|-------|----------|
| `core` | Customers, campaigns, budgets, ad groups, keywords, ads, conversions, GAQL |
| `assets` | Assets, asset groups, asset sets, campaign/ad group/customer assets |
| `targeting` | Criteria, geo targets, audiences, custom interests, user lists |
| `bidding` | Strategies, bid modifiers, data exclusions, seasonality adjustments |
| `planning` | Keyword plans, reach planning, brand suggestions |
| `reporting` | Search, fields, recommendations, invoices, audience insights |
| `conversion` | Uploads, adjustments, value rules, goals, user data, remarketing |
| `organization` | Labels, shared sets, shared criteria |
| `customizers` | Customizer attributes, campaign/ad group/customer customizers, ad parameters |
| `account` | Access, manager links, billing, payments, identity, product/data links |
| `other` | Smart campaigns, batch jobs, user data |

## MCP Client

Example stdio configuration:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "uv",
      "args": ["run", "main.py", "--groups", "all"],
      "cwd": "/path/to/google-ads-mcp",
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "...",
        "GOOGLE_ADS_CLIENT_ID": "...",
        "GOOGLE_ADS_CLIENT_SECRET": "...",
        "GOOGLE_ADS_REFRESH_TOKEN": "..."
      }
    }
  }
}
```

Use narrower groups for production agents when you want to reduce tool count and keep routing focused.

## Development

```bash
# Format
uv run ruff format .

# Type check
uv run pyright

# Test
uv run pytest
```

When adding a service:

1. Check the Google Ads API v24 generated service types.
2. Implement the service wrapper with generated protobuf request, operation, resource, and enum types.
3. Register lightweight MCP tools for the service.
4. Add focused tests.
5. Update [`TRACKER.md`](./TRACKER.md).
6. Run `uv run ruff format .` and `uv run pyright`.

## Related

| Project | Description |
|---------|-------------|
| [OpenPromo](https://openpromo.app) | AI-native workspace for creating, publishing, and managing ads |
| [`@promobase/ad-platforms`](https://www.npmjs.com/package/@promobase/ad-platforms) | TypeScript ad platform SDK with AI SDK tools for Meta, TikTok, and Google Ads work |
| [`promobase/ad-platform-sdks`](https://github.com/promobase/ad-platform-sdks) | Source repo for Promobase's multi-platform ad SDKs |

## License

MIT © [Promobase](https://openpromo.app)

## Disclaimer

This is an unofficial Google Ads API integration. It is not affiliated with, endorsed by, or supported by Google.
