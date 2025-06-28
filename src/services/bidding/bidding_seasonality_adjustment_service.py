"""Bidding seasonality adjustment service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.bidding_seasonality_adjustment_service import (
    BiddingSeasonalityAdjustmentServiceClient,
)
from google.ads.googleads.v20.services.types.bidding_seasonality_adjustment_service import (
    MutateBiddingSeasonalityAdjustmentsRequest,
    MutateBiddingSeasonalityAdjustmentsResponse,
    BiddingSeasonalityAdjustmentOperation,
)
from google.ads.googleads.v20.resources.types.bidding_seasonality_adjustment import (
    BiddingSeasonalityAdjustment,
)
from google.ads.googleads.v20.enums.types.seasonality_event_scope import (
    SeasonalityEventScopeEnum,
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


class BiddingSeasonalityAdjustmentService:
    """Bidding seasonality adjustment service for managing seasonal bid adjustments."""

    def __init__(self) -> None:
        """Initialize the bidding seasonality adjustment service."""
        self._client: Optional[BiddingSeasonalityAdjustmentServiceClient] = None

    @property
    def client(self) -> BiddingSeasonalityAdjustmentServiceClient:
        """Get the bidding seasonality adjustment service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "BiddingSeasonalityAdjustmentService"
            )
        assert self._client is not None
        return self._client

    async def create_bidding_seasonality_adjustment(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        scope: str,
        start_date_time: str,
        end_date_time: str,
        conversion_rate_modifier: float,
        status: str = "ENABLED",
        campaigns: Optional[List[str]] = None,
        advertising_channel_types: Optional[List[str]] = None,
        devices: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a bidding seasonality adjustment for seasonal conversion rate changes.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name for the seasonality adjustment
            scope: Scope of the adjustment (CUSTOMER, CAMPAIGN, CHANNEL)
            start_date_time: Start date and time (YYYY-MM-DD HH:MM:SS)
            end_date_time: End date and time (YYYY-MM-DD HH:MM:SS)
            conversion_rate_modifier: Expected conversion rate change (0.1 to 10.0)
            status: Status of the adjustment (ENABLED, PAUSED, REMOVED)
            campaigns: List of campaign resource names (required if scope is CAMPAIGN)
            advertising_channel_types: List of advertising channel types (required if scope is CHANNEL)
            devices: List of device types to apply to (DESKTOP, MOBILE, TABLET)
            description: Optional description for the adjustment

        Returns:
            Created bidding seasonality adjustment details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding seasonality adjustment
            adjustment = BiddingSeasonalityAdjustment()
            adjustment.name = name
            adjustment.scope = getattr(
                SeasonalityEventScopeEnum.SeasonalityEventScope, scope
            )
            adjustment.start_date_time = start_date_time
            adjustment.end_date_time = end_date_time
            adjustment.conversion_rate_modifier = conversion_rate_modifier

            if description:
                adjustment.description = description

            # Set campaigns if scope is CAMPAIGN
            if scope == "CAMPAIGN" and campaigns:
                adjustment.campaigns.extend(campaigns)

            # Set advertising channel types if scope is CHANNEL
            if scope == "CHANNEL" and advertising_channel_types:
                for channel_type in advertising_channel_types:
                    adjustment.advertising_channel_types.append(
                        getattr(
                            AdvertisingChannelTypeEnum.AdvertisingChannelType,
                            channel_type,
                        )
                    )

            # Set devices
            if devices:
                for device in devices:
                    adjustment.devices.append(getattr(DeviceEnum.Device, device))

            # Create operation
            operation = BiddingSeasonalityAdjustmentOperation()
            operation.create = adjustment

            # Create request
            request = MutateBiddingSeasonalityAdjustmentsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingSeasonalityAdjustmentsResponse = (
                self.client.mutate_bidding_seasonality_adjustments(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created bidding seasonality adjustment: {name}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create bidding seasonality adjustment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_bidding_seasonality_adjustment(
        self,
        ctx: Context,
        customer_id: str,
        adjustment_resource_name: str,
        name: Optional[str] = None,
        start_date_time: Optional[str] = None,
        end_date_time: Optional[str] = None,
        conversion_rate_modifier: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a bidding seasonality adjustment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            adjustment_resource_name: Resource name of the adjustment to update
            name: Optional new name
            start_date_time: Optional new start date and time
            end_date_time: Optional new end date and time
            conversion_rate_modifier: Optional new conversion rate modifier
            description: Optional new description

        Returns:
            Updated bidding seasonality adjustment details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding seasonality adjustment with resource name
            adjustment = BiddingSeasonalityAdjustment()
            adjustment.resource_name = adjustment_resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                adjustment.name = name
                update_mask_paths.append("name")

            if start_date_time is not None:
                adjustment.start_date_time = start_date_time
                update_mask_paths.append("start_date_time")

            if end_date_time is not None:
                adjustment.end_date_time = end_date_time
                update_mask_paths.append("end_date_time")

            if conversion_rate_modifier is not None:
                adjustment.conversion_rate_modifier = conversion_rate_modifier
                update_mask_paths.append("conversion_rate_modifier")

            if description is not None:
                adjustment.description = description
                update_mask_paths.append("description")

            # Create operation
            operation = BiddingSeasonalityAdjustmentOperation()
            operation.update = adjustment
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateBiddingSeasonalityAdjustmentsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_bidding_seasonality_adjustments(
                request=request
            )

            await ctx.log(
                level="info",
                message="Updated bidding seasonality adjustment",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update bidding seasonality adjustment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_bidding_seasonality_adjustments(
        self,
        ctx: Context,
        customer_id: str,
        scope_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List bidding seasonality adjustments for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            scope_filter: Optional scope filter (CUSTOMER, CAMPAIGN, CHANNEL)

        Returns:
            List of bidding seasonality adjustments
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
                    bidding_seasonality_adjustment.resource_name,
                    bidding_seasonality_adjustment.seasonality_adjustment_id,
                    bidding_seasonality_adjustment.scope,
                    bidding_seasonality_adjustment.status,
                    bidding_seasonality_adjustment.name,
                    bidding_seasonality_adjustment.description,
                    bidding_seasonality_adjustment.start_date_time,
                    bidding_seasonality_adjustment.end_date_time,
                    bidding_seasonality_adjustment.conversion_rate_modifier,
                    bidding_seasonality_adjustment.campaigns,
                    bidding_seasonality_adjustment.advertising_channel_types,
                    bidding_seasonality_adjustment.devices
                FROM bidding_seasonality_adjustment
            """

            if scope_filter:
                query += (
                    f" WHERE bidding_seasonality_adjustment.scope = '{scope_filter}'"
                )

            query += " ORDER BY bidding_seasonality_adjustment.seasonality_adjustment_id DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            adjustments = []
            for row in response:
                adjustment = row.bidding_seasonality_adjustment

                adjustment_dict = {
                    "resource_name": adjustment.resource_name,
                    "seasonality_adjustment_id": str(
                        adjustment.seasonality_adjustment_id
                    ),
                    "scope": adjustment.scope.name if adjustment.scope else "UNKNOWN",
                    "status": adjustment.status.name
                    if adjustment.status
                    else "UNKNOWN",
                    "name": adjustment.name,
                    "description": adjustment.description,
                    "start_date_time": adjustment.start_date_time,
                    "end_date_time": adjustment.end_date_time,
                    "conversion_rate_modifier": adjustment.conversion_rate_modifier,
                    "campaigns": list(adjustment.campaigns),
                    "advertising_channel_types": [
                        channel_type.name
                        for channel_type in adjustment.advertising_channel_types
                    ],
                    "devices": [device.name for device in adjustment.devices],
                }

                adjustments.append(adjustment_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(adjustments)} bidding seasonality adjustments",
            )

            return adjustments

        except Exception as e:
            error_msg = f"Failed to list bidding seasonality adjustments: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_bidding_seasonality_adjustment(
        self,
        ctx: Context,
        customer_id: str,
        adjustment_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a bidding seasonality adjustment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            adjustment_resource_name: Resource name of the adjustment to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = BiddingSeasonalityAdjustmentOperation()
            operation.remove = adjustment_resource_name

            # Create request
            request = MutateBiddingSeasonalityAdjustmentsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_bidding_seasonality_adjustments(
                request=request
            )

            await ctx.log(
                level="info",
                message="Removed bidding seasonality adjustment",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove bidding seasonality adjustment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_bidding_seasonality_adjustment_tools(
    service: BiddingSeasonalityAdjustmentService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the bidding seasonality adjustment service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_bidding_seasonality_adjustment(
        ctx: Context,
        customer_id: str,
        name: str,
        scope: str,
        start_date_time: str,
        end_date_time: str,
        conversion_rate_modifier: float,
        status: str = "ENABLED",
        campaigns: Optional[List[str]] = None,
        advertising_channel_types: Optional[List[str]] = None,
        devices: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a bidding seasonality adjustment for seasonal conversion rate changes.

        Args:
            customer_id: The customer ID
            name: Name for the seasonality adjustment
            scope: Scope (CUSTOMER for account-wide, CAMPAIGN for specific campaigns, CHANNEL for channel types)
            start_date_time: Start date and time in YYYY-MM-DD HH:MM:SS format
            end_date_time: End date and time in YYYY-MM-DD HH:MM:SS format (max 14 days from start)
            conversion_rate_modifier: Expected conversion rate change (0.1 to 10.0, 1.0 = no change)
            status: Status (ENABLED, PAUSED, REMOVED)
            campaigns: List of campaign resource names (required if scope is CAMPAIGN)
            advertising_channel_types: List of channel types (SEARCH, DISPLAY, SHOPPING - required if scope is CHANNEL)
            devices: List of device types (DESKTOP, MOBILE, TABLET)
            description: Optional description for the adjustment

        Returns:
            Created bidding seasonality adjustment details with resource_name
        """
        return await service.create_bidding_seasonality_adjustment(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            scope=scope,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            conversion_rate_modifier=conversion_rate_modifier,
            status=status,
            campaigns=campaigns,
            advertising_channel_types=advertising_channel_types,
            devices=devices,
            description=description,
        )

    async def update_bidding_seasonality_adjustment(
        ctx: Context,
        customer_id: str,
        adjustment_resource_name: str,
        name: Optional[str] = None,
        start_date_time: Optional[str] = None,
        end_date_time: Optional[str] = None,
        conversion_rate_modifier: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a bidding seasonality adjustment.

        Args:
            customer_id: The customer ID
            adjustment_resource_name: Resource name of the adjustment to update
            name: Optional new name
            start_date_time: Optional new start date and time (YYYY-MM-DD HH:MM:SS)
            end_date_time: Optional new end date and time (YYYY-MM-DD HH:MM:SS)
            conversion_rate_modifier: Optional new conversion rate modifier (0.1 to 10.0)
            description: Optional new description

        Returns:
            Updated bidding seasonality adjustment details with list of updated fields
        """
        return await service.update_bidding_seasonality_adjustment(
            ctx=ctx,
            customer_id=customer_id,
            adjustment_resource_name=adjustment_resource_name,
            name=name,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            conversion_rate_modifier=conversion_rate_modifier,
            description=description,
        )

    async def list_bidding_seasonality_adjustments(
        ctx: Context,
        customer_id: str,
        scope_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List bidding seasonality adjustments for a customer.

        Args:
            customer_id: The customer ID
            scope_filter: Optional scope filter (CUSTOMER, CAMPAIGN, CHANNEL)

        Returns:
            List of bidding seasonality adjustments with details including conversion rate modifiers
        """
        return await service.list_bidding_seasonality_adjustments(
            ctx=ctx,
            customer_id=customer_id,
            scope_filter=scope_filter,
        )

    async def remove_bidding_seasonality_adjustment(
        ctx: Context,
        customer_id: str,
        adjustment_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a bidding seasonality adjustment.

        Args:
            customer_id: The customer ID
            adjustment_resource_name: Resource name of the adjustment to remove

        Returns:
            Removal result with status
        """
        return await service.remove_bidding_seasonality_adjustment(
            ctx=ctx,
            customer_id=customer_id,
            adjustment_resource_name=adjustment_resource_name,
        )

    tools.extend(
        [
            create_bidding_seasonality_adjustment,
            update_bidding_seasonality_adjustment,
            list_bidding_seasonality_adjustments,
            remove_bidding_seasonality_adjustment,
        ]
    )
    return tools


def register_bidding_seasonality_adjustment_tools(
    mcp: FastMCP[Any],
) -> BiddingSeasonalityAdjustmentService:
    """Register bidding seasonality adjustment tools with the MCP server.

    Returns the BiddingSeasonalityAdjustmentService instance for testing purposes.
    """
    service = BiddingSeasonalityAdjustmentService()
    tools = create_bidding_seasonality_adjustment_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
