"""Asset server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.assets.asset_service import register_asset_tools

# Create the asset server
asset_sdk_server = FastMCP(
    name="asset",
    instructions="""This server provides tools for managing Google Ads assets (images, videos, text).

    Available tools:
    - create_text_asset: Create a text asset for use in ads
    - create_image_asset: Create an image asset from binary data
    - create_youtube_video_asset: Create a YouTube video asset from video ID
    - search_assets: Search and list assets in the account

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
asset_service = register_asset_tools(asset_sdk_server)
