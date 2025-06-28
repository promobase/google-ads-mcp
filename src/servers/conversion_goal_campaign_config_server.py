"""Conversion goal campaign config server module."""

from fastmcp import FastMCP

from src.services.conversions.conversion_goal_campaign_config_service import (
    register_conversion_goal_campaign_config_tools,
)

# Create the FastMCP instance for conversion goal campaign config
conversion_goal_campaign_config_server = FastMCP(
    name="conversion_goal_campaign_config_sdk_server",
    instructions="Conversion goal campaign config server for Google Ads API",
)

# Register the tools with the server
register_conversion_goal_campaign_config_tools(conversion_goal_campaign_config_server)
