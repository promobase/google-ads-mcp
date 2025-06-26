# Google Ads MCP Server

An unofficial Model Context Protocol (MCP) server implementation for Google Ads APIs using the official Python SDK.

## Overview

This project provides an MCP server that wraps the Google Ads API v20, enabling Large Language Models (LLMs) to interact with Google Ads accounts through a standardized interface. The server uses the official Google Ads Python SDK with full type annotations for robust and reliable API interactions.

## Features

- **Full Type Safety**: Implemented with strict type annotations using pyright
- **SDK-Based**: Built on top of the official Google Ads Python SDK for reliability
- **Comprehensive Coverage**: Implements major Google Ads services for campaign management
- **MCP Compliant**: Follows the Model Context Protocol specification for LLM integration
- **Async Support**: Leverages FastMCP for asynchronous operations

## Installation

```bash
git clone https://github.com/promobase/google-ads-mcp.git
cd google-ads-mcp

# Install dependencies using uv
uv sync

# Set up Google Ads credentials
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
```

## Usage

```bash
uv run main.py
```

## Feature Parity Table

Below is a comprehensive table showing the implementation status of Google Ads API v20 services in this MCP server:

| Service Name                      | Category      | Implemented | Test Coverage | Notes                         |
| --------------------------------- | ------------- | ----------- | ------------- | ----------------------------- |
| **Core Campaign Management**      |
| CampaignService                   | Campaign      | ✅ Yes      | ⚠️ Partial    | Core campaign CRUD operations |
| BudgetService                     | Campaign      | ✅ Yes      | ❌ No         | Budget management             |
| AdGroupService                    | Campaign      | ✅ Yes      | ❌ No         | Ad group management           |
| AdGroupAdService                  | Campaign      | ✅ Yes      | ❌ No         | Ad-to-ad group associations   |
| AdService                         | Campaign      | ✅ Yes      | ❌ No         | Ad creation and management    |
| KeywordService                    | Campaign      | ✅ Yes      | ❌ No         | Keyword management            |
| **Bidding & Budget**              |
| BiddingStrategyService            | Bidding       | ✅ Yes      | ❌ No         | Automated bidding strategies  |
| BiddingDataExclusionService       | Bidding       | ✅ Yes      | ❌ No         | Data exclusions for bidding   |
| CampaignBidModifierService        | Bidding       | ✅ Yes      | ❌ No         | Campaign bid adjustments      |
| AdGroupBidModifierService         | Bidding       | ✅ Yes      | ❌ No         | Ad group bid adjustments      |
| AccountBudgetProposalService      | Budget        | ✅ Yes      | ❌ No         | Account budget proposals      |
| **Targeting & Criteria**          |
| CampaignCriterionService          | Targeting     | ✅ Yes      | ❌ No         | Campaign-level targeting      |
| AdGroupCriterionService           | Targeting     | ✅ Yes      | ❌ No         | Ad group-level targeting      |
| CustomerNegativeCriterionService  | Targeting     | ✅ Yes      | ❌ No         | Account-level exclusions      |
| GeoTargetConstantService          | Targeting     | ✅ Yes      | ❌ No         | Geographic targeting          |
| **Assets & Extensions**           |
| AssetService                      | Assets        | ✅ Yes      | ❌ No         | Image, text, video assets     |
| AssetGroupService                 | Assets        | ✅ Yes      | ❌ No         | Performance Max asset groups  |
| CampaignAssetService              | Assets        | ✅ Yes      | ❌ No         | Campaign-level asset linking  |
| AssetSetService                   | Assets        | ✅ Yes      | ❌ No         | Asset set management          |
| AdGroupAssetService               | Assets        | ✅ Yes      | ❌ No         | Ad group-level asset linking  |
| **Audiences & Remarketing**       |
| UserListService                   | Audiences     | ✅ Yes      | ❌ No         | Remarketing lists             |
| CustomInterestService             | Audiences     | ✅ Yes      | ❌ No         | Custom interest audiences     |
| CustomAudienceService             | Audiences     | ✅ Yes      | ❌ No         | Custom audience segments      |
| RemarketingActionService          | Audiences     | ✅ Yes      | ❌ No         | Remarketing tags              |
| AudienceService                   | Audiences     | ✅ Yes      | ❌ No         | Combined audiences            |
| AudienceInsightsService           | Audiences     | ✅ Yes      | ❌ No         | Audience analysis & insights  |
| **Conversions & Measurement**     |
| ConversionService                 | Conversions   | ✅ Yes      | ❌ No         | Conversion tracking           |
| ConversionUploadService           | Conversions   | ✅ Yes      | ❌ No         | Offline conversion upload     |
| ConversionAdjustmentUploadService | Conversions   | ✅ Yes      | ❌ No         | Conversion adjustments        |
| ConversionValueRuleService        | Conversions   | ✅ Yes      | ❌ No         | Value rules                   |
| **Account Management**            |
| CustomerService                   | Account       | ✅ Yes      | ✅ Yes        | Account information           |
| CustomerUserAccessService         | Account       | ✅ Yes      | ❌ No         | User access management        |
| CustomerClientLinkService         | Account       | ✅ Yes      | ❌ No         | Manager account linking       |
| AccountLinkService                | Account       | ✅ Yes      | ❌ No         | Third-party account linking   |
| BillingSetupService               | Account       | ✅ Yes      | ❌ No         | Billing configuration         |
| InvoiceService                    | Account       | ✅ Yes      | ❌ No         | Billing invoices              |
| **Labels & Organization**         |
| LabelService                      | Organization  | ✅ Yes      | ❌ No         | Label management              |
| CampaignLabelService              | Organization  | ✅ Yes      | ❌ No         | Campaign label associations   |
| AdGroupLabelService               | Organization  | ✅ Yes      | ❌ No         | Ad group label associations   |
| SharedSetService                  | Organization  | ✅ Yes      | ❌ No         | Shared negative lists         |
| SharedCriterionService            | Organization  | ✅ Yes      | ❌ No         | Shared criteria               |
| CampaignSharedSetService          | Organization  | ✅ Yes      | ❌ No         | Campaign-shared set linking   |
| **Smart Campaigns**               |
| SmartCampaignService              | Smart         | ✅ Yes      | ❌ No         | Smart campaign management     |
| SmartCampaignSettingService       | Smart         | ❌ No       | ❌ No         | Smart campaign settings       |
| SmartCampaignSuggestService       | Smart         | ❌ No       | ❌ No         | Smart campaign suggestions    |
| **Experiments & Testing**         |
| ExperimentService                 | Testing       | ✅ Yes      | ❌ No         | Campaign experiments          |
| ExperimentArmService              | Testing       | ❌ No       | ❌ No         | Experiment variations         |
| CampaignDraftService              | Testing       | ✅ Yes      | ❌ No         | Campaign drafts               |
| **Planning Tools**                |
| KeywordPlanService                | Planning      | ✅ Yes      | ❌ No         | Keyword planning              |
| KeywordPlanIdeaService            | Planning      | ✅ Yes      | ❌ No         | Keyword ideas                 |
| ReachPlanService                  | Planning      | ✅ Yes      | ❌ No         | Reach planning                |
| **Recommendations**               |
| RecommendationService             | Optimization  | ✅ Yes      | ❌ No         | Account recommendations       |
| RecommendationSubscriptionService | Optimization  | ❌ No       | ❌ No         | Recommendation subscriptions  |
| **Metadata & Discovery**          |
| GoogleAdsFieldService             | Metadata      | ✅ Yes      | ❌ No         | Field metadata                |
| SearchService                     | Core          | ✅ Yes      | ❌ No         | Search operations (GAQL)      |
| **Advanced Features**             |
| BatchJobService                   | Bulk Ops      | ✅ Yes      | ❌ No         | Bulk operations               |
| OfflineUserDataJobService         | Data Import   | ✅ Yes      | ❌ No         | Customer match                |
| UserDataService                   | Data Import   | ✅ Yes      | ❌ No         | Enhanced conversions          |
| CustomizerAttributeService        | Customization | ✅ Yes      | ❌ No         | Ad customizers                |
| DataLinkService                   | Integration   | ✅ Yes      | ❌ No         | Third-party data links        |

### Summary Statistics

- **Total Services Implemented**: 56
- **Services with Tests**: 1 (1.8% of implemented)
- **Core Services Coverage**: 100% (all essential services implemented)
- **Advanced Features Coverage**: High (most advanced features implemented)

### Implementation Highlights

This MCP server provides comprehensive coverage of the Google Ads API v20:

1. ✅ **Complete Core Services**: All essential campaign management services
2. ✅ **Advanced Features**: Bulk operations, offline conversions, and data imports
3. ✅ **Account Management**: Full billing, user access, and account linking support
4. ✅ **Analytics & Insights**: Audience insights, recommendations, and search capabilities
5. ✅ **Type Safety**: All services use proto-plus message serialization for reliable responses

### Key Features

- **Proto-Plus Serialization**: All mutation responses use `serialize_proto_message` for consistent, type-safe responses
- **Lazy Client Initialization**: Services initialize clients only when needed for better performance
- **Comprehensive Error Handling**: Detailed error messages from Google Ads API exceptions
- **Async Support**: All operations are async-first using FastMCP
- **Type Annotations**: Full type coverage verified with pyright (0 errors)

### Notable Services Not Yet Implemented

While this MCP server has excellent coverage, some Google Ads API v20 services are not yet implemented:

- **SmartCampaignSettingService** & **SmartCampaignSuggestService**: Advanced Smart Campaign features
- **ExperimentArmService**: Experiment variation management
- **RecommendationSubscriptionService**: Automated recommendation subscriptions
- **FeedService** & **FeedItemService**: Shopping feed management
- **ExtensionFeedItemService**: Ad extensions management
- **CampaignSimulationService**: Campaign performance simulations
- **ProductLinkService**: Merchant Center and other product integrations

## Testing

```bash
# Run tests
uv run pytest

# Run type checking
uv run pyright

# Run code formatting
uv run ruff format .
```

## Contributing

Contributions are welcome! Please ensure:

1. All code has proper type annotations
2. Tests are added for new functionality
3. Code passes `uv run pyright` with no errors
4. Code is formatted with `uv run ruff format`

## License

MIT.

## Disclaimer

This is an unofficial implementation and is not affiliated with, endorsed by, or supported by Google.
