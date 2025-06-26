"""Ad group label service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.ad_group_label import AdGroupLabel
from google.ads.googleads.v20.services.services.ad_group_label_service import (
    AdGroupLabelServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_label_service import (
    AdGroupLabelOperation,
    MutateAdGroupLabelsRequest,
    MutateAdGroupLabelsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupLabelService:
    """Ad group label service for organizing ad groups with labels."""

    def __init__(self) -> None:
        """Initialize the ad group label service."""
        self._client: Optional[AdGroupLabelServiceClient] = None

    @property
    def client(self) -> AdGroupLabelServiceClient:
        """Get the ad group label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupLabelService")
        assert self._client is not None
        return self._client

    async def apply_label_to_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Apply a label to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            label_id: The label ID

        Returns:
            Created ad group label details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"
            label_resource = f"customers/{customer_id}/labels/{label_id}"

            # Create ad group label
            ad_group_label = AdGroupLabel()
            ad_group_label.ad_group = ad_group_resource
            ad_group_label.label = label_resource

            # Create operation
            operation = AdGroupLabelOperation()
            operation.create = ad_group_label

            # Create request
            request = MutateAdGroupLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupLabelsResponse = self.client.mutate_ad_group_labels(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Applied label {label_id} to ad group {ad_group_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply label to ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_labels_to_ad_groups(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_label_pairs: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Apply labels to multiple ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_label_pairs: List of dicts with 'ad_group_id' and 'label_id'

        Returns:
            List of created ad group label details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for pair in ad_group_label_pairs:
                ad_group_id = pair["ad_group_id"]
                label_id = pair["label_id"]
                ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"
                label_resource = f"customers/{customer_id}/labels/{label_id}"

                # Create ad group label
                ad_group_label = AdGroupLabel()
                ad_group_label.ad_group = ad_group_resource
                ad_group_label.label = label_resource

                # Create operation
                operation = AdGroupLabelOperation()
                operation.create = ad_group_label
                operations.append(operation)

            # Create request
            request = MutateAdGroupLabelsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupLabelsResponse = self.client.mutate_ad_group_labels(
                request=request
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                pair = ad_group_label_pairs[i]
                results.append(
                    {
                        "resource_name": result.resource_name,
                        "ad_group_id": pair["ad_group_id"],
                        "label_id": pair["label_id"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Applied {len(results)} labels to ad groups",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply labels to ad groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_label_from_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Remove a label from an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            label_id: The label ID

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_label_resource = (
                f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
            )

            # Create operation
            operation = AdGroupLabelOperation()
            operation.remove = ad_group_label_resource

            # Create request
            request = MutateAdGroupLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Removed label {label_id} from ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove label from ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_labels(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        label_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group labels.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            label_id: Optional label ID to filter by
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of ad group labels
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
                    ad_group_label.resource_name,
                    ad_group_label.ad_group,
                    ad_group_label.label,
                    ad_group.id,
                    ad_group.name,
                    ad_group.campaign,
                    campaign.id,
                    campaign.name,
                    label.id,
                    label.name,
                    label.status,
                    label.text_label.background_color,
                    label.text_label.description
                FROM ad_group_label
            """

            conditions = []
            if ad_group_id:
                conditions.append(f"ad_group.id = {ad_group_id}")
            if label_id:
                conditions.append(f"label.id = {label_id}")
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ad_group.id, label.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            ad_group_labels = []
            for row in response:
                ad_group_label = row.ad_group_label
                ad_group = row.ad_group
                campaign = row.campaign
                label = row.label

                label_dict = {
                    "resource_name": ad_group_label.resource_name,
                    "ad_group_resource": ad_group_label.ad_group,
                    "label_resource": ad_group_label.label,
                    "ad_group_id": str(ad_group.id),
                    "ad_group_name": ad_group.name,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "label_id": str(label.id),
                    "label_name": label.name,
                    "label_status": label.status.name if label.status else "UNKNOWN",
                }

                if label.text_label:
                    label_dict["background_color"] = label.text_label.background_color
                    label_dict["description"] = label.text_label.description

                ad_group_labels.append(label_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(ad_group_labels)} ad group labels",
            )

            return ad_group_labels

        except Exception as e:
            error_msg = f"Failed to list ad group labels: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_label_tools(
    service: AdGroupLabelService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group label service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def apply_label_to_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Apply a label to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            label_id: The label ID to apply

        Returns:
            Created ad group label details including resource_name
        """
        return await service.apply_label_to_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
        )

    async def apply_labels_to_ad_groups(
        ctx: Context,
        customer_id: str,
        ad_group_label_pairs: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Apply labels to multiple ad groups.

        Args:
            customer_id: The customer ID
            ad_group_label_pairs: List of dicts with:
                - ad_group_id: The ad group ID
                - label_id: The label ID to apply

        Returns:
            List of created ad group label details
        """
        return await service.apply_labels_to_ad_groups(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_label_pairs=ad_group_label_pairs,
        )

    async def remove_label_from_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        label_id: str,
    ) -> Dict[str, Any]:
        """Remove a label from an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            label_id: The label ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_label_from_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
        )

    async def list_ad_group_labels(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        label_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group labels.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            label_id: Optional label ID to filter by
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of ad group labels with ad group and label details
        """
        return await service.list_ad_group_labels(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
            campaign_id=campaign_id,
        )

    tools.extend(
        [
            apply_label_to_ad_group,
            apply_labels_to_ad_groups,
            remove_label_from_ad_group,
            list_ad_group_labels,
        ]
    )
    return tools


def register_ad_group_label_tools(mcp: FastMCP[Any]) -> AdGroupLabelService:
    """Register ad group label tools with the MCP server.

    Returns the AdGroupLabelService instance for testing purposes.
    """
    service = AdGroupLabelService()
    tools = create_ad_group_label_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
