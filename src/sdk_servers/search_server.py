"""Search server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.metadata.search_service import register_search_tools

# Create the search server
search_sdk_server = FastMCP(
    name="search",
    instructions="""This server provides tools for searching and querying Google Ads data.

    Available tools:
    - search_campaigns: Search for campaigns with filtering options
    - search_ad_groups: Search for ad groups with campaign filtering
    - search_keywords: Search for keywords with ad group filtering
    - execute_query: Execute custom GAQL (Google Ads Query Language) queries

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
search_service = register_search_tools(search_sdk_server)
