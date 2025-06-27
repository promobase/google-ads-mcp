"""Campaign bid modifier server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_bid_modifier_service import (
    register_campaign_bid_modifier_tools,
)

# Create the FastMCP server instance
campaign_bid_modifier_sdk_server = FastMCP[Any](name="campaign_bid_modifier_sdk_server")

# Register the tools with the server instance
register_campaign_bid_modifier_tools(campaign_bid_modifier_sdk_server)
