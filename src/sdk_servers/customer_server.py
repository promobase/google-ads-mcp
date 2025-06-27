"""Customer server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.customer_service import register_customer_tools

# Create the customer server
customer_sdk_server = FastMCP(name="customer-service")

# Register the tools
register_customer_tools(customer_sdk_server)
