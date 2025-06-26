"""Campaign criterion server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_criterion_service import (
    register_campaign_criterion_tools,
)

# Create the campaign criterion server
campaign_criterion_sdk_server = FastMCP(
    name="campaign_criterion",
    instructions="""This server provides tools for managing campaign-level targeting criteria.

    Available tools:
    - add_location_criteria: Add location targeting to campaigns
    - add_language_criteria: Add language targeting to campaigns
    - add_device_criteria: Add device targeting with bid adjustments
    - add_negative_keyword_criteria: Add negative keywords at campaign level
    - remove_campaign_criterion: Remove any campaign criterion

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
campaign_criterion_service = register_campaign_criterion_tools(
    campaign_criterion_sdk_server
)
