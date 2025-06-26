"""Conversion server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_service import register_conversion_tools

# Create the conversion server
conversion_sdk_server = FastMCP(
    name="conversion",
    instructions="""This server provides tools for managing Google Ads conversion tracking.

    Available tools:
    - create_conversion_action: Create a new conversion action with tracking settings
    - update_conversion_action: Update conversion action settings and values

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
conversion_service = register_conversion_tools(conversion_sdk_server)
