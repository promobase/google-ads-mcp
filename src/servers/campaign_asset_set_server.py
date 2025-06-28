"""Campaign asset set server module."""

from fastmcp import FastMCP

from src.services.campaign.campaign_asset_set_service import (
    register_campaign_asset_set_tools,
)

# Create the campaign asset set SDK server instance
campaign_asset_set_server = FastMCP()

# Register tools with the server
register_campaign_asset_set_tools(campaign_asset_set_server)
