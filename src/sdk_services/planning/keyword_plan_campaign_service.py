"""Google Ads Keyword Plan Campaign Service

This module provides functionality for managing keyword plan campaigns in Google Ads.
Keyword plan campaigns define the targeting and settings for keyword planning.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
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

from src.sdk_client import get_sdk_client


class KeywordPlanCampaignService:
    """Service for managing Google Ads keyword plan campaigns."""

    def __init__(self) -> None:
        """Initialize the keyword plan campaign service."""
        self._client: Optional[KeywordPlanCampaignServiceClient] = None

    @property
    def client(self) -> KeywordPlanCampaignServiceClient:
        """Get the keyword plan campaign service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordPlanCampaignService")
        assert self._client is not None
        return self._client

    def mutate_keyword_plan_campaigns(  # pyright: ignore[reportUnusedFunction]
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
        return self.client.mutate_keyword_plan_campaigns(request=request)

    def create_keyword_plan_campaign_operation(  # pyright: ignore[reportUnusedFunction]
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

    def update_keyword_plan_campaign_operation(  # pyright: ignore[reportUnusedFunction]
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

    def remove_keyword_plan_campaign_operation(  # pyright: ignore[reportUnusedFunction]
        self, resource_name: str
    ) -> KeywordPlanCampaignOperation:
        """Create a keyword plan campaign operation for removal.

        Args:
            resource_name: The keyword plan campaign resource name

        Returns:
            KeywordPlanCampaignOperation: The operation to remove the keyword plan campaign
        """
        return KeywordPlanCampaignOperation(remove=resource_name)


def register_keyword_plan_campaign_tools(mcp: FastMCP[Any]) -> None:
    """Register keyword plan campaign tools with the MCP server."""

    @mcp.tool
    async def mutate_keyword_plan_campaigns(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> str:
        """Create, update, or remove keyword plan campaigns.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan campaign operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = KeywordPlanCampaignService()

        def _get_network_enum(
            network_str: str,
        ) -> KeywordPlanNetworkEnum.KeywordPlanNetwork:
            """Convert string to network enum."""
            if network_str == "GOOGLE_SEARCH":
                return KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
            elif network_str == "GOOGLE_SEARCH_AND_PARTNERS":
                return (
                    KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
                )
            else:
                raise ValueError(f"Invalid network: {network_str}")

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_keyword_plan_campaign_operation(
                    keyword_plan=op_data["keyword_plan"],
                    name=op_data["name"],
                    keyword_plan_network=_get_network_enum(
                        op_data["keyword_plan_network"]
                    ),
                    cpc_bid_micros=op_data["cpc_bid_micros"],
                    language_constants=op_data.get("language_constants"),
                    geo_target_constants=op_data.get("geo_target_constants"),
                )
            elif op_type == "update":
                network = None
                if "keyword_plan_network" in op_data:
                    network = _get_network_enum(op_data["keyword_plan_network"])

                operation = service.update_keyword_plan_campaign_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    keyword_plan_network=network,
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                    language_constants=op_data.get("language_constants"),
                    geo_target_constants=op_data.get("geo_target_constants"),
                )
            elif op_type == "remove":
                operation = service.remove_keyword_plan_campaign_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_keyword_plan_campaigns(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

        return f"Successfully processed {len(response.results)} keyword plan campaign operations"

    @mcp.tool
    async def create_keyword_plan_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        keyword_plan: str,
        name: str,
        keyword_plan_network: str,
        cpc_bid_micros: int,
        language_constants: list[str] = [],
        geo_target_constants: list[str] = [],
    ) -> str:
        """Create a new keyword plan campaign.

        Args:
            customer_id: The customer ID
            keyword_plan: The keyword plan resource name
            name: Name of the keyword plan campaign
            keyword_plan_network: Targeting network (GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS)
            cpc_bid_micros: Default CPC bid in micros
            language_constants: List of language constant resource names
            geo_target_constants: List of geo target constant resource names

        Returns:
            The created keyword plan campaign resource name
        """
        service = KeywordPlanCampaignService()

        def _get_network_enum(
            network_str: str,
        ) -> KeywordPlanNetworkEnum.KeywordPlanNetwork:
            """Convert string to network enum."""
            if network_str == "GOOGLE_SEARCH":
                return KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
            elif network_str == "GOOGLE_SEARCH_AND_PARTNERS":
                return (
                    KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
                )
            else:
                raise ValueError(f"Invalid network: {network_str}")

        operation = service.create_keyword_plan_campaign_operation(
            keyword_plan=keyword_plan,
            name=name,
            keyword_plan_network=_get_network_enum(keyword_plan_network),
            cpc_bid_micros=cpc_bid_micros,
            language_constants=language_constants,
            geo_target_constants=geo_target_constants,
        )

        response = service.mutate_keyword_plan_campaigns(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Created keyword plan campaign: {result.resource_name}"

    @mcp.tool
    async def update_keyword_plan_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        keyword_plan_network: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
        language_constants: Optional[list[str]] = None,
        geo_target_constants: Optional[list[str]] = None,
    ) -> str:
        """Update an existing keyword plan campaign.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan campaign resource name
            name: Name of the keyword plan campaign
            keyword_plan_network: Targeting network (GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS)
            cpc_bid_micros: Default CPC bid in micros
            language_constants: List of language constant resource names
            geo_target_constants: List of geo target constant resource names

        Returns:
            The updated keyword plan campaign resource name
        """
        service = KeywordPlanCampaignService()

        def _get_network_enum(
            network_str: str,
        ) -> KeywordPlanNetworkEnum.KeywordPlanNetwork:
            """Convert string to network enum."""
            if network_str == "GOOGLE_SEARCH":
                return KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
            elif network_str == "GOOGLE_SEARCH_AND_PARTNERS":
                return (
                    KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
                )
            else:
                raise ValueError(f"Invalid network: {network_str}")

        network = None
        if keyword_plan_network is not None:
            network = _get_network_enum(keyword_plan_network)

        operation = service.update_keyword_plan_campaign_operation(
            resource_name=resource_name,
            name=name,
            keyword_plan_network=network,
            cpc_bid_micros=cpc_bid_micros,
            language_constants=language_constants,
            geo_target_constants=geo_target_constants,
        )

        response = service.mutate_keyword_plan_campaigns(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated keyword plan campaign: {result.resource_name}"

    @mcp.tool
    async def remove_keyword_plan_campaign(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove a keyword plan campaign.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan campaign resource name

        Returns:
            Success message
        """
        service = KeywordPlanCampaignService()

        operation = service.remove_keyword_plan_campaign_operation(
            resource_name=resource_name
        )

        service.mutate_keyword_plan_campaigns(
            customer_id=customer_id, operations=[operation]
        )

        return f"Removed keyword plan campaign: {resource_name}"
