"""Google Ads Brand Suggestion Service

This module provides functionality for getting brand suggestions in Google Ads.
Brand suggestions help advertisers find relevant brands for their campaigns.
"""

from typing import List, Optional

from google.ads.googleads.v20.services.services.brand_suggestion_service import (
    BrandSuggestionServiceClient,
)
from google.ads.googleads.v20.services.types.brand_suggestion_service import (
    SuggestBrandsRequest,
    SuggestBrandsResponse,
)


class BrandSuggestionService:
    """Service for getting Google Ads brand suggestions."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("BrandSuggestionService")

    def suggest_brands(
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
        return self.service.suggest_brands(request=request)
