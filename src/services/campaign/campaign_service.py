"""Campaign service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types import ManualCpc
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_experiment_type import (
    CampaignExperimentTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v20.resources.types.campaign import Campaign
from google.ads.googleads.v20.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_service import (
    CampaignOperation,
    MutateCampaignsRequest,
    MutateCampaignsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignService:
    """Campaign service for managing Google Ads campaigns."""

    def __init__(self) -> None:
        """Initialize the campaign service."""
        self._client: Optional[CampaignServiceClient] = None

    @property
    def client(self) -> CampaignServiceClient:
        """Get the campaign service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignService")
        assert self._client is not None
        return self._client

    async def create_campaign(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: AdvertisingChannelTypeEnum.AdvertisingChannelType = AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH,
        status: CampaignStatusEnum.CampaignStatus = CampaignStatusEnum.CampaignStatus.PAUSED,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget
            advertising_channel_type: Type of advertising channel (SEARCH, DISPLAY, etc.)
            status: Campaign status (ENABLED, PAUSED, REMOVED)
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create a new campaign
            campaign = Campaign()
            campaign.name = name
            campaign.campaign_budget = budget_resource_name
            # Set network settings
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = True
            campaign.network_settings.target_content_network = True
            campaign.network_settings.target_partner_search_network = False

            # Set advertising channel type
            campaign.advertising_channel_type = advertising_channel_type

            # Set status
            campaign.status = status

            # Set campaign experiment type
            campaign.experiment_type = (
                CampaignExperimentTypeEnum.CampaignExperimentType.BASE
            )
            # Set manual CPC bidding strategy
            manual_cpc: ManualCpc = ManualCpc()
            campaign.manual_cpc = manual_cpc

            # Set dates if provided
            if start_date:
                campaign.start_date = start_date.replace("-", "")
            if end_date:
                campaign.end_date = end_date.replace("-", "")

            # Create the operation
            operation = CampaignOperation()
            operation.create = campaign

            # Create the request
            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignsResponse = self.client.mutate_campaigns(
                request=request
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[CampaignStatusEnum.CampaignStatus] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name (optional)
            status: New campaign status (optional)
            start_date: New start date (optional)
            end_date: New end date (optional)

        Returns:
            Updated campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create campaign with resource name
            campaign = Campaign()
            campaign.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                campaign.name = name
                update_mask_fields.append("name")

            if status is not None:
                campaign.status = status
                update_mask_fields.append("status")

            if start_date is not None:
                campaign.start_date = start_date.replace("-", "")
                update_mask_fields.append("start_date")

            if end_date is not None:
                campaign.end_date = end_date.replace("-", "")
                update_mask_fields.append("end_date")

            # Create the operation
            operation = CampaignOperation()
            operation.update = campaign
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaigns(request=request)

            await ctx.log(
                level="info",
                message=f"Updated campaign {campaign_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_tools(
    service: CampaignService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_campaign(
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: str = "SEARCH",
        status: str = "PAUSED",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget (e.g., customers/123/campaignBudgets/456)
            advertising_channel_type: Type of advertising channel (SEARCH, DISPLAY, SHOPPING, VIDEO)
            status: Campaign status (ENABLED, PAUSED, REMOVED)
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details
        """
        # Convert string enums to proper enum types
        channel_type_enum = getattr(
            AdvertisingChannelTypeEnum.AdvertisingChannelType, advertising_channel_type
        )
        status_enum = getattr(CampaignStatusEnum.CampaignStatus, status)

        return await service.create_campaign(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
            advertising_channel_type=channel_type_enum,
            status=status_enum,
            start_date=start_date,
            end_date=end_date,
        )

    async def update_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name (optional)
            status: New campaign status (ENABLED, PAUSED, REMOVED) (optional)
            start_date: New start date (YYYY-MM-DD) (optional)
            end_date: New end date (YYYY-MM-DD) (optional)

        Returns:
            Updated campaign details
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(CampaignStatusEnum.CampaignStatus, status) if status else None
        )

        return await service.update_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=status_enum,
            start_date=start_date,
            end_date=end_date,
        )

    tools.extend([create_campaign, update_campaign])
    return tools


def register_campaign_tools(mcp: FastMCP[Any]) -> CampaignService:
    """Register campaign tools with the MCP server.

    Returns the CampaignService instance for testing purposes.
    """
    service = CampaignService()
    tools = create_campaign_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
