"""Campaign bid modifier service implementation using Google Ads SDK.

Note: In Google Ads API v20, bid modifiers for most criteria (device, location,
demographics, etc.) are managed through CampaignCriterion with the bid_modifier field.
CampaignBidModifier is specifically for interaction type bid modifiers.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import InteractionTypeInfo
from google.ads.googleads.v20.enums.types.interaction_type import InteractionTypeEnum
from google.ads.googleads.v20.resources.types.campaign_bid_modifier import (
    CampaignBidModifier,
)
from google.ads.googleads.v20.services.services.campaign_bid_modifier_service import (
    CampaignBidModifierServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
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
    """Campaign bid modifier service for interaction type bid adjustments.

    Note: For device, location, demographic, and ad schedule bid modifiers,
    use CampaignCriterionService instead.
    """

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

    async def create_interaction_type_bid_modifier(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        interaction_type: InteractionTypeEnum.InteractionType,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create an interaction type bid modifier for a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            interaction_type: Interaction type enum value
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 is no change)

        Returns:
            Created bid modifier details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create interaction type bid modifier
            bid_modifier_obj = CampaignBidModifier()
            bid_modifier_obj.campaign = campaign_resource
            bid_modifier_obj.bid_modifier = bid_modifier

            # Set interaction type criterion
            interaction_info = InteractionTypeInfo()
            interaction_info.type_ = interaction_type
            bid_modifier_obj.interaction_type = interaction_info

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
                message=f"Created interaction type bid modifier for campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create interaction type bid modifier: {str(e)}"
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
        """List campaign bid modifiers (interaction type only).

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
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    campaign_bid_modifier.resource_name,
                    campaign_bid_modifier.campaign,
                    campaign_bid_modifier.criterion_id,
                    campaign_bid_modifier.bid_modifier,
                    campaign_bid_modifier.interaction_type.type,
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
                    "criterion_id": str(bid_modifier.criterion_id)
                    if bid_modifier.criterion_id
                    else None,
                    "interaction_type": None,
                }

                # Add interaction type if present
                if (
                    bid_modifier.interaction_type
                    and bid_modifier.interaction_type.type_
                ):
                    modifier_dict["interaction_type"] = (
                        bid_modifier.interaction_type.type_.name
                    )

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

    async def create_interaction_type_bid_modifier(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        interaction_type: str,
        bid_modifier: float,
    ) -> Dict[str, Any]:
        """Create an interaction type bid modifier for a campaign.

        Note: For device, location, demographic, and ad schedule bid modifiers,
        use the campaign criterion service instead.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            interaction_type: Interaction type - CALLS
            bid_modifier: Bid modifier value (0.1-10.0, where 1.0 means no change)

        Returns:
            Created bid modifier details with resource_name
        """
        # Convert string enum to proper enum type
        interaction_type_enum = getattr(
            InteractionTypeEnum.InteractionType, interaction_type
        )

        return await service.create_interaction_type_bid_modifier(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            interaction_type=interaction_type_enum,
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
        """List campaign bid modifiers (interaction type only).

        Note: This only lists interaction type bid modifiers. For device, location,
        demographic, and ad schedule bid modifiers, use the campaign criterion service.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of campaign bid modifiers with interaction type details
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
            create_interaction_type_bid_modifier,
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
