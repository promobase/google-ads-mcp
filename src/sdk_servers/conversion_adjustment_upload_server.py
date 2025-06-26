"""Conversion adjustment upload server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_adjustment_upload_service import (
    register_conversion_adjustment_upload_tools,
)


def register_conversion_adjustment_upload_server(mcp: FastMCP[Any]) -> None:
    """Register conversion adjustment upload server tools with the MCP server."""
    register_conversion_adjustment_upload_tools(mcp)
