"""Asset group service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_group_status import AssetGroupStatusEnum
from google.ads.googleads.v20.resources.types.asset_group import AssetGroup
from google.ads.googleads.v20.services.services.asset_group_service import (
    AssetGroupServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.asset_group_service import (
    AssetGroupOperation,
    MutateAssetGroupsRequest,
    MutateAssetGroupsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AssetGroupService:
    """Asset group service for managing Performance Max asset groups."""

    def __init__(self) -> None:
        """Initialize the asset group service."""
        self._client: Optional[AssetGroupServiceClient] = None

    @property
    def client(self) -> AssetGroupServiceClient:
        """Get the asset group service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetGroupService")
        assert self._client is not None
        return self._client

    async def create_asset_group(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        final_urls: List[str],
        final_mobile_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AssetGroupStatusEnum.AssetGroupStatus = AssetGroupStatusEnum.AssetGroupStatus.ENABLED,
    ) -> Dict[str, Any]:
        """Create a new asset group for Performance Max campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The Performance Max campaign ID
            name: Asset group name
            final_urls: List of final URLs
            final_mobile_urls: Optional list of mobile URLs
            path1: Optional first path element
            path2: Optional second path element
            status: Asset group status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created asset group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create asset group
            asset_group = AssetGroup()
            asset_group.name = name
            asset_group.campaign = campaign_resource
            asset_group.final_urls.extend(final_urls)

            if final_mobile_urls:
                asset_group.final_mobile_urls.extend(final_mobile_urls)

            if path1:
                asset_group.path1 = path1
            if path2:
                asset_group.path2 = path2

            asset_group.status = status

            # Create operation
            operation = AssetGroupOperation()
            operation.create = asset_group

            # Create request
            request = MutateAssetGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAssetGroupsResponse = self.client.mutate_asset_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created asset group '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create asset group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_asset_group(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        name: Optional[str] = None,
        final_urls: Optional[List[str]] = None,
        final_mobile_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: Optional[AssetGroupStatusEnum.AssetGroupStatus] = None,
    ) -> Dict[str, Any]:
        """Update an asset group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_id: The asset group ID to update
            name: Optional new name
            final_urls: Optional new final URLs
            final_mobile_urls: Optional new mobile URLs
            path1: Optional new first path element
            path2: Optional new second path element
            status: Optional new status

        Returns:
            Updated asset group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetGroups/{asset_group_id}"

            # Create asset group with resource name
            asset_group = AssetGroup()
            asset_group.resource_name = resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                asset_group.name = name
                update_mask_paths.append("name")

            if final_urls is not None:
                asset_group.final_urls.clear()
                asset_group.final_urls.extend(final_urls)
                update_mask_paths.append("final_urls")

            if final_mobile_urls is not None:
                asset_group.final_mobile_urls.clear()
                asset_group.final_mobile_urls.extend(final_mobile_urls)
                update_mask_paths.append("final_mobile_urls")

            if path1 is not None:
                asset_group.path1 = path1
                update_mask_paths.append("path1")

            if path2 is not None:
                asset_group.path2 = path2
                update_mask_paths.append("path2")

            if status is not None:
                asset_group.status = status
                update_mask_paths.append("status")

            # Create operation
            operation = AssetGroupOperation()
            operation.update = asset_group
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateAssetGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_asset_groups(request=request)

            await ctx.log(
                level="info",
                message=f"Updated asset group {asset_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update asset group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_asset_groups(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            include_removed: Whether to include removed asset groups
            limit: Maximum number of results

        Returns:
            List of asset groups
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
                    asset_group.id,
                    asset_group.name,
                    asset_group.campaign,
                    asset_group.final_urls,
                    asset_group.final_mobile_urls,
                    asset_group.status,
                    asset_group.path1,
                    asset_group.path2,
                    asset_group.resource_name,
                    campaign.id,
                    campaign.name
                FROM asset_group
            """

            conditions = []
            if not include_removed:
                conditions.append("asset_group.status != 'REMOVED'")
            if campaign_id:
                conditions.append(f"campaign.id = {campaign_id}")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY asset_group.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            asset_groups = []
            for row in response:
                asset_group = row.asset_group
                campaign = row.campaign

                asset_group_dict = {
                    "asset_group_id": str(asset_group.id),
                    "name": asset_group.name,
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "campaign_resource": asset_group.campaign,
                    "final_urls": list(asset_group.final_urls),
                    "final_mobile_urls": list(asset_group.final_mobile_urls),
                    "status": asset_group.status.name
                    if asset_group.status
                    else "UNKNOWN",
                    "path1": asset_group.path1,
                    "path2": asset_group.path2,
                    "resource_name": asset_group.resource_name,
                }

                asset_groups.append(asset_group_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(asset_groups)} asset groups",
            )

            return asset_groups

        except Exception as e:
            error_msg = f"Failed to list asset groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_group(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
    ) -> Dict[str, Any]:
        """Remove an asset group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_id: The asset group ID to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetGroups/{asset_group_id}"

            # Create operation
            operation = AssetGroupOperation()
            operation.remove = resource_name

            # Create request
            request = MutateAssetGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_asset_groups(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset group {asset_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_group_tools(
    service: AssetGroupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset group service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_asset_group(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        final_urls: List[str],
        final_mobile_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new asset group for Performance Max campaigns.

        Args:
            customer_id: The customer ID
            campaign_id: The Performance Max campaign ID
            name: Asset group name (max 255 characters)
            final_urls: List of final URLs for the asset group
            final_mobile_urls: Optional list of mobile-specific URLs
            path1: Optional first URL path element (max 15 characters)
            path2: Optional second URL path element (max 15 characters)
            status: Asset group status - ENABLED, PAUSED, or REMOVED

        Returns:
            Created asset group details including resource_name and asset_group_id
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AssetGroupStatusEnum.AssetGroupStatus, status)

        return await service.create_asset_group(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            final_urls=final_urls,
            final_mobile_urls=final_mobile_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
        )

    async def update_asset_group(
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        name: Optional[str] = None,
        final_urls: Optional[List[str]] = None,
        final_mobile_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an asset group.

        Args:
            customer_id: The customer ID
            asset_group_id: The asset group ID to update
            name: Optional new name (max 255 characters)
            final_urls: Optional new final URLs
            final_mobile_urls: Optional new mobile URLs
            path1: Optional new first path element (max 15 characters)
            path2: Optional new second path element (max 15 characters)
            status: Optional new status - ENABLED, PAUSED, or REMOVED

        Returns:
            Updated asset group details with list of updated fields
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(AssetGroupStatusEnum.AssetGroupStatus, status) if status else None
        )

        return await service.update_asset_group(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            name=name,
            final_urls=final_urls,
            final_mobile_urls=final_mobile_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
        )

    async def list_asset_groups(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset groups.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            include_removed: Whether to include removed asset groups
            limit: Maximum number of results

        Returns:
            List of asset groups with details
        """
        return await service.list_asset_groups(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            include_removed=include_removed,
            limit=limit,
        )

    async def remove_asset_group(
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
    ) -> Dict[str, Any]:
        """Remove an asset group.

        Args:
            customer_id: The customer ID
            asset_group_id: The asset group ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_asset_group(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
        )

    tools.extend(
        [
            create_asset_group,
            update_asset_group,
            list_asset_groups,
            remove_asset_group,
        ]
    )
    return tools


def register_asset_group_tools(mcp: FastMCP[Any]) -> AssetGroupService:
    """Register asset group tools with the MCP server.

    Returns the AssetGroupService instance for testing purposes.
    """
    service = AssetGroupService()
    tools = create_asset_group_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
