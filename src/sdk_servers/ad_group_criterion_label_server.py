"""Ad group criterion label server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_criterion_label_service import (
    register_ad_group_criterion_label_tools,
)

# Create the ad group criterion label server
ad_group_criterion_label_sdk_server = FastMCP(name="ad-group-criterion-label-service")

# Register the tools
register_ad_group_criterion_label_tools(ad_group_criterion_label_sdk_server)
