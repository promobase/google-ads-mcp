"""Campaign conversion goal server using SDK implementation."""

from fastmcp import FastMCP

from src.services.campaign.campaign_conversion_goal_service import (
    register_campaign_conversion_goal_tools,
)

# Create the campaign conversion goal server
campaign_conversion_goal_server = FastMCP(name="campaign-conversion-goal-service")

# Register the tools
register_campaign_conversion_goal_tools(campaign_conversion_goal_server)
