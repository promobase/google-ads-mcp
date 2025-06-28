"""Campaign shared set server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.campaign.campaign_shared_set_service import (
    register_campaign_shared_set_tools,
)

# Create the FastMCP server instance
campaign_shared_set_server = FastMCP[Any](name="campaign_shared_set_sdk_server")

# Register the tools with the server instance
register_campaign_shared_set_tools(campaign_shared_set_server)
