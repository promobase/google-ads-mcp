"""Geo target constant server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.targeting.geo_target_constant_service import (
    register_geo_target_constant_tools,
)

# Create the geo target constant server
geo_target_constant_sdk_server = FastMCP(
    name="geo_target_constant",
    instructions="""This server provides tools for searching and suggesting geo targeting locations.

    Available tools:
    - suggest_geo_targets_by_location: Find geo targets by location names
    - suggest_geo_targets_by_address: Find geo targets by address
    - search_geo_targets: Search for geo targets using a query

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
geo_target_constant_service = register_geo_target_constant_tools(
    geo_target_constant_sdk_server
)
