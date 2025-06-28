"""Campaign label server module."""

from fastmcp import FastMCP

from src.services.campaign.campaign_label_service import (
    register_campaign_label_tools,
)

# Create the campaign label SDK server instance
campaign_label_server = FastMCP()

# Register tools with the server
register_campaign_label_tools(campaign_label_server)
