"""Ad server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_service import register_ad_tools

# Create the ad server
ad_server = FastMCP(name="ad-service")

# Register the tools
register_ad_tools(ad_server)
