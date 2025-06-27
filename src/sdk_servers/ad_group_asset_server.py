"""Ad group asset server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_asset_service import (
    register_ad_group_asset_tools,
)

# Create the ad group asset server
ad_group_asset_sdk_server = FastMCP(name="ad-group-asset-service")

# Register the tools
register_ad_group_asset_tools(ad_group_asset_sdk_server)
