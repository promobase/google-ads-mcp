"""Ad group ad label service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.ad_group_ad_label_service import (
    AdGroupAdLabelServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_ad_label_service import (
    MutateAdGroupAdLabelsRequest,
    MutateAdGroupAdLabelsResponse,
    AdGroupAdLabelOperation,
)
from google.ads.googleads.v20.resources.types.ad_group_ad_label import (
    AdGroupAdLabel,
)
from google.ads.googleads.errors import GoogleAdsException

from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupAdLabelService:
    """Ad group ad label service for managing labels on ad group ads."""

    def __init__(self) -> None:
        """Initialize the ad group ad label service."""
        self._client: Optional[AdGroupAdLabelServiceClient] = None

    @property
    def client(self) -> AdGroupAdLabelServiceClient:
        """Get the ad group ad label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAdLabelService")
        assert self._client is not None
        return self._client

    async def create_ad_group_ad_label(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
        label_resource_name: str,
    ) -> Dict[str, Any]:
        """Create an ad group ad label to attach a label to an ad group ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_ad_resource_name: Resource name of the ad group ad
            label_resource_name: Resource name of the label

        Returns:
            Created ad group ad label details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create ad group ad label
            ad_group_ad_label = AdGroupAdLabel()
            ad_group_ad_label.ad_group_ad = ad_group_ad_resource_name
            ad_group_ad_label.label = label_resource_name

            # Create operation
            operation = AdGroupAdLabelOperation()
            operation.create = ad_group_ad_label

            # Create request
            request = MutateAdGroupAdLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAdLabelsResponse = (
                self.client.mutate_ad_group_ad_labels(request=request)
            )

            await ctx.log(
                level="info",
                message="Created ad group ad label",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad group ad label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_ad_labels(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group ad labels for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID filter
            label_id: Optional label ID filter

        Returns:
            List of ad group ad labels
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
                    ad_group_ad_label.resource_name,
                    ad_group_ad_label.ad_group_ad,
                    ad_group_ad_label.label,
                    ad_group_ad.ad.id,
                    ad_group_ad.ad_group,
                    label.id,
                    label.name,
                    label.description
                FROM ad_group_ad_label
            """

            conditions = []
            if ad_group_id:
                conditions.append(
                    f"ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'"
                )
            if label_id:
                conditions.append(f"label.id = {label_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ad_group_ad_label.resource_name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            labels = []
            for row in response:
                ad_group_ad_label = row.ad_group_ad_label
                ad_group_ad = row.ad_group_ad
                label = row.label

                label_dict = {
                    "resource_name": ad_group_ad_label.resource_name,
                    "ad_group_ad_resource_name": ad_group_ad_label.ad_group_ad,
                    "label_resource_name": ad_group_ad_label.label,
                    "ad_id": str(ad_group_ad.ad.id) if ad_group_ad.ad.id else None,
                    "ad_group_resource_name": ad_group_ad.ad_group,
                    "label_id": str(label.id) if label.id else None,
                    "label_name": label.name,
                    "label_description": label.description,
                }

                labels.append(label_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(labels)} ad group ad labels",
            )

            return labels

        except Exception as e:
            error_msg = f"Failed to list ad group ad labels: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group_ad_label(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_ad_label_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group ad label.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_ad_label_resource_name: Resource name of the ad group ad label to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AdGroupAdLabelOperation()
            operation.remove = ad_group_ad_label_resource_name

            # Create request
            request = MutateAdGroupAdLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_ad_labels(request=request)

            await ctx.log(
                level="info",
                message="Removed ad group ad label",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group ad label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_ad_label_tools(
    service: AdGroupAdLabelService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group ad label service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group_ad_label(
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
        label_resource_name: str,
    ) -> Dict[str, Any]:
        """Create an ad group ad label to attach a label to an ad group ad.

        Args:
            customer_id: The customer ID
            ad_group_ad_resource_name: Resource name of the ad group ad
            label_resource_name: Resource name of the label

        Returns:
            Created ad group ad label details with resource_name
        """
        return await service.create_ad_group_ad_label(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_ad_resource_name=ad_group_ad_resource_name,
            label_resource_name=label_resource_name,
        )

    async def list_ad_group_ad_labels(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group ad labels for a customer.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID filter
            label_id: Optional label ID filter

        Returns:
            List of ad group ad labels with ad and label details
        """
        return await service.list_ad_group_ad_labels(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
        )

    async def remove_ad_group_ad_label(
        ctx: Context,
        customer_id: str,
        ad_group_ad_label_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group ad label.

        Args:
            customer_id: The customer ID
            ad_group_ad_label_resource_name: Resource name of the ad group ad label to remove

        Returns:
            Removal result with status
        """
        return await service.remove_ad_group_ad_label(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_ad_label_resource_name=ad_group_ad_label_resource_name,
        )

    tools.extend(
        [
            create_ad_group_ad_label,
            list_ad_group_ad_labels,
            remove_ad_group_ad_label,
        ]
    )
    return tools


def register_ad_group_ad_label_tools(
    mcp: FastMCP[Any],
) -> AdGroupAdLabelService:
    """Register ad group ad label tools with the MCP server.

    Returns the AdGroupAdLabelService instance for testing purposes.
    """
    service = AdGroupAdLabelService()
    tools = create_ad_group_ad_label_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
