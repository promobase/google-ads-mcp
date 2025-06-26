"""Server wrapper for bidding data exclusion service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.bidding.bidding_data_exclusion_service import (
    register_bidding_data_exclusion_tools,
    BiddingDataExclusionService,
)


def register_bidding_data_exclusion_server(
    mcp: FastMCP[Any],
) -> BiddingDataExclusionService:
    """Register bidding data exclusion tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The BiddingDataExclusionService instance for testing purposes
    """
    return register_bidding_data_exclusion_tools(mcp)
