"""Server wrapper for account budget proposal service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.account_budget_proposal_service import (
    register_account_budget_proposal_tools,
    AccountBudgetProposalService,
)


def register_account_budget_proposal_server(
    mcp: FastMCP[Any],
) -> AccountBudgetProposalService:
    """Register account budget proposal tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The AccountBudgetProposalService instance for testing purposes
    """
    return register_account_budget_proposal_tools(mcp)
