"""Server wrapper for customer user access invitation service."""

from fastmcp import FastMCP

from src.sdk_services.account.customer_user_access_invitation_service import (
    register_customer_user_access_invitation_tools,
)

# Create FastMCP instance
customer_user_access_invitation_sdk_server = FastMCP(
    name="customer-user-access-invitation-server",
    instructions="Server for managing customer user access invitations",
)

# Register tools with the server
register_customer_user_access_invitation_tools(
    customer_user_access_invitation_sdk_server
)
