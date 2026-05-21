# Google Ads API v24 Feature Parity

This table tracks high-level service parity between Google Ads API v24 and this
MCP server. [`TRACKER.md`](../TRACKER.md) remains the source of truth for
service-by-service implementation notes and next work.

Last synced from [`TRACKER.md`](../TRACKER.md): 2026-04-28.

| Area | Total services | Implemented | Missing | Remaining gaps |
|------|----------------|-------------|---------|----------------|
| Account management | 11 | 11 | 0 | None |
| Ad groups and ads | 15 | 15 | 0 | None |
| Assets | 10 | 6 | 4 | `asset_group_listing_group_filter`, `asset_set_asset`, `customer_asset_set`, `travel_asset_suggestion` |
| Audiences and targeting | 10 | 8 | 2 | `user_list_customer_type`, `keyword_theme_constant` |
| Bidding and budgets | 5 | 4 | 1 | Separate `campaign_budget` service wrapper |
| Campaigns | 17 | 13 | 4 | `campaign_group`, `campaign_lifecycle_goal`, `smart_campaign_setting`, `shareable_preview` |
| Conversions | 11 | 8 | 3 | `conversion_value_rule_set`, `customer_sk_ad_network_conversion_value_schema`, `customer_lifecycle_goal` |
| Data import and jobs | 5 | 3 | 2 | `data_link`, `local_services_lead` |
| Labels and organization | 4 | 4 | 0 | None |
| Metadata and search | 3 | 3 | 0 | None |
| Planning and insights | 9 | 8 | 1 | `recommendation_subscription` |
| Product integration | 5 | 2 | 3 | `content_creator_insights`, `product_link_invitation`, `third_party_app_analytics_link` |
| Shared resources | 4 | 4 | 0 | None |
| **Total** | **103** | **90** | **13** | See tracker for service details |

## API Coverage Notes

| Coverage level | Services |
|----------------|----------|
| Full 1:1 coverage | `google_ads`, `customer`, `campaign`, `ad_group`, `budget`, `ad`, `bidding_strategy`, `conversion_action`, `asset`, `user_list` |
| Partial coverage | `keyword_plan`, `reach_plan`, `recommendation` |

Known partial-operation gaps:

| Service | Missing operations |
|---------|--------------------|
| `keyword_plan` | `generate_forecast_curve`, `generate_forecast_time_series`, `generate_forecast_metrics` |
| `reach_plan` | `generate_reach_forecast` |
| `recommendation` | `dismiss_recommendation` |

## Maintenance Rules

When a service is added, removed, or reclassified:

1. Update [`TRACKER.md`](../TRACKER.md) with implementation detail.
2. Update this parity table so README coverage stays scannable.
3. Run `uv run ruff format .` and `uv run pyright`.
