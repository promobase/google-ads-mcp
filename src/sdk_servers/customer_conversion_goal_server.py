"""MCP server for customer conversion goal service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.customer_conversion_goal_service import (
    register_customer_conversion_goal_tools,
)


def register_customer_conversion_goal_server(
    mcp: FastMCP[Any],
) -> None:
    """Register customer conversion goal server with MCP.

    This server provides tools for managing customer-level conversion goal biddability,
    which controls whether conversion actions with specific categories and origins
    are eligible for bidding optimization.

    Args:
        mcp: The FastMCP server instance
    """
    register_customer_conversion_goal_tools(mcp)
