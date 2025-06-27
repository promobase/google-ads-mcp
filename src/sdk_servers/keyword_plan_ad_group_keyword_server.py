"""Keyword plan ad group keyword server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_ad_group_keyword_service import (
    register_keyword_plan_ad_group_keyword_tools,
)


def register_keyword_plan_ad_group_keyword_server(mcp: FastMCP[Any]) -> None:
    """Register keyword plan ad group keyword server tools with the MCP server."""
    register_keyword_plan_ad_group_keyword_tools(mcp)
