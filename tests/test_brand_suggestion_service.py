"""Tests for Google Ads Brand Suggestion Service"""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v23.enums.types.brand_state import BrandStateEnum
from google.ads.googleads.v23.services.types.brand_suggestion_service import (
    BrandSuggestion,
    SuggestBrandsResponse,
)

from src.services.planning.brand_suggestion_service import BrandSuggestionService


class TestBrandSuggestionService:
    """Test cases for BrandSuggestionService"""

    @pytest.fixture
    def mock_service_client(self) -> Any:
        """Mock BrandSuggestionService API client."""
        return Mock()

    @pytest.fixture
    def brand_suggestion_service(self, mock_service_client: Any) -> Any:
        """Create BrandSuggestionService instance with mock client"""
        service = BrandSuggestionService()
        service._client = mock_service_client  # type: ignore[reportPrivateUsage]
        return service

    def test_suggest_brands(
        self, brand_suggestion_service: Any, mock_service_client: Any
    ):
        """Test suggesting brands"""
        # Setup
        customer_id = "1234567890"
        brand_prefix = "nike"
        selected_brands = ["brand123"]

        mock_response = SuggestBrandsResponse(
            brands=[
                BrandSuggestion(
                    id="brand456",
                    name="Nike",
                    urls=["https://www.nike.com"],
                    state=BrandStateEnum.BrandState.APPROVED,
                ),
                BrandSuggestion(
                    id="brand789",
                    name="Nike Air",
                    urls=["https://www.nike.com/air"],
                    state=BrandStateEnum.BrandState.APPROVED,
                ),
            ]
        )
        mock_service_client.suggest_brands.return_value = mock_response  # type: ignore

        # Execute
        response = brand_suggestion_service.suggest_brands(
            customer_id=customer_id,
            brand_prefix=brand_prefix,
            selected_brands=selected_brands,
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_service_client.suggest_brands.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.brand_prefix == brand_prefix
        assert request.selected_brands == selected_brands

    def test_suggest_brands_without_selected_brands(
        self, brand_suggestion_service: Any, mock_service_client: Any
    ):
        """Test suggesting brands without selected brands"""
        # Setup
        customer_id = "1234567890"
        brand_prefix = "adidas"

        mock_response = SuggestBrandsResponse(
            brands=[
                BrandSuggestion(
                    id="brand101",
                    name="Adidas",
                    urls=["https://www.adidas.com"],
                    state=BrandStateEnum.BrandState.APPROVED,
                )
            ]
        )
        mock_service_client.suggest_brands.return_value = mock_response  # type: ignore

        # Execute
        response = brand_suggestion_service.suggest_brands(
            customer_id=customer_id, brand_prefix=brand_prefix
        )

        # Verify
        assert response == mock_response

        # Verify request
        call_args = mock_service_client.suggest_brands.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.brand_prefix == brand_prefix
        assert request.selected_brands == []
