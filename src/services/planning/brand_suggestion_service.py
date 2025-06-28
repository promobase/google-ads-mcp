"""Google Ads Brand Suggestion Service

This module provides functionality for getting brand suggestions in Google Ads.
Brand suggestions help advertisers find relevant brands for their campaigns.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.services.services.brand_suggestion_service import (
    BrandSuggestionServiceClient,
)
from google.ads.googleads.v20.services.types.brand_suggestion_service import (
    SuggestBrandsRequest,
    SuggestBrandsResponse,
)

from src.sdk_client import get_sdk_client


class BrandSuggestionService:
    """Service for getting Google Ads brand suggestions."""

    def __init__(self) -> None:
        """Initialize the brand suggestion service."""
        self._client: Optional[BrandSuggestionServiceClient] = None

    @property
    def client(self) -> BrandSuggestionServiceClient:
        """Get the brand suggestion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BrandSuggestionService")
        assert self._client is not None
        return self._client

    def suggest_brands(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        brand_prefix: str,
        selected_brands: Optional[List[str]] = None,
    ) -> SuggestBrandsResponse:
        """Get brand suggestions based on a brand prefix.

        Args:
            customer_id: The customer ID
            brand_prefix: The prefix of a brand name to search for
            selected_brands: Optional list of brand IDs to exclude from results

        Returns:
            SuggestBrandsResponse: The response containing brand suggestions
        """
        request = SuggestBrandsRequest(
            customer_id=customer_id,
            brand_prefix=brand_prefix,
            selected_brands=selected_brands or [],
        )
        return self.client.suggest_brands(request=request)


def register_brand_suggestion_tools(mcp: FastMCP[Any]) -> None:
    """Register brand suggestion tools with the MCP server."""

    @mcp.tool
    async def suggest_brands(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        brand_prefix: str,
        selected_brands: list[str] = [],
    ) -> str:
        """Get brand suggestions based on a brand prefix.

        Args:
            customer_id: The customer ID
            brand_prefix: The prefix of a brand name to search for
            selected_brands: Optional list of brand IDs to exclude from results

        Returns:
            JSON string containing brand suggestions
        """
        service = BrandSuggestionService()

        response = service.suggest_brands(
            customer_id=customer_id,
            brand_prefix=brand_prefix,
            selected_brands=selected_brands,
        )

        suggestions = []
        for brand in response.brands:
            suggestions.append(
                {
                    "id": brand.id,
                    "name": brand.name,
                    "state": brand.state.name if brand.state else "UNKNOWN",
                }
            )

        return f"Found {len(suggestions)} brand suggestions: {suggestions}"
