"""Conversion custom variable server using SDK implementation."""

from fastmcp import FastMCP

from src.services.conversions.conversion_custom_variable_service import (
    register_conversion_custom_variable_tools,
)

# Create the conversion custom variable server
conversion_custom_variable_server = FastMCP(name="conversion-custom-variable-service")

# Register the tools
register_conversion_custom_variable_tools(conversion_custom_variable_server)
