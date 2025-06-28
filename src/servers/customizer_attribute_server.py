"""Server wrapper for customizer attribute service."""

from fastmcp import FastMCP

from src.services.shared.customizer_attribute_service import (
    register_customizer_attribute_tools,
)

# Create the FastMCP instance
customizer_sdk_server = FastMCP(name="customizer-attribute-service")

# Register the tools with the server instance
register_customizer_attribute_tools(customizer_sdk_server)
