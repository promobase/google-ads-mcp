"""Ad server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_service import register_ad_tools

# Create the ad server
ad_sdk_server = FastMCP(
    name="ad",
    instructions="""This server provides tools for managing Google Ads ads.

    Available tools:
    - create_responsive_search_ad: Create a responsive search ad with multiple headlines and descriptions
    - create_expanded_text_ad: Create an expanded text ad with fixed headlines and descriptions
    - update_ad_status: Update the status of an ad (enable, pause, or remove)

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
ad_service = register_ad_tools(ad_sdk_server)
