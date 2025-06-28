"""Ad group server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_group_service import register_ad_group_tools

# Create the ad group server
ad_group_server = FastMCP(name="ad-group-service")

# Register the tools
register_ad_group_tools(ad_group_server)
