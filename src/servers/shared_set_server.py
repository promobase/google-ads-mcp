"""Shared set server using SDK implementation."""

from fastmcp import FastMCP

from src.services.shared.shared_set_service import register_shared_set_tools

# Create the shared set server
shared_set_server = FastMCP(
    name="shared_set",
    instructions="""This server provides tools for managing shared negative keyword and placement lists.

    Available tools:
    - create_shared_set: Create a new shared set for negative keywords or placements
    - update_shared_set: Update shared set name or status
    - list_shared_sets: List all shared sets in the account
    - attach_shared_set_to_campaigns: Attach a shared set to campaigns

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
shared_set_service = register_shared_set_tools(shared_set_server)
