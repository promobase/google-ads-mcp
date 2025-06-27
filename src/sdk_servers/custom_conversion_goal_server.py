"""Custom conversion goal server module."""

from fastmcp import FastMCP

from src.sdk_services.conversions.custom_conversion_goal_service import (
    register_custom_conversion_goal_tools,
)

# Create the FastMCP instance for custom conversion goal
custom_conversion_goal_sdk_server = FastMCP(
    name="custom_conversion_goal_sdk_server",
    instructions="Custom conversion goal server for Google Ads API",
)

# Register the tools with the server
register_custom_conversion_goal_tools(custom_conversion_goal_sdk_server)
