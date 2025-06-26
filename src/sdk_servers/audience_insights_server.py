"""Server wrapper for audience insights service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.audiences.audience_insights_service import (
    register_audience_insights_tools,
    AudienceInsightsService,
)


def register_audience_insights_server(
    mcp: FastMCP[Any],
) -> AudienceInsightsService:
    """Register audience insights tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The AudienceInsightsService instance for testing purposes
    """
    return register_audience_insights_tools(mcp)
