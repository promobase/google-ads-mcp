"""Customer customizer server module."""

from fastmcp import FastMCP

from src.services.account.customer_customizer_service import (
    register_customer_customizer_tools,
)

# Create FastMCP instance
customer_customizer_server = FastMCP(
    name="customer-customizer-server",
    instructions="Server for managing customer customizers",
)

# Register tools with the server
register_customer_customizer_tools(customer_customizer_server)
