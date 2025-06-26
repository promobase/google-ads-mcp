"""Ad group service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.ad_group_status import AdGroupStatusEnum
from google.ads.googleads.v20.enums.types.ad_group_type import AdGroupTypeEnum
from google.ads.googleads.v20.resources.types.ad_group import AdGroup
from google.ads.googleads.v20.services.services.ad_group_service import (
    AdGroupServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_service import (
    AdGroupOperation,
    MutateAdGroupsRequest,
    MutateAdGroupsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupService:
    """Ad group service for managing Google Ads ad groups."""

    def __init__(self) -> None:
        """Initialize the ad group service."""
        self._client: Optional[AdGroupServiceClient] = None

    @property
    def client(self) -> AdGroupServiceClient:
        """Get the ad group service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupService")
        assert self._client is not None
        return self._client

    async def create_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        status: AdGroupStatusEnum.AdGroupStatus = AdGroupStatusEnum.AdGroupStatus.ENABLED,
        type: AdGroupTypeEnum.AdGroupType = AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            name: Ad group name
            status: Ad group status enum value
            type: Ad group type enum value
            cpc_bid_micros: Cost per click bid in micros (1 million micros = 1 unit)
            cpm_bid_micros: Cost per thousand impressions bid in micros

        Returns:
            Created ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create a new ad group
            ad_group = AdGroup()
            ad_group.name = name
            ad_group.campaign = campaign_resource_name

            # Set status
            ad_group.status = status

            # Set type
            ad_group.type_ = type

            # Set bidding if provided
            if cpc_bid_micros is not None:
                ad_group.cpc_bid_micros = cpc_bid_micros
            if cpm_bid_micros is not None:
                ad_group.cpm_bid_micros = cpm_bid_micros

            # Create the operation
            operation = AdGroupOperation()
            operation.create = ad_group

            # Create the request
            request = MutateAdGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupsResponse = self.client.mutate_ad_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created ad group in campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        name: Optional[str] = None,
        status: Optional[AdGroupStatusEnum.AdGroupStatus] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID to update
            name: New ad group name (optional)
            status: New ad group status enum value (optional)
            cpc_bid_micros: New CPC bid in micros (optional)
            cpm_bid_micros: New CPM bid in micros (optional)

        Returns:
            Updated ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad group with resource name
            ad_group = AdGroup()
            ad_group.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                ad_group.name = name
                update_mask_fields.append("name")

            if status is not None:
                ad_group.status = status
                update_mask_fields.append("status")

            if cpc_bid_micros is not None:
                ad_group.cpc_bid_micros = cpc_bid_micros
                update_mask_fields.append("cpc_bid_micros")

            if cpm_bid_micros is not None:
                ad_group.cpm_bid_micros = cpm_bid_micros
                update_mask_fields.append("cpm_bid_micros")

            # Create the operation
            operation = AdGroupOperation()
            operation.update = ad_group
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateAdGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_groups(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad group {ad_group_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_tools(
    service: AdGroupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        status: str = "ENABLED",
        type: str = "SEARCH_STANDARD",
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new ad group.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            name: Ad group name
            status: Ad group status (ENABLED, PAUSED, REMOVED)
            type: Ad group type (SEARCH_STANDARD, DISPLAY_STANDARD, SHOPPING_PRODUCT_ADS, etc.)
            cpc_bid_micros: Cost per click bid in micros (1 million micros = 1 unit)
            cpm_bid_micros: Cost per thousand impressions bid in micros

        Returns:
            Created ad group details
        """
        # Convert string enums to proper enum types
        status_enum = getattr(AdGroupStatusEnum.AdGroupStatus, status)
        type_enum = getattr(AdGroupTypeEnum.AdGroupType, type)

        return await service.create_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=status_enum,
            type=type_enum,
            cpc_bid_micros=cpc_bid_micros,
            cpm_bid_micros=cpm_bid_micros,
        )

    async def update_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID to update
            name: New ad group name (optional)
            status: New ad group status (ENABLED, PAUSED, REMOVED) (optional)
            cpc_bid_micros: New CPC bid in micros (optional)
            cpm_bid_micros: New CPM bid in micros (optional)

        Returns:
            Updated ad group details
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(AdGroupStatusEnum.AdGroupStatus, status) if status else None
        )

        return await service.update_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            name=name,
            status=status_enum,
            cpc_bid_micros=cpc_bid_micros,
            cpm_bid_micros=cpm_bid_micros,
        )

    tools.extend([create_ad_group, update_ad_group])
    return tools


def register_ad_group_tools(mcp: FastMCP[Any]) -> AdGroupService:
    """Register ad group tools with the MCP server.

    Returns the AdGroupService instance for testing purposes.
    """
    service = AdGroupService()
    tools = create_ad_group_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
