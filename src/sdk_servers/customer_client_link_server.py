"""Server wrapper for customer client link service."""

from fastmcp import FastMCP

from src.sdk_services.account.customer_client_link_service import (
    register_customer_client_link_tools,
)

# Create FastMCP instance
customer_client_link_sdk_server = FastMCP(
    name="customer-client-link-server",
    instructions="Server for managing customer client links",
)

# Register tools with the server
register_customer_client_link_tools(customer_client_link_sdk_server)
