"""Tests for SearchService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from src.services.metadata.search_service import (
    SearchService,
    register_search_tools,
)


@pytest.fixture
def search_service(mock_sdk_client: Any) -> SearchService:
    """Create a SearchService instance with mocked dependencies."""
    # Mock GoogleAdsService
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_google_ads_service  # type: ignore

    with patch(
        "src.sdk_services.metadata.search_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = SearchService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_search_campaigns(
    search_service: SearchService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching for campaigns."""
    # Arrange
    customer_id = "1234567890"
    include_removed = False
    limit = 10

    # Create mock search results
    mock_results = []
    for i in range(2):
        row = Mock()
        row.campaign = Mock()
        row.campaign.id = f"1000{i}"
        row.campaign.name = f"Campaign {i}"
        row.campaign.status = "ENABLED"
        row.campaign_budget = Mock()
        row.campaign_budget.id = f"2000{i}"
        row.campaign_budget.amount_micros = 10000000
        mock_results.append(row)

    # Get the mocked GoogleAdsService from the fixture
    mock_google_ads_service = search_service.client  # type: ignore
    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    with patch(
        "src.sdk_services.metadata.search_service.serialize_proto_message",
        side_effect=[{"campaign": f"data{i}"} for i in range(2)],
    ):
        # Act
        results = await search_service.search_campaigns(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_removed=include_removed,
            limit=limit,
        )

    # Assert
    assert len(results) == 2

    # Verify the query
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert "WHERE campaign.status != 'REMOVED'" in request.query
    assert "LIMIT 10" in request.query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 campaigns for customer 1234567890",
    )


@pytest.mark.asyncio
async def test_search_ad_groups(
    search_service: SearchService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching for ad groups."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    include_removed = False
    limit = 5

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.ad_group = Mock()
        row.ad_group.id = f"3000{i}"
        row.ad_group.name = f"Ad Group {i}"
        row.ad_group.status = "PAUSED"
        row.ad_group.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        row.campaign = Mock()
        row.campaign.name = "Test Campaign"
        mock_results.append(row)

    # Get the mocked GoogleAdsService from the fixture
    mock_google_ads_service = search_service.client  # type: ignore
    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    with patch(
        "src.sdk_services.metadata.search_service.serialize_proto_message",
        side_effect=[{"ad_group": f"data{i}"} for i in range(3)],
    ):
        # Act
        results = await search_service.search_ad_groups(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            include_removed=include_removed,
            limit=limit,
        )

    # Assert
    assert len(results) == 3

    # Verify the query
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert f"campaign.id = {campaign_id}" in request.query
    assert "ad_group.status != 'REMOVED'" in request.query
    assert "LIMIT 5" in request.query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 ad groups",
    )


@pytest.mark.asyncio
async def test_search_keywords(
    search_service: SearchService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching for keywords."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "444555666"
    include_negative = False
    limit = 20

    # Create mock search results
    mock_results = []
    for i in range(5):
        row = Mock()
        row.ad_group_criterion = Mock()
        row.ad_group_criterion.criterion_id = f"5000{i}"
        row.ad_group_criterion.keyword = Mock()
        row.ad_group_criterion.keyword.text = f"keyword {i}"
        row.ad_group_criterion.keyword.match_type = "EXACT"
        row.ad_group_criterion.status = "ENABLED"
        row.ad_group = Mock()
        row.ad_group.name = "Test Ad Group"
        row.campaign = Mock()
        row.campaign.name = "Test Campaign"
        mock_results.append(row)

    # Get the mocked GoogleAdsService from the fixture
    mock_google_ads_service = search_service.client  # type: ignore
    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    with patch(
        "src.sdk_services.metadata.search_service.serialize_proto_message",
        side_effect=[{"keyword": f"data{i}"} for i in range(5)],
    ):
        # Act
        results = await search_service.search_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            include_negative=include_negative,
            limit=limit,
        )

    # Assert
    assert len(results) == 5

    # Verify the query
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert f"ad_group.id = {ad_group_id}" in request.query
    # Since include_negative is False, we should only get positive keywords
    assert "ad_group_criterion.type = 'KEYWORD'" in request.query
    assert "LIMIT 20" in request.query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 5 keywords",
    )


@pytest.mark.asyncio
async def test_execute_query(
    search_service: SearchService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test executing a custom query."""
    # Arrange
    customer_id = "1234567890"
    query = """
        SELECT campaign.id, campaign.name, metrics.impressions
        FROM campaign
        WHERE segments.date DURING LAST_7_DAYS
    """

    # Create mock search results
    mock_results = []
    for i in range(2):
        row = Mock()
        row.campaign = Mock()
        row.campaign.id = f"1000{i}"
        row.campaign.name = f"Campaign {i}"
        row.metrics = Mock()
        row.metrics.impressions = 1000 * (i + 1)
        mock_results.append(row)

    # Get the mocked GoogleAdsService from the fixture
    mock_google_ads_service = search_service.client  # type: ignore
    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    with patch(
        "src.sdk_services.metadata.search_service.serialize_proto_message",
        side_effect=[{"row": f"data{i}"} for i in range(2)],
    ):
        # Act
        results = await search_service.execute_query(
            ctx=mock_ctx,
            customer_id=customer_id,
            query=query,
        )

    # Assert
    assert len(results) == 2

    # Verify the query
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.query.strip() == query.strip()

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Query returned 2 rows",
    )


@pytest.mark.asyncio
async def test_error_handling(
    search_service: SearchService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked GoogleAdsService from the fixture and make it raise exception
    mock_google_ads_service = search_service.client  # type: ignore
    mock_google_ads_service.search.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await search_service.search_campaigns(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    assert "Failed to search campaigns" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to search campaigns: Test Google Ads Exception",
    )


def test_register_search_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_search_tools(mock_mcp)

    # Assert
    assert isinstance(service, SearchService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "search_campaigns",
        "search_ad_groups",
        "search_keywords",
        "execute_query",
    ]

    assert set(tool_names) == set(expected_tools)
