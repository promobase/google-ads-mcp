"""Bidding data exclusion service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.bidding_data_exclusion_service import (
    BiddingDataExclusionServiceClient,
)
from google.ads.googleads.v20.services.types.bidding_data_exclusion_service import (
    MutateBiddingDataExclusionsRequest,
    MutateBiddingDataExclusionsResponse,
    BiddingDataExclusionOperation,
)
from google.ads.googleads.v20.resources.types.bidding_data_exclusion import (
    BiddingDataExclusion,
)
from google.ads.googleads.v20.enums.types.seasonality_event_scope import (
    SeasonalityEventScopeEnum,
)
from google.ads.googleads.v20.enums.types.seasonality_event_status import (
    SeasonalityEventStatusEnum,
)
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.errors import GoogleAdsException

from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BiddingDataExclusionService:
    """Bidding data exclusion service for managing bid strategy data exclusions."""

    def __init__(self) -> None:
        """Initialize the bidding data exclusion service."""
        self._client: Optional[BiddingDataExclusionServiceClient] = None

    @property
    def client(self) -> BiddingDataExclusionServiceClient:
        """Get the bidding data exclusion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BiddingDataExclusionService")
        assert self._client is not None
        return self._client

    async def create_bidding_data_exclusion(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        scope: str,
        start_date_time: str,
        end_date_time: str,
        status: str = "ENABLED",
        campaigns: Optional[List[str]] = None,
        advertising_channel_types: Optional[List[str]] = None,
        devices: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a bidding data exclusion to exclude date ranges from automated bidding.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name for the data exclusion
            scope: Scope of the exclusion (CUSTOMER, CAMPAIGN)
            start_date_time: Start date and time (YYYY-MM-DD HH:MM:SS)
            end_date_time: End date and time (YYYY-MM-DD HH:MM:SS)
            status: Status of the exclusion (ENABLED, PAUSED, REMOVED)
            campaigns: List of campaign resource names (required if scope is CAMPAIGN)
            advertising_channel_types: List of advertising channel types to apply to
            devices: List of device types to apply to (DESKTOP, MOBILE, TABLET)
            description: Optional description for the exclusion

        Returns:
            Created bidding data exclusion details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding data exclusion
            exclusion = BiddingDataExclusion()
            exclusion.name = name
            exclusion.scope = getattr(
                SeasonalityEventScopeEnum.SeasonalityEventScope, scope
            )
            exclusion.status = getattr(
                SeasonalityEventStatusEnum.SeasonalityEventStatus, status
            )
            exclusion.start_date_time = start_date_time
            exclusion.end_date_time = end_date_time

            if description:
                exclusion.description = description

            # Set campaigns if scope is CAMPAIGN
            if scope == "CAMPAIGN" and campaigns:
                exclusion.campaigns.extend(campaigns)

            # Set advertising channel types
            if advertising_channel_types:
                for channel_type in advertising_channel_types:
                    exclusion.advertising_channel_types.append(
                        getattr(
                            AdvertisingChannelTypeEnum.AdvertisingChannelType,
                            channel_type,
                        )
                    )

            # Set devices
            if devices:
                for device in devices:
                    exclusion.devices.append(getattr(DeviceEnum.Device, device))

            # Create operation
            operation = BiddingDataExclusionOperation()
            operation.create = exclusion

            # Create request
            request = MutateBiddingDataExclusionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingDataExclusionsResponse = (
                self.client.mutate_bidding_data_exclusions(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created bidding data exclusion: {name}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create bidding data exclusion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_bidding_data_exclusion(
        self,
        ctx: Context,
        customer_id: str,
        exclusion_resource_name: str,
        name: Optional[str] = None,
        start_date_time: Optional[str] = None,
        end_date_time: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a bidding data exclusion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            exclusion_resource_name: Resource name of the exclusion to update
            name: Optional new name
            start_date_time: Optional new start date and time
            end_date_time: Optional new end date and time
            status: Optional new status (ENABLED, PAUSED, REMOVED)
            description: Optional new description

        Returns:
            Updated bidding data exclusion details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding data exclusion with resource name
            exclusion = BiddingDataExclusion()
            exclusion.resource_name = exclusion_resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                exclusion.name = name
                update_mask_paths.append("name")

            if start_date_time is not None:
                exclusion.start_date_time = start_date_time
                update_mask_paths.append("start_date_time")

            if end_date_time is not None:
                exclusion.end_date_time = end_date_time
                update_mask_paths.append("end_date_time")

            if status is not None:
                exclusion.status = getattr(
                    SeasonalityEventStatusEnum.SeasonalityEventStatus, status
                )
                update_mask_paths.append("status")

            if description is not None:
                exclusion.description = description
                update_mask_paths.append("description")

            # Create operation
            operation = BiddingDataExclusionOperation()
            operation.update = exclusion
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateBiddingDataExclusionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_bidding_data_exclusions(request=request)

            await ctx.log(
                level="info",
                message="Updated bidding data exclusion",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update bidding data exclusion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_bidding_data_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        scope_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List bidding data exclusions for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            scope_filter: Optional scope filter (CUSTOMER, CAMPAIGN)

        Returns:
            List of bidding data exclusions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT 
                    bidding_data_exclusion.resource_name,
                    bidding_data_exclusion.data_exclusion_id,
                    bidding_data_exclusion.scope,
                    bidding_data_exclusion.status,
                    bidding_data_exclusion.name,
                    bidding_data_exclusion.description,
                    bidding_data_exclusion.start_date_time,
                    bidding_data_exclusion.end_date_time,
                    bidding_data_exclusion.campaigns,
                    bidding_data_exclusion.advertising_channel_types,
                    bidding_data_exclusion.devices
                FROM bidding_data_exclusion
            """

            if scope_filter:
                query += f" WHERE bidding_data_exclusion.scope = '{scope_filter}'"

            query += " ORDER BY bidding_data_exclusion.data_exclusion_id DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            exclusions = []
            for row in response:
                exclusion = row.bidding_data_exclusion

                exclusion_dict = {
                    "resource_name": exclusion.resource_name,
                    "data_exclusion_id": str(exclusion.data_exclusion_id),
                    "scope": exclusion.scope.name if exclusion.scope else "UNKNOWN",
                    "status": exclusion.status.name if exclusion.status else "UNKNOWN",
                    "name": exclusion.name,
                    "description": exclusion.description,
                    "start_date_time": exclusion.start_date_time,
                    "end_date_time": exclusion.end_date_time,
                    "campaigns": list(exclusion.campaigns),
                    "advertising_channel_types": [
                        channel_type.name
                        for channel_type in exclusion.advertising_channel_types
                    ],
                    "devices": [device.name for device in exclusion.devices],
                }

                exclusions.append(exclusion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(exclusions)} bidding data exclusions",
            )

            return exclusions

        except Exception as e:
            error_msg = f"Failed to list bidding data exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_bidding_data_exclusion(
        self,
        ctx: Context,
        customer_id: str,
        exclusion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a bidding data exclusion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            exclusion_resource_name: Resource name of the exclusion to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = BiddingDataExclusionOperation()
            operation.remove = exclusion_resource_name

            # Create request
            request = MutateBiddingDataExclusionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_bidding_data_exclusions(request=request)

            await ctx.log(
                level="info",
                message="Removed bidding data exclusion",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove bidding data exclusion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_bidding_data_exclusion_tools(
    service: BiddingDataExclusionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the bidding data exclusion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_bidding_data_exclusion(
        ctx: Context,
        customer_id: str,
        name: str,
        scope: str,
        start_date_time: str,
        end_date_time: str,
        status: str = "ENABLED",
        campaigns: Optional[List[str]] = None,
        advertising_channel_types: Optional[List[str]] = None,
        devices: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a bidding data exclusion to exclude specific date ranges from automated bidding.

        Args:
            customer_id: The customer ID
            name: Name for the data exclusion
            scope: Scope of the exclusion (CUSTOMER for account-wide, CAMPAIGN for specific campaigns)
            start_date_time: Start date and time in YYYY-MM-DD HH:MM:SS format
            end_date_time: End date and time in YYYY-MM-DD HH:MM:SS format
            status: Status (ENABLED, PAUSED, REMOVED)
            campaigns: List of campaign resource names (required if scope is CAMPAIGN)
            advertising_channel_types: List of channel types (SEARCH, DISPLAY, SHOPPING, etc.)
            devices: List of device types (DESKTOP, MOBILE, TABLET)
            description: Optional description for the exclusion

        Returns:
            Created bidding data exclusion details with resource_name
        """
        return await service.create_bidding_data_exclusion(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            scope=scope,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            status=status,
            campaigns=campaigns,
            advertising_channel_types=advertising_channel_types,
            devices=devices,
            description=description,
        )

    async def update_bidding_data_exclusion(
        ctx: Context,
        customer_id: str,
        exclusion_resource_name: str,
        name: Optional[str] = None,
        start_date_time: Optional[str] = None,
        end_date_time: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a bidding data exclusion.

        Args:
            customer_id: The customer ID
            exclusion_resource_name: Resource name of the exclusion to update
            name: Optional new name
            start_date_time: Optional new start date and time (YYYY-MM-DD HH:MM:SS)
            end_date_time: Optional new end date and time (YYYY-MM-DD HH:MM:SS)
            status: Optional new status (ENABLED, PAUSED, REMOVED)
            description: Optional new description

        Returns:
            Updated bidding data exclusion details with list of updated fields
        """
        return await service.update_bidding_data_exclusion(
            ctx=ctx,
            customer_id=customer_id,
            exclusion_resource_name=exclusion_resource_name,
            name=name,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            status=status,
            description=description,
        )

    async def list_bidding_data_exclusions(
        ctx: Context,
        customer_id: str,
        scope_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List bidding data exclusions for a customer.

        Args:
            customer_id: The customer ID
            scope_filter: Optional scope filter (CUSTOMER, CAMPAIGN)

        Returns:
            List of bidding data exclusions with details including date ranges and scope
        """
        return await service.list_bidding_data_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            scope_filter=scope_filter,
        )

    async def remove_bidding_data_exclusion(
        ctx: Context,
        customer_id: str,
        exclusion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a bidding data exclusion.

        Args:
            customer_id: The customer ID
            exclusion_resource_name: Resource name of the exclusion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_bidding_data_exclusion(
            ctx=ctx,
            customer_id=customer_id,
            exclusion_resource_name=exclusion_resource_name,
        )

    tools.extend(
        [
            create_bidding_data_exclusion,
            update_bidding_data_exclusion,
            list_bidding_data_exclusions,
            remove_bidding_data_exclusion,
        ]
    )
    return tools


def register_bidding_data_exclusion_tools(
    mcp: FastMCP[Any],
) -> BiddingDataExclusionService:
    """Register bidding data exclusion tools with the MCP server.

    Returns the BiddingDataExclusionService instance for testing purposes.
    """
    service = BiddingDataExclusionService()
    tools = create_bidding_data_exclusion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
