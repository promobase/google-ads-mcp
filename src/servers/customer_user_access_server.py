"""Server wrapper for customer user access service."""

from fastmcp import FastMCP

from src.services.account.customer_user_access_service import (
    register_customer_user_access_tools,
)

# Create FastMCP instance
customer_user_access_server = FastMCP(
    name="customer-user-access-server",
    instructions="Server for managing customer user access",
)

# Register tools with the server
register_customer_user_access_tools(customer_user_access_server)
