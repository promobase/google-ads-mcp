"""Account link server using SDK implementation."""

from fastmcp import FastMCP

from src.services.account.account_link_service import (
    register_account_link_tools,
)

# Create the account link server
account_link_server = FastMCP(name="account-link-service")

# Register the tools
register_account_link_tools(account_link_server)
