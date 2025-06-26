"""Label service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.text_label import TextLabel
from google.ads.googleads.v20.enums.types.label_status import LabelStatusEnum
from google.ads.googleads.v20.resources.types.label import Label
from google.ads.googleads.v20.services.services.label_service import (
    LabelServiceClient,
)
from google.ads.googleads.v20.services.types.label_service import (
    LabelOperation,
    MutateLabelsRequest,
    MutateLabelsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class LabelService:
    """Label service for managing Google Ads labels."""

    def __init__(self) -> None:
        """Initialize the label service."""
        self._client: Optional[LabelServiceClient] = None

    @property
    def client(self) -> LabelServiceClient:
        """Get the label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("LabelService")
        assert self._client is not None
        return self._client

    async def create_label(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        background_color: Optional[str] = None,
        status: LabelStatusEnum.LabelStatus = LabelStatusEnum.LabelStatus.ENABLED,
    ) -> Dict[str, Any]:
        """Create a new label.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The label name
            description: Optional description
            background_color: Optional hex color (e.g., "#FF0000")
            status: Status (ENABLED or REMOVED)

        Returns:
            Created label details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create label
            label = Label()
            label.name = name
            label.status = status

            # Create text label
            text_label = TextLabel()
            if description:
                text_label.description = description
            if background_color:
                text_label.background_color = background_color

            label.text_label = text_label

            # Create operation
            operation = LabelOperation()
            operation.create = label

            # Create request
            request = MutateLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateLabelsResponse = self.client.mutate_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Created label '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_label(
        self,
        ctx: Context,
        customer_id: str,
        label_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        background_color: Optional[str] = None,
        status: Optional[LabelStatusEnum.LabelStatus] = None,
    ) -> Dict[str, Any]:
        """Update an existing label.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            label_id: The label ID to update
            name: New name (optional)
            description: New description (optional)
            background_color: New background color (optional)
            status: New status (optional)

        Returns:
            Updated label details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/labels/{label_id}"

            # Create label with resource name
            label = Label()
            label.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                label.name = name
                update_mask_fields.append("name")

            if status is not None:
                label.status = status
                update_mask_fields.append("status")

            # Update text label fields
            if description is not None or background_color is not None:
                text_label = TextLabel()
                if description is not None:
                    text_label.description = description
                    update_mask_fields.append("text_label.description")
                if background_color is not None:
                    text_label.background_color = background_color
                    update_mask_fields.append("text_label.background_color")
                label.text_label = text_label

            # Create operation
            operation = LabelOperation()
            operation.update = label
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Updated label {label_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_labels(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all labels in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            status_filter: Optional filter by status (ENABLED or REMOVED)

        Returns:
            List of labels
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    label.id,
                    label.name,
                    label.status,
                    label.text_label.description,
                    label.text_label.background_color,
                    label.resource_name
                FROM label
            """

            if status_filter:
                query += f" WHERE label.status = '{status_filter}'"

            query += " ORDER BY label.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            labels = []
            for row in response:
                label = row.label
                labels.append(
                    {
                        "label_id": str(label.id),
                        "name": label.name,
                        "status": label.status.name if label.status else "UNKNOWN",
                        "description": label.text_label.description
                        if label.text_label
                        else None,
                        "background_color": label.text_label.background_color
                        if label.text_label
                        else None,
                        "resource_name": label.resource_name,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Found {len(labels)} labels",
            )

            return labels

        except Exception as e:
            error_msg = f"Failed to list labels: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_label_to_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        label_id: str,
        campaign_ids: List[str],
    ) -> Dict[str, Any]:
        """Apply a label to multiple campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            label_id: The label ID to apply
            campaign_ids: List of campaign IDs

        Returns:
            Application result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use CampaignLabelService
            sdk_client = get_sdk_client()
            campaign_label_service = sdk_client.client.get_service(
                "CampaignLabelService"
            )

            from google.ads.googleads.v20.resources.types.campaign_label import (
                CampaignLabel,
            )
            from google.ads.googleads.v20.services.types.campaign_label_service import (
                CampaignLabelOperation,
                MutateCampaignLabelsRequest,
            )

            # Create operations
            operations = []
            label_resource = f"customers/{customer_id}/labels/{label_id}"

            for campaign_id in campaign_ids:
                campaign_label = CampaignLabel()
                campaign_label.campaign = (
                    f"customers/{customer_id}/campaigns/{campaign_id}"
                )
                campaign_label.label = label_resource

                operation = CampaignLabelOperation()
                operation.create = campaign_label
                operations.append(operation)

            # Create request
            request = MutateCampaignLabelsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            campaign_label_service.mutate_campaign_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Applied label {label_id} to {len(campaign_ids)} campaigns",
            )

            return {
                "label_id": label_id,
                "campaign_ids": campaign_ids,
                "status": "APPLIED",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply label to campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_label_to_ad_groups(
        self,
        ctx: Context,
        customer_id: str,
        label_id: str,
        ad_group_ids: List[str],
    ) -> Dict[str, Any]:
        """Apply a label to multiple ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            label_id: The label ID to apply
            ad_group_ids: List of ad group IDs

        Returns:
            Application result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use AdGroupLabelService
            sdk_client = get_sdk_client()
            ad_group_label_service = sdk_client.client.get_service(
                "AdGroupLabelService"
            )

            from google.ads.googleads.v20.resources.types.ad_group_label import (
                AdGroupLabel,
            )
            from google.ads.googleads.v20.services.types.ad_group_label_service import (
                AdGroupLabelOperation,
                MutateAdGroupLabelsRequest,
            )

            # Create operations
            operations = []
            label_resource = f"customers/{customer_id}/labels/{label_id}"

            for ad_group_id in ad_group_ids:
                ad_group_label = AdGroupLabel()
                ad_group_label.ad_group = (
                    f"customers/{customer_id}/adGroups/{ad_group_id}"
                )
                ad_group_label.label = label_resource

                operation = AdGroupLabelOperation()
                operation.create = ad_group_label
                operations.append(operation)

            # Create request
            request = MutateAdGroupLabelsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            ad_group_label_service.mutate_ad_group_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Applied label {label_id} to {len(ad_group_ids)} ad groups",
            )

            return {
                "label_id": label_id,
                "ad_group_ids": ad_group_ids,
                "status": "APPLIED",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply label to ad groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_label_tools(service: LabelService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the label service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_label(
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        background_color: Optional[str] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new label for organizing campaigns, ad groups, and ads.

        Args:
            customer_id: The customer ID
            name: The label name
            description: Optional description for the label
            background_color: Optional hex color code (e.g., "#FF0000" for red)
            status: Status - ENABLED or REMOVED

        Returns:
            Created label details with resource_name and label_id
        """
        # Convert string enum to proper enum type
        status_enum = getattr(LabelStatusEnum.LabelStatus, status)

        return await service.create_label(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            background_color=background_color,
            status=status_enum,
        )

    async def update_label(
        ctx: Context,
        customer_id: str,
        label_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        background_color: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing label.

        Args:
            customer_id: The customer ID
            label_id: The label ID to update
            name: New name (optional)
            description: New description (optional)
            background_color: New hex color code (optional)
            status: New status - ENABLED or REMOVED (optional)

        Returns:
            Updated label details with updated_fields list
        """
        # Convert string enum to proper enum type if provided
        status_enum = getattr(LabelStatusEnum.LabelStatus, status) if status else None

        return await service.update_label(
            ctx=ctx,
            customer_id=customer_id,
            label_id=label_id,
            name=name,
            description=description,
            background_color=background_color,
            status=status_enum,
        )

    async def list_labels(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all labels in the account.

        Args:
            customer_id: The customer ID
            status_filter: Optional filter by status - ENABLED or REMOVED

        Returns:
            List of labels with details
        """
        return await service.list_labels(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    async def apply_label_to_campaigns(
        ctx: Context,
        customer_id: str,
        label_id: str,
        campaign_ids: List[str],
    ) -> Dict[str, Any]:
        """Apply a label to multiple campaigns.

        Args:
            customer_id: The customer ID
            label_id: The label ID to apply
            campaign_ids: List of campaign IDs to label

        Returns:
            Application result with status
        """
        return await service.apply_label_to_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            label_id=label_id,
            campaign_ids=campaign_ids,
        )

    async def apply_label_to_ad_groups(
        ctx: Context,
        customer_id: str,
        label_id: str,
        ad_group_ids: List[str],
    ) -> Dict[str, Any]:
        """Apply a label to multiple ad groups.

        Args:
            customer_id: The customer ID
            label_id: The label ID to apply
            ad_group_ids: List of ad group IDs to label

        Returns:
            Application result with status
        """
        return await service.apply_label_to_ad_groups(
            ctx=ctx,
            customer_id=customer_id,
            label_id=label_id,
            ad_group_ids=ad_group_ids,
        )

    tools.extend(
        [
            create_label,
            update_label,
            list_labels,
            apply_label_to_campaigns,
            apply_label_to_ad_groups,
        ]
    )
    return tools


def register_label_tools(mcp: FastMCP[Any]) -> LabelService:
    """Register label tools with the MCP server.

    Returns the LabelService instance for testing purposes.
    """
    service = LabelService()
    tools = create_label_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
