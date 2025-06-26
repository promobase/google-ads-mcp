"""Asset service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.asset_types import (
    ImageAsset,
    TextAsset,
    YoutubeVideoAsset,
)
from google.ads.googleads.v20.enums.types.asset_type import AssetTypeEnum
from google.ads.googleads.v20.resources.types.asset import Asset
from google.ads.googleads.v20.services.services.asset_service import (
    AssetServiceClient,
)
from google.ads.googleads.v20.services.types.asset_service import (
    AssetOperation,
    MutateAssetsRequest,
    MutateAssetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AssetService:
    """Asset service for managing Google Ads assets (images, videos, text)."""

    def __init__(self) -> None:
        """Initialize the asset service."""
        self._client: Optional[AssetServiceClient] = None

    @property
    def client(self) -> AssetServiceClient:
        """Get the asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetService")
        assert self._client is not None
        return self._client

    async def create_text_asset(
        self,
        ctx: Context,
        customer_id: str,
        text: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a text asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            text: The text content
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.TEXT

            # Set name if provided
            if name:
                asset.name = name
            else:
                asset.name = f"Text: {text[:50]}"  # Use first 50 chars as name

            # Create text asset
            text_asset = TextAsset()
            text_asset.text = text
            asset.text_asset = text_asset

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create text asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_image_asset(
        self,
        ctx: Context,
        customer_id: str,
        image_data: bytes,
        name: str,
        mime_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Create an image asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            image_data: The image data as bytes
            name: Name for the asset
            mime_type: MIME type (image/jpeg, image/png, etc.)

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.IMAGE
            asset.name = name

            # Create image asset
            image_asset = ImageAsset()
            image_asset.data = image_data
            image_asset.mime_type = self._get_mime_type_enum(mime_type)
            asset.image_asset = image_asset

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create image asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_youtube_video_asset(
        self,
        ctx: Context,
        customer_id: str,
        youtube_video_id: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            youtube_video_id: The YouTube video ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.YOUTUBE_VIDEO

            # Set name
            if name:
                asset.name = name
            else:
                asset.name = f"YouTube: {youtube_video_id}"

            # Create YouTube video asset
            youtube_video = YoutubeVideoAsset()
            youtube_video.youtube_video_id = youtube_video_id
            asset.youtube_video_asset = youtube_video

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create YouTube video asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_assets(
        self,
        ctx: Context,
        customer_id: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for assets in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_types: Optional list of asset types to filter by
            limit: Maximum number of results

        Returns:
            List of asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    asset.id,
                    asset.name,
                    asset.type,
                    asset.resource_name,
                    asset.text_asset.text,
                    asset.image_asset.file_size,
                    asset.youtube_video_asset.youtube_video_id
                FROM asset
            """

            if asset_types:
                type_conditions = [f"asset.type = '{t}'" for t in asset_types]
                query += " WHERE " + " OR ".join(type_conditions)

            query += f" ORDER BY asset.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            assets = []
            for row in response:
                asset = row.asset
                asset_dict = {
                    "asset_id": str(asset.id),
                    "name": asset.name,
                    "type": asset.type_.name,
                    "resource_name": asset.resource_name,
                }

                # Add type-specific fields
                if asset.type_ == AssetTypeEnum.AssetType.TEXT:
                    asset_dict["text"] = asset.text_asset.text
                elif asset.type_ == AssetTypeEnum.AssetType.IMAGE:
                    asset_dict["file_size"] = asset.image_asset.file_size
                elif asset.type_ == AssetTypeEnum.AssetType.YOUTUBE_VIDEO:
                    asset_dict["youtube_video_id"] = (
                        asset.youtube_video_asset.youtube_video_id
                    )

                assets.append(asset_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(assets)} assets",
            )

            return assets

        except Exception as e:
            error_msg = f"Failed to search assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def _get_mime_type_enum(self, mime_type: str):
        """Convert MIME type string to enum value."""
        from google.ads.googleads.v20.enums.types.mime_type import MimeTypeEnum

        mime_type_map = {
            "image/jpeg": MimeTypeEnum.MimeType.IMAGE_JPEG,
            "image/png": MimeTypeEnum.MimeType.IMAGE_PNG,
            "image/gif": MimeTypeEnum.MimeType.IMAGE_GIF,
        }

        return mime_type_map.get(
            mime_type.lower(),
            MimeTypeEnum.MimeType.IMAGE_JPEG,  # Default
        )


def create_asset_tools(service: AssetService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_text_asset(
        ctx: Context,
        customer_id: str,
        text: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a text asset.

        Args:
            customer_id: The customer ID
            text: The text content
            name: Optional name for the asset

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_text_asset(
            ctx=ctx,
            customer_id=customer_id,
            text=text,
            name=name,
        )

    async def create_image_asset(
        ctx: Context,
        customer_id: str,
        image_data: bytes,
        name: str,
        mime_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Create an image asset.

        Args:
            customer_id: The customer ID
            image_data: The image data as bytes
            name: Name for the asset
            mime_type: MIME type (image/jpeg, image/png, image/gif)

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_image_asset(
            ctx=ctx,
            customer_id=customer_id,
            image_data=image_data,
            name=name,
            mime_type=mime_type,
        )

    async def create_youtube_video_asset(
        ctx: Context,
        customer_id: str,
        youtube_video_id: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video asset.

        Args:
            customer_id: The customer ID
            youtube_video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ")
            name: Optional name for the asset

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_youtube_video_asset(
            ctx=ctx,
            customer_id=customer_id,
            youtube_video_id=youtube_video_id,
            name=name,
        )

    async def search_assets(
        ctx: Context,
        customer_id: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for assets in the account.

        Args:
            customer_id: The customer ID
            asset_types: Optional list of asset types to filter by (TEXT, IMAGE, YOUTUBE_VIDEO)
            limit: Maximum number of results

        Returns:
            List of asset details
        """
        return await service.search_assets(
            ctx=ctx,
            customer_id=customer_id,
            asset_types=asset_types,
            limit=limit,
        )

    tools.extend(
        [
            create_text_asset,
            create_image_asset,
            create_youtube_video_asset,
            search_assets,
        ]
    )
    return tools


def register_asset_tools(mcp: FastMCP[Any]) -> AssetService:
    """Register asset tools with the MCP server.

    Returns the AssetService instance for testing purposes.
    """
    service = AssetService()
    tools = create_asset_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
