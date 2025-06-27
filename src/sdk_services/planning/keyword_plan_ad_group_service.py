"""Google Ads Keyword Plan Ad Group Service

This module provides functionality for managing keyword plan ad groups in Google Ads.
Keyword plan ad groups organize keywords within keyword plan campaigns for planning purposes.
"""

from typing import List, Optional

from google.ads.googleads.v20.resources.types.keyword_plan_ad_group import (
    KeywordPlanAdGroup,
)
from google.ads.googleads.v20.services.services.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupOperation,
    MutateKeywordPlanAdGroupsRequest,
    MutateKeywordPlanAdGroupsResponse,
)


class KeywordPlanAdGroupService:
    """Service for managing Google Ads keyword plan ad groups."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("KeywordPlanAdGroupService")

    def mutate_keyword_plan_ad_groups(
        self,
        customer_id: str,
        operations: List[KeywordPlanAdGroupOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanAdGroupsResponse:
        """Mutate keyword plan ad groups.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanAdGroupsResponse: The response containing results
        """
        request = MutateKeywordPlanAdGroupsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.service.mutate_keyword_plan_ad_groups(request=request)

    def create_keyword_plan_ad_group_operation(
        self,
        keyword_plan_campaign: str,
        name: str,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for creation.

        Args:
            keyword_plan_campaign: The keyword plan campaign resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to create the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(
            keyword_plan_campaign=keyword_plan_campaign,
            name=name,
        )

        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros

        return KeywordPlanAdGroupOperation(create=keyword_plan_ad_group)

    def update_keyword_plan_ad_group_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for update.

        Args:
            resource_name: The keyword plan ad group resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to update the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(resource_name=resource_name)

        update_mask = []
        if name is not None:
            keyword_plan_ad_group.name = name
            update_mask.append("name")
        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")

        return KeywordPlanAdGroupOperation(
            update=keyword_plan_ad_group,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_ad_group_operation(
        self, resource_name: str
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for removal.

        Args:
            resource_name: The keyword plan ad group resource name

        Returns:
            KeywordPlanAdGroupOperation: The operation to remove the keyword plan ad group
        """
        return KeywordPlanAdGroupOperation(remove=resource_name)
