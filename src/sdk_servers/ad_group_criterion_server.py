"""Ad group criterion server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_criterion_service import (
    register_ad_group_criterion_tools,
)

# Create the ad group criterion server
ad_group_criterion_sdk_server = FastMCP(
    name="ad_group_criterion",
    instructions="""This server provides tools for managing ad group-level targeting criteria.

    Available tools:
    - add_keywords: Add keyword criteria (positive or negative) to ad groups
    - add_audience_criteria: Add audience/remarketing list targeting
    - add_demographic_criteria: Add demographic targeting (age, gender, etc.)
    - update_criterion_bid: Update CPC bids or bid modifiers
    - remove_ad_group_criterion: Remove any ad group criterion

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
ad_group_criterion_service = register_ad_group_criterion_tools(
    ad_group_criterion_sdk_server
)
