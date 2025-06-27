"""Google Ads Keyword Plan Campaign Keyword Service

This module provides functionality for managing keyword plan campaign keywords in Google Ads.
Note: Only negative keywords are supported for campaign-level keywords in keyword plans.
"""

from typing import List, Optional

from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.keyword_plan_campaign_keyword import (
    KeywordPlanCampaignKeyword,
)
from google.ads.googleads.v20.services.services.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordOperation,
    MutateKeywordPlanCampaignKeywordsRequest,
    MutateKeywordPlanCampaignKeywordsResponse,
)


class KeywordPlanCampaignKeywordService:
    """Service for managing Google Ads keyword plan campaign keywords (negative keywords only)."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("KeywordPlanCampaignKeywordService")

    def mutate_keyword_plan_campaign_keywords(
        self,
        customer_id: str,
        operations: List[KeywordPlanCampaignKeywordOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanCampaignKeywordsResponse:
        """Mutate keyword plan campaign keywords.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan campaign keyword operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanCampaignKeywordsResponse: The response containing results
        """
        request = MutateKeywordPlanCampaignKeywordsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.service.mutate_keyword_plan_campaign_keywords(request=request)

    def create_keyword_plan_campaign_keyword_operation(
        self,
        keyword_plan_campaign: str,
        text: str,
        match_type: KeywordMatchTypeEnum.KeywordMatchType,
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for creation.

        Note: Only negative keywords are supported at the campaign level.

        Args:
            keyword_plan_campaign: The keyword plan campaign resource name
            text: The keyword text
            match_type: The keyword match type

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to create the keyword plan campaign keyword
        """
        keyword_plan_campaign_keyword = KeywordPlanCampaignKeyword(
            keyword_plan_campaign=keyword_plan_campaign,
            text=text,
            match_type=match_type,
            negative=True,  # Only negative keywords are supported
        )

        return KeywordPlanCampaignKeywordOperation(create=keyword_plan_campaign_keyword)

    def update_keyword_plan_campaign_keyword_operation(
        self,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[KeywordMatchTypeEnum.KeywordMatchType] = None,
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for update.

        Args:
            resource_name: The keyword plan campaign keyword resource name
            text: The keyword text
            match_type: The keyword match type

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to update the keyword plan campaign keyword
        """
        keyword_plan_campaign_keyword = KeywordPlanCampaignKeyword(
            resource_name=resource_name
        )

        update_mask = []
        if text is not None:
            keyword_plan_campaign_keyword.text = text
            update_mask.append("text")
        if match_type is not None:
            keyword_plan_campaign_keyword.match_type = match_type
            update_mask.append("match_type")

        return KeywordPlanCampaignKeywordOperation(
            update=keyword_plan_campaign_keyword,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_campaign_keyword_operation(
        self, resource_name: str
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for removal.

        Args:
            resource_name: The keyword plan campaign keyword resource name

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to remove the keyword plan campaign keyword
        """
        return KeywordPlanCampaignKeywordOperation(remove=resource_name)
