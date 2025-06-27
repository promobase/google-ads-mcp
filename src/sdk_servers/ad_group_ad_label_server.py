"""Server wrapper for ad group ad label service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_ad_label_service import (
    register_ad_group_ad_label_tools,
    AdGroupAdLabelService,
)


def register_ad_group_ad_label_server(
    mcp: FastMCP[Any],
) -> AdGroupAdLabelService:
    """Register ad group ad label tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The AdGroupAdLabelService instance for testing purposes
    """
    return register_ad_group_ad_label_tools(mcp)
