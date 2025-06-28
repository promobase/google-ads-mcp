"""Campaign draft server using SDK implementation."""

from fastmcp import FastMCP

from src.services.campaign.campaign_draft_service import (
    register_campaign_draft_tools,
)

# Create the campaign draft server
campaign_draft_server = FastMCP(name="campaign-draft-service")

# Register the tools
register_campaign_draft_tools(campaign_draft_server)
