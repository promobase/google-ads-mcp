"""Bidding seasonality adjustment server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.bidding.bidding_seasonality_adjustment_service import (
    register_bidding_seasonality_adjustment_tools,
)

# Create the bidding seasonality adjustment server
bidding_seasonality_adjustment_sdk_server = FastMCP(
    name="bidding-seasonality-adjustment-service"
)

# Register the tools
register_bidding_seasonality_adjustment_tools(bidding_seasonality_adjustment_sdk_server)
