# Service Organization Structure

Services are organized into 13 logical categories:

## Service Count by Category

1. **Campaign** (9 services) - Campaign management and experiments
2. **Ad Group** (8 services) - Ad groups, ads, and keywords
3. **Assets** (3 services) - Creative assets and asset groups
4. **Targeting** (2 services) - Geographic and negative targeting
5. **Audiences** (6 services) - Audience segments and remarketing
6. **Conversions** (4 services) - Conversion tracking and uploads
7. **Account** (7 services) - Account management and billing
8. **Bidding** (3 services) - Bidding strategies and budgets
9. **Planning** (4 services) - Keyword and reach planning
10. **Shared** (4 services) - Shared resources and labels
11. **Metadata** (2 services) - Field metadata and search
12. **Data Import** (4 services) - Bulk operations and data imports

**Total: 56 services**

## Benefits of This Structure

1. **Logical Grouping**: Related services are together
2. **Easier Navigation**: Find services by their function
3. **Cleaner Imports**: Import from specific categories
4. **Better Modularity**: Each category can evolve independently
5. **Improved Maintainability**: Clear ownership and boundaries

## Import Examples

```python
# Old way
from src.sdk_services.campaign_service import CampaignService

# New way - explicit
from src.sdk_services.campaign.campaign_service import CampaignService

# New way - using __init__.py
from src.sdk_services.campaign import CampaignService
```