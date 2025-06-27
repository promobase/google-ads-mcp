"""Campaign server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_service import register_campaign_tools

# Create the campaign server
campaign_sdk_server = FastMCP(name="campaign-service")

# Register the tools
register_campaign_tools(campaign_sdk_server)
