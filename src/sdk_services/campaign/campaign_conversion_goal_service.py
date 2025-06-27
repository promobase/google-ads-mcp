"""Campaign Conversion Goal service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.conversion_action_category import (
    ConversionActionCategoryEnum,
)
from google.ads.googleads.v20.enums.types.conversion_origin import (
    ConversionOriginEnum,
)
from google.ads.googleads.v20.resources.types.campaign_conversion_goal import (
    CampaignConversionGoal,
)
from google.ads.googleads.v20.services.services.campaign_conversion_goal_service import (
    CampaignConversionGoalServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_conversion_goal_service import (
    CampaignConversionGoalOperation,
    MutateCampaignConversionGoalsRequest,
    MutateCampaignConversionGoalsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignConversionGoalService:
    """Service for managing campaign-specific conversion goals.

    Campaign conversion goals allow you to control which conversions are used
    for bidding at the campaign level, overriding account-level settings.
    """

    def __init__(self) -> None:
        """Initialize the campaign conversion goal service."""
        self._client: Optional[CampaignConversionGoalServiceClient] = None

    @property
    def client(self) -> CampaignConversionGoalServiceClient:
        """Get the campaign conversion goal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CampaignConversionGoalService"
            )
        assert self._client is not None
        return self._client

    async def update_campaign_conversion_goal(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        category: ConversionActionCategoryEnum.ConversionActionCategory,
        origin: ConversionOriginEnum.ConversionOrigin,
        biddable: bool,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update a campaign conversion goal's biddability setting.

        This controls whether conversions of a specific category and origin
        are used for bidding optimization in this campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            category: Conversion category (PURCHASE, LEAD, SIGNUP, etc.)
            origin: Conversion origin (WEBSITE, APP, UPLOAD, etc.)
            biddable: Whether to use these conversions for bidding
            validate_only: If true, only validates without executing

        Returns:
            Updated campaign conversion goal details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create resource name based on campaign, category, and origin
            resource_name = (
                f"customers/{customer_id}/campaignConversionGoals/"
                f"{campaign_id}~{category.name}~{origin.name}"
            )

            # Create campaign conversion goal
            conversion_goal = CampaignConversionGoal()
            conversion_goal.resource_name = resource_name
            conversion_goal.campaign = campaign_resource
            conversion_goal.category = category
            conversion_goal.origin = origin
            conversion_goal.biddable = biddable

            # Create the operation - only biddable can be updated
            operation = CampaignConversionGoalOperation()
            operation.update = conversion_goal
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["biddable"]))

            # Create the request
            request = MutateCampaignConversionGoalsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            # Execute the mutation
            response: MutateCampaignConversionGoalsResponse = (
                self.client.mutate_campaign_conversion_goals(request=request)
            )

            await ctx.log(
                level="info",
                message=(
                    f"Updated conversion goal for campaign {campaign_id}: "
                    f"{category.name}/{origin.name} biddable={biddable}"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign conversion goal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_conversion_goal_tools(
    service: CampaignConversionGoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign conversion goal service."""
    tools = []

    async def update_campaign_conversion_goal(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        category: str,
        origin: str,
        biddable: bool,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update whether specific conversion types are used for bidding in a campaign.

        This allows you to include or exclude certain conversion categories/origins
        from being used for bid optimization at the campaign level.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            category: Conversion category - PURCHASE, LEAD, SIGNUP, PAGE_VIEW, DOWNLOAD, etc.
            origin: Conversion origin - WEBSITE, APP, UPLOAD, STORE, PHONE_CALL_FROM_ADS, etc.
            biddable: Whether to use these conversions for bidding optimization
            validate_only: If true, only validates without executing

        Returns:
            Updated campaign conversion goal details

        Example:
            # Exclude app downloads from bidding for a specific campaign
            result = await update_campaign_conversion_goal(
                customer_id="1234567890",
                campaign_id="9876543210",
                category="DOWNLOAD",
                origin="APP",
                biddable=False
            )

            # Include website purchases for bidding
            result = await update_campaign_conversion_goal(
                customer_id="1234567890",
                campaign_id="9876543210",
                category="PURCHASE",
                origin="WEBSITE",
                biddable=True
            )
        """
        # Convert string enums to proper enum types
        category_enum = getattr(
            ConversionActionCategoryEnum.ConversionActionCategory, category
        )
        origin_enum = getattr(ConversionOriginEnum.ConversionOrigin, origin)

        return await service.update_campaign_conversion_goal(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            category=category_enum,
            origin=origin_enum,
            biddable=biddable,
            validate_only=validate_only,
        )

    tools.append(update_campaign_conversion_goal)
    return tools


def register_campaign_conversion_goal_tools(
    mcp: FastMCP[Any],
) -> CampaignConversionGoalService:
    """Register campaign conversion goal tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = CampaignConversionGoalService()
    tools = create_campaign_conversion_goal_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
