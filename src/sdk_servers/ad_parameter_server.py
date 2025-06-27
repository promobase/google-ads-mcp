"""MCP server for ad parameter service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_parameter_service import (
    register_ad_parameter_tools,
)


def register_ad_parameter_server(
    mcp: FastMCP[Any],
) -> None:
    """Register ad parameter server with MCP.
    
    This server provides tools for managing ad parameters,
    which allow dynamic numeric values in ads (like prices or inventory levels).
    
    Args:
        mcp: The FastMCP server instance
    """
    return register_ad_parameter_tools(mcp)