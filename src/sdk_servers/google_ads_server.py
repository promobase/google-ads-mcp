"""Google Ads server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.metadata.google_ads_service import register_google_ads_tools


def register_google_ads_server(mcp: FastMCP[Any]) -> None:
    """Register Google Ads server with the MCP server."""
    register_google_ads_tools(mcp)
