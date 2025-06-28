"""Brand suggestion server module."""

from fastmcp import FastMCP

from src.services.planning.brand_suggestion_service import (
    register_brand_suggestion_tools,
)

# Create the FastMCP instance for brand suggestion
brand_suggestion_server = FastMCP(
    name="brand_suggestion_sdk_server",
    instructions="Brand suggestion server for Google Ads API",
)

# Register the tools with the server
register_brand_suggestion_tools(brand_suggestion_server)
