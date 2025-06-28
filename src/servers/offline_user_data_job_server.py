"""Server wrapper for offline user data job service."""

from fastmcp import FastMCP

from src.services.data_import.offline_user_data_job_service import (
    register_offline_user_data_job_tools,
)

# Create the FastMCP instance
offline_user_data_job_server = FastMCP(name="offline-user-data-job-service")

# Register the tools with the server instance
register_offline_user_data_job_tools(offline_user_data_job_server)
