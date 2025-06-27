"""Server wrapper for user data service."""

from fastmcp import FastMCP

from src.sdk_services.data_import.user_data_service import (
    register_user_data_tools,
)

# Create the FastMCP instance
user_data_sdk_server = FastMCP(name="user-data-service")

# Register the tools with the server instance
register_user_data_tools(user_data_sdk_server)
