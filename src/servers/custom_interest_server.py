"""Custom interest server using SDK implementation."""

from fastmcp import FastMCP

from src.services.audiences.custom_interest_service import (
    register_custom_interest_tools,
)

# Create the custom interest server
custom_interest_server = FastMCP(
    name="custom_interest",
    instructions="""This server provides tools for managing custom interests (custom affinity and intent audiences).

    Available tools:
    - create_custom_interest: Create a new custom affinity or intent audience
    - update_custom_interest: Update custom interest properties or members
    - list_custom_interests: List all custom interests in the account
    - get_custom_interest_details: Get detailed information including all members

    Custom interests allow you to create audiences based on:
    - Keywords: Terms that describe user interests
    - URLs: Websites that your audience visits

    Types:
    - CUSTOM_AFFINITY: Reach users based on their passions and habits
    - CUSTOM_INTENT: Reach users actively researching products/services

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
custom_interest_service = register_custom_interest_tools(custom_interest_server)
