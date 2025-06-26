"""Bidding strategy server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.bidding.bidding_strategy_service import (
    register_bidding_strategy_tools,
)

# Create the bidding strategy server
bidding_strategy_sdk_server = FastMCP(
    name="bidding_strategy",
    instructions="""This server provides tools for managing Google Ads automated bidding strategies.

    Available tools:
    - create_target_cpa_strategy: Create a Target CPA bidding strategy
    - create_target_roas_strategy: Create a Target ROAS (Return on Ad Spend) strategy
    - create_maximize_conversions_strategy: Create a Maximize Conversions strategy
    - create_target_impression_share_strategy: Create a Target Impression Share strategy

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
bidding_strategy_service = register_bidding_strategy_tools(bidding_strategy_sdk_server)
