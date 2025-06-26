"""Campaign server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_service import register_campaign_tools

# Create the campaign server
campaign_sdk_server = FastMCP(
    name="campaign",
    instructions="""This server provides tools for managing Google Ads campaigns.

    Available tools:
    - create_campaign: Create a new campaign with budget and settings
    - update_campaign: Update campaign name, status, or dates

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
campaign_service = register_campaign_tools(campaign_sdk_server)
