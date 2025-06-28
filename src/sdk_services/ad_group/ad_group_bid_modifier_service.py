"""Ad group bid modifier service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    DeviceInfo,
    HotelCheckInDayInfo,
    HotelDateSelectionTypeInfo,
)
from google.ads.googleads.v20.enums.types.day_of_week import DayOfWeekEnum
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.hotel_date_selection_type import (
    HotelDateSelectionTypeEnum,
)
from google.ads.googleads.v20.resources.types.ad_group_bid_modifier import (
    AdGroupBidModifier,
)
from google.ads.googleads.v20.services.services.ad_group_bid_modifier_service import (
    AdGroupBidModifierServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_bid_modifier_service import (
    AdGroupBidModifierOperation,
    MutateAdGroupBidModifiersRequest,
    MutateAdGroupBidModifiersResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupBidModifierService:
    """Ad group bid modifier service for adjusting bids at the ad group level."""

    def __init__(self) -> None:
        """Initialize the ad group bid modifier service."""
        self._client: Optional[AdGroupBidModifierServiceClient] = None

    @property
    def client(self) -> AdGroupBidModifierServiceClient:
        """Get the ad group bid modifier service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupBidModifierService")
        assert self._client is not None
        return self._client

    async def create_device_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        device_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a device bid modifier for an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            device_type: Device type (MOBILE, DESKTOP, TABLET)
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 is no change)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create device bid modifier
            bid_modifier_obj = AdGroupBidModifier()
            bid_modifier_obj.ad_group = ad_group_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set device criterion
            device_info = DeviceInfo()
            device_info.type_ = getattr(DeviceEnum.Device, device_type)
            bid_modifier_obj.device = device_info

            # Create operation
            operation = AdGroupBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateAdGroupBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupBidModifiersResponse = (
                self.client.mutate_ad_group_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created device bid modifier for ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create device bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_hotel_check_in_day_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        day_of_week: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a hotel check-in day bid modifier for an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            day_of_week: Day of week (MONDAY, TUESDAY, etc.)
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create bid modifier
            bid_modifier_obj = AdGroupBidModifier()
            bid_modifier_obj.ad_group = ad_group_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set hotel check-in day criterion
            hotel_check_in_day = HotelCheckInDayInfo()
            hotel_check_in_day.day_of_week = getattr(
                DayOfWeekEnum.DayOfWeek, day_of_week
            )
            bid_modifier_obj.hotel_check_in_day = hotel_check_in_day

            # Create operation
            operation = AdGroupBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateAdGroupBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupBidModifiersResponse = (
                self.client.mutate_ad_group_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created hotel check-in day bid modifier for ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create hotel check-in day bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_hotel_date_selection_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        date_selection_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a hotel date selection bid modifier for an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            date_selection_type: Date selection type (DEFAULT_SELECTION or USER_SELECTED)
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create bid modifier
            bid_modifier_obj = AdGroupBidModifier()
            bid_modifier_obj.ad_group = ad_group_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set hotel date selection type criterion
            hotel_date_selection = HotelDateSelectionTypeInfo()
            hotel_date_selection.type_ = getattr(
                HotelDateSelectionTypeEnum.HotelDateSelectionType, date_selection_type
            )
            bid_modifier_obj.hotel_date_selection_type = hotel_date_selection

            # Create operation
            operation = AdGroupBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateAdGroupBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupBidModifiersResponse = (
                self.client.mutate_ad_group_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created hotel date selection bid modifier for ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create hotel date selection bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
        new_bid_modifier: float,
    ) -> Dict[str, Any]:
        """Update an existing bid modifier.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            bid_modifier_resource_name: Resource name of the bid modifier
            new_bid_modifier: New bid modifier value (0.1-10.0)

        Returns:
            Updated bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bid modifier with updated value
            bid_modifier_obj = AdGroupBidModifier()
            bid_modifier_obj.resource_name = bid_modifier_resource_name
            bid_modifier_obj.bid_modifier = new_bid_modifier

            # Create operation
            operation = AdGroupBidModifierOperation()
            operation.update = bid_modifier_obj
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=["bid_modifier"])
            )

            # Create request
            request = MutateAdGroupBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_bid_modifiers(request=request)

            await ctx.log(
                level="info",
                message=f"Updated bid modifier to {new_bid_modifier}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_bid_modifiers(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group bid modifiers.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of ad group bid modifiers
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
                    ad_group_bid_modifier.resource_name,
                    ad_group_bid_modifier.ad_group,
                    ad_group_bid_modifier.bid_modifier,
                    ad_group_bid_modifier.device.type,
                    ad_group_bid_modifier.hotel_date_selection_type.type,
                    ad_group_bid_modifier.hotel_advance_booking_window.min_days,
                    ad_group_bid_modifier.hotel_advance_booking_window.max_days,
                    ad_group_bid_modifier.hotel_length_of_stay.min_nights,
                    ad_group_bid_modifier.hotel_length_of_stay.max_nights,
                    ad_group_bid_modifier.hotel_check_in_day.day_of_week,
                    ad_group_bid_modifier.hotel_check_in_date_range.start_date,
                    ad_group_bid_modifier.hotel_check_in_date_range.end_date,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name
                FROM ad_group_bid_modifier
            """

            conditions = []
            if ad_group_id:
                conditions.append(f"ad_group.id = {ad_group_id}")
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ad_group.id, ad_group_bid_modifier.resource_name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            bid_modifiers = []
            for row in response:
                bid_modifier = row.ad_group_bid_modifier
                ad_group = row.ad_group
                campaign = row.campaign

                modifier_dict = {
                    "resource_name": bid_modifier.resource_name,
                    "ad_group_id": str(ad_group.id),
                    "ad_group_name": ad_group.name,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "bid_modifier": bid_modifier.bid_modifier,
                    "criterion_type": "UNKNOWN",
                    "criterion_details": {},
                }

                # Determine criterion type and details
                if bid_modifier.device.type:
                    modifier_dict["criterion_type"] = "DEVICE"
                    modifier_dict["criterion_details"] = {
                        "device_type": bid_modifier.device.type.name
                    }
                elif bid_modifier.hotel_date_selection_type.type:
                    modifier_dict["criterion_type"] = "HOTEL_DATE_SELECTION"
                    modifier_dict["criterion_details"] = {
                        "type": bid_modifier.hotel_date_selection_type.type.name
                    }
                elif bid_modifier.hotel_advance_booking_window:
                    modifier_dict["criterion_type"] = "HOTEL_ADVANCE_BOOKING_WINDOW"
                    modifier_dict["criterion_details"] = {
                        "min_days": bid_modifier.hotel_advance_booking_window.min_days,
                        "max_days": bid_modifier.hotel_advance_booking_window.max_days,
                    }
                elif bid_modifier.hotel_length_of_stay:
                    modifier_dict["criterion_type"] = "HOTEL_LENGTH_OF_STAY"
                    modifier_dict["criterion_details"] = {
                        "min_nights": bid_modifier.hotel_length_of_stay.min_nights,
                        "max_nights": bid_modifier.hotel_length_of_stay.max_nights,
                    }
                elif bid_modifier.hotel_check_in_day.day_of_week:
                    modifier_dict["criterion_type"] = "HOTEL_CHECK_IN_DAY"
                    modifier_dict["criterion_details"] = {
                        "day_of_week": bid_modifier.hotel_check_in_day.day_of_week.name
                    }
                elif bid_modifier.hotel_check_in_date_range.start_date:
                    modifier_dict["criterion_type"] = "HOTEL_CHECK_IN_DATE_RANGE"
                    modifier_dict["criterion_details"] = {
                        "start_date": bid_modifier.hotel_check_in_date_range.start_date,
                        "end_date": bid_modifier.hotel_check_in_date_range.end_date,
                    }

                bid_modifiers.append(modifier_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(bid_modifiers)} ad group bid modifiers",
            )

            return bid_modifiers

        except Exception as e:
            error_msg = f"Failed to list ad group bid modifiers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group bid modifier.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            bid_modifier_resource_name: Resource name of the bid modifier

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AdGroupBidModifierOperation()
            operation.remove = bid_modifier_resource_name

            # Create request
            request = MutateAdGroupBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_bid_modifiers(request=request)

            await ctx.log(
                level="info",
                message="Removed ad group bid modifier",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_bid_modifier_tools(
    service: AdGroupBidModifierService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group bid modifier service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group_device_bid_modifier(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        device_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a device bid modifier for an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            device_type: Device type - MOBILE, DESKTOP, or TABLET
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 means no change)

        Returns:
            Created bid modifier details with resource_name
        """
        return await service.create_device_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            device_type=device_type,
            bid_modifier=bid_modifier,
        )

    async def create_ad_group_hotel_check_in_day_bid_modifier(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        day_of_week: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a hotel check-in day bid modifier for an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            day_of_week: Day of week (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY)
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        return await service.create_hotel_check_in_day_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            day_of_week=day_of_week,
            bid_modifier=bid_modifier,
        )

    async def create_ad_group_hotel_date_selection_bid_modifier(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        date_selection_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a hotel date selection bid modifier for an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            date_selection_type: Date selection type - DEFAULT_SELECTION or USER_SELECTED
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        return await service.create_hotel_date_selection_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            date_selection_type=date_selection_type,
            bid_modifier=bid_modifier,
        )

    async def update_ad_group_bid_modifier(
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
        new_bid_modifier: float,
    ) -> Dict[str, Any]:
        """Update an existing ad group bid modifier.

        Args:
            customer_id: The customer ID
            bid_modifier_resource_name: Resource name of the bid modifier
            new_bid_modifier: New bid modifier value (0.1-10.0)

        Returns:
            Updated bid modifier details
        """
        return await service.update_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
            new_bid_modifier=new_bid_modifier,
        )

    async def list_ad_group_bid_modifiers(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group bid modifiers.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of ad group bid modifiers with criterion details
        """
        return await service.list_ad_group_bid_modifiers(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            campaign_id=campaign_id,
        )

    async def remove_ad_group_bid_modifier(
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group bid modifier.

        Args:
            customer_id: The customer ID
            bid_modifier_resource_name: Resource name of the bid modifier

        Returns:
            Removal result
        """
        return await service.remove_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
        )

    tools.extend(
        [
            create_ad_group_device_bid_modifier,
            create_ad_group_hotel_check_in_day_bid_modifier,
            create_ad_group_hotel_date_selection_bid_modifier,
            update_ad_group_bid_modifier,
            list_ad_group_bid_modifiers,
            remove_ad_group_bid_modifier,
        ]
    )
    return tools


def register_ad_group_bid_modifier_tools(
    mcp: FastMCP[Any],
) -> AdGroupBidModifierService:
    """Register ad group bid modifier tools with the MCP server.

    Returns the AdGroupBidModifierService instance for testing purposes.
    """
    service = AdGroupBidModifierService()
    tools = create_ad_group_bid_modifier_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
