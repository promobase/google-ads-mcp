"""Google Ads Keyword Plan Campaign Service

This module provides functionality for managing keyword plan campaigns in Google Ads.
Keyword plan campaigns define the targeting and settings for keyword planning.
"""

from typing import List, Optional

from google.ads.googleads.v20.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)
from google.ads.googleads.v20.resources.types.keyword_plan_campaign import (
    KeywordPlanCampaign,
    KeywordPlanGeoTarget,
)
from google.ads.googleads.v20.services.services.keyword_plan_campaign_service import (
    KeywordPlanCampaignServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_campaign_service import (
    KeywordPlanCampaignOperation,
    MutateKeywordPlanCampaignsRequest,
    MutateKeywordPlanCampaignsResponse,
)


class KeywordPlanCampaignService:
    """Service for managing Google Ads keyword plan campaigns."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("KeywordPlanCampaignService")

    def mutate_keyword_plan_campaigns(
        self,
        customer_id: str,
        operations: List[KeywordPlanCampaignOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanCampaignsResponse:
        """Mutate keyword plan campaigns.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan campaign operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanCampaignsResponse: The response containing results
        """
        request = MutateKeywordPlanCampaignsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.service.mutate_keyword_plan_campaigns(request=request)

    def create_keyword_plan_campaign_operation(
        self,
        keyword_plan: str,
        name: str,
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork,
        cpc_bid_micros: int,
        language_constants: Optional[List[str]] = None,
        geo_target_constants: Optional[List[str]] = None,
    ) -> KeywordPlanCampaignOperation:
        """Create a keyword plan campaign operation for creation.

        Args:
            keyword_plan: The keyword plan resource name
            name: The name of the keyword plan campaign
            keyword_plan_network: The targeting network
            cpc_bid_micros: Default CPC bid in micros
            language_constants: List of language constant resource names
            geo_target_constants: List of geo target constant resource names

        Returns:
            KeywordPlanCampaignOperation: The operation to create the keyword plan campaign
        """
        geo_targets = []
        if geo_target_constants:
            geo_targets = [
                KeywordPlanGeoTarget(geo_target_constant=geo_target)
                for geo_target in geo_target_constants
            ]

        keyword_plan_campaign = KeywordPlanCampaign(
            keyword_plan=keyword_plan,
            name=name,
            keyword_plan_network=keyword_plan_network,
            cpc_bid_micros=cpc_bid_micros,
            language_constants=language_constants or [],
            geo_targets=geo_targets,
        )

        return KeywordPlanCampaignOperation(create=keyword_plan_campaign)

    def update_keyword_plan_campaign_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        keyword_plan_network: Optional[
            KeywordPlanNetworkEnum.KeywordPlanNetwork
        ] = None,
        cpc_bid_micros: Optional[int] = None,
        language_constants: Optional[List[str]] = None,
        geo_target_constants: Optional[List[str]] = None,
    ) -> KeywordPlanCampaignOperation:
        """Create a keyword plan campaign operation for update.

        Args:
            resource_name: The keyword plan campaign resource name
            name: The name of the keyword plan campaign
            keyword_plan_network: The targeting network
            cpc_bid_micros: Default CPC bid in micros
            language_constants: List of language constant resource names
            geo_target_constants: List of geo target constant resource names

        Returns:
            KeywordPlanCampaignOperation: The operation to update the keyword plan campaign
        """
        keyword_plan_campaign = KeywordPlanCampaign(resource_name=resource_name)

        update_mask = []
        if name is not None:
            keyword_plan_campaign.name = name
            update_mask.append("name")
        if keyword_plan_network is not None:
            keyword_plan_campaign.keyword_plan_network = keyword_plan_network
            update_mask.append("keyword_plan_network")
        if cpc_bid_micros is not None:
            keyword_plan_campaign.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")
        if language_constants is not None:
            keyword_plan_campaign.language_constants = language_constants
            update_mask.append("language_constants")
        if geo_target_constants is not None:
            geo_targets = [
                KeywordPlanGeoTarget(geo_target_constant=geo_target)
                for geo_target in geo_target_constants
            ]
            keyword_plan_campaign.geo_targets = geo_targets
            update_mask.append("geo_targets")

        return KeywordPlanCampaignOperation(
            update=keyword_plan_campaign,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_campaign_operation(
        self, resource_name: str
    ) -> KeywordPlanCampaignOperation:
        """Create a keyword plan campaign operation for removal.

        Args:
            resource_name: The keyword plan campaign resource name

        Returns:
            KeywordPlanCampaignOperation: The operation to remove the keyword plan campaign
        """
        return KeywordPlanCampaignOperation(remove=resource_name)
