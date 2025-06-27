"""Bidding data exclusion server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.bidding.bidding_data_exclusion_service import (
    register_bidding_data_exclusion_tools,
)

# Create the bidding data exclusion server
bidding_data_exclusion_sdk_server = FastMCP(name="bidding-data-exclusion-service")

# Register the tools
register_bidding_data_exclusion_tools(bidding_data_exclusion_sdk_server)
