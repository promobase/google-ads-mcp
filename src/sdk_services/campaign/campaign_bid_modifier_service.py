"""Campaign bid modifier service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    AdScheduleInfo,
    AgeRangeInfo,
    DeviceInfo,
    GenderInfo,
    IncomeRangeInfo,
    LocationInfo,
    ParentalStatusInfo,
)
from google.ads.googleads.v20.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v20.enums.types.day_of_week import DayOfWeekEnum
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v20.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v20.enums.types.minute_of_hour import MinuteOfHourEnum
from google.ads.googleads.v20.enums.types.parental_status_type import (
    ParentalStatusTypeEnum,
)
from google.ads.googleads.v20.resources.types.campaign_bid_modifier import (
    CampaignBidModifier,
)
from google.ads.googleads.v20.services.services.campaign_bid_modifier_service import (
    CampaignBidModifierServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_bid_modifier_service import (
    CampaignBidModifierOperation,
    MutateCampaignBidModifiersRequest,
    MutateCampaignBidModifiersResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignBidModifierService:
    """Campaign bid modifier service for adjusting bids based on targeting criteria."""

    def __init__(self) -> None:
        """Initialize the campaign bid modifier service."""
        self._client: Optional[CampaignBidModifierServiceClient] = None

    @property
    def client(self) -> CampaignBidModifierServiceClient:
        """Get the campaign bid modifier service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignBidModifierService")
        assert self._client is not None
        return self._client

    async def create_device_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a device bid modifier for a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_type: Device type (MOBILE, DESKTOP, TABLET)
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 is no change)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create device bid modifier
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.campaign = campaign_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set device criterion
            device_info = DeviceInfo()
            device_info.type_ = getattr(DeviceEnum.Device, device_type)
            bid_modifier_obj.device = device_info

            # Create operation
            operation = CampaignBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignBidModifiersResponse = (
                self.client.mutate_campaign_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created device bid modifier for campaign {campaign_id}",
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

    async def create_location_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_id: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a location bid modifier for a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_id: Geographic location criterion ID
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create location bid modifier
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.campaign = campaign_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set location criterion
            location_info = LocationInfo()
            location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
            bid_modifier_obj.location = location_info

            # Create operation
            operation = CampaignBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignBidModifiersResponse = (
                self.client.mutate_campaign_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created location bid modifier for campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create location bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_ad_schedule_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        day_of_week: str,
        start_hour: int,
        start_minute: str,
        end_hour: int,
        end_minute: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create an ad schedule bid modifier for a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            day_of_week: Day of week (MONDAY, TUESDAY, etc.)
            start_hour: Start hour (0-23)
            start_minute: Start minute (ZERO, FIFTEEN, THIRTY, FORTY_FIVE)
            end_hour: End hour (0-23)
            end_minute: End minute (ZERO, FIFTEEN, THIRTY, FORTY_FIVE)
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create ad schedule bid modifier
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.campaign = campaign_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set ad schedule criterion
            ad_schedule_info = AdScheduleInfo()
            ad_schedule_info.day_of_week = getattr(DayOfWeekEnum.DayOfWeek, day_of_week)
            ad_schedule_info.start_hour = start_hour
            ad_schedule_info.start_minute = getattr(
                MinuteOfHourEnum.MinuteOfHour, start_minute
            )
            ad_schedule_info.end_hour = end_hour
            ad_schedule_info.end_minute = getattr(
                MinuteOfHourEnum.MinuteOfHour, end_minute
            )
            bid_modifier_obj.ad_schedule = ad_schedule_info

            # Create operation
            operation = CampaignBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignBidModifiersResponse = (
                self.client.mutate_campaign_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created ad schedule bid modifier for campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad schedule bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_demographic_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        demographic_type: str,
        demographic_value: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a demographic bid modifier for a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            demographic_type: Type of demographic (GENDER, AGE_RANGE, INCOME_RANGE, PARENTAL_STATUS)
            demographic_value: Specific demographic value
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create demographic bid modifier
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.campaign = campaign_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set demographic criterion based on type
            if demographic_type == "GENDER":
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, demographic_value
                )
                bid_modifier_obj.gender = gender_info
            elif demographic_type == "AGE_RANGE":
                age_range_info = AgeRangeInfo()
                age_range_info.type_ = getattr(
                    AgeRangeTypeEnum.AgeRangeType, demographic_value
                )
                bid_modifier_obj.age_range = age_range_info
            elif demographic_type == "INCOME_RANGE":
                income_range_info = IncomeRangeInfo()
                income_range_info.type_ = getattr(
                    IncomeRangeTypeEnum.IncomeRangeType, demographic_value
                )
                bid_modifier_obj.income_range = income_range_info
            elif demographic_type == "PARENTAL_STATUS":
                parental_status_info = ParentalStatusInfo()
                parental_status_info.type_ = getattr(
                    ParentalStatusTypeEnum.ParentalStatusType, demographic_value
                )
                bid_modifier_obj.parental_status = parental_status_info
            else:
                raise ValueError(f"Unsupported demographic type: {demographic_type}")

            # Create operation
            operation = CampaignBidModifierOperation()
            operation.create = bid_modifier_obj

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignBidModifiersResponse = (
                self.client.mutate_campaign_bid_modifiers(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created {demographic_type} bid modifier for campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create demographic bid modifier: {str(e)}"
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
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.resource_name = bid_modifier_resource_name
            bid_modifier_obj.bid_modifier = new_bid_modifier

            # Create operation
            operation = CampaignBidModifierOperation()
            operation.update = bid_modifier_obj
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=["bid_modifier"])
            )

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_bid_modifiers(request=request)

            await ctx.log(
                level="info",
                message=f"Updated bid modifier to {new_bid_modifier}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update bid modifier: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_campaign_bid_modifiers(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign bid modifiers.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of campaign bid modifiers
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    campaign_bid_modifier.resource_name,
                    campaign_bid_modifier.campaign,
                    campaign_bid_modifier.bid_modifier,
                    campaign_bid_modifier.device.type,
                    campaign_bid_modifier.location.geo_target_constant,
                    campaign_bid_modifier.ad_schedule.day_of_week,
                    campaign_bid_modifier.ad_schedule.start_hour,
                    campaign_bid_modifier.ad_schedule.start_minute,
                    campaign_bid_modifier.ad_schedule.end_hour,
                    campaign_bid_modifier.ad_schedule.end_minute,
                    campaign_bid_modifier.gender.type,
                    campaign_bid_modifier.age_range.type,
                    campaign_bid_modifier.income_range.type,
                    campaign_bid_modifier.parental_status.type,
                    campaign.id,
                    campaign.name
                FROM campaign_bid_modifier
            """

            if campaign_id:
                query += f" WHERE campaign.id = {campaign_id}"

            query += " ORDER BY campaign.id, campaign_bid_modifier.resource_name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            bid_modifiers = []
            for row in response:
                bid_modifier = row.campaign_bid_modifier
                campaign = row.campaign

                modifier_dict = {
                    "resource_name": bid_modifier.resource_name,
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
                elif bid_modifier.location.geo_target_constant:
                    modifier_dict["criterion_type"] = "LOCATION"
                    modifier_dict["criterion_details"] = {
                        "geo_target_constant": bid_modifier.location.geo_target_constant
                    }
                elif bid_modifier.ad_schedule.day_of_week:
                    modifier_dict["criterion_type"] = "AD_SCHEDULE"
                    modifier_dict["criterion_details"] = {
                        "day_of_week": bid_modifier.ad_schedule.day_of_week.name,
                        "start_hour": bid_modifier.ad_schedule.start_hour,
                        "start_minute": bid_modifier.ad_schedule.start_minute.name,
                        "end_hour": bid_modifier.ad_schedule.end_hour,
                        "end_minute": bid_modifier.ad_schedule.end_minute.name,
                    }
                elif bid_modifier.gender.type:
                    modifier_dict["criterion_type"] = "GENDER"
                    modifier_dict["criterion_details"] = {
                        "gender": bid_modifier.gender.type.name
                    }
                elif bid_modifier.age_range.type:
                    modifier_dict["criterion_type"] = "AGE_RANGE"
                    modifier_dict["criterion_details"] = {
                        "age_range": bid_modifier.age_range.type.name
                    }
                elif bid_modifier.income_range.type:
                    modifier_dict["criterion_type"] = "INCOME_RANGE"
                    modifier_dict["criterion_details"] = {
                        "income_range": bid_modifier.income_range.type.name
                    }
                elif bid_modifier.parental_status.type:
                    modifier_dict["criterion_type"] = "PARENTAL_STATUS"
                    modifier_dict["criterion_details"] = {
                        "parental_status": bid_modifier.parental_status.type.name
                    }

                bid_modifiers.append(modifier_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(bid_modifiers)} campaign bid modifiers",
            )

            return bid_modifiers

        except Exception as e:
            error_msg = f"Failed to list campaign bid modifiers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a campaign bid modifier.

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
            operation = CampaignBidModifierOperation()
            operation.remove = bid_modifier_resource_name

            # Create request
            request = MutateCampaignBidModifiersRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_bid_modifiers(request=request)

            await ctx.log(
                level="info",
                message="Removed campaign bid modifier",
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


def create_campaign_bid_modifier_tools(
    service: CampaignBidModifierService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign bid modifier service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_device_bid_modifier(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a device bid modifier for a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_type: Device type - MOBILE, DESKTOP, or TABLET
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 means no change)

        Returns:
            Created bid modifier details with resource_name
        """
        return await service.create_device_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_type=device_type,
            bid_modifier=bid_modifier,
        )

    async def create_location_bid_modifier(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_id: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a location bid modifier for a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_id: Geographic location criterion ID
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        return await service.create_location_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_id=location_id,
            bid_modifier=bid_modifier,
        )

    async def create_ad_schedule_bid_modifier(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        day_of_week: str,
        start_hour: int,
        start_minute: str,
        end_hour: int,
        end_minute: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create an ad schedule bid modifier for a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            day_of_week: Day of week (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY)
            start_hour: Start hour (0-23)
            start_minute: Start minute (ZERO, FIFTEEN, THIRTY, FORTY_FIVE)
            end_hour: End hour (0-23)
            end_minute: End minute (ZERO, FIFTEEN, THIRTY, FORTY_FIVE)
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        return await service.create_ad_schedule_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            day_of_week=day_of_week,
            start_hour=start_hour,
            start_minute=start_minute,
            end_hour=end_hour,
            end_minute=end_minute,
            bid_modifier=bid_modifier,
        )

    async def create_demographic_bid_modifier(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        demographic_type: str,
        demographic_value: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create a demographic bid modifier for a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            demographic_type: Type of demographic (GENDER, AGE_RANGE, INCOME_RANGE, PARENTAL_STATUS)
            demographic_value: Specific demographic value:
                - For GENDER: MALE, FEMALE, UNDETERMINED
                - For AGE_RANGE: AGE_RANGE_18_24, AGE_RANGE_25_34, AGE_RANGE_35_44, AGE_RANGE_45_54, AGE_RANGE_55_64, AGE_RANGE_65_UP, AGE_RANGE_UNDETERMINED
                - For INCOME_RANGE: INCOME_RANGE_0_50, INCOME_RANGE_50_60, INCOME_RANGE_60_70, INCOME_RANGE_70_80, INCOME_RANGE_80_90, INCOME_RANGE_90_UP, INCOME_RANGE_UNDETERMINED
                - For PARENTAL_STATUS: PARENT, NOT_A_PARENT, UNDETERMINED
            bid_modifier: Bid modifier value (0.1-10.0)

        Returns:
            Created bid modifier details
        """
        return await service.create_demographic_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            demographic_type=demographic_type,
            demographic_value=demographic_value,
            bid_modifier=bid_modifier,
        )

    async def update_bid_modifier(
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
        new_bid_modifier: float,
    ) -> Dict[str, Any]:
        """Update an existing bid modifier.

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

    async def list_campaign_bid_modifiers(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign bid modifiers.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of campaign bid modifiers with criterion details
        """
        return await service.list_campaign_bid_modifiers(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    async def remove_bid_modifier(
        ctx: Context,
        customer_id: str,
        bid_modifier_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a campaign bid modifier.

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
            create_device_bid_modifier,
            create_location_bid_modifier,
            create_ad_schedule_bid_modifier,
            create_demographic_bid_modifier,
            update_bid_modifier,
            list_campaign_bid_modifiers,
            remove_bid_modifier,
        ]
    )
    return tools


def register_campaign_bid_modifier_tools(
    mcp: FastMCP[Any],
) -> CampaignBidModifierService:
    """Register campaign bid modifier tools with the MCP server.

    Returns the CampaignBidModifierService instance for testing purposes.
    """
    service = CampaignBidModifierService()
    tools = create_campaign_bid_modifier_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
