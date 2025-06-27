"""Google Ads Keyword Plan Ad Group Keyword Service

This module provides functionality for managing keyword plan ad group keywords in Google Ads.
Keyword plan ad group keywords define the keywords within keyword plan ad groups for planning purposes.
"""

from typing import List, Optional

from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.keyword_plan_ad_group_keyword import (
    KeywordPlanAdGroupKeyword,
)
from google.ads.googleads.v20.services.services.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordOperation,
    MutateKeywordPlanAdGroupKeywordsRequest,
    MutateKeywordPlanAdGroupKeywordsResponse,
)


class KeywordPlanAdGroupKeywordService:
    """Service for managing Google Ads keyword plan ad group keywords."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("KeywordPlanAdGroupKeywordService")

    def mutate_keyword_plan_ad_group_keywords(
        self,
        customer_id: str,
        operations: List[KeywordPlanAdGroupKeywordOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanAdGroupKeywordsResponse:
        """Mutate keyword plan ad group keywords.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group keyword operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanAdGroupKeywordsResponse: The response containing results
        """
        request = MutateKeywordPlanAdGroupKeywordsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.service.mutate_keyword_plan_ad_group_keywords(request=request)

    def create_keyword_plan_ad_group_keyword_operation(
        self,
        keyword_plan_ad_group: str,
        text: str,
        match_type: KeywordMatchTypeEnum.KeywordMatchType,
        cpc_bid_micros: Optional[int] = None,
        negative: bool = False,
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for creation.

        Args:
            keyword_plan_ad_group: The keyword plan ad group resource name
            text: The keyword text
            match_type: The keyword match type
            cpc_bid_micros: CPC bid in micros
            negative: Whether this is a negative keyword

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to create the keyword plan ad group keyword
        """
        keyword_plan_ad_group_keyword = KeywordPlanAdGroupKeyword(
            keyword_plan_ad_group=keyword_plan_ad_group,
            text=text,
            match_type=match_type,
            negative=negative,
        )

        if cpc_bid_micros is not None:
            keyword_plan_ad_group_keyword.cpc_bid_micros = cpc_bid_micros

        return KeywordPlanAdGroupKeywordOperation(create=keyword_plan_ad_group_keyword)

    def update_keyword_plan_ad_group_keyword_operation(
        self,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[KeywordMatchTypeEnum.KeywordMatchType] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for update.

        Args:
            resource_name: The keyword plan ad group keyword resource name
            text: The keyword text
            match_type: The keyword match type
            cpc_bid_micros: CPC bid in micros

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to update the keyword plan ad group keyword
        """
        keyword_plan_ad_group_keyword = KeywordPlanAdGroupKeyword(
            resource_name=resource_name
        )

        update_mask = []
        if text is not None:
            keyword_plan_ad_group_keyword.text = text
            update_mask.append("text")
        if match_type is not None:
            keyword_plan_ad_group_keyword.match_type = match_type
            update_mask.append("match_type")
        if cpc_bid_micros is not None:
            keyword_plan_ad_group_keyword.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")

        return KeywordPlanAdGroupKeywordOperation(
            update=keyword_plan_ad_group_keyword,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_ad_group_keyword_operation(
        self, resource_name: str
    ) -> KeywordPlanAdGroupKeywordOperation:
        """Create a keyword plan ad group keyword operation for removal.

        Args:
            resource_name: The keyword plan ad group keyword resource name

        Returns:
            KeywordPlanAdGroupKeywordOperation: The operation to remove the keyword plan ad group keyword
        """
        return KeywordPlanAdGroupKeywordOperation(remove=resource_name)
