"""Bidding strategy server using SDK implementation."""

from fastmcp import FastMCP

from src.services.bidding.bidding_strategy_service import (
    register_bidding_strategy_tools,
)

# Create the bidding strategy server
bidding_strategy_server = FastMCP(name="bidding-strategy-service")

# Register the tools
register_bidding_strategy_tools(bidding_strategy_server)
