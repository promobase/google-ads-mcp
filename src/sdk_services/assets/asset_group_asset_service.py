"""Asset Group Asset service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.enums.types.asset_link_status import AssetLinkStatusEnum
from google.ads.googleads.v20.resources.types.asset_group_asset import AssetGroupAsset
from google.ads.googleads.v20.services.services.asset_group_asset_service import (
    AssetGroupAssetServiceClient,
)
from google.ads.googleads.v20.services.types.asset_group_asset_service import (
    AssetGroupAssetOperation,
    MutateAssetGroupAssetsRequest,
    MutateAssetGroupAssetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AssetGroupAssetService:
    """Service for managing asset group assets in Google Ads.

    Asset group assets link assets to asset groups in Performance Max campaigns,
    specifying how assets should be used (e.g., as headlines, images, videos).
    """

    def __init__(self) -> None:
        """Initialize the asset group asset service."""
        self._client: Optional[AssetGroupAssetServiceClient] = None

    @property
    def client(self) -> AssetGroupAssetServiceClient:
        """Get the asset group asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetGroupAssetService")
        assert self._client is not None
        return self._client

    async def create_asset_group_asset(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a new asset group asset link.

        Links an asset to an asset group with a specific field type,
        determining how the asset will be used in ads.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_id: The asset group ID
            asset_id: The asset ID to link
            field_type: How the asset will be used (HEADLINE, MARKETING_IMAGE, etc.)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created asset group asset details
        """
        try:
            customer_id = format_customer_id(customer_id)
            asset_group_resource = (
                f"customers/{customer_id}/assetGroups/{asset_group_id}"
            )
            asset_resource = f"customers/{customer_id}/assets/{asset_id}"

            # Create a new asset group asset
            asset_group_asset = AssetGroupAsset()
            asset_group_asset.asset_group = asset_group_resource
            asset_group_asset.asset = asset_resource
            asset_group_asset.field_type = field_type
            # Status is automatically set to ENABLED for new assets

            # Create the operation
            operation = AssetGroupAssetOperation()
            operation.create = asset_group_asset

            # Create the request
            request = MutateAssetGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response: MutateAssetGroupAssetsResponse = (
                self.client.mutate_asset_group_assets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created asset group asset link: asset {asset_id} to asset group {asset_group_id} as {field_type.name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create asset group asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_asset_group_asset_status(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        status: AssetLinkStatusEnum.AssetLinkStatus,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update the status of an asset group asset link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_id: The asset group ID
            asset_id: The asset ID
            field_type: The field type of the asset link
            status: New status (ENABLED, PAUSED, REMOVED)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Updated asset group asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Construct resource name using the unique ~ delimiter format
            resource_name = (
                f"customers/{customer_id}/assetGroupAssets/"
                f"{asset_group_id}~{asset_id}~{field_type.name}"
            )

            # Create asset group asset with resource name and new status
            asset_group_asset = AssetGroupAsset()
            asset_group_asset.resource_name = resource_name
            asset_group_asset.status = status

            # Create the operation with update mask
            operation = AssetGroupAssetOperation()
            operation.update = asset_group_asset
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create the request
            request = MutateAssetGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response = self.client.mutate_asset_group_assets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated asset group asset status: {asset_id} in asset group {asset_group_id} to {status.name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update asset group asset status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_group_asset(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove an asset group asset link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_id: The asset group ID
            asset_id: The asset ID
            field_type: The field type of the asset link
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Construct resource name using the unique ~ delimiter format
            resource_name = (
                f"customers/{customer_id}/assetGroupAssets/"
                f"{asset_group_id}~{asset_id}~{field_type.name}"
            )

            # Create the operation
            operation = AssetGroupAssetOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateAssetGroupAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response = self.client.mutate_asset_group_assets(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset group asset: asset {asset_id} from asset group {asset_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset group asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_group_asset_tools(
    service: AssetGroupAssetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset group asset service."""
    tools = []

    async def create_asset_group_asset(
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link an asset to an asset group in a Performance Max campaign.

        This determines how the asset will be used in ads (e.g., as a headline, image, or video).

        Args:
            customer_id: The customer ID
            asset_group_id: The asset group ID (from Performance Max campaign)
            asset_id: The asset ID to link
            field_type: How the asset will be used - HEADLINE, DESCRIPTION, MARKETING_IMAGE,
                       SQUARE_MARKETING_IMAGE, YOUTUBE_VIDEO, LOGO, etc.
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created asset group asset link details

        Example:
            # Link a headline asset to an asset group
            result = await create_asset_group_asset(
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="1111111111",
                field_type="HEADLINE"
            )

            # Link a marketing image to an asset group
            result = await create_asset_group_asset(
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="2222222222",
                field_type="MARKETING_IMAGE"
            )
        """
        # Convert string enum to proper enum type
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)

        return await service.create_asset_group_asset(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            asset_id=asset_id,
            field_type=field_type_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def update_asset_group_asset_status(
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: str,
        status: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update the status of an asset link in an asset group.

        Args:
            customer_id: The customer ID
            asset_group_id: The asset group ID
            asset_id: The asset ID
            field_type: The field type of the asset link (must match existing link)
            status: New status - ENABLED, PAUSED, or REMOVED
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Updated asset group asset details

        Example:
            # Pause a headline asset in an asset group
            result = await update_asset_group_asset_status(
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="1111111111",
                field_type="HEADLINE",
                status="PAUSED"
            )
        """
        # Convert string enums to proper enum types
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)
        status_enum = getattr(AssetLinkStatusEnum.AssetLinkStatus, status)

        return await service.update_asset_group_asset_status(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            asset_id=asset_id,
            field_type=field_type_enum,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def remove_asset_group_asset(
        ctx: Context,
        customer_id: str,
        asset_group_id: str,
        asset_id: str,
        field_type: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove an asset from an asset group.

        This unlinks the asset from the asset group. The asset itself is not deleted.

        Args:
            customer_id: The customer ID
            asset_group_id: The asset group ID
            asset_id: The asset ID
            field_type: The field type of the asset link to remove
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details

        Example:
            result = await remove_asset_group_asset(
                customer_id="1234567890",
                asset_group_id="9876543210",
                asset_id="1111111111",
                field_type="HEADLINE"
            )
        """
        # Convert string enum to proper enum type
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)

        return await service.remove_asset_group_asset(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            asset_id=asset_id,
            field_type=field_type_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.extend(
        [
            create_asset_group_asset,
            update_asset_group_asset_status,
            remove_asset_group_asset,
        ]
    )
    return tools


def register_asset_group_asset_tools(
    mcp: FastMCP[Any],
) -> AssetGroupAssetService:
    """Register asset group asset tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = AssetGroupAssetService()
    tools = create_asset_group_asset_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
