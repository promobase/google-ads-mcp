"""Server wrapper for campaign draft service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_draft_service import (
    register_campaign_draft_tools,
    CampaignDraftService,
)


def register_campaign_draft_server(
    mcp: FastMCP[Any],
) -> CampaignDraftService:
    """Register campaign draft tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The CampaignDraftService instance for testing purposes
    """
    return register_campaign_draft_tools(mcp)
