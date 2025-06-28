"""Keyword plan ad group keyword server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.planning.keyword_plan_ad_group_keyword_service import (
    register_keyword_plan_ad_group_keyword_tools,
)

# Create the FastMCP instance for keyword plan ad group keyword
keyword_plan_ad_group_keyword_server = FastMCP[Any](
    name="keyword_plan_ad_group_keyword_sdk_server"
)

# Register the tools with the server instance
register_keyword_plan_ad_group_keyword_tools(keyword_plan_ad_group_keyword_server)
