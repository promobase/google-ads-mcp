"""Server wrapper for offline user data job service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.data_import.offline_user_data_job_service import (
    register_offline_user_data_job_tools,
    OfflineUserDataJobService,
)


def register_offline_user_data_job_server(
    mcp: FastMCP[Any],
) -> OfflineUserDataJobService:
    """Register offline user data job tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The OfflineUserDataJobService instance for testing purposes
    """
    return register_offline_user_data_job_tools(mcp)
