"""Audience server module."""

from fastmcp import FastMCP

from src.services.audiences.audience_service import register_audience_tools

# Create the audience SDK server instance
audience_server = FastMCP()

# Register tools with the server
register_audience_tools(audience_server)
