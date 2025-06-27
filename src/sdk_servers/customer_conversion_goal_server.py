"""MCP server for customer conversion goal service."""

from fastmcp import FastMCP

from src.sdk_services.conversions.customer_conversion_goal_service import (
    register_customer_conversion_goal_tools,
)

# Create the FastMCP instance for customer conversion goal
customer_conversion_goal_sdk_server = FastMCP(
    name="customer_conversion_goal_sdk_server",
    instructions="""Customer conversion goal server for Google Ads API.
    
    This server provides tools for managing customer-level conversion goal biddability,
    which controls whether conversion actions with specific categories and origins
    are eligible for bidding optimization.""",
)

# Register the tools with the server
register_customer_conversion_goal_tools(customer_conversion_goal_sdk_server)
