"""Ad group server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_service import register_ad_group_tools

# Create the ad group server
ad_group_sdk_server = FastMCP(
    name="ad_group",
    instructions="""This server provides tools for managing Google Ads ad groups.

    Available tools:
    - create_ad_group: Create a new ad group in a campaign
    - update_ad_group: Update ad group name, status, or bids

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
ad_group_service = register_ad_group_tools(ad_group_sdk_server)
