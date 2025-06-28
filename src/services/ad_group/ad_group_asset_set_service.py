"""Ad group asset set service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.ad_group_asset_set_service import (
    AdGroupAssetSetServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_asset_set_service import (
    MutateAdGroupAssetSetsRequest,
    MutateAdGroupAssetSetsResponse,
    AdGroupAssetSetOperation,
)
from google.ads.googleads.v20.resources.types.ad_group_asset_set import (
    AdGroupAssetSet,
)
from google.ads.googleads.errors import GoogleAdsException

from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupAssetSetService:
    """Ad group asset set service for managing asset set links to ad groups."""

    def __init__(self) -> None:
        """Initialize the ad group asset set service."""
        self._client: Optional[AdGroupAssetSetServiceClient] = None

    @property
    def client(self) -> AdGroupAssetSetServiceClient:
        """Get the ad group asset set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAssetSetService")
        assert self._client is not None
        return self._client

    async def create_ad_group_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_resource_name: str,
        asset_set_resource_name: str,
    ) -> Dict[str, Any]:
        """Create an ad group asset set to link an asset set to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_resource_name: Resource name of the ad group
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created ad group asset set details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create ad group asset set
            ad_group_asset_set = AdGroupAssetSet()
            ad_group_asset_set.ad_group = ad_group_resource_name
            ad_group_asset_set.asset_set = asset_set_resource_name

            # Create operation
            operation = AdGroupAssetSetOperation()
            operation.create = ad_group_asset_set

            # Create request
            request = MutateAdGroupAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAdGroupAssetSetsResponse = (
                self.client.mutate_ad_group_asset_sets(request=request)
            )

            await ctx.log(
                level="info",
                message="Created ad group asset set",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad group asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_ad_group_asset_sets(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        asset_set_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group asset sets for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID filter
            asset_set_id: Optional asset set ID filter

        Returns:
            List of ad group asset sets
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
                    ad_group_asset_set.resource_name,
                    ad_group_asset_set.ad_group,
                    ad_group_asset_set.asset_set,
                    ad_group_asset_set.status,
                    ad_group.id,
                    ad_group.name,
                    asset_set.id,
                    asset_set.name,
                    asset_set.type_
                FROM ad_group_asset_set
            """

            conditions = []
            if ad_group_id:
                conditions.append(f"ad_group.id = {ad_group_id}")
            if asset_set_id:
                conditions.append(f"asset_set.id = {asset_set_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ad_group_asset_set.resource_name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            asset_sets = []
            for row in response:
                ad_group_asset_set = row.ad_group_asset_set
                ad_group = row.ad_group
                asset_set = row.asset_set

                asset_set_dict = {
                    "resource_name": ad_group_asset_set.resource_name,
                    "ad_group_resource_name": ad_group_asset_set.ad_group,
                    "asset_set_resource_name": ad_group_asset_set.asset_set,
                    "status": ad_group_asset_set.status.name
                    if ad_group_asset_set.status
                    else "UNKNOWN",
                    "ad_group_id": str(ad_group.id) if ad_group.id else None,
                    "ad_group_name": ad_group.name,
                    "asset_set_id": str(asset_set.id) if asset_set.id else None,
                    "asset_set_name": asset_set.name,
                    "asset_set_type": asset_set.type_.name
                    if asset_set.type_
                    else "UNKNOWN",
                }

                asset_sets.append(asset_set_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(asset_sets)} ad group asset sets",
            )

            return asset_sets

        except Exception as e:
            error_msg = f"Failed to list ad group asset sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_asset_set_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_asset_set_resource_name: Resource name of the ad group asset set to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AdGroupAssetSetOperation()
            operation.remove = ad_group_asset_set_resource_name

            # Create request
            request = MutateAdGroupAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_asset_sets(request=request)

            await ctx.log(
                level="info",
                message="Removed ad group asset set",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_asset_set_tools(
    service: AdGroupAssetSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group asset set service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group_asset_set(
        ctx: Context,
        customer_id: str,
        ad_group_resource_name: str,
        asset_set_resource_name: str,
    ) -> Dict[str, Any]:
        """Create an ad group asset set to link an asset set to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_resource_name: Resource name of the ad group
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created ad group asset set details with resource_name
        """
        return await service.create_ad_group_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_resource_name=ad_group_resource_name,
            asset_set_resource_name=asset_set_resource_name,
        )

    async def list_ad_group_asset_sets(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        asset_set_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List ad group asset sets for a customer.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID filter
            asset_set_id: Optional asset set ID filter

        Returns:
            List of ad group asset sets with ad group and asset set details
        """
        return await service.list_ad_group_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_set_id=asset_set_id,
        )

    async def remove_ad_group_asset_set(
        ctx: Context,
        customer_id: str,
        ad_group_asset_set_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group asset set.

        Args:
            customer_id: The customer ID
            ad_group_asset_set_resource_name: Resource name of the ad group asset set to remove

        Returns:
            Removal result with status
        """
        return await service.remove_ad_group_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_asset_set_resource_name=ad_group_asset_set_resource_name,
        )

    tools.extend(
        [
            create_ad_group_asset_set,
            list_ad_group_asset_sets,
            remove_ad_group_asset_set,
        ]
    )
    return tools


def register_ad_group_asset_set_tools(
    mcp: FastMCP[Any],
) -> AdGroupAssetSetService:
    """Register ad group asset set tools with the MCP server.

    Returns the AdGroupAssetSetService instance for testing purposes.
    """
    service = AdGroupAssetSetService()
    tools = create_ad_group_asset_set_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
