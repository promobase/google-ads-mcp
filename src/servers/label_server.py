"""Label server using SDK implementation."""

from fastmcp import FastMCP

from src.services.shared.label_service import register_label_tools

# Create the label server
label_server = FastMCP(
    name="label",
    instructions="""This server provides tools for managing labels to organize campaigns, ad groups, and ads.

    Available tools:
    - create_label: Create a new label with optional color coding
    - update_label: Update label properties
    - list_labels: List all labels in the account
    - apply_label_to_campaigns: Apply a label to multiple campaigns
    - apply_label_to_ad_groups: Apply a label to multiple ad groups

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
label_service = register_label_tools(label_server)
