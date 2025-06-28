"""Ad group ad server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_group_ad_service import register_ad_group_ad_tools

# Create the ad group ad server
ad_group_ad_server = FastMCP(name="ad-group-ad-service")

# Register the tools
register_ad_group_ad_tools(ad_group_ad_server)
