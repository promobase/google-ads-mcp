"""Ad group asset set server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_group_asset_set_service import (
    register_ad_group_asset_set_tools,
)

# Create the ad group asset set server
ad_group_asset_set_server = FastMCP(name="ad-group-asset-set-service")

# Register the tools
register_ad_group_asset_set_tools(ad_group_asset_set_server)
