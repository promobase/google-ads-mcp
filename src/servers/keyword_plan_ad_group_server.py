"""Keyword plan ad group server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.planning.keyword_plan_ad_group_service import (
    register_keyword_plan_ad_group_tools,
)

# Create the FastMCP instance for keyword plan ad group
keyword_plan_ad_group_server = FastMCP[Any](name="keyword_plan_ad_group_sdk_server")

# Register the tools with the server instance
register_keyword_plan_ad_group_tools(keyword_plan_ad_group_server)
