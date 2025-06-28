"""Customer Manager Link server wrapper for MCP registration."""

from fastmcp import FastMCP

from src.services.account.customer_manager_link_service import (
    register_customer_manager_link_tools,
)

# Create FastMCP instance
customer_manager_link_server = FastMCP(
    name="customer-manager-link-server",
    instructions="Server for managing customer manager links",
)

# Register tools with the server
register_customer_manager_link_tools(customer_manager_link_server)
