"""Custom audience server using SDK implementation."""

from fastmcp import FastMCP

from src.services.audiences.custom_audience_service import (
    register_custom_audience_tools,
)

# Create the custom audience server
custom_audience_server = FastMCP(
    name="custom_audience",
    instructions="""This server provides tools for managing custom audiences (custom segments).

    Available tools:
    - create_custom_audience: Create a new custom segment
    - update_custom_audience: Update custom audience properties or members
    - list_custom_audiences: List all custom audiences in the account
    - get_custom_audience_details: Get detailed information including all members

    Custom audiences allow you to create segments based on:
    - Keywords: Terms that describe your target audience
    - URLs: Websites that your audience visits
    - Apps: Mobile apps that your audience uses
    - Place categories: Types of places your audience visits

    Types:
    - CUSTOM: Standard custom segment
    - INTEREST: Interest-based segment
    - PURCHASE_INTENT: Purchase intent segment
    - SEARCH: Search-based segment

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
custom_audience_service = register_custom_audience_tools(custom_audience_server)
