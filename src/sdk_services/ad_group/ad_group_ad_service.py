"""Ad group ad service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
from google.ads.googleads.v20.resources.types.ad_group_ad import AdGroupAd
from google.ads.googleads.v20.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_ad_service import (
    AdGroupAdOperation,
    MutateAdGroupAdsRequest,
    MutateAdGroupAdsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupAdService:
    """Ad group ad service for managing ads within ad groups."""

    def __init__(self) -> None:
        """Initialize the ad group ad service."""
        self._client: Optional[AdGroupAdServiceClient] = None

    @property
    def client(self) -> AdGroupAdServiceClient:
        """Get the ad group ad service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAdService")
        assert self._client is not None
        return self._client

    async def create_ad_group_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_resource_name: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new ad group ad (associate an ad with an ad group).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_resource_name: The resource name of the ad to add
            status: Ad group ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad group ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad group ad
            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource
            ad_group_ad.ad = ad_resource_name  # type: ignore
            ad_group_ad.status = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

            # Create operation
            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad group ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_group_ad_status(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of an ad group ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_ad_resource_name: The resource name of the ad group ad
            status: New status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated ad group ad details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create ad group ad with updated status
            ad_group_ad = AdGroupAd()
            ad_group_ad.resource_name = ad_group_ad_resource_name
            ad_group_ad.status = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

            # Create operation
            operation = AdGroupAdOperation()
            operation.update = ad_group_ad
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_ads(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad group ad status to {status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad group ad status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_ads(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        include_policy_data: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List ad group ads.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            include_policy_data: Whether to include policy approval data
            limit: Maximum number of results

        Returns:
            List of ad group ads
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    ad_group_ad.resource_name,
                    ad_group_ad.ad_group,
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.ad.type,
                    ad_group_ad.status,
                    ad_group.id,
                    ad_group.name
            """

            if include_policy_data:
                query += """,
                    ad_group_ad.policy_summary.approval_status,
                    ad_group_ad.policy_summary.review_status
                """

            query += """
                FROM ad_group_ad
                WHERE ad_group_ad.status != 'REMOVED'
            """

            if ad_group_id:
                query += f" AND ad_group.id = {ad_group_id}"

            query += f" ORDER BY ad_group.id LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            ad_group_ads = []
            for row in response:
                ad_group_ad = row.ad_group_ad
                ad = ad_group_ad.ad
                ad_group = row.ad_group

                ad_dict = {
                    "resource_name": ad_group_ad.resource_name,
                    "ad_group": ad_group_ad.ad_group,
                    "ad_group_id": str(ad_group.id),
                    "ad_group_name": ad_group.name,
                    "ad_id": str(ad.id),
                    "ad_name": ad.name,
                    "ad_type": ad.type_.name if ad.type_ else "UNKNOWN",
                    "status": ad_group_ad.status.name
                    if ad_group_ad.status
                    else "UNKNOWN",
                }

                if include_policy_data and ad_group_ad.policy_summary:
                    ad_dict["policy_summary"] = {
                        "approval_status": ad_group_ad.policy_summary.approval_status.name
                        if ad_group_ad.policy_summary.approval_status
                        else "UNKNOWN",
                        "review_status": ad_group_ad.policy_summary.review_status.name
                        if ad_group_ad.policy_summary.review_status
                        else "UNKNOWN",
                    }

                ad_group_ads.append(ad_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(ad_group_ads)} ad group ads",
            )

            return ad_group_ads

        except Exception as e:
            error_msg = f"Failed to list ad group ads: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad from an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_ad_resource_name: The resource name of the ad group ad to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AdGroupAdOperation()
            operation.remove = ad_group_ad_resource_name

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_ads(request=request)

            await ctx.log(
                level="info",
                message=f"Removed ad group ad: {ad_group_ad_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_ad_tools(
    service: AdGroupAdService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group ad service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_resource_name: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new ad group ad (associate an ad with an ad group).

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_resource_name: The resource name of the ad to add (e.g., "customers/123/ads/456")
            status: Ad group ad status - ENABLED, PAUSED, or REMOVED

        Returns:
            Created ad group ad details including resource_name and status
        """
        return await service.create_ad_group_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_resource_name=ad_resource_name,
            status=status,
        )

    async def update_ad_group_ad_status(
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
        status: str,
    ) -> Dict[str, Any]:
        """Update the status of an ad group ad.

        Args:
            customer_id: The customer ID
            ad_group_ad_resource_name: The resource name of the ad group ad
            status: New status - ENABLED, PAUSED, or REMOVED

        Returns:
            Updated ad group ad details
        """
        return await service.update_ad_group_ad_status(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_ad_resource_name=ad_group_ad_resource_name,
            status=status,
        )

    async def list_ad_group_ads(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        include_policy_data: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List ad group ads.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            include_policy_data: Whether to include policy approval and review status
            limit: Maximum number of results

        Returns:
            List of ad group ads with details
        """
        return await service.list_ad_group_ads(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            include_policy_data=include_policy_data,
            limit=limit,
        )

    async def remove_ad_group_ad(
        ctx: Context,
        customer_id: str,
        ad_group_ad_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad from an ad group.

        Args:
            customer_id: The customer ID
            ad_group_ad_resource_name: The resource name of the ad group ad to remove

        Returns:
            Removal result with status
        """
        return await service.remove_ad_group_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_ad_resource_name=ad_group_ad_resource_name,
        )

    tools.extend(
        [
            create_ad_group_ad,
            update_ad_group_ad_status,
            list_ad_group_ads,
            remove_ad_group_ad,
        ]
    )
    return tools


def register_ad_group_ad_tools(mcp: FastMCP[Any]) -> AdGroupAdService:
    """Register ad group ad tools with the MCP server.

    Returns the AdGroupAdService instance for testing purposes.
    """
    service = AdGroupAdService()
    tools = create_ad_group_ad_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
