"""Keyword plan campaign server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_campaign_service import (
    register_keyword_plan_campaign_tools,
)


def register_keyword_plan_campaign_server(mcp: FastMCP[Any]) -> None:
    """Register keyword plan campaign server tools with the MCP server."""
    register_keyword_plan_campaign_tools(mcp)
