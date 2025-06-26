"""Customer server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.customer_service import register_customer_tools

# Create the customer server
customer_sdk_server = FastMCP(
    name="customer",
    instructions="""This server provides tools for managing Google Ads customers and account relationships.

    Available tools:
    - create_customer_client: Create a new client customer under a manager
    - list_accessible_customers: List all accessible customers for the authenticated user

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
customer_service = register_customer_tools(customer_sdk_server)
