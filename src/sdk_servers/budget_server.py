"""Budget server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.bidding.budget_service import register_budget_tools

# Create the budget server
budget_sdk_server = FastMCP(
    name="budget",
    instructions="""This server provides tools for managing Google Ads campaign budgets.

    Available tools:
    - create_campaign_budget: Create a new campaign budget with amount and delivery settings
    - update_campaign_budget: Update budget name, amount, or delivery method

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
budget_service = register_budget_tools(budget_sdk_server)
