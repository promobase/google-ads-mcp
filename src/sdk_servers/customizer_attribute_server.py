"""Server wrapper for customizer attribute service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.shared.customizer_attribute_service import (
    register_customizer_attribute_tools,
    CustomizerAttributeService,
)


def register_customizer_attribute_server(
    mcp: FastMCP[Any],
) -> CustomizerAttributeService:
    """Register customizer attribute tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The CustomizerAttributeService instance for testing purposes
    """
    return register_customizer_attribute_tools(mcp)
