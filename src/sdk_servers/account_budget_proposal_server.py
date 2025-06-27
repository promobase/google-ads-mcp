"""Account budget proposal server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.account.account_budget_proposal_service import (
    register_account_budget_proposal_tools,
)

# Create the account budget proposal server
account_budget_proposal_sdk_server = FastMCP(name="account-budget-proposal-service")

# Register the tools
register_account_budget_proposal_tools(account_budget_proposal_sdk_server)
