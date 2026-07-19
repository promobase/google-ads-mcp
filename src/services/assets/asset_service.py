"""Asset service implementation using Google Ads SDK."""

import base64
import mimetypes
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aiohttp

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.asset_types import (
    CallAsset,
    CalloutAsset,
    ImageAsset,
    SitelinkAsset,
    StructuredSnippetAsset,
    TextAsset,
    YoutubeVideoAsset,
)
from google.ads.googleads.v23.enums.types.asset_type import AssetTypeEnum
from google.ads.googleads.v23.resources.types.asset import Asset
from google.ads.googleads.v23.services.services.asset_service import (
    AssetServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.asset_service import (
    AssetOperation,
    MutateAssetsRequest,
    MutateAssetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_ads_error,
    format_customer_id,
    get_logger,
    serialize_proto_message,
)

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
            self._client = sdk_client.client.get_service("AssetService", version="v23")
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
            error_msg = format_ads_error(e)
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
        name: str,
        image_data_base64: Optional[str] = None,
        image_url: Optional[str] = None,
        image_file_path: Optional[str] = None,
        mime_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Create an image asset from base64, a URL, or a local file.

        Provide exactly one of the three source parameters.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name for the asset
            image_data_base64: Base64-encoded image bytes
            image_url: Public URL to download the image from
            image_file_path: Absolute path to a local image file
            mime_type: MIME type (auto-detected from URL or file extension)

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            if image_file_path:
                p = Path(image_file_path)
                raw_bytes = p.read_bytes()
                guessed = mimetypes.guess_type(str(p))[0]
                if guessed:
                    mime_type = guessed
            elif image_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        resp.raise_for_status()
                        raw_bytes = await resp.read()
                        content_type = resp.content_type or mime_type
                        if "png" in content_type:
                            mime_type = "image/png"
                        elif "gif" in content_type:
                            mime_type = "image/gif"
            elif image_data_base64:
                raw_bytes = base64.b64decode(image_data_base64)
            else:
                raise ValueError(
                    "Provide one of: image_file_path, image_url, or image_data_base64"
                )

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.IMAGE
            asset.name = name

            image_asset = ImageAsset()
            image_asset.data = raw_bytes
            image_asset.mime_type = self.get_mime_type_enum(mime_type)
            asset.image_asset = image_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
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
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create YouTube video asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_sitelink_asset(
        self,
        ctx: Context,
        customer_id: str,
        link_text: str,
        final_urls: List[str],
        description1: Optional[str] = None,
        description2: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a sitelink asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            link_text: Display text for the sitelink (1-25 chars)
            final_urls: Landing page URLs
            description1: First description line (1-35 chars)
            description2: Second description line (1-35 chars)
            name: Optional asset name

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.SITELINK
            asset.name = name or f"Sitelink: {link_text}"
            asset.final_urls.extend(final_urls)

            sitelink = SitelinkAsset()
            sitelink.link_text = link_text
            if description1:
                sitelink.description1 = description1
            if description2:
                sitelink.description2 = description2
            asset.sitelink_asset = sitelink

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create sitelink asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_callout_asset(
        self,
        ctx: Context,
        customer_id: str,
        callout_text: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a callout asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            callout_text: Callout text (1-25 chars)
            name: Optional asset name

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.CALLOUT
            asset.name = name or f"Callout: {callout_text}"

            callout = CalloutAsset()
            callout.callout_text = callout_text
            asset.callout_asset = callout

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create callout asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_structured_snippet_asset(
        self,
        ctx: Context,
        customer_id: str,
        header: str,
        values: List[str],
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a structured snippet asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            header: Snippet header (predefined, e.g. "Brands", "Types")
            values: Snippet values (3-10 items, each 1-25 chars)
            name: Optional asset name

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.STRUCTURED_SNIPPET
            asset.name = name or f"Snippet: {header}"

            snippet = StructuredSnippetAsset()
            snippet.header = header
            snippet.values.extend(values)
            asset.structured_snippet_asset = snippet

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create structured snippet asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_call_asset(
        self,
        ctx: Context,
        customer_id: str,
        country_code: str,
        phone_number: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a call asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            country_code: Two-letter country code (e.g. "US")
            phone_number: Phone number (e.g. "1234567890")
            name: Optional asset name

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.CALL
            asset.name = name or f"Call: {country_code} {phone_number}"

            call = CallAsset()
            call.country_code = country_code
            call.phone_number = phone_number
            asset.call_asset = call

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create call asset: {str(e)}"
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
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

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
                    asset_dict["file_size"] = str(asset.image_asset.file_size)
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

    def get_mime_type_enum(self, mime_type: str):
        """Convert MIME type string to enum value."""
        from google.ads.googleads.v23.enums.types.mime_type import MimeTypeEnum

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
        name: str,
        image_data_base64: Optional[str] = None,
        image_url: Optional[str] = None,
        image_file_path: Optional[str] = None,
        mime_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Create an image asset from a local file, URL, or base64 string.

        Provide exactly one of the three source parameters.

        Args:
            customer_id: The customer ID
            name: Name for the asset (e.g. "Hero Banner 1200x628")
            image_data_base64: Base64-encoded image data
            image_url: Public URL to download the image from
            image_file_path: Absolute local file path (e.g. "C:/images/logo.png")
            mime_type: MIME type - auto-detected from file extension or URL

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_image_asset(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            image_data_base64=image_data_base64,
            image_url=image_url,
            image_file_path=image_file_path,
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

    async def create_sitelink_asset(
        ctx: Context,
        customer_id: str,
        link_text: str,
        final_urls: List[str],
        description1: Optional[str] = None,
        description2: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a sitelink extension asset.

        Args:
            customer_id: The customer ID
            link_text: Display text for the sitelink (1-25 chars)
            final_urls: Landing page URLs for the sitelink
            description1: Optional first description line (1-35 chars)
            description2: Optional second description line (1-35 chars)
            name: Optional asset name

        Returns:
            Created sitelink asset details including resource_name
        """
        return await service.create_sitelink_asset(
            ctx=ctx,
            customer_id=customer_id,
            link_text=link_text,
            final_urls=final_urls,
            description1=description1,
            description2=description2,
            name=name,
        )

    async def create_callout_asset(
        ctx: Context,
        customer_id: str,
        callout_text: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a callout extension asset.

        Args:
            customer_id: The customer ID
            callout_text: The callout text (1-25 chars)
            name: Optional asset name

        Returns:
            Created callout asset details including resource_name
        """
        return await service.create_callout_asset(
            ctx=ctx,
            customer_id=customer_id,
            callout_text=callout_text,
            name=name,
        )

    async def create_structured_snippet_asset(
        ctx: Context,
        customer_id: str,
        header: str,
        values: List[str],
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a structured snippet extension asset.

        Args:
            customer_id: The customer ID
            header: Snippet header (e.g. "Brands", "Types", "Destinations", "Styles")
            values: List of snippet values (3-10 items, each 1-25 chars)
            name: Optional asset name

        Returns:
            Created structured snippet asset details including resource_name
        """
        return await service.create_structured_snippet_asset(
            ctx=ctx,
            customer_id=customer_id,
            header=header,
            values=values,
            name=name,
        )

    async def create_call_asset(
        ctx: Context,
        customer_id: str,
        country_code: str,
        phone_number: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a call extension asset.

        Args:
            customer_id: The customer ID
            country_code: Two-letter country code (e.g. "US", "GB")
            phone_number: Phone number (e.g. "1234567890", "(123)456-7890")
            name: Optional asset name

        Returns:
            Created call asset details including resource_name
        """
        return await service.create_call_asset(
            ctx=ctx,
            customer_id=customer_id,
            country_code=country_code,
            phone_number=phone_number,
            name=name,
        )

    tools.extend(
        [
            create_text_asset,
            create_image_asset,
            create_youtube_video_asset,
            create_sitelink_asset,
            create_callout_asset,
            create_structured_snippet_asset,
            create_call_asset,
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
