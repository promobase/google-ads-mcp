"""Customer asset server module."""

from fastmcp import FastMCP

from src.services.assets.customer_asset_service import register_customer_asset_tools

# Create FastMCP instance
customer_asset_server = FastMCP(
    name="customer-asset-server",
    instructions="Server for managing customer assets",
)

# Register tools with the server
register_customer_asset_tools(customer_asset_server)
