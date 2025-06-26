"""Shared criterion server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.shared.shared_criterion_service import (
    register_shared_criterion_tools,
)

# Create the shared criterion server
shared_criterion_sdk_server = FastMCP(
    name="shared_criterion",
    instructions="""This server provides tools for managing items within shared sets.

    Available tools:
    - add_keywords_to_shared_set: Add negative keywords to a shared set
    - add_placements_to_shared_set: Add placement exclusions to a shared set
    - list_shared_criteria: List all criteria in a shared set
    - remove_shared_criterion: Remove a criterion from a shared set

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
shared_criterion_service = register_shared_criterion_tools(shared_criterion_sdk_server)
