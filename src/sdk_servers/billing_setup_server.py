"""Billing setup server module."""

from fastmcp import FastMCP

from src.sdk_services.account.billing_setup_service import register_billing_setup_tools

# Create the FastMCP instance
billing_setup_sdk_server = FastMCP(name="billing-setup-service")

# Register the tools with the server instance
register_billing_setup_tools(billing_setup_sdk_server)
