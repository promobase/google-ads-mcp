# Google Ads MCP Server

An unofficial Model Context Protocol (MCP) server implementation for Google Ads APIs using the official Python SDK.

## Overview

This project provides an MCP server that wraps the Google Ads API v20, enabling Large Language Models (LLMs) to interact with Google Ads accounts through a standardized interface. The server uses the official Google Ads Python SDK with full type annotations for robust and reliable API interactions.

## Features

- **Full Type Safety**: Implemented with strict type annotations using pyright
- **SDK-Based**: Built on top of the official Google Ads Python SDK for reliability
- **Comprehensive Coverage**: Implements 89 Google Ads services for campaign management
- **MCP Compliant**: Follows the Model Context Protocol specification for LLM integration
- **Async Support**: Leverages FastMCP for asynchronous operations
- **Extensive Test Coverage**: 72 services have test coverage

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
| CampaignService                   | Campaign      | ✅ Yes      | ✅ Yes        | Core campaign CRUD operations |
| BudgetService                     | Campaign      | ✅ Yes      | ✅ Yes        | Budget management             |
| AdGroupService                    | Campaign      | ✅ Yes      | ✅ Yes        | Ad group management           |
| AdGroupAdService                  | Campaign      | ✅ Yes      | ✅ Yes        | Ad-to-ad group associations   |
| AdService                         | Campaign      | ✅ Yes      | ✅ Yes        | Ad creation and management    |
| KeywordService                    | Campaign      | ✅ Yes      | ✅ Yes        | Keyword management            |
| **Bidding & Budget**              |
| BiddingStrategyService            | Bidding       | ✅ Yes      | ✅ Yes        | Automated bidding strategies  |
| BiddingDataExclusionService       | Bidding       | ✅ Yes      | ✅ Yes        | Data exclusions for bidding   |
| BiddingSeasonalityAdjustmentService| Bidding      | ✅ Yes      | ❌ No         | Seasonal bid adjustments      |
| CampaignBidModifierService        | Bidding       | ✅ Yes      | ✅ Yes        | Campaign bid adjustments      |
| AdGroupBidModifierService         | Bidding       | ✅ Yes      | ✅ Yes        | Ad group bid adjustments      |
| AccountBudgetProposalService      | Budget        | ✅ Yes      | ✅ Yes        | Account budget proposals      |
| **Targeting & Criteria**          |
| CampaignCriterionService          | Targeting     | ✅ Yes      | ✅ Yes        | Campaign-level targeting      |
| AdGroupCriterionService           | Targeting     | ✅ Yes      | ✅ Yes        | Ad group-level targeting      |
| CustomerNegativeCriterionService  | Targeting     | ✅ Yes      | ❌ No         | Account-level exclusions      |
| GeoTargetConstantService          | Targeting     | ✅ Yes      | ✅ Yes        | Geographic targeting          |
| **Assets & Extensions**           |
| AssetService                      | Assets        | ✅ Yes      | ✅ Yes        | Image, text, video assets     |
| AssetGroupService                 | Assets        | ✅ Yes      | ✅ Yes        | Performance Max asset groups  |
| AssetGroupAssetService            | Assets        | ✅ Yes      | ✅ Yes        | Asset group asset linking     |
| AssetGroupSignalService           | Assets        | ✅ Yes      | ✅ Yes        | Asset group signals           |
| CampaignAssetService              | Assets        | ✅ Yes      | ✅ Yes        | Campaign-level asset linking  |
| CampaignAssetSetService           | Assets        | ✅ Yes      | ✅ Yes        | Campaign asset set linking    |
| AssetSetService                   | Assets        | ✅ Yes      | ✅ Yes        | Asset set management          |
| AdGroupAssetService               | Assets        | ✅ Yes      | ✅ Yes        | Ad group-level asset linking  |
| AdGroupAssetSetService            | Assets        | ✅ Yes      | ❌ No         | Ad group asset set linking    |
| CustomerAssetService              | Assets        | ✅ Yes      | ✅ Yes        | Customer-level asset linking  |
| **Audiences & Remarketing**       |
| UserListService                   | Audiences     | ✅ Yes      | ✅ Yes        | Remarketing lists             |
| CustomInterestService             | Audiences     | ✅ Yes      | ✅ Yes        | Custom interest audiences     |
| CustomAudienceService             | Audiences     | ✅ Yes      | ✅ Yes        | Custom audience segments      |
| RemarketingActionService          | Audiences     | ✅ Yes      | ✅ Yes        | Remarketing tags              |
| AudienceService                   | Audiences     | ✅ Yes      | ✅ Yes        | Combined audiences            |
| AudienceInsightsService           | Audiences     | ✅ Yes      | ✅ Yes        | Audience analysis & insights  |
| **Conversions & Measurement**     |
| ConversionService                 | Conversions   | ✅ Yes      | ✅ Yes        | Conversion tracking           |
| ConversionUploadService           | Conversions   | ✅ Yes      | ✅ Yes        | Offline conversion upload     |
| ConversionAdjustmentUploadService | Conversions   | ✅ Yes      | ❌ No         | Conversion adjustments        |
| ConversionValueRuleService        | Conversions   | ✅ Yes      | ❌ No         | Value rules                   |
| ConversionCustomVariableService   | Conversions   | ✅ Yes      | ✅ Yes        | Custom conversion variables   |
| ConversionGoalCampaignConfigService| Conversions  | ✅ Yes      | ✅ Yes        | Campaign conversion goals     |
| CustomerConversionGoalService     | Conversions   | ✅ Yes      | ✅ Yes        | Customer conversion goals     |
| CustomConversionGoalService       | Conversions   | ✅ Yes      | ❌ No         | Custom conversion goals       |
| **Account Management**            |
| CustomerService                   | Account       | ✅ Yes      | ✅ Yes        | Account information           |
| CustomerUserAccessService         | Account       | ✅ Yes      | ✅ Yes        | User access management        |
| CustomerUserAccessInvitationService| Account      | ✅ Yes      | ❌ No         | Access invitations            |
| CustomerClientLinkService         | Account       | ✅ Yes      | ✅ Yes        | Manager account linking       |
| CustomerManagerLinkService        | Account       | ✅ Yes      | ✅ Yes        | Manager link management       |
| AccountLinkService                | Account       | ✅ Yes      | ✅ Yes        | Third-party account linking   |
| BillingSetupService               | Account       | ✅ Yes      | ✅ Yes        | Billing configuration         |
| InvoiceService                    | Account       | ✅ Yes      | ✅ Yes        | Billing invoices              |
| PaymentsAccountService            | Account       | ✅ Yes      | ❌ No         | Payments account info         |
| IdentityVerificationService       | Account       | ✅ Yes      | ❌ No         | Identity verification         |
| **Labels & Organization**         |
| LabelService                      | Organization  | ✅ Yes      | ✅ Yes        | Label management              |
| CampaignLabelService              | Organization  | ✅ Yes      | ✅ Yes        | Campaign label associations   |
| AdGroupLabelService               | Organization  | ✅ Yes      | ✅ Yes        | Ad group label associations   |
| AdGroupAdLabelService             | Organization  | ✅ Yes      | ❌ No         | Ad label associations         |
| AdGroupCriterionLabelService      | Organization  | ✅ Yes      | ✅ Yes        | Criterion label associations  |
| CustomerLabelService              | Organization  | ✅ Yes      | ✅ Yes        | Customer label associations   |
| SharedSetService                  | Organization  | ✅ Yes      | ✅ Yes        | Shared negative lists         |
| SharedCriterionService            | Organization  | ✅ Yes      | ❌ No         | Shared criteria               |
| CampaignSharedSetService          | Organization  | ✅ Yes      | ✅ Yes        | Campaign-shared set linking   |
| **Smart Campaigns**               |
| SmartCampaignService              | Smart         | ✅ Yes      | ✅ Yes        | Smart campaign management     |
| SmartCampaignSettingService       | Smart         | ❌ No       | ❌ No         | Smart campaign settings       |
| SmartCampaignSuggestService       | Smart         | ❌ No       | ❌ No         | Smart campaign suggestions    |
| **Experiments & Testing**         |
| ExperimentService                 | Testing       | ✅ Yes      | ✅ Yes        | Campaign experiments          |
| ExperimentArmService              | Testing       | ✅ Yes      | ✅ Yes        | Experiment variations         |
| CampaignDraftService              | Testing       | ✅ Yes      | ✅ Yes        | Campaign drafts               |
| **Planning Tools**                |
| KeywordPlanService                | Planning      | ✅ Yes      | ✅ Yes        | Keyword planning              |
| KeywordPlanCampaignService        | Planning      | ✅ Yes      | ✅ Yes        | Keyword plan campaigns        |
| KeywordPlanCampaignKeywordService | Planning      | ✅ Yes      | ✅ Yes        | Campaign keywords in plan     |
| KeywordPlanAdGroupService         | Planning      | ✅ Yes      | ✅ Yes        | Keyword plan ad groups        |
| KeywordPlanAdGroupKeywordService  | Planning      | ✅ Yes      | ✅ Yes        | Ad group keywords in plan     |
| KeywordPlanIdeaService            | Planning      | ✅ Yes      | ✅ Yes        | Keyword ideas                 |
| ReachPlanService                  | Planning      | ✅ Yes      | ✅ Yes        | Reach planning                |
| **Recommendations**               |
| RecommendationService             | Optimization  | ✅ Yes      | ✅ Yes        | Account recommendations       |
| RecommendationSubscriptionService | Optimization  | ❌ No       | ❌ No         | Recommendation subscriptions  |
| **Metadata & Discovery**          |
| GoogleAdsFieldService             | Metadata      | ✅ Yes      | ✅ Yes        | Field metadata                |
| GoogleAdsService                  | Core          | ✅ Yes      | ✅ Yes        | Search operations (GAQL)      |
| SearchService                     | Core          | ✅ Yes      | ✅ Yes        | Alternative search interface  |
| **Advanced Features**             |
| BatchJobService                   | Bulk Ops      | ✅ Yes      | ✅ Yes        | Bulk operations               |
| OfflineUserDataJobService         | Data Import   | ✅ Yes      | ❌ No         | Customer match                |
| UserDataService                   | Data Import   | ✅ Yes      | ✅ Yes        | Enhanced conversions          |
| CustomizerAttributeService        | Customization | ✅ Yes      | ❌ No         | Ad customizers                |
| CampaignCustomizerService         | Customization | ✅ Yes      | ✅ Yes        | Campaign customizers          |
| AdGroupCustomizerService          | Customization | ✅ Yes      | ✅ Yes        | Ad group customizers          |
| AdGroupCriterionCustomizerService | Customization | ✅ Yes      | ✅ Yes        | Criterion customizers         |
| CustomerCustomizerService         | Customization | ✅ Yes      | ❌ No         | Customer customizers          |
| AdParameterService                | Customization | ✅ Yes      | ✅ Yes        | Ad parameters                 |
| DataLinkService                   | Integration   | ✅ Yes      | ❌ No         | Third-party data links        |
| ProductLinkService                | Integration   | ✅ Yes      | ✅ Yes        | Product integrations          |
| BrandSuggestionService            | Discovery     | ✅ Yes      | ✅ Yes        | Brand suggestions             |

### Summary Statistics

- **Total Services Implemented**: 89 out of ~120 Google Ads API v20 services
- **Services with Tests**: 72 (81% test coverage)
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
- **RecommendationSubscriptionService**: Automated recommendation subscriptions
- **FeedService** & **FeedItemService**: Shopping feed management
- **ExtensionFeedItemService**: Ad extensions management
- **CampaignSimulationService**: Campaign performance simulations
- **LocalServicesLeadService**: Local services lead management
- **TravelAssetSuggestionService**: Travel-specific asset suggestions

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

MIT

## Disclaimer

This is an unofficial implementation and is not affiliated with, endorsed by, or supported by Google.