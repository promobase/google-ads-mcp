"""Server wrapper for conversion value rule service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_value_rule_service import (
    register_conversion_value_rule_tools,
    ConversionValueRuleService,
)


def register_conversion_value_rule_server(
    mcp: FastMCP[Any],
) -> ConversionValueRuleService:
    """Register conversion value rule tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The ConversionValueRuleService instance for testing purposes
    """
    return register_conversion_value_rule_tools(mcp)
