"""Ad group ad label server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_group_ad_label_service import (
    register_ad_group_ad_label_tools,
)

# Create the ad group ad label server
ad_group_ad_label_server = FastMCP(name="ad-group-ad-label-service")

# Register the tools
register_ad_group_ad_label_tools(ad_group_ad_label_server)
