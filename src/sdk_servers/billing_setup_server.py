"""Billing setup server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.billing_setup_service import register_billing_setup_tools


def register_billing_setup_server(mcp: FastMCP[Any]) -> None:
    """Register billing setup server tools with the MCP server."""
    register_billing_setup_tools(mcp)
