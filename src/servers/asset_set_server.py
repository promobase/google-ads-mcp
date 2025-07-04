"""Asset set server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.assets.asset_set_service import register_asset_set_tools

# Initialize the server instance
asset_set_server = FastMCP[Any]()

# Register tools with the server
register_asset_set_tools(asset_set_server)
