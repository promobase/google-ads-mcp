"""Tests for Google Ads service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.summary_row_setting import (
    SummaryRowSettingEnum,
)
from google.ads.googleads.v20.services.types.google_ads_service import (
    GoogleAdsRow,
    MutateGoogleAdsResponse,
    MutateOperation,
    MutateOperationResponse,
    SearchGoogleAdsResponse,
    SearchGoogleAdsStreamResponse,
)

from src.sdk_services.metadata.google_ads_service import (
    GoogleAdsService,
    create_google_ads_tools,
)


@pytest.fixture
def google_ads_service():
    """Create a Google Ads service instance."""
    return GoogleAdsService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Google Ads service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestGoogleAdsService:
    """Test cases for GoogleAdsService."""

    async def test_search_success(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful search operation."""
        # Mock the client
        google_ads_service._client = mock_client

        # Create mock response
        mock_row = GoogleAdsRow()
        mock_row.campaign.id = 123  # type: ignore
        mock_row.campaign.name = "Test Campaign"  # type: ignore

        mock_response = SearchGoogleAdsResponse()
        mock_response.results.append(mock_row)  # type: ignore
        mock_response.next_page_token = "next_token_123"
        mock_response.total_results_count = 1
        mock_response.field_mask.paths.extend(["campaign.id", "campaign.name"])  # type: ignore

        mock_client.search.return_value = mock_response  # type: ignore

        # Execute search
        result = await google_ads_service.search(
            ctx=mock_context,
            customer_id="123-456-7890",
            query="SELECT campaign.id, campaign.name FROM campaign",
            page_size=100,
        )

        # Verify the request
        request = mock_client.search.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"
        assert request.query == "SELECT campaign.id, campaign.name FROM campaign"
        assert request.page_size == 100
        assert request.validate_only is False
        assert (
            request.summary_row_setting
            == SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW
        )

        # Verify the result
        assert len(result["results"]) == 1
        assert result["next_page_token"] == "next_token_123"
        assert result["total_results_count"] == 1
        assert result["field_mask"] == ["campaign.id", "campaign.name"]
        assert result["summary_row"] is None

    async def test_search_with_pagination(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test search with pagination token."""
        google_ads_service._client = mock_client

        mock_response = SearchGoogleAdsResponse()
        mock_response.next_page_token = "page2"
        mock_client.search.return_value = mock_response  # type: ignore

        await google_ads_service.search(
            ctx=mock_context,
            customer_id="1234567890",
            query="SELECT campaign.id FROM campaign",
            page_token="page1",
        )

        request = mock_client.search.call_args[1]["request"]  # type: ignore
        assert request.page_token == "page1"

    async def test_search_with_summary_row(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test search with summary row."""
        google_ads_service._client = mock_client

        # Create mock response with summary row
        mock_summary = GoogleAdsRow()
        mock_summary.metrics.clicks = 100  # type: ignore
        mock_summary.metrics.impressions = 1000  # type: ignore

        mock_response = SearchGoogleAdsResponse()
        mock_response.summary_row.CopyFrom(mock_summary)  # type: ignore
        mock_client.search.return_value = mock_response  # type: ignore

        result = await google_ads_service.search(
            ctx=mock_context,
            customer_id="1234567890",
            query="SELECT metrics.clicks FROM campaign",
            summary_row_setting=SummaryRowSettingEnum.SummaryRowSetting.SUMMARY_ROW_WITH_RESULTS,
        )

        assert result["summary_row"] is not None

    async def test_search_stream_success(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful search stream operation."""
        google_ads_service._client = mock_client

        # Create mock stream responses
        batch1 = SearchGoogleAdsStreamResponse()
        row1 = GoogleAdsRow()
        row1.campaign.id = 1
        batch1.results.append(row1)

        batch2 = SearchGoogleAdsStreamResponse()
        row2 = GoogleAdsRow()
        row2.campaign.id = 2
        batch2.results.append(row2)

        mock_client.search_stream.return_value = iter([batch1, batch2])  # type: ignore

        # Execute search stream
        results = await google_ads_service.search_stream(
            ctx=mock_context,
            customer_id="1234567890",
            query="SELECT campaign.id FROM campaign",
        )

        # Verify results
        assert len(results) == 2
        assert mock_context.log.call_count >= 1  # type: ignore

    async def test_search_stream_large_results(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test search stream with large result set."""
        google_ads_service._client = mock_client

        # Create mock responses with many rows
        batches = []
        for i in range(15):  # 15 batches
            batch = SearchGoogleAdsStreamResponse()
            for j in range(1000):  # 1000 rows per batch
                row = GoogleAdsRow()
                row.campaign.id = i * 1000 + j
                batch.results.append(row)
            batches.append(batch)

        mock_client.search_stream.return_value = iter(batches)  # type: ignore

        results = await google_ads_service.search_stream(
            ctx=mock_context,
            customer_id="1234567890",
            query="SELECT campaign.id FROM campaign",
        )

        assert len(results) == 15000
        # Should log progress at 10000
        progress_logs = [
            call
            for call in mock_context.log.call_args_list
            if "Processed" in str(call)  # type: ignore
        ]
        assert len(progress_logs) >= 1

    async def test_mutate_success(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful mutate operation."""
        google_ads_service._client = mock_client

        # Create mock operations
        operations = [
            MutateOperation(
                campaign_operation={
                    "create": {
                        "name": "New Campaign",
                        "campaign_budget": "customers/123/campaignBudgets/456",
                    }
                }
            )
        ]

        # Create mock response
        mock_response = MutateGoogleAdsResponse()
        result = MutateOperationResponse()
        result.campaign_result.resource_name = "customers/123/campaigns/789"
        mock_response.mutate_operation_responses.append(result)  # type: ignore

        mock_client.mutate.return_value = mock_response  # type: ignore

        # Execute mutate
        result = await google_ads_service.mutate(
            ctx=mock_context,
            customer_id="1234567890",
            operations=operations,
            partial_failure=True,
        )

        # Verify request
        request = mock_client.mutate.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"
        assert len(request.mutate_operations) == 1
        assert request.partial_failure is True
        assert request.validate_only is False
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

        # Verify result
        assert len(result["results"]) == 1
        assert result["partial_failure_error"] is None

    async def test_search_api_error(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test search with API error."""
        google_ads_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()  # type: ignore
        error.failure.__str__ = Mock(return_value="Invalid query")  # type: ignore
        mock_client.search.side_effect = error  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await google_ads_service.search(
                ctx=mock_context,
                customer_id="1234567890",
                query="INVALID QUERY",
            )

        assert "Google Ads API error: Invalid query" in str(exc_info.value)
        mock_context.log.assert_called_with(  # type: ignore
            level="error", message="Google Ads API error: Invalid query"
        )

    async def test_search_general_error(
        self, google_ads_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test search with general error."""
        google_ads_service._client = mock_client
        mock_client.search.side_effect = Exception("Network error")  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await google_ads_service.search(
                ctx=mock_context,
                customer_id="1234567890",
                query="SELECT campaign.id FROM campaign",
            )

        assert "Failed to execute search: Network error" in str(exc_info.value)


@pytest.mark.asyncio
class TestGoogleAdsTools:
    """Test cases for Google Ads tool functions."""

    async def test_search_google_ads_tool(self, mock_context: Any):
        """Test search_google_ads tool function."""
        service = GoogleAdsService()
        tools = create_google_ads_tools(service)
        search_tool = tools[0]  # First tool is search_google_ads

        # Mock the service method
        with patch.object(service, "search") as mock_search:
            mock_search.return_value = {"results": [], "next_page_token": ""}  # type: ignore

            await search_tool(
                ctx=mock_context,
                customer_id="1234567890",
                query="SELECT campaign.id FROM campaign",
                include_summary_row=True,
            )

            mock_search.assert_called_once()  # type: ignore
            call_args = mock_search.call_args[1]  # type: ignore
            assert call_args["customer_id"] == "1234567890"
            assert (
                call_args["summary_row_setting"]
                == SummaryRowSettingEnum.SummaryRowSetting.SUMMARY_ROW_WITH_RESULTS
            )

    async def test_search_google_ads_stream_tool(self, mock_context: Any):
        """Test search_google_ads_stream tool function."""
        service = GoogleAdsService()
        tools = create_google_ads_tools(service)
        stream_tool = tools[1]  # Second tool is search_google_ads_stream

        # Mock the service method
        with patch.object(service, "search_stream") as mock_stream:
            mock_stream.return_value = []  # type: ignore

            await stream_tool(
                ctx=mock_context,
                customer_id="1234567890",
                query="SELECT campaign.id FROM campaign",
                include_summary_row=False,
            )

            mock_stream.assert_called_once()  # type: ignore
            call_args = mock_stream.call_args[1]  # type: ignore
            assert call_args["customer_id"] == "1234567890"
            assert (
                call_args["summary_row_setting"]
                == SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW
            )
