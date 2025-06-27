"""Payments account server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.payments_account_service import (
    register_payments_account_tools,
)

# Create the payments account server
payments_account_sdk_server = FastMCP(name="payments-account-service")

# Register the tools
register_payments_account_tools(payments_account_sdk_server)
