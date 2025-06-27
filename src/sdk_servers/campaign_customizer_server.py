"""Campaign customizer server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_customizer_service import (
    register_campaign_customizer_tools,
)

# Create the campaign customizer server
campaign_customizer_sdk_server = FastMCP(name="campaign-customizer-service")

# Register the tools
register_campaign_customizer_tools(campaign_customizer_sdk_server)
