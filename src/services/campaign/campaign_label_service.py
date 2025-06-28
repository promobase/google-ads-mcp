"""Campaign label service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.campaign_label import CampaignLabel
from google.ads.googleads.v20.services.services.campaign_label_service import (
    CampaignLabelServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_label_service import (
    CampaignLabelOperation,
    MutateCampaignLabelsRequest,
    MutateCampaignLabelsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignLabelService:
    """Campaign label service for organizing campaigns with labels."""

    def __init__(self) -> None:
        """Initialize the campaign label service."""
        self._client: Optional[CampaignLabelServiceClient] = None

    @property
    def client(self) -> CampaignLabelServiceClient:
        """Get the campaign label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignLabelService")
        assert self._client is not None
        return self._client

    async def apply_label_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Apply a label to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            label_id: The label ID

        Returns:
            Created campaign label details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
            label_resource = f"customers/{customer_id}/labels/{label_id}"

            # Create campaign label
            campaign_label = CampaignLabel()
            campaign_label.campaign = campaign_resource
            campaign_label.label = label_resource

            # Create operation
            operation = CampaignLabelOperation()
            operation.create = campaign_label

            # Create request
            request = MutateCampaignLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignLabelsResponse = self.client.mutate_campaign_labels(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Applied label {label_id} to campaign {campaign_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply label to campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_labels_to_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        campaign_label_pairs: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Apply labels to multiple campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_label_pairs: List of dicts with 'campaign_id' and 'label_id'

        Returns:
            List of created campaign label details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for pair in campaign_label_pairs:
                campaign_id = pair["campaign_id"]
                label_id = pair["label_id"]
                campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"
                label_resource = f"customers/{customer_id}/labels/{label_id}"

                # Create campaign label
                campaign_label = CampaignLabel()
                campaign_label.campaign = campaign_resource
                campaign_label.label = label_resource

                # Create operation
                operation = CampaignLabelOperation()
                operation.create = campaign_label
                operations.append(operation)

            # Create request
            request = MutateCampaignLabelsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCampaignLabelsResponse = self.client.mutate_campaign_labels(
                request=request
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                pair = campaign_label_pairs[i]
                results.append(
                    {
                        "resource_name": result.resource_name,
                        "campaign_id": pair["campaign_id"],
                        "label_id": pair["label_id"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Applied {len(results)} labels to campaigns",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply labels to campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_label_from_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Remove a label from a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            label_id: The label ID

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_label_resource = (
                f"customers/{customer_id}/campaignLabels/{campaign_id}~{label_id}"
            )

            # Create operation
            operation = CampaignLabelOperation()
            operation.remove = campaign_label_resource

            # Create request
            request = MutateCampaignLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Removed label {label_id} from campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove label from campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_campaign_labels(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign labels.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            label_id: Optional label ID to filter by

        Returns:
            List of campaign labels
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
                    campaign_label.resource_name,
                    campaign_label.campaign,
                    campaign_label.label,
                    campaign.id,
                    campaign.name,
                    label.id,
                    label.name,
                    label.status,
                    label.text_label.background_color,
                    label.text_label.description
                FROM campaign_label
            """

            conditions = []
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")
            if label_id:
                conditions.append(f"label.id = {label_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY campaign.id, label.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            campaign_labels = []
            for row in response:
                campaign_label = row.campaign_label
                campaign = row.campaign
                label = row.label

                label_dict = {
                    "resource_name": campaign_label.resource_name,
                    "campaign_resource": campaign_label.campaign,
                    "label_resource": campaign_label.label,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "label_id": str(label.id),
                    "label_name": label.name,
                    "label_status": label.status.name if label.status else "UNKNOWN",
                }

                if label.text_label:
                    label_dict["background_color"] = label.text_label.background_color
                    label_dict["description"] = label.text_label.description

                campaign_labels.append(label_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(campaign_labels)} campaign labels",
            )

            return campaign_labels

        except Exception as e:
            error_msg = f"Failed to list campaign labels: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_label_tools(
    service: CampaignLabelService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign label service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def apply_label_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Apply a label to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            label_id: The label ID to apply

        Returns:
            Created campaign label details including resource_name
        """
        return await service.apply_label_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    async def apply_labels_to_campaigns(
        ctx: Context,
        customer_id: str,
        campaign_label_pairs: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Apply labels to multiple campaigns.

        Args:
            customer_id: The customer ID
            campaign_label_pairs: List of dicts with:
                - campaign_id: The campaign ID
                - label_id: The label ID to apply

        Returns:
            List of created campaign label details
        """
        return await service.apply_labels_to_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            campaign_label_pairs=campaign_label_pairs,
        )

    async def remove_label_from_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Remove a label from a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            label_id: The label ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_label_from_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    async def list_campaign_labels(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaign labels.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            label_id: Optional label ID to filter by

        Returns:
            List of campaign labels with campaign and label details
        """
        return await service.list_campaign_labels(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    tools.extend(
        [
            apply_label_to_campaign,
            apply_labels_to_campaigns,
            remove_label_from_campaign,
            list_campaign_labels,
        ]
    )
    return tools


def register_campaign_label_tools(mcp: FastMCP[Any]) -> CampaignLabelService:
    """Register campaign label tools with the MCP server.

    Returns the CampaignLabelService instance for testing purposes.
    """
    service = CampaignLabelService()
    tools = create_campaign_label_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
