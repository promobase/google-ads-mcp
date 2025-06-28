"""Conversion server using SDK implementation."""

from fastmcp import FastMCP

from src.services.conversions.conversion_service import register_conversion_tools

# Create the conversion server
conversion_server = FastMCP(name="conversion-service")

# Register the tools
register_conversion_tools(conversion_server)
