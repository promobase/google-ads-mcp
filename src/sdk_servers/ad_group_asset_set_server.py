"""Server wrapper for ad group asset set service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_asset_set_service import (
    register_ad_group_asset_set_tools,
    AdGroupAssetSetService,
)


def register_ad_group_asset_set_server(
    mcp: FastMCP[Any],
) -> AdGroupAssetSetService:
    """Register ad group asset set tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The AdGroupAssetSetService instance for testing purposes
    """
    return register_ad_group_asset_set_tools(mcp)
