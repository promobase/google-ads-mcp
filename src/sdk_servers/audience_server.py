"""Audience server module."""

from fastmcp import FastMCP

from src.sdk_services.audiences.audience_service import register_audience_tools


# Create the audience SDK server instance
audience_sdk_server = FastMCP()

# Register tools with the server
register_audience_tools(audience_sdk_server)
