"""Asset server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.assets.asset_service import register_asset_tools

# Create the asset server
asset_sdk_server = FastMCP(name="asset-service")

# Register the tools
register_asset_tools(asset_sdk_server)
