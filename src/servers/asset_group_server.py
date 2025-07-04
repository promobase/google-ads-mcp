"""Asset group server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.assets.asset_group_service import register_asset_group_tools

# Initialize the server instance
asset_group_server = FastMCP[Any]()

# Register tools with the server
register_asset_group_tools(asset_group_server)
