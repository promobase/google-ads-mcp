"""Remarketing action server using SDK implementation."""

from fastmcp import FastMCP

from src.services.audiences.remarketing_action_service import (
    register_remarketing_action_tools,
)

# Create the remarketing action server
remarketing_action_server = FastMCP(
    name="remarketing_action",
    instructions="""This server provides tools for managing remarketing tags and actions.

    Available tools:
    - create_remarketing_action: Create a new remarketing tag
    - update_remarketing_action: Update remarketing action name
    - list_remarketing_actions: List all remarketing actions
    - get_remarketing_action_tags: Get JavaScript tag snippets

    Remarketing actions allow you to:
    - Track website visitors for remarketing campaigns
    - Build audience lists based on site behavior
    - Create custom combinations of audiences

    Tag implementation:
    - Global Site Tag: Add to every page of your website
    - Event Snippet: Add to specific conversion pages
    - Both snippets work together to track users

    The tags enable:
    - Dynamic remarketing with product data
    - Conversion tracking
    - Audience list building
    - Cross-device tracking

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
remarketing_action_service = register_remarketing_action_tools(
    remarketing_action_server
)
