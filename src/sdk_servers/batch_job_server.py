"""Batch job server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.data_import.batch_job_service import (
    register_batch_job_tools,
)

# Create the batch job server
batch_job_sdk_server = FastMCP(name="batch-job-service")

# Register the tools
register_batch_job_tools(batch_job_sdk_server)
