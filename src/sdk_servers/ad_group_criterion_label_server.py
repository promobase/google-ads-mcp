"""Ad group criterion label server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_criterion_label_service import (
    register_ad_group_criterion_label_tools,
)


def register_ad_group_criterion_label_server(mcp: FastMCP[Any]) -> None:
    """Register ad group criterion label server tools with the MCP server."""
    register_ad_group_criterion_label_tools(mcp)