"""Data link server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.data_import.data_link_service import (
    register_data_link_tools,
)

# Create the data link server
data_link_sdk_server = FastMCP(name="data-link-service")

# Register the tools
register_data_link_tools(data_link_sdk_server)
