"""Keyword server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.keyword_service import register_keyword_tools

# Create the keyword server
keyword_sdk_server = FastMCP(
    name="keyword",
    instructions="""This server provides tools for managing Google Ads keywords.

    Available tools:
    - add_keywords: Add keywords to an ad group with match types and bids
    - update_keyword_bid: Update the CPC bid for a keyword
    - remove_keyword: Remove a keyword from an ad group

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
keyword_service = register_keyword_tools(keyword_sdk_server)
