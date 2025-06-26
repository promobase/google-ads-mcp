"""Tests for KeywordPlanService."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.keyword_plan_forecast_interval import (
    KeywordPlanForecastIntervalEnum,
)
from google.ads.googleads.v20.enums.types.keyword_match_type import (
    KeywordMatchTypeEnum,
)
from google.ads.googleads.v20.services.services.keyword_plan_service import (
    KeywordPlanServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_service import (
    MutateKeywordPlansResponse,
)

from src.sdk_services.planning.keyword_plan_service import (
    KeywordPlanService,
    register_keyword_plan_tools,
)


@pytest.fixture
def keyword_plan_service(mock_sdk_client: Any) -> KeywordPlanService:
    """Create a KeywordPlanService instance with mocked dependencies."""
    # Mock KeywordPlanService client
    mock_keyword_plan_client = Mock(spec=KeywordPlanServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_keyword_plan_client

    with patch(
        "src.sdk_services.planning.keyword_plan_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = KeywordPlanService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_keyword_plan(
    keyword_plan_service: KeywordPlanService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a keyword plan."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Keyword Plan"
    forecast_period_days = 30

    # Create mock response
    mock_response = Mock(spec=MutateKeywordPlansResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/keywordPlans/123"

    # Get the mocked keyword plan service client
    mock_keyword_plan_client = keyword_plan_service.client  # type: ignore
    mock_keyword_plan_client.mutate_keyword_plans.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/keywordPlans/123"}]
    }

    with patch(
        "src.sdk_services.planning.keyword_plan_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_plan_service.create_keyword_plan(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            forecast_period_days=forecast_period_days,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_keyword_plan_client.mutate_keyword_plans.assert_called_once()  # type: ignore
    call_args = mock_keyword_plan_client.mutate_keyword_plans.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.forecast_period.date_interval
        == KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval.NEXT_MONTH
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created keyword plan '{name}'",
    )


@pytest.mark.asyncio
async def test_get_keyword_ideas(
    keyword_plan_service: KeywordPlanService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting keyword ideas."""
    # Arrange
    customer_id = "1234567890"
    keywords = ["running shoes", "athletic footwear"]
    location_ids = ["2840"]  # US
    language_id = "1000"  # English
    limit = 10

    # Mock KeywordPlanIdeaService
    mock_idea_service = Mock()

    # Create mock keyword ideas
    mock_ideas = []
    for i in range(3):
        idea = Mock()
        idea.text = f"keyword idea {i}"
        idea.keyword_idea_metrics = Mock()
        idea.keyword_idea_metrics.avg_monthly_searches = 1000 * (i + 1)
        idea.keyword_idea_metrics.competition = Mock()
        idea.keyword_idea_metrics.competition.name = ["LOW", "MEDIUM", "HIGH"][i]
        idea.keyword_idea_metrics.competition_index = 30 * (i + 1)
        idea.keyword_idea_metrics.low_top_of_page_bid_micros = 500000 * (i + 1)
        idea.keyword_idea_metrics.high_top_of_page_bid_micros = 1000000 * (i + 1)
        mock_ideas.append(idea)

    mock_idea_service.generate_keyword_ideas.return_value = mock_ideas

    def get_service_side_effect(service_name: str):
        if service_name == "KeywordPlanIdeaService":
            return mock_idea_service
        return keyword_plan_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    # Mock serialize_proto_message to return the same structure
    def serialize_side_effect(obj: Any) -> Dict[str, Any]:
        return {
            "text": obj.text,
            "keyword_idea_metrics": {
                "avg_monthly_searches": obj.keyword_idea_metrics.avg_monthly_searches,
                "competition": obj.keyword_idea_metrics.competition.name,
                "competition_index": obj.keyword_idea_metrics.competition_index,
                "low_top_of_page_bid_micros": obj.keyword_idea_metrics.low_top_of_page_bid_micros,
                "high_top_of_page_bid_micros": obj.keyword_idea_metrics.high_top_of_page_bid_micros,
            },
        }

    with (
        patch(
            "src.sdk_services.planning.keyword_plan_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.planning.keyword_plan_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await keyword_plan_service.get_keyword_ideas(
            ctx=mock_ctx,
            customer_id=customer_id,
            keywords=keywords,
            location_ids=location_ids,
            language_id=language_id,
            include_adult_keywords=False,
            limit=limit,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["text"] == "keyword idea 0"
    assert result[0]["keyword_idea_metrics"]["avg_monthly_searches"] == 1000

    # Verify the API call
    mock_idea_service.generate_keyword_ideas.assert_called_once()  # type: ignore
    call_args = mock_idea_service.generate_keyword_ideas.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.keyword_seed.keywords) == 2
    assert request.keyword_seed.keywords[0] == "running shoes"
    assert request.language == "languageConstants/1000"
    assert request.geo_target_constants[0] == "geoTargetConstants/2840"
    assert request.include_adult_keywords is False

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 3 keyword ideas",
    )


@pytest.mark.asyncio
async def test_create_keyword_plan_campaign(
    keyword_plan_service: KeywordPlanService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a keyword plan campaign."""
    # Arrange
    customer_id = "1234567890"
    keyword_plan_id = "123"
    name = "Test Campaign"
    cpc_bid_micros = 1000000  # $1.00
    location_ids = ["2840"]  # US
    language_id = "1000"  # English

    # Mock KeywordPlanCampaignService
    mock_campaign_service = Mock()
    mock_response = Mock()
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/keywordPlanCampaigns/456"
    mock_campaign_service.mutate_keyword_plan_campaigns.return_value = mock_response

    def get_service_side_effect(service_name: str):
        if service_name == "KeywordPlanCampaignService":
            return mock_campaign_service
        return keyword_plan_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/keywordPlanCampaigns/456"}
        ]
    }

    with (
        patch(
            "src.sdk_services.planning.keyword_plan_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.planning.keyword_plan_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await keyword_plan_service.create_keyword_plan_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            keyword_plan_id=keyword_plan_id,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
            location_ids=location_ids,
            language_id=language_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_service.mutate_keyword_plan_campaigns.assert_called_once()  # type: ignore
    call_args = mock_campaign_service.mutate_keyword_plan_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.keyword_plan
        == f"customers/{customer_id}/keywordPlans/{keyword_plan_id}"
    )
    assert operation.create.cpc_bid_micros == cpc_bid_micros
    assert operation.create.language_constants[0] == "languageConstants/1000"
    assert len(operation.create.geo_targets) == 1
    assert (
        operation.create.geo_targets[0].geo_target_constant == "geoTargetConstants/2840"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created keyword plan campaign '{name}'",
    )


@pytest.mark.asyncio
async def test_add_keywords_to_plan(
    keyword_plan_service: KeywordPlanService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keywords to a keyword plan."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "789"
    keywords = [
        {"text": "running shoes", "match_type": "EXACT"},
        {
            "text": "athletic footwear",
            "match_type": "PHRASE",
            "cpc_bid_micros": 1500000,
        },
        {"text": "sports shoes"},  # Should default to BROAD
    ]

    # Mock KeywordPlanAdGroupKeywordService
    mock_keyword_service = Mock()
    mock_response = Mock()
    mock_response.results = []
    for i in range(len(keywords)):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/keywordPlanAdGroupKeywords/{i + 1000}"
        )
        mock_response.results.append(result)
    mock_keyword_service.mutate_keyword_plan_ad_group_keywords.return_value = (
        mock_response
    )

    def get_service_side_effect(service_name: str):
        if service_name == "KeywordPlanAdGroupKeywordService":
            return mock_keyword_service
        return keyword_plan_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.planning.keyword_plan_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await keyword_plan_service.add_keywords_to_plan(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["text"] == "running shoes"
    assert result[0]["match_type"] == "EXACT"
    assert result[1]["text"] == "athletic footwear"
    assert result[1]["match_type"] == "PHRASE"
    assert result[2]["text"] == "sports shoes"
    assert result[2]["match_type"] == "BROAD"

    # Verify the API call
    mock_keyword_service.mutate_keyword_plan_ad_group_keywords.assert_called_once()  # type: ignore
    call_args = mock_keyword_service.mutate_keyword_plan_ad_group_keywords.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Check first keyword
    op1 = request.operations[0]
    assert op1.create.text == "running shoes"
    assert op1.create.match_type == KeywordMatchTypeEnum.KeywordMatchType.EXACT
    assert (
        op1.create.keyword_plan_ad_group
        == f"customers/{customer_id}/keywordPlanAdGroups/{ad_group_id}"
    )

    # Check second keyword with custom bid
    op2 = request.operations[1]
    assert op2.create.text == "athletic footwear"
    assert op2.create.match_type == KeywordMatchTypeEnum.KeywordMatchType.PHRASE
    assert op2.create.cpc_bid_micros == 1500000

    # Check third keyword (defaults to BROAD)
    op3 = request.operations[2]
    assert op3.create.text == "sports shoes"
    assert op3.create.match_type == KeywordMatchTypeEnum.KeywordMatchType.BROAD

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Added 3 keywords to plan",
    )


@pytest.mark.asyncio
async def test_error_handling(
    keyword_plan_service: KeywordPlanService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked keyword plan service client and make it raise exception
    mock_keyword_plan_client = keyword_plan_service.client  # type: ignore
    mock_keyword_plan_client.mutate_keyword_plans.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await keyword_plan_service.create_keyword_plan(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Plan",
        )

    assert "Failed to create keyword plan" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create keyword plan: Test Google Ads Exception",
    )


def test_register_keyword_plan_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_keyword_plan_tools(mock_mcp)

    # Assert
    assert isinstance(service, KeywordPlanService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_keyword_plan",
        "get_keyword_ideas",
        "create_keyword_plan_campaign",
        "add_keywords_to_plan",
    ]

    assert set(tool_names) == set(expected_tools)
