# Google Ads MCP Services Structure

The services are organized into logical folders based on their functionality:

## Folder Structure

### `/campaign`
Campaign-level management services:
- `campaign_service.py` - Core campaign CRUD operations
- `campaign_criterion_service.py` - Campaign-level targeting criteria
- `campaign_bid_modifier_service.py` - Campaign bid adjustments
- `campaign_label_service.py` - Campaign labeling
- `campaign_asset_service.py` - Campaign-level assets
- `campaign_shared_set_service.py` - Shared set associations
- `campaign_draft_service.py` - Campaign drafts
- `smart_campaign_service.py` - Smart campaigns
- `experiment_service.py` - Campaign experiments

### `/ad_group`
Ad group and ad management:
- `ad_group_service.py` - Ad group CRUD operations
- `ad_group_criterion_service.py` - Ad group targeting
- `ad_group_bid_modifier_service.py` - Ad group bid adjustments
- `ad_group_label_service.py` - Ad group labeling
- `ad_group_asset_service.py` - Ad group assets
- `ad_group_ad_service.py` - Ad to ad group associations
- `ad_service.py` - Ad creation and management
- `keyword_service.py` - Keyword management

### `/assets`
Asset management:
- `asset_service.py` - Core asset operations
- `asset_group_service.py` - Performance Max asset groups
- `asset_set_service.py` - Asset set management

### `/targeting`
Targeting and geographic services:
- `geo_target_constant_service.py` - Geographic targeting constants
- `customer_negative_criterion_service.py` - Account-level exclusions

### `/audiences`
Audience and remarketing:
- `audience_service.py` - Combined audiences
- `audience_insights_service.py` - Audience analysis
- `custom_audience_service.py` - Custom audience segments
- `custom_interest_service.py` - Custom interests
- `user_list_service.py` - Remarketing lists
- `remarketing_action_service.py` - Remarketing tags

### `/conversions`
Conversion tracking:
- `conversion_service.py` - Conversion actions
- `conversion_upload_service.py` - Offline conversions
- `conversion_adjustment_upload_service.py` - Conversion adjustments
- `conversion_value_rule_service.py` - Value rules

### `/account`
Account management and billing:
- `customer_service.py` - Customer account info
- `customer_user_access_service.py` - User access control
- `customer_client_link_service.py` - Manager account linking
- `account_link_service.py` - Third-party linking
- `billing_setup_service.py` - Billing configuration
- `invoice_service.py` - Invoice access
- `account_budget_proposal_service.py` - Budget proposals

### `/bidding`
Bidding and budget:
- `bidding_strategy_service.py` - Automated bidding strategies
- `bidding_data_exclusion_service.py` - Data exclusions
- `budget_service.py` - Campaign budgets

### `/planning`
Planning and optimization:
- `keyword_plan_service.py` - Keyword planning
- `keyword_plan_idea_service.py` - Keyword suggestions
- `reach_plan_service.py` - Reach planning
- `recommendation_service.py` - Account recommendations

### `/shared`
Shared resources:
- `shared_set_service.py` - Shared negative lists
- `shared_criterion_service.py` - Shared criteria
- `label_service.py` - Label management
- `customizer_attribute_service.py` - Ad customizers

### `/metadata`
Metadata and search:
- `google_ads_field_service.py` - Field metadata
- `search_service.py` - GAQL search operations

### `/data_import`
Data import and batch operations:
- `batch_job_service.py` - Bulk operations
- `offline_user_data_job_service.py` - Customer match
- `user_data_service.py` - Enhanced conversions
- `data_link_service.py` - Third-party data links

## Usage

Services can be imported from their respective folders:

```python
# Import from specific folder
from src.sdk_services.campaign.campaign_service import CampaignService

# Or use the folder's __init__.py (if configured)
from src.sdk_services.campaign import CampaignService
```

## Adding New Services

When adding a new service:
1. Determine the appropriate folder based on functionality
2. Create the service file in that folder
3. Update the folder's `__init__.py` to include the new service
4. Update any server files that use the service