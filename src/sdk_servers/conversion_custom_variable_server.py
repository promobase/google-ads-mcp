"""Conversion Custom Variable server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_custom_variable_service import (
    register_conversion_custom_variable_tools,
)


def register_conversion_custom_variable_server(mcp: FastMCP[Any]) -> None:
    """Register Conversion Custom Variable server with the MCP server."""
    register_conversion_custom_variable_tools(mcp)
