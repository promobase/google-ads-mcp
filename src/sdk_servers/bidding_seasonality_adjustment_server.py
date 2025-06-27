"""Server wrapper for bidding seasonality adjustment service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.bidding.bidding_seasonality_adjustment_service import (
    register_bidding_seasonality_adjustment_tools,
    BiddingSeasonalityAdjustmentService,
)


def register_bidding_seasonality_adjustment_server(
    mcp: FastMCP[Any],
) -> BiddingSeasonalityAdjustmentService:
    """Register bidding seasonality adjustment tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The BiddingSeasonalityAdjustmentService instance for testing purposes
    """
    return register_bidding_seasonality_adjustment_tools(mcp)
