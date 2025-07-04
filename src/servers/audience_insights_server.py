"""Audience insights server using SDK implementation."""

from fastmcp import FastMCP

from src.services.audiences.audience_insights_service import (
    register_audience_insights_tools,
)

# Create the audience insights server
audience_insights_server = FastMCP(name="audience-insights-service")

# Register the tools
register_audience_insights_tools(audience_insights_server)
