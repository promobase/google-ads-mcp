"""Asset Group Asset server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.services.assets.asset_group_asset_service import (
    register_asset_group_asset_tools,
)

# Initialize the server instance
asset_group_asset_server = FastMCP[Any]()

# Register tools with the server
register_asset_group_asset_tools(asset_group_asset_server)
