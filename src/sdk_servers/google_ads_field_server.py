"""Google Ads field server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.metadata.google_ads_field_service import (
    register_google_ads_field_tools,
)

# Create the Google Ads field server
google_ads_field_sdk_server = FastMCP(
    name="google_ads_field",
    instructions="""This server provides tools for discovering field metadata and validating queries in Google Ads.

    Available tools:
    - get_field_metadata: Get detailed metadata for a specific field
    - search_fields: Search for fields based on criteria
    - get_resource_fields: Get all available fields for a resource
    - validate_query_fields: Validate if fields can be selected together

    Field metadata includes:
    - Category: RESOURCE, ATTRIBUTE, SEGMENT, or METRIC
    - Data type: STRING, INT64, DOUBLE, BOOLEAN, etc.
    - Selectability: Whether the field can be used in SELECT
    - Filterability: Whether the field can be used in WHERE
    - Sortability: Whether the field can be used in ORDER BY

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
google_ads_field_service = register_google_ads_field_tools(google_ads_field_sdk_server)
