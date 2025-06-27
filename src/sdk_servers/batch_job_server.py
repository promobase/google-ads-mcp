"""Server wrapper for batch job service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.data_import.batch_job_service import (
    register_batch_job_tools,
    BatchJobService,
)


def register_batch_job_server(
    mcp: FastMCP[Any],
) -> BatchJobService:
    """Register batch job tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The BatchJobService instance for testing purposes
    """
    return register_batch_job_tools(mcp)
