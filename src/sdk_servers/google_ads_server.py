"""Google Ads server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.metadata.google_ads_service import register_google_ads_tools

# Create the Google Ads server
google_ads_sdk_server = FastMCP(name="google-ads-service")

# Register the tools
register_google_ads_tools(google_ads_sdk_server)
