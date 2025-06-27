"""Keyword plan campaign keyword server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_campaign_keyword_service import (
    register_keyword_plan_campaign_keyword_tools,
)

# Create the FastMCP instance for keyword plan campaign keyword
keyword_plan_campaign_keyword_sdk_server = FastMCP[Any](
    name="keyword_plan_campaign_keyword_sdk_server"
)

# Register the tools with the server instance
register_keyword_plan_campaign_keyword_tools(keyword_plan_campaign_keyword_sdk_server)
