"""Customer server using SDK implementation."""

from fastmcp import FastMCP

from src.services.account.customer_service import register_customer_tools

# Create the customer server
customer_service_server = FastMCP(name="customer-service")

# Register the tools
register_customer_tools(customer_service_server)
