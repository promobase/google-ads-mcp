"""MCP server for ad group criterion customizer service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_criterion_customizer_service import (
    register_ad_group_criterion_customizer_tools,
)


def register_ad_group_criterion_customizer_server(
    mcp: FastMCP[Any],
) -> None:
    """Register ad group criterion customizer server with MCP.

    This server provides tools for managing ad group criterion customizers,
    which allow dynamic customization of ads at the keyword/criterion level.

    Args:
        mcp: The FastMCP server instance
    """
    register_ad_group_criterion_customizer_tools(mcp)
