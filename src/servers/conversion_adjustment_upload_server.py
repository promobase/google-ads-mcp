"""Conversion adjustment upload server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.conversions.conversion_adjustment_upload_service import (
    register_conversion_adjustment_upload_tools,
)

# Create the FastMCP server instance
conversion_adjustment_upload_server = FastMCP[Any](
    name="conversion_adjustment_upload_sdk_server"
)

# Register the tools with the server instance
register_conversion_adjustment_upload_tools(conversion_adjustment_upload_server)
