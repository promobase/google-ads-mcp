"""Ad parameter server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.ad_parameter_service import (
    register_ad_parameter_tools,
)

# Create the ad parameter server
ad_parameter_server = FastMCP(name="ad-parameter-service")

# Register the tools
register_ad_parameter_tools(ad_parameter_server)
