"""Ad group customizer server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_group_customizer_service import (
    register_ad_group_customizer_tools,
)

# Create the ad group customizer server
ad_group_customizer_server = FastMCP(name="ad-group-customizer-service")

# Register the tools
register_ad_group_customizer_tools(ad_group_customizer_server)
