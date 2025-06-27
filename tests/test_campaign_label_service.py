"""Tests for CampaignLabelService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.campaign_label_service import (
    CampaignLabelServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_label_service import (
    MutateCampaignLabelsResponse,
)

from src.sdk_services.campaign.campaign_label_service import (
    CampaignLabelService,
    register_campaign_label_tools,
)


@pytest.fixture
def campaign_label_service(mock_sdk_client: Any) -> CampaignLabelService:
    """Create a CampaignLabelService instance with mocked dependencies."""
    # Mock CampaignLabelService client
    mock_campaign_label_client = Mock(spec=CampaignLabelServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_label_client

    with patch(
        "src.sdk_services.campaign.campaign_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignLabelService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_apply_label_to_campaign(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test applying a label to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    label_id = "444555666"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignLabelsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        "customers/1234567890/campaignLabels/111222333~444555666"
    )
    mock_response.results = [mock_result]

    # Get the mocked campaign label service client
    mock_campaign_label_client = campaign_label_service.client  # type: ignore
    mock_campaign_label_client.mutate_campaign_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/campaignLabels/111222333~444555666"}
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_label_service.apply_label_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_label_client.mutate_campaign_labels.assert_called_once()  # type: ignore
    call_args = mock_campaign_label_client.mutate_campaign_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert operation.create.label == f"customers/{customer_id}/labels/{label_id}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Applied label {label_id} to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_apply_labels_to_campaigns(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test applying labels to multiple campaigns."""
    # Arrange
    customer_id = "1234567890"
    campaign_label_pairs = [
        {"campaign_id": "111222333", "label_id": "444555666"},
        {"campaign_id": "999888777", "label_id": "444555666"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignLabelsResponse)
    mock_results = []
    for pair in campaign_label_pairs:
        mock_result = Mock()
        mock_result.resource_name = f"customers/{customer_id}/campaignLabels/{pair['campaign_id']}~{pair['label_id']}"
        mock_results.append(mock_result)
    mock_response.results = mock_results

    # Get the mocked campaign label service client
    mock_campaign_label_client = campaign_label_service.client  # type: ignore
    mock_campaign_label_client.mutate_campaign_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    # The service returns individual results for each pair
    expected_result = [
        {
            "resource_name": f"customers/{customer_id}/campaignLabels/{pair['campaign_id']}~{pair['label_id']}",
            "campaign_id": pair["campaign_id"],
            "label_id": pair["label_id"],
        }
        for pair in campaign_label_pairs
    ]

    # Act
    result = await campaign_label_service.apply_labels_to_campaigns(
        ctx=mock_ctx,
        customer_id=customer_id,
        campaign_label_pairs=campaign_label_pairs,
    )

    # Assert
    assert len(result) == 2
    assert result[0]["campaign_id"] == "111222333"
    assert result[0]["label_id"] == "444555666"
    assert result[1]["campaign_id"] == "999888777"

    # Verify the API call - single call with multiple operations
    mock_campaign_label_client.mutate_campaign_labels.assert_called_once()  # type: ignore
    call_args = mock_campaign_label_client.mutate_campaign_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 2  # Two operations in one call

    # Verify both operations
    for i, pair in enumerate(campaign_label_pairs):
        operation = request.operations[i]
        assert (
            operation.create.campaign
            == f"customers/{customer_id}/campaigns/{pair['campaign_id']}"
        )
        assert (
            operation.create.label
            == f"customers/{customer_id}/labels/{pair['label_id']}"
        )


@pytest.mark.asyncio
async def test_list_campaign_labels(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing labels for a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    label_info = [
        {"id": "444555666", "name": "Spring Sale", "color": "#FF0000"},
        {"id": "777888999", "name": "High Priority", "color": "#00FF00"},
    ]

    for info in label_info:
        row = Mock()
        row.campaign_label = Mock()
        row.campaign_label.resource_name = (
            f"customers/{customer_id}/campaignLabels/{campaign_id}~{info['id']}"
        )
        row.campaign_label.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        row.campaign_label.label = f"customers/{customer_id}/labels/{info['id']}"

        row.label = Mock()
        row.label.resource_name = f"customers/{customer_id}/labels/{info['id']}"
        row.label.id = info["id"]
        row.label.name = info["name"]
        row.label.text_label = Mock()
        row.label.text_label.background_color = info["color"]

        row.campaign = Mock()
        row.campaign.id = campaign_id
        row.campaign.name = "Test Campaign"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_label_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.campaign.campaign_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_label_service.list_campaign_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    # Assert
    assert len(result) == 2

    # Check first label
    assert result[0]["campaign_id"] == campaign_id
    assert result[0]["campaign_name"] == "Test Campaign"
    assert result[0]["label_id"] == "444555666"
    assert result[0]["label_name"] == "Spring Sale"
    assert result[0]["background_color"] == "#FF0000"

    # Check second label
    assert result[1]["label_id"] == "777888999"
    assert result[1]["label_name"] == "High Priority"
    assert result[1]["background_color"] == "#00FF00"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert "FROM campaign_label" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 campaign labels",
    )


@pytest.mark.asyncio
async def test_remove_label_from_campaign(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a label from a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    label_id = "444555666"
    resource_name = f"customers/{customer_id}/campaignLabels/{campaign_id}~{label_id}"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignLabelsResponse)
    mock_result = Mock()
    mock_result.resource_name = resource_name
    mock_response.results = [mock_result]

    # Get the mocked campaign label service client
    mock_campaign_label_client = campaign_label_service.client  # type: ignore
    mock_campaign_label_client.mutate_campaign_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": resource_name}]}

    with patch(
        "src.sdk_services.campaign.campaign_label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_label_service.remove_label_from_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_label_client.mutate_campaign_labels.assert_called_once()  # type: ignore
    call_args = mock_campaign_label_client.mutate_campaign_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed label {label_id} from campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_error_handling_apply_label(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when applying label fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    label_id = "444555666"

    # Get the mocked campaign label service client and make it raise exception
    mock_campaign_label_client = campaign_label_service.client  # type: ignore
    mock_campaign_label_client.mutate_campaign_labels.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_label_service.apply_label_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    assert "Failed to apply label to campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to apply label to campaign: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_labels(
    campaign_label_service: CampaignLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing labels fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_label_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.campaign.campaign_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await campaign_label_service.list_campaign_labels(
                ctx=mock_ctx,
                customer_id=customer_id,
                campaign_id=campaign_id,
            )

    assert "Failed to list campaign labels" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list campaign labels: Search failed",
    )


def test_register_campaign_label_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_label_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignLabelService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "apply_label_to_campaign",
        "apply_labels_to_campaigns",
        "list_campaign_labels",
        "remove_label_from_campaign",
    ]

    assert set(tool_names) == set(expected_tools)
