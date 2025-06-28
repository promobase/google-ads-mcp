"""Customer negative criterion server using SDK implementation."""

from fastmcp import FastMCP

from src.services.targeting.customer_negative_criterion_service import (
    register_customer_negative_criterion_tools,
)

# Create the customer negative criterion server
customer_negative_criterion_server = FastMCP(
    name="customer_negative_criterion",
    instructions="""This server provides tools for managing account-level negative criteria (exclusions).

    Available tools:
    - add_negative_keywords: Add negative keywords at the account level
    - add_placement_exclusions: Exclude specific websites from all campaigns
    - add_content_label_exclusions: Exclude content categories (e.g., sensitive content)
    - list_negative_criteria: List all account-level exclusions
    - remove_negative_criterion: Remove an account-level exclusion

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
customer_negative_criterion_service = register_customer_negative_criterion_tools(
    customer_negative_criterion_server
)
