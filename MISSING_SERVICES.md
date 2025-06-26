# Google Ads MCP - Missing Services

This document lists all Google Ads API v20 services that are available in the SDK but not yet implemented in the MCP server.

## Currently Implemented Services (51)
Based on the imports in `main.py` and the files in `src/sdk_services/`:

1. AccountLinkService
2. AdGroupAdService  
3. AdGroupAssetService
4. AdGroupBidModifierService
5. AdGroupCriterionService
6. AdGroupLabelService
7. AdGroupService
8. AdService
9. AssetGroupService
10. AssetService
11. AssetSetService
12. AudienceService
13. BatchJobService (implemented but not imported in main.py)
14. BiddingStrategyService
15. BillingSetupService
16. BudgetService (CampaignBudgetService)
17. CampaignAssetService
18. CampaignBidModifierService
19. CampaignCriterionService
20. CampaignLabelService
21. CampaignService
22. CampaignSharedSetService
23. ConversionAdjustmentUploadService
24. ConversionService (ConversionActionService)
25. ConversionUploadService
26. ConversionValueRuleService
27. CustomAudienceService
28. CustomInterestService
29. CustomerNegativeCriterionService
30. CustomerService
31. CustomerUserAccessService
32. CustomizerAttributeService
33. DataLinkService
34. ExperimentService
35. GeoTargetConstantService
36. GoogleAdsFieldService
37. KeywordPlanIdeaService
38. KeywordPlanService
39. KeywordService (part of AdGroupCriterionService)
40. LabelService
41. OfflineUserDataJobService
42. ReachPlanService
43. RecommendationService
44. RemarketingActionService
45. SearchService (part of GoogleAdsService)
46. SharedCriterionService
47. SharedSetService
48. SmartCampaignService (SmartCampaignSuggestService)
49. UserDataService
50. UserListService
51. ExtensionFeedItemService (commented out as not available in v20)

## Missing Services (60+)
Services available in Google Ads API v20 SDK but not implemented in MCP:

### Account Management
1. **AccountBudgetProposalService** - Manage account budget proposals
2. **CustomerClientLinkService** - Manage links between manager and client accounts
3. **CustomerManagerLinkService** - Manage manager account relationships
4. **CustomerSkAdNetworkConversionValueSchemaService** - iOS SKAdNetwork schema management
5. **PaymentsAccountService** - Manage payments accounts for billing

### Ad Management
6. **AdGroupAdLabelService** - Manage labels on ad group ads
7. **AdParameterService** - Manage ad customizer parameters
8. **AdGroupCriterionCustomizerService** - Ad group criterion customizers
9. **AdGroupCriterionLabelService** - Labels for ad group criteria
10. **AdGroupCustomizerService** - Ad group level customizers

### Asset Management  
11. **AdGroupAssetSetService** - Link asset sets to ad groups
12. **AssetGroupAssetService** - Manage assets within asset groups
13. **AssetGroupListingGroupFilterService** - Listing group filters for Performance Max
14. **AssetGroupSignalService** - Audience signals for asset groups
15. **AssetSetAssetService** - Manage assets within asset sets
16. **CustomerAssetService** - Customer-level assets
17. **CustomerAssetSetService** - Customer-level asset sets
18. **TravelAssetSuggestionService** - Travel-specific asset suggestions

### Campaign Management
19. **CampaignAssetSetService** - Link asset sets to campaigns
20. **CampaignConversionGoalService** - Campaign-specific conversion goals
21. **CampaignCustomizerService** - Campaign-level customizers
22. **CampaignDraftService** - Campaign drafts for testing changes
23. **CampaignGroupService** - Grouping campaigns for Performance Max
24. **CampaignLifecycleGoalService** - Campaign lifecycle goals

### Conversion Tracking
25. **ConversionCustomVariableService** - Custom variables for conversions
26. **ConversionValueRuleSetService** - Sets of conversion value rules
27. **CustomConversionGoalService** - Custom conversion goals
28. **ConversionGoalCampaignConfigService** - Campaign conversion goal configs
29. **CustomerConversionGoalService** - Customer-level conversion goals

### Customer Management
30. **CustomerCustomizerService** - Customer-level customizers
31. **CustomerLabelService** - Labels at the customer level
32. **CustomerLifecycleGoalService** - Customer lifecycle goals
33. **CustomerUserAccessInvitationService** - User access invitations

### Insights & Analytics
34. **AudienceInsightsService** - Audience insights and analysis
35. **ContentCreatorInsightsService** - YouTube creator insights
36. **ThirdPartyAppAnalyticsLinkService** - Links to third-party analytics

### Keyword Planning
37. **KeywordPlanAdGroupService** - Ad groups in keyword plans
38. **KeywordPlanAdGroupKeywordService** - Keywords in keyword plan ad groups
39. **KeywordPlanCampaignService** - Campaigns in keyword plans
40. **KeywordPlanCampaignKeywordService** - Keywords in keyword plan campaigns
41. **KeywordThemeConstantService** - Smart campaign keyword themes

### Billing & Verification
42. **BrandSuggestionService** - Brand suggestions for targeting
43. **IdentityVerificationService** - Identity verification for accounts
44. **InvoiceService** - Access billing invoices

### Advanced Features
45. **BiddingDataExclusionService** - Exclude date ranges from bidding
46. **BiddingSeasonalityAdjustmentService** - Seasonal bid adjustments
47. **ExperimentArmService** - Arms within experiments
48. **GoogleAdsService** - Core service for search/mutate (partially implemented)
49. **LocalServicesLeadService** - Local Services ads leads
50. **ProductLinkService** - Links to Merchant Center, etc.
51. **ProductLinkInvitationService** - Invitations for product links
52. **RecommendationSubscriptionService** - Subscribe to recommendations
53. **ShareablePreviewService** - Generate ad previews
54. **SmartCampaignSettingService** - Smart campaign settings
55. **UserListCustomerTypeService** - Customer types for user lists

### New in v20
56. **DataLinkService** - Already implemented
57. Several services related to Performance Max and Discovery campaigns

## Priority Recommendations

Based on common use cases, the following services should be prioritized:

1. **GoogleAdsService** - Core service for search and mutate operations (partially implemented)
2. **CampaignBudgetService** - Essential for budget management
3. **AccountBudgetProposalService** - Account-level budget management
4. **InvoiceService** - Billing and invoicing
5. **BiddingDataExclusionService** - Important for bid strategy management
6. **CampaignDraftService** - Testing changes before applying
7. **CustomerClientLinkService** - Manager account operations
8. **ProductLinkService** - Integration with Merchant Center
9. **AudienceInsightsService** - Audience analysis
10. **KeywordThemeConstantService** - Smart campaign support

## Notes

- Some services like ExtensionFeedItemService are not available in v20
- BatchJobService is implemented but not imported in main.py
- Some functionality might be covered by existing services (e.g., keyword management is part of AdGroupCriterionService)
- The total count of missing services is approximately 60+