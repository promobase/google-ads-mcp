"""Tests for KeywordPlanIdeaService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)
from google.ads.googleads.v20.services.services.keyword_plan_idea_service import (
    KeywordPlanIdeaServiceClient,
)

from src.sdk_services.planning.keyword_plan_idea_service import (
    KeywordPlanIdeaService,
    register_keyword_plan_idea_tools,
)


@pytest.fixture
def keyword_plan_idea_service(mock_sdk_client: Any) -> KeywordPlanIdeaService:
    """Create a KeywordPlanIdeaService instance with mocked dependencies."""
    # Mock KeywordPlanIdeaService client
    mock_idea_client = Mock(spec=KeywordPlanIdeaServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_idea_client

    with patch(
        "src.sdk_services.planning.keyword_plan_idea_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = KeywordPlanIdeaService()
        # Force client initialization
        _ = service.client
        return service


def create_mock_keyword_idea(
    text: str = "test keyword",
    avg_monthly_searches: int = 1000,
    competition: str = "MEDIUM",
    competition_index: int = 50,
    low_bid: int = 500000,
    high_bid: int = 1000000,
) -> Mock:
    """Create a mock keyword idea result."""
    idea = Mock()
    idea.text = text

    # Mock metrics
    idea.keyword_idea_metrics = Mock()
    idea.keyword_idea_metrics.avg_monthly_searches = avg_monthly_searches
    idea.keyword_idea_metrics.competition = Mock()
    idea.keyword_idea_metrics.competition.name = competition
    idea.keyword_idea_metrics.competition_index = competition_index
    idea.keyword_idea_metrics.low_top_of_page_bid_micros = low_bid
    idea.keyword_idea_metrics.high_top_of_page_bid_micros = high_bid

    # Mock monthly search volumes
    volume1 = Mock()
    volume1.year = 2024
    volume1.month = Mock()
    volume1.month.name = "JANUARY"
    volume1.monthly_searches = 1100

    volume2 = Mock()
    volume2.year = 2024
    volume2.month = Mock()
    volume2.month.name = "FEBRUARY"
    volume2.monthly_searches = 900

    idea.keyword_idea_metrics.monthly_search_volumes = [volume1, volume2]

    # Mock annotations
    idea.keyword_annotations = Mock()
    concept = Mock()
    concept.name = "Running"
    concept.concept_group = Mock()
    concept.concept_group.name = "Sports & Fitness"
    concept.concept_group.type_ = Mock()
    concept.concept_group.type_.name = "CATEGORY"
    idea.keyword_annotations.concepts = [concept]

    return idea


@pytest.mark.asyncio
async def test_generate_keyword_ideas_from_keywords(
    keyword_plan_idea_service: KeywordPlanIdeaService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating keyword ideas from keywords."""
    # Arrange
    customer_id = "1234567890"
    keywords = ["running shoes", "athletic footwear"]
    language = "languageConstants/1000"
    geo_target_constants = ["geoTargetConstants/2840"]  # US

    # Mock response
    mock_ideas = [
        create_mock_keyword_idea(
            "running shoes sale", 5000, "HIGH", 80, 750000, 1500000
        ),
        create_mock_keyword_idea(
            "best running shoes", 3000, "MEDIUM", 60, 600000, 1200000
        ),
        create_mock_keyword_idea(
            "cheap athletic footwear", 1500, "LOW", 30, 400000, 800000
        ),
    ]

    # Get the mocked idea service client
    mock_idea_client = keyword_plan_idea_service.client  # type: ignore
    mock_idea_client.generate_keyword_ideas.return_value = mock_ideas  # type: ignore

    # Act
    result = await keyword_plan_idea_service.generate_keyword_ideas_from_keywords(
        ctx=mock_ctx,
        customer_id=customer_id,
        keywords=keywords,
        language=language,
        geo_target_constants=geo_target_constants,
        keyword_plan_network=KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords=False,
        page_size=100,
    )

    # Assert
    assert len(result) == 3
    assert result[0]["text"] == "running shoes sale"
    assert result[0]["keyword_idea_metrics"]["avg_monthly_searches"] == 5000
    assert result[0]["keyword_idea_metrics"]["competition"] == "HIGH"
    assert result[0]["keyword_idea_metrics"]["competition_index"] == 80
    assert result[0]["keyword_idea_metrics"]["low_top_of_page_bid_micros"] == 750000
    assert result[0]["keyword_idea_metrics"]["high_top_of_page_bid_micros"] == 1500000
    assert len(result[0]["keyword_idea_metrics"]["monthly_search_volumes"]) == 2
    assert result[0]["keyword_annotations"]["concepts"][0]["name"] == "Running"

    # Verify the API call
    mock_idea_client.generate_keyword_ideas.assert_called_once()  # type: ignore
    call_args = mock_idea_client.generate_keyword_ideas.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert list(request.keyword_seed.keywords) == keywords
    assert request.language == language
    assert list(request.geo_target_constants) == geo_target_constants
    assert (
        request.keyword_plan_network
        == KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
    )
    assert request.include_adult_keywords is False
    assert request.page_size == 100

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 3 keyword ideas from 2 seed keywords",
    )


@pytest.mark.asyncio
async def test_generate_keyword_ideas_from_url(
    keyword_plan_idea_service: KeywordPlanIdeaService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating keyword ideas from a URL."""
    # Arrange
    customer_id = "1234567890"
    page_url = "https://example.com/running-shoes"
    language = "languageConstants/1000"
    geo_target_constants = ["geoTargetConstants/2840"]

    # Mock response
    mock_ideas = [
        create_mock_keyword_idea(
            "marathon running shoes", 2000, "MEDIUM", 55, 650000, 1300000
        ),
        create_mock_keyword_idea(
            "trail running footwear", 1200, "LOW", 35, 450000, 900000
        ),
    ]

    # Get the mocked idea service client
    mock_idea_client = keyword_plan_idea_service.client  # type: ignore
    mock_idea_client.generate_keyword_ideas.return_value = mock_ideas  # type: ignore

    # Act
    result = await keyword_plan_idea_service.generate_keyword_ideas_from_url(
        ctx=mock_ctx,
        customer_id=customer_id,
        page_url=page_url,
        language=language,
        geo_target_constants=geo_target_constants,
        keyword_plan_network=KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH,
        include_adult_keywords=False,
        page_size=50,
    )

    # Assert
    assert len(result) == 2
    assert result[0]["text"] == "marathon running shoes"
    assert result[1]["text"] == "trail running footwear"

    # Verify the API call
    mock_idea_client.generate_keyword_ideas.assert_called_once()  # type: ignore
    call_args = mock_idea_client.generate_keyword_ideas.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.url_seed.url == page_url
    assert request.language == language
    assert (
        request.keyword_plan_network
        == KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Generated 2 keyword ideas from URL: {page_url}",
    )


@pytest.mark.asyncio
async def test_generate_keyword_ideas_from_site(
    keyword_plan_idea_service: KeywordPlanIdeaService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating keyword ideas from a site."""
    # Arrange
    customer_id = "1234567890"
    site_url = "example.com"
    language = "languageConstants/1000"
    geo_target_constants = ["geoTargetConstants/2840"]

    # Mock response
    mock_ideas = [
        create_mock_keyword_idea(
            "sports equipment online", 8000, "HIGH", 75, 800000, 1600000
        ),
    ]

    # Get the mocked idea service client
    mock_idea_client = keyword_plan_idea_service.client  # type: ignore
    mock_idea_client.generate_keyword_ideas.return_value = mock_ideas  # type: ignore

    # Act
    result = await keyword_plan_idea_service.generate_keyword_ideas_from_site(
        ctx=mock_ctx,
        customer_id=customer_id,
        site_url=site_url,
        language=language,
        geo_target_constants=geo_target_constants,
    )

    # Assert
    assert len(result) == 1
    assert result[0]["text"] == "sports equipment online"

    # Verify the API call
    mock_idea_client.generate_keyword_ideas.assert_called_once()  # type: ignore
    call_args = mock_idea_client.generate_keyword_ideas.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.site_seed.site == site_url

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Generated 1 keyword ideas from site: {site_url}",
    )


@pytest.mark.asyncio
async def test_generate_keyword_ideas_from_keywords_and_url(
    keyword_plan_idea_service: KeywordPlanIdeaService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating keyword ideas from both keywords and URL."""
    # Arrange
    customer_id = "1234567890"
    keywords = ["running", "fitness"]
    page_url = "https://example.com/sports"
    language = "languageConstants/1000"
    geo_target_constants = ["geoTargetConstants/2840"]

    # Mock response
    mock_ideas = [
        create_mock_keyword_idea(
            "fitness running gear", 4500, "MEDIUM", 65, 700000, 1400000
        ),
        create_mock_keyword_idea(
            "running fitness tracker", 3500, "MEDIUM", 60, 650000, 1300000
        ),
    ]

    # Get the mocked idea service client
    mock_idea_client = keyword_plan_idea_service.client  # type: ignore
    mock_idea_client.generate_keyword_ideas.return_value = mock_ideas  # type: ignore

    # Act
    result = (
        await keyword_plan_idea_service.generate_keyword_ideas_from_keywords_and_url(
            ctx=mock_ctx,
            customer_id=customer_id,
            keywords=keywords,
            page_url=page_url,
            language=language,
            geo_target_constants=geo_target_constants,
            include_adult_keywords=True,
            page_size=200,
        )
    )

    # Assert
    assert len(result) == 2
    assert result[0]["text"] == "fitness running gear"
    assert result[1]["text"] == "running fitness tracker"

    # Verify the API call
    mock_idea_client.generate_keyword_ideas.assert_called_once()  # type: ignore
    call_args = mock_idea_client.generate_keyword_ideas.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert list(request.keyword_and_url_seed.keywords) == keywords
    assert request.keyword_and_url_seed.url == page_url
    assert request.include_adult_keywords is True
    assert request.page_size == 200

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 2 keyword ideas from keywords and URL",
    )


@pytest.mark.asyncio
async def test_error_handling(
    keyword_plan_idea_service: KeywordPlanIdeaService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked idea service client and make it raise exception
    mock_idea_client = keyword_plan_idea_service.client  # type: ignore
    mock_idea_client.generate_keyword_ideas.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await keyword_plan_idea_service.generate_keyword_ideas_from_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            keywords=["test"],
            language="languageConstants/1000",
            geo_target_constants=["geoTargetConstants/2840"],
        )

    assert "Failed to generate keyword ideas" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to generate keyword ideas: Test Google Ads Exception",
    )


def test_register_keyword_plan_idea_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_keyword_plan_idea_tools(mock_mcp)

    # Assert
    assert isinstance(service, KeywordPlanIdeaService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "generate_keyword_ideas_from_keywords",
        "generate_keyword_ideas_from_url",
        "generate_keyword_ideas_from_site",
        "generate_keyword_ideas_from_keywords_and_url",
    ]

    assert set(tool_names) == set(expected_tools)
