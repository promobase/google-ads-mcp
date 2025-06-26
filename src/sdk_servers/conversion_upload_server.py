"""Conversion upload server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_upload_service import (
    register_conversion_upload_tools,
)

# Create the conversion upload server
conversion_upload_sdk_server = FastMCP(
    name="conversion_upload",
    instructions="""This server provides tools for uploading offline conversions.

    Available tools:
    - upload_click_conversions: Upload conversions from ad clicks
    - upload_call_conversions: Upload conversions from phone calls

    Click conversions require:
    - GCLID (Google Click ID) from the original ad click
    - Conversion action ID to credit
    - Conversion date/time

    Call conversions require:
    - Caller's phone number
    - Call start date/time
    - Conversion action ID to credit
    - Conversion date/time

    Enhanced conversions:
    - Optionally provide hashed user identifiers (email, phone, address)
    - Improves conversion attribution accuracy
    - All personal data is automatically hashed with SHA256

    Features:
    - Batch upload multiple conversions
    - Partial failure handling
    - Deduplication with order IDs
    - Currency and value tracking

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
conversion_upload_service = register_conversion_upload_tools(
    conversion_upload_sdk_server
)
