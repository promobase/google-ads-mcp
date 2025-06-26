"""Audience server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.audiences.audience_service import register_audience_tools


def register_audience_server(mcp: FastMCP[Any]) -> None:
    """Register audience server tools with the MCP server."""
    register_audience_tools(mcp)
