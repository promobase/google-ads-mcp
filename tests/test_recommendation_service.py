"""Tests for RecommendationService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.recommendation_service import (
    RecommendationServiceClient,
)
from google.ads.googleads.v20.services.types.recommendation_service import (
    ApplyRecommendationResponse,
    DismissRecommendationResponse,
)

from src.sdk_services.planning.recommendation_service import (
    RecommendationService,
    register_recommendation_tools,
)


@pytest.fixture
def recommendation_service(mock_sdk_client: Any) -> RecommendationService:
    """Create a RecommendationService instance with mocked dependencies."""
    # Mock RecommendationService client
    mock_recommendation_client = Mock(spec=RecommendationServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_recommendation_client  # type: ignore

    with patch(
        "src.sdk_services.planning.recommendation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = RecommendationService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_get_recommendations(
    recommendation_service: RecommendationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting recommendations."""
    # Arrange
    customer_id = "1234567890"
    types = ["CAMPAIGN_BUDGET", "KEYWORD"]
    campaign_ids = ["111", "222"]
    limit = 10

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock()

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.recommendation = Mock()
        row.recommendation.resource_name = (
            f"customers/{customer_id}/recommendations/{i + 1000}"
        )
        row.recommendation.type = Mock()
        row.recommendation.type.name = ["CAMPAIGN_BUDGET", "KEYWORD", "TEXT_AD"][i]
        row.recommendation.dismissed = False

        # Mock impact
        row.recommendation.impact = Mock()
        row.recommendation.impact.base_metrics = Mock()
        row.recommendation.impact.base_metrics.impressions = 1000 * (i + 1)
        row.recommendation.impact.base_metrics.clicks = 100 * (i + 1)
        row.recommendation.impact.base_metrics.cost_micros = 50000000 * (i + 1)
        row.recommendation.impact.base_metrics.conversions = 10.5 * (i + 1)
        row.recommendation.impact.base_metrics.conversions_value = 500.0 * (i + 1)

        row.recommendation.impact.potential_metrics = Mock()
        row.recommendation.impact.potential_metrics.impressions = 1500 * (i + 1)
        row.recommendation.impact.potential_metrics.clicks = 150 * (i + 1)
        row.recommendation.impact.potential_metrics.cost_micros = 60000000 * (i + 1)
        row.recommendation.impact.potential_metrics.conversions = 15.5 * (i + 1)
        row.recommendation.impact.potential_metrics.conversions_value = 750.0 * (i + 1)

        # Add type-specific recommendation data
        if i == 0:
            row.recommendation.campaign_budget_recommendation = Mock()
            # Create a proper mock budget option
            mock_budget_option = Mock()
            mock_budget_option.budget_amount_micros = 100000000
            mock_budget_option.impact = Mock()
            mock_budget_option.impact.impressions = 1000  # type: ignore
            mock_budget_option.impact.clicks = 100  # type: ignore
            mock_budget_option.impact.cost_micros = 50000000  # type: ignore
            mock_budget_option.impact.conversions = 10  # type: ignore
            row.recommendation.campaign_budget_recommendation.budget_options = [
                mock_budget_option
            ]
            row.recommendation.campaign_budget_recommendation.current_budget_amount_micros = 50000000
            row.recommendation.campaign_budget_recommendation.recommended_budget_amount_micros = 100000000
            # Set other recommendation types to None
            row.recommendation.keyword_recommendation = None
            row.recommendation.text_ad_recommendation = None
        elif i == 1:
            row.recommendation.keyword_recommendation = Mock()
            row.recommendation.keyword_recommendation.keyword = Mock()
            row.recommendation.keyword_recommendation.keyword.text = "new keyword"
            row.recommendation.keyword_recommendation.keyword.match_type = Mock()
            row.recommendation.keyword_recommendation.keyword.match_type.name = "BROAD"
            row.recommendation.keyword_recommendation.recommended_cpc_bid_micros = (
                1000000
            )
            # Set other recommendation types to None
            row.recommendation.campaign_budget_recommendation = None
            row.recommendation.text_ad_recommendation = None
        else:
            row.recommendation.text_ad_recommendation = Mock()
            row.recommendation.text_ad_recommendation.ad = Mock()
            # Create mock headlines
            headline1 = Mock()
            headline1.text = "Great Products"
            headline2 = Mock()
            headline2.text = "Best Prices"
            row.recommendation.text_ad_recommendation.ad.headlines = [
                headline1,
                headline2,
            ]
            # Create mock descriptions
            desc1 = Mock()
            desc1.text = "Shop now for amazing deals"
            desc2 = Mock()
            desc2.text = "Free shipping on all orders"
            row.recommendation.text_ad_recommendation.ad.descriptions = [desc1, desc2]
            row.recommendation.text_ad_recommendation.ad.final_urls = [
                "https://example.com"
            ]
            # Set other recommendation types to None
            row.recommendation.campaign_budget_recommendation = None
            row.recommendation.keyword_recommendation = None

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return recommendation_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with patch(
        "src.sdk_services.planning.recommendation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await recommendation_service.get_recommendations(
            ctx=mock_ctx,
            customer_id=customer_id,
            types=types,
            campaign_ids=campaign_ids,
            dismissed=False,
            limit=limit,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["type"] == "CAMPAIGN_BUDGET"
    assert result[0]["dismissed"] is False
    assert "impact" in result[0]
    assert result[0]["impact"]["base_metrics"]["clicks"] == 100
    assert result[0]["impact"]["potential_metrics"]["clicks"] == 150

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "recommendation.dismissed = FALSE" in query
    assert "recommendation.type = 'CAMPAIGN_BUDGET'" in query
    assert "recommendation.type = 'KEYWORD'" in query
    assert f"recommendation.campaign = 'customers/{customer_id}/campaigns/111'" in query
    assert f"LIMIT {limit}" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 recommendations",
    )


@pytest.mark.asyncio
async def test_apply_recommendation(
    recommendation_service: RecommendationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test applying a recommendation."""
    # Arrange
    customer_id = "1234567890"
    recommendation_resource_name = f"customers/{customer_id}/recommendations/1000"

    # Create mock response
    mock_response = Mock(spec=ApplyRecommendationResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = recommendation_resource_name

    # Get the mocked recommendation service client
    mock_recommendation_client = recommendation_service.client  # type: ignore
    mock_recommendation_client.apply_recommendation.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": recommendation_resource_name}]}

    with patch(
        "src.sdk_services.planning.recommendation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await recommendation_service.apply_recommendation(
            ctx=mock_ctx,
            customer_id=customer_id,
            recommendation_resource_name=recommendation_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_recommendation_client.apply_recommendation.assert_called_once()  # type: ignore
    call_args = mock_recommendation_client.apply_recommendation.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1
    assert request.operations[0].resource_name == recommendation_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Applied recommendation: {recommendation_resource_name}",
    )


@pytest.mark.asyncio
async def test_dismiss_recommendation(
    recommendation_service: RecommendationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test dismissing recommendations."""
    # Arrange
    customer_id = "1234567890"
    recommendation_resource_names = [
        f"customers/{customer_id}/recommendations/1000",
        f"customers/{customer_id}/recommendations/1001",
    ]

    # Create mock response
    mock_response = Mock(spec=DismissRecommendationResponse)
    mock_response.results = []
    for resource_name in recommendation_resource_names:
        result = Mock()
        result.resource_name = resource_name
        mock_response.results.append(result)  # type: ignore

    # Get the mocked recommendation service client
    mock_recommendation_client = recommendation_service.client  # type: ignore
    mock_recommendation_client.dismiss_recommendation.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": rn} for rn in recommendation_resource_names]
    }

    with patch(
        "src.sdk_services.planning.recommendation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await recommendation_service.dismiss_recommendation(
            ctx=mock_ctx,
            customer_id=customer_id,
            recommendation_resource_names=recommendation_resource_names,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_recommendation_client.dismiss_recommendation.assert_called_once()  # type: ignore
    call_args = mock_recommendation_client.dismiss_recommendation.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Dismissed {len(recommendation_resource_names)} recommendations",
    )


@pytest.mark.asyncio
async def test_get_recommendations_minimal(
    recommendation_service: RecommendationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting recommendations with minimal parameters."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock()
    mock_google_ads_service.search.return_value = []  # type: ignore

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return recommendation_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with patch(
        "src.sdk_services.planning.recommendation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await recommendation_service.get_recommendations(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert result == []

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    # Should have default filter for non-dismissed
    assert "recommendation.dismissed = FALSE" in query


@pytest.mark.asyncio
async def test_error_handling(
    recommendation_service: RecommendationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    recommendation_resource_name = f"customers/{customer_id}/recommendations/1000"

    # Get the mocked recommendation service client and make it raise exception
    mock_recommendation_client = recommendation_service.client  # type: ignore
    mock_recommendation_client.apply_recommendation.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await recommendation_service.apply_recommendation(
            ctx=mock_ctx,
            customer_id=customer_id,
            recommendation_resource_name=recommendation_resource_name,
        )

    assert "Failed to apply recommendation" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to apply recommendation: Test Google Ads Exception",
    )


def test_register_recommendation_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_recommendation_tools(mock_mcp)

    # Assert
    assert isinstance(service, RecommendationService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "get_recommendations",
        "apply_recommendation",
        "dismiss_recommendation",
    ]

    assert set(tool_names) == set(expected_tools)
