"""Product link server module."""

from fastmcp import FastMCP

from src.services.product_integration.product_link_service import (
    register_product_link_tools,
)

# Create the FastMCP instance for product link
product_link_server = FastMCP(
    name="product_link_sdk_server",
    instructions="Product link server for Google Ads API",
)

# Register the tools with the server
register_product_link_tools(product_link_server)
