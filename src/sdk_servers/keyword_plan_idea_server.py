"""Keyword plan idea server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_idea_service import (
    register_keyword_plan_idea_tools,
)

# Create the FastMCP instance for keyword plan idea
keyword_plan_idea_sdk_server = FastMCP[Any](name="keyword_plan_idea_sdk_server")

# Register the tools with the server instance
register_keyword_plan_idea_tools(keyword_plan_idea_sdk_server)
