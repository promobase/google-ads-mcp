"""Budget server using SDK implementation."""

from fastmcp import FastMCP

from src.services.bidding.budget_service import register_budget_tools

# Create the budget server
budget_server = FastMCP(name="budget-service")

# Register the tools
register_budget_tools(budget_server)
