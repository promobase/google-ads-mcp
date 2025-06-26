"""Campaign shared set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.campaign_shared_set_status import (
    CampaignSharedSetStatusEnum,
)
from google.ads.googleads.v20.resources.types.campaign_shared_set import (
    CampaignSharedSet,
)
from google.ads.googleads.v20.services.services.campaign_shared_set_service import (
    CampaignSharedSetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_shared_set_service import (
    CampaignSharedSetOperation,
    MutateCampaignSharedSetsRequest,
    MutateCampaignSharedSetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignSharedSetService:
    """Campaign shared set service for linking campaigns to shared sets."""

    def __init__(self) -> None:
        """Initialize the campaign shared set service."""
        self._client: Optional[CampaignSharedSetServiceClient] = None

    @property
    def client(self) -> CampaignSharedSetServiceClient:
        """Get the campaign shared set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignSharedSetService")
        assert self._client is not None
        return self._client

    async def attach_shared_set_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Attach a shared set to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID
            status: Status of the attachment (ENABLED, PAUSED, REMOVED)

        Returns:
            Created campaign shared set details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
            shared_set_resource = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            # Create campaign shared set
            campaign_shared_set = CampaignSharedSet()
            campaign_shared_set.campaign = campaign_resource
            campaign_shared_set.shared_set = shared_set_resource
            campaign_shared_set.status = getattr(
                CampaignSharedSetStatusEnum.CampaignSharedSetStatus, status
            )

            # Create operation
            operation = CampaignSharedSetOperation()
            operation.create = campaign_shared_set

            # Create request
            request = MutateCampaignSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignSharedSetsResponse = (
                self.client.mutate_campaign_shared_sets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Attached shared set {shared_set_id} to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to attach shared set to campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def attach_shared_sets_to_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        attachments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Attach multiple shared sets to campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            attachments: List of dicts with 'campaign_id', 'shared_set_id', and optional 'status'

        Returns:
            List of created campaign shared set attachments
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for attachment in attachments:
                campaign_id = attachment["campaign_id"]
                shared_set_id = attachment["shared_set_id"]
                status = attachment.get("status", "ENABLED")

                campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
                shared_set_resource = (
                    f"customers/{customer_id}/sharedSets/{shared_set_id}"
                )

                # Create campaign shared set
                campaign_shared_set = CampaignSharedSet()
                campaign_shared_set.campaign = campaign_resource
                campaign_shared_set.shared_set = shared_set_resource
                campaign_shared_set.status = getattr(
                    CampaignSharedSetStatusEnum.CampaignSharedSetStatus, status
                )

                # Create operation
                operation = CampaignSharedSetOperation()
                operation.create = campaign_shared_set
                operations.append(operation)

            # Create request
            request = MutateCampaignSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignSharedSetsResponse = (
                self.client.mutate_campaign_shared_sets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Attached {len(response.results)} shared sets to campaigns",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to attach shared sets to campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign_shared_set_status(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of a campaign shared set attachment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID
            status: New status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated campaign shared set details
        """
        try:
            customer_id = format_customer_id(customer_id)
            # Campaign shared set resource names use ~ as separator
            resource_name = f"customers/{customer_id}/campaignSharedSets/{campaign_id}~{shared_set_id}"

            # Create campaign shared set with updated status
            campaign_shared_set = CampaignSharedSet()
            campaign_shared_set.resource_name = resource_name
            campaign_shared_set.status = getattr(
                CampaignSharedSetStatusEnum.CampaignSharedSetStatus, status
            )

            # Create operation
            operation = CampaignSharedSetOperation()
            operation.update = campaign_shared_set
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create request
            request = MutateCampaignSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_shared_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated campaign shared set status to {status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign shared set status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_campaign_shared_sets(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        shared_set_id: Optional[str] = None,
        shared_set_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign shared set attachments.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            shared_set_id: Optional shared set ID to filter by
            shared_set_type: Optional shared set type to filter by

        Returns:
            List of campaign shared sets
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
                    campaign_shared_set.resource_name,
                    campaign_shared_set.campaign,
                    campaign_shared_set.shared_set,
                    campaign_shared_set.status,
                    campaign.id,
                    campaign.name,
                    shared_set.id,
                    shared_set.name,
                    shared_set.type,
                    shared_set.status
                FROM campaign_shared_set
            """

            conditions = []
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")
            if shared_set_id:
                conditions.append(f"shared_set.id = {shared_set_id}")
            if shared_set_type:
                conditions.append(f"shared_set.type = '{shared_set_type}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY campaign.id, shared_set.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            results = []
            for row in response:
                results.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(results)} campaign shared sets",
            )

            return results

        except Exception as e:
            error_msg = f"Failed to list campaign shared sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def detach_shared_set_from_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
    ) -> Dict[str, Any]:
        """Detach a shared set from a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID to detach

        Returns:
            Detachment result
        """
        try:
            customer_id = format_customer_id(customer_id)
            # Campaign shared set resource names use ~ as separator
            campaign_shared_set_resource = f"customers/{customer_id}/campaignSharedSets/{campaign_id}~{shared_set_id}"

            # Create operation
            operation = CampaignSharedSetOperation()
            operation.remove = campaign_shared_set_resource

            # Create request
            request = MutateCampaignSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_shared_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Detached shared set {shared_set_id} from campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to detach shared set from campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_campaigns_using_shared_set(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all campaigns using a specific shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID

        Returns:
            List of campaigns using the shared set
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = f"""
                SELECT
                    campaign_shared_set.resource_name,
                    campaign_shared_set.status,
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type
                FROM campaign_shared_set
                WHERE shared_set.id = {shared_set_id}
                ORDER BY campaign.name
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            campaigns = []
            for row in response:
                campaigns.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(campaigns)} campaigns using shared set {shared_set_id}",
            )

            return campaigns

        except Exception as e:
            error_msg = f"Failed to get campaigns using shared set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_shared_set_tools(
    service: CampaignSharedSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign shared set service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def attach_shared_set_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Attach a shared set to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID to attach
            status: Status of the attachment - ENABLED, PAUSED, or REMOVED

        Returns:
            Created campaign shared set attachment details
        """
        return await service.attach_shared_set_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            status=status,
        )

    async def attach_shared_sets_to_campaigns(
        ctx: Context,
        customer_id: str,
        attachments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Attach multiple shared sets to campaigns.

        Args:
            customer_id: The customer ID
            attachments: List of dicts with:
                - campaign_id: The campaign ID
                - shared_set_id: The shared set ID
                - status: Optional status (defaults to ENABLED)

        Returns:
            Mutation response with results for each attachment
        """
        return await service.attach_shared_sets_to_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            attachments=attachments,
        )

    async def update_campaign_shared_set_status(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of a campaign shared set attachment.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID
            status: New status - ENABLED, PAUSED, or REMOVED

        Returns:
            Updated campaign shared set details
        """
        return await service.update_campaign_shared_set_status(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            status=status,
        )

    async def list_campaign_shared_sets(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        shared_set_id: Optional[str] = None,
        shared_set_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign shared set attachments.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            shared_set_id: Optional shared set ID to filter by
            shared_set_type: Optional shared set type to filter by (NEGATIVE_KEYWORDS, NEGATIVE_PLACEMENTS)

        Returns:
            List of campaign shared sets with details
        """
        return await service.list_campaign_shared_sets(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
            shared_set_type=shared_set_type,
        )

    async def detach_shared_set_from_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_id: str,
    ) -> Dict[str, Any]:
        """Detach a shared set from a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_id: The shared set ID to detach

        Returns:
            Detachment result
        """
        return await service.detach_shared_set_from_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_id=shared_set_id,
        )

    async def get_campaigns_using_shared_set(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all campaigns using a specific shared set.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID

        Returns:
            List of campaigns using the shared set with attachment details
        """
        return await service.get_campaigns_using_shared_set(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
        )

    tools.extend(
        [
            attach_shared_set_to_campaign,
            attach_shared_sets_to_campaigns,
            update_campaign_shared_set_status,
            list_campaign_shared_sets,
            detach_shared_set_from_campaign,
            get_campaigns_using_shared_set,
        ]
    )
    return tools


def register_campaign_shared_set_tools(mcp: FastMCP[Any]) -> CampaignSharedSetService:
    """Register campaign shared set tools with the MCP server.

    Returns the CampaignSharedSetService instance for testing purposes.
    """
    service = CampaignSharedSetService()
    tools = create_campaign_shared_set_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
