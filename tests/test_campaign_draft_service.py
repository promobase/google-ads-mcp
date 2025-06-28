"""Tests for CampaignDraftService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.campaign_draft_service import (
    CampaignDraftServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_draft_service import (
    MutateCampaignDraftsResponse,
)
from google.ads.googleads.v20.enums.types.campaign_draft_status import (
    CampaignDraftStatusEnum,
)

from src.services.campaign.campaign_draft_service import (
    CampaignDraftService,
    register_campaign_draft_tools,
)


@pytest.fixture
def campaign_draft_service(mock_sdk_client: Any) -> CampaignDraftService:
    """Create a CampaignDraftService instance with mocked dependencies."""
    # Mock CampaignDraftService client
    mock_draft_client = Mock(spec=CampaignDraftServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_draft_client  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_draft_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignDraftService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_campaign_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign draft."""
    # Arrange
    customer_id = "1234567890"
    base_campaign = "customers/1234567890/campaigns/111222333"
    draft_name = "Test Campaign Draft"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignDraftsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaignDrafts/444555666"
    mock_result.campaign_draft = (
        "customers/1234567890/campaignDrafts/111222333~444555666"
    )
    mock_response.results = [mock_result]

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.mutate_campaign_drafts.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": "customers/1234567890/campaignDrafts/444555666",
                "campaign_draft": "customers/1234567890/campaignDrafts/111222333~444555666",
            }
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_draft_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_draft_service.create_campaign_draft(
            ctx=mock_ctx,
            customer_id=customer_id,
            base_campaign=base_campaign,
            draft_name=draft_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_draft_client.mutate_campaign_drafts.assert_called_once()  # type: ignore
    call_args = mock_draft_client.mutate_campaign_drafts.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.base_campaign == base_campaign
    assert operation.create.name == draft_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created campaign draft: {draft_name}",
    )


@pytest.mark.asyncio
async def test_update_campaign_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign draft."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"
    draft_name = "Updated Draft Name"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignDraftsResponse)
    mock_result = Mock()
    mock_result.resource_name = draft_resource_name
    mock_response.results = [mock_result]

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.mutate_campaign_drafts.return_value = mock_response  # type: ignore

    # Act
    result = await campaign_draft_service.update_campaign_draft(
        ctx=mock_ctx,
        customer_id=customer_id,
        draft_resource_name=draft_resource_name,
        draft_name=draft_name,
    )

    # Assert
    assert result["resource_name"] == draft_resource_name
    assert result["updated_fields"] == ["name"]

    # Verify the API call
    mock_draft_client.mutate_campaign_drafts.assert_called_once()  # type: ignore
    call_args = mock_draft_client.mutate_campaign_drafts.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.update.resource_name == draft_resource_name
    assert operation.update.name == draft_name
    assert "name" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Updated campaign draft",
    )


@pytest.mark.asyncio
async def test_list_campaign_drafts(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign drafts."""
    # Arrange
    customer_id = "1234567890"
    base_campaign_filter = "customers/1234567890/campaigns/111222333"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    draft_info = [
        {
            "draft_id": "444555666",
            "name": "Test Draft 1",
            "status": CampaignDraftStatusEnum.CampaignDraftStatus.PROPOSED,
            "has_experiment": False,
        },
        {
            "draft_id": "777888999",
            "name": "Test Draft 2",
            "status": CampaignDraftStatusEnum.CampaignDraftStatus.PROMOTING,
            "has_experiment": True,
        },
    ]

    for info in draft_info:
        row = Mock()
        row.campaign_draft = Mock()
        row.campaign_draft.resource_name = (
            f"customers/{customer_id}/campaignDrafts/{info['draft_id']}"
        )
        row.campaign_draft.draft_id = info["draft_id"]
        row.campaign_draft.base_campaign = base_campaign_filter
        row.campaign_draft.name = info["name"]
        row.campaign_draft.draft_campaign = (
            f"customers/{customer_id}/campaigns/{info['draft_id']}"
        )
        row.campaign_draft.status = info["status"]
        row.campaign_draft.has_experiment_running = info["has_experiment"]
        row.campaign_draft.long_running_operation = (
            "operations/12345"
            if info["status"] == CampaignDraftStatusEnum.CampaignDraftStatus.PROMOTING
            else ""
        )
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_draft_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_draft_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_draft_service.list_campaign_drafts(
            ctx=mock_ctx,
            customer_id=customer_id,
            base_campaign_filter=base_campaign_filter,
        )

    # Assert
    assert len(result) == 2

    # Check first draft
    assert result[0]["draft_id"] == "444555666"
    assert result[0]["name"] == "Test Draft 1"
    assert result[0]["status"] == "PROPOSED"
    assert result[0]["has_experiment_running"] is False

    # Check second draft
    assert result[1]["draft_id"] == "777888999"
    assert result[1]["name"] == "Test Draft 2"
    assert result[1]["status"] == "PROMOTING"
    assert result[1]["has_experiment_running"] is True
    assert result[1]["long_running_operation"] == "operations/12345"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign_draft.base_campaign = '{base_campaign_filter}'" in query
    assert "FROM campaign_draft" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 campaign drafts",
    )


@pytest.mark.asyncio
async def test_promote_campaign_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test promoting a campaign draft."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"

    # Create mock long running operation
    class MockOperation:
        def __str__(self):
            return "operations/promote_12345"

    mock_operation = MockOperation()

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.promote_campaign_draft.return_value = mock_operation  # type: ignore

    # Act
    result = await campaign_draft_service.promote_campaign_draft(
        ctx=mock_ctx,
        customer_id=customer_id,
        draft_resource_name=draft_resource_name,
    )

    # Assert
    assert result["draft_resource_name"] == draft_resource_name
    assert result["long_running_operation"] == "operations/promote_12345"
    assert result["status"] == "PROMOTING"

    # Verify the API call
    mock_draft_client.promote_campaign_draft.assert_called_once()  # type: ignore
    call_args = mock_draft_client.promote_campaign_draft.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.campaign_draft == draft_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Started campaign draft promotion",
    )


@pytest.mark.asyncio
async def test_list_campaign_draft_async_errors(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign draft async errors."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"

    # Create mock error pages
    class MockErrorPage1:
        def __str__(self):
            return "Error 1: Invalid bid strategy"

    class MockErrorPage2:
        def __str__(self):
            return "Error 2: Budget constraint violation"

    mock_error_page1 = MockErrorPage1()
    mock_error_page2 = MockErrorPage2()

    # Create mock response that iterates over pages
    mock_response = [mock_error_page1, mock_error_page2]

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.list_campaign_draft_async_errors.return_value = mock_response  # type: ignore

    # Act
    result = await campaign_draft_service.list_campaign_draft_async_errors(
        ctx=mock_ctx,
        customer_id=customer_id,
        draft_resource_name=draft_resource_name,
    )

    # Assert
    assert len(result) == 2
    assert result[0]["error"] == "Error 1: Invalid bid strategy"
    assert result[0]["type"] == "async_error"
    assert result[1]["error"] == "Error 2: Budget constraint violation"

    # Verify the API call
    mock_draft_client.list_campaign_draft_async_errors.assert_called_once()  # type: ignore
    call_args = mock_draft_client.list_campaign_draft_async_errors.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == draft_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 async errors for campaign draft",
    )


@pytest.mark.asyncio
async def test_list_campaign_draft_async_errors_empty(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign draft async errors when iteration fails."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"

    # Create mock response that fails on iteration
    mock_response = Mock()
    # Configure the mock to raise exception when iterated
    mock_response.__iter__ = Mock(side_effect=Exception("Iteration failed"))

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.list_campaign_draft_async_errors.return_value = mock_response  # type: ignore

    # Act
    result = await campaign_draft_service.list_campaign_draft_async_errors(
        ctx=mock_ctx,
        customer_id=customer_id,
        draft_resource_name=draft_resource_name,
    )

    # Assert - should return empty list when iteration fails
    assert result == []

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 0 async errors for campaign draft",
    )


@pytest.mark.asyncio
async def test_remove_campaign_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a campaign draft."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignDraftsResponse)
    mock_result = Mock()
    mock_result.resource_name = draft_resource_name
    mock_response.results = [mock_result]

    # Get the mocked draft service client
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.mutate_campaign_drafts.return_value = mock_response  # type: ignore

    # Act
    result = await campaign_draft_service.remove_campaign_draft(
        ctx=mock_ctx,
        customer_id=customer_id,
        draft_resource_name=draft_resource_name,
    )

    # Assert
    assert result["resource_name"] == draft_resource_name
    assert result["status"] == "REMOVED"

    # Verify the API call
    mock_draft_client.mutate_campaign_drafts.assert_called_once()  # type: ignore
    call_args = mock_draft_client.mutate_campaign_drafts.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == draft_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed campaign draft",
    )


@pytest.mark.asyncio
async def test_error_handling_create_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating campaign draft fails."""
    # Arrange
    customer_id = "1234567890"
    base_campaign = "customers/1234567890/campaigns/111222333"
    draft_name = "Test Campaign Draft"

    # Get the mocked draft service client and make it raise exception
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.mutate_campaign_drafts.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_draft_service.create_campaign_draft(
            ctx=mock_ctx,
            customer_id=customer_id,
            base_campaign=base_campaign,
            draft_name=draft_name,
        )

    assert "Failed to create campaign draft" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create campaign draft: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_promote_draft(
    campaign_draft_service: CampaignDraftService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when promoting campaign draft fails."""
    # Arrange
    customer_id = "1234567890"
    draft_resource_name = "customers/1234567890/campaignDrafts/444555666"

    # Get the mocked draft service client and make it raise exception
    mock_draft_client = campaign_draft_service.client  # type: ignore
    mock_draft_client.promote_campaign_draft.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_draft_service.promote_campaign_draft(
            ctx=mock_ctx,
            customer_id=customer_id,
            draft_resource_name=draft_resource_name,
        )

    assert "Failed to promote campaign draft" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to promote campaign draft: Test Google Ads Exception",
    )


def test_register_campaign_draft_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_draft_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignDraftService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 6  # 6 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_campaign_draft",
        "update_campaign_draft",
        "list_campaign_drafts",
        "promote_campaign_draft",
        "list_campaign_draft_async_errors",
        "remove_campaign_draft",
    ]

    assert set(tool_names) == set(expected_tools)
