"""Ad group bid modifier server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.ad_group.ad_group_bid_modifier_service import (
    register_ad_group_bid_modifier_tools,
)

# Create the FastMCP server instance
ad_group_bid_modifier_server = FastMCP[Any](name="ad_group_bid_modifier_sdk_server")

# Register the tools with the server instance
register_ad_group_bid_modifier_tools(ad_group_bid_modifier_server)
