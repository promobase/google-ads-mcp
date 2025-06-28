"""Customer Label server wrapper for MCP registration."""

from fastmcp import FastMCP

from src.services.account.customer_label_service import (
    register_customer_label_tools,
)

# Create FastMCP instance
customer_label_server = FastMCP(
    name="customer-label-server",
    instructions="Server for managing customer labels",
)

# Register tools with the server
register_customer_label_tools(customer_label_server)
