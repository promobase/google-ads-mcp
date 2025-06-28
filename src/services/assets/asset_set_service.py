"""Asset set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_set_status import AssetSetStatusEnum
from google.ads.googleads.v20.enums.types.asset_set_type import AssetSetTypeEnum
from google.ads.googleads.v20.resources.types.asset_set import AssetSet
from google.ads.googleads.v20.services.services.asset_set_service import (
    AssetSetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.asset_set_service import (
    AssetSetOperation,
    MutateAssetSetsRequest,
    MutateAssetSetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AssetSetService:
    """Asset set service for managing collections of assets."""

    def __init__(self) -> None:
        """Initialize the asset set service."""
        self._client: Optional[AssetSetServiceClient] = None

    @property
    def client(self) -> AssetSetServiceClient:
        """Get the asset set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetSetService")
        assert self._client is not None
        return self._client

    async def create_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        asset_set_type: AssetSetTypeEnum.AssetSetType,
        status: AssetSetStatusEnum.AssetSetStatus = AssetSetStatusEnum.AssetSetStatus.ENABLED,
    ) -> Dict[str, Any]:
        """Create a new asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Asset set name
            asset_set_type: Type of asset set (MERCHANT_CENTER_FEED, DYNAMIC_EDUCATION, etc.)
            status: Asset set status (ENABLED, REMOVED)

        Returns:
            Created asset set details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset set
            asset_set = AssetSet()
            asset_set.name = name
            asset_set.type_ = asset_set_type
            asset_set.status = status

            # Create operation
            operation = AssetSetOperation()
            operation.create = asset_set

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAssetSetsResponse = self.client.mutate_asset_sets(
                request=request
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        name: Optional[str] = None,
        status: Optional[AssetSetStatusEnum.AssetSetStatus] = None,
    ) -> Dict[str, Any]:
        """Update an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_id: The asset set ID to update
            name: Optional new name
            status: Optional new status

        Returns:
            Updated asset set details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"

            # Create asset set with resource name
            asset_set = AssetSet()
            asset_set.resource_name = resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                asset_set.name = name
                update_mask_paths.append("name")

            if status is not None:
                asset_set.status = status
                update_mask_paths.append("status")

            # Create operation
            operation = AssetSetOperation()
            operation.update = asset_set
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_asset_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated asset set {asset_set_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_asset_sets(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_type: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset sets.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_type: Optional asset set type to filter by
            include_removed: Whether to include removed asset sets
            limit: Maximum number of results

        Returns:
            List of asset sets
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
                    asset_set.id,
                    asset_set.name,
                    asset_set.type,
                    asset_set.status,
                    asset_set.resource_name
                FROM asset_set
            """

            conditions = []
            if not include_removed:
                conditions.append("asset_set.status != 'REMOVED'")
            if asset_set_type:
                conditions.append(f"asset_set.type = '{asset_set_type}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY asset_set.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            asset_sets = []
            for row in response:
                asset_set = row.asset_set

                asset_set_dict = {
                    "asset_set_id": str(asset_set.id),
                    "name": asset_set.name,
                    "type": asset_set.type_.name if asset_set.type_ else "UNKNOWN",
                    "status": asset_set.status.name if asset_set.status else "UNKNOWN",
                    "resource_name": asset_set.resource_name,
                }

                asset_sets.append(asset_set_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(asset_sets)} asset sets",
            )

            return asset_sets

        except Exception as e:
            error_msg = f"Failed to list asset sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
    ) -> Dict[str, Any]:
        """Remove an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_id: The asset set ID to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"

            # Create operation
            operation = AssetSetOperation()
            operation.remove = resource_name

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_asset_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset set {asset_set_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_set_tools(
    service: AssetSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset set service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_asset_set(
        ctx: Context,
        customer_id: str,
        name: str,
        asset_set_type: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new asset set.

        Args:
            customer_id: The customer ID
            name: Asset set name
            asset_set_type: Type of asset set:
                - MERCHANT_CENTER_FEED: For retail/e-commerce assets
                - DYNAMIC_EDUCATION: For education assets
                - DYNAMIC_FLIGHTS: For travel/flight assets
                - DYNAMIC_HOTELS_AND_RENTALS: For hotel assets
                - DYNAMIC_JOBS: For job posting assets
                - DYNAMIC_LOCAL: For local business assets
                - DYNAMIC_REAL_ESTATE: For real estate assets
                - DYNAMIC_CUSTOM: For custom dynamic assets
                - DYNAMIC_TRAVEL: For travel assets
                - CHAIN_SET: For location extension assets
                - BUSINESS_PROFILE_LOCATION_SET: For Google Business Profile locations
            status: Asset set status - ENABLED or REMOVED

        Returns:
            Created asset set details including resource_name and asset_set_id
        """
        # Convert string enums to proper enum types
        asset_set_type_enum = getattr(AssetSetTypeEnum.AssetSetType, asset_set_type)
        status_enum = getattr(AssetSetStatusEnum.AssetSetStatus, status)

        return await service.create_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            asset_set_type=asset_set_type_enum,
            status=status_enum,
        )

    async def update_asset_set(
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an asset set.

        Args:
            customer_id: The customer ID
            asset_set_id: The asset set ID to update
            name: Optional new name
            status: Optional new status - ENABLED or REMOVED

        Returns:
            Updated asset set details with list of updated fields
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(AssetSetStatusEnum.AssetSetStatus, status) if status else None
        )

        return await service.update_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            name=name,
            status=status_enum,
        )

    async def list_asset_sets(
        ctx: Context,
        customer_id: str,
        asset_set_type: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset sets.

        Args:
            customer_id: The customer ID
            asset_set_type: Optional asset set type to filter by
            include_removed: Whether to include removed asset sets
            limit: Maximum number of results

        Returns:
            List of asset sets with details
        """
        return await service.list_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_type=asset_set_type,
            include_removed=include_removed,
            limit=limit,
        )

    async def remove_asset_set(
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
    ) -> Dict[str, Any]:
        """Remove an asset set.

        Args:
            customer_id: The customer ID
            asset_set_id: The asset set ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
        )

    tools.extend(
        [
            create_asset_set,
            update_asset_set,
            list_asset_sets,
            remove_asset_set,
        ]
    )
    return tools


def register_asset_set_tools(mcp: FastMCP[Any]) -> AssetSetService:
    """Register asset set tools with the MCP server.

    Returns the AssetSetService instance for testing purposes.
    """
    service = AssetSetService()
    tools = create_asset_set_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
