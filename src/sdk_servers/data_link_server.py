"""Server wrapper for data link service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.data_import.data_link_service import (
    register_data_link_tools,
    DataLinkService,
)


def register_data_link_server(
    mcp: FastMCP[Any],
) -> DataLinkService:
    """Register data link tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The DataLinkService instance for testing purposes
    """
    return register_data_link_tools(mcp)
