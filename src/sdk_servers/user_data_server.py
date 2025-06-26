"""Server wrapper for user data service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.data_import.user_data_service import (
    register_user_data_tools,
    UserDataService,
)


def register_user_data_server(mcp: FastMCP[Any]) -> UserDataService:
    """Register user data tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The UserDataService instance for testing purposes
    """
    return register_user_data_tools(mcp)
