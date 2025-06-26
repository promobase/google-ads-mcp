"""Server wrapper for invoice service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.invoice_service import (
    register_invoice_tools,
    InvoiceService,
)


def register_invoice_server(
    mcp: FastMCP[Any],
) -> InvoiceService:
    """Register invoice tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The InvoiceService instance for testing purposes
    """
    return register_invoice_tools(mcp)
