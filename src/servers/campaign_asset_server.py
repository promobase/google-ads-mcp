"""Campaign asset server module."""

from fastmcp import FastMCP

from src.services.campaign.campaign_asset_service import (
    register_campaign_asset_tools,
)

# Create the campaign asset SDK server instance
campaign_asset_server = FastMCP()

# Register tools with the server
register_campaign_asset_tools(campaign_asset_server)
