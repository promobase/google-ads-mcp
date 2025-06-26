"""Keyword plan idea server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_idea_service import (
    register_keyword_plan_idea_tools,
)


def register_keyword_plan_idea_server(mcp: FastMCP[Any]) -> None:
    """Register keyword plan idea server tools with the MCP server."""
    register_keyword_plan_idea_tools(mcp)
