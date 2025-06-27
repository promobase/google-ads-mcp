"""Tests for AdGroupLabelService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.label_status import LabelStatusEnum
from google.ads.googleads.v20.services.services.ad_group_label_service import (
    AdGroupLabelServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_label_service import (
    MutateAdGroupLabelsResponse,
)

from src.sdk_services.ad_group.ad_group_label_service import (
    AdGroupLabelService,
    register_ad_group_label_tools,
)


@pytest.fixture
def ad_group_label_service(mock_sdk_client: Any) -> AdGroupLabelService:
    """Create an AdGroupLabelService instance with mocked dependencies."""
    # Mock AdGroupLabelService client
    mock_ad_group_label_client = Mock(spec=AdGroupLabelServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_label_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupLabelService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_apply_label_to_ad_group(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test applying a label to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    label_id = "999"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupLabelsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked ad group label service client
    mock_ad_group_label_client = ad_group_label_service.client  # type: ignore
    mock_ad_group_label_client.mutate_ad_group_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_label_service.apply_label_to_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_label_client.mutate_ad_group_labels.assert_called_once()  # type: ignore
    call_args = mock_ad_group_label_client.mutate_ad_group_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.label == f"customers/{customer_id}/labels/{label_id}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Applied label {label_id} to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_apply_labels_to_ad_groups(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test applying labels to multiple ad groups."""
    # Arrange
    customer_id = "1234567890"
    ad_group_label_pairs = [
        {"ad_group_id": "111", "label_id": "100"},
        {"ad_group_id": "222", "label_id": "100"},
        {"ad_group_id": "333", "label_id": "200"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupLabelsResponse)
    mock_results = []
    for pair in ad_group_label_pairs:
        mock_result = Mock()
        mock_result.resource_name = f"customers/{customer_id}/adGroupLabels/{pair['ad_group_id']}~{pair['label_id']}"
        mock_results.append(mock_result)
    mock_response.results = mock_results

    # Get the mocked ad group label service client
    mock_ad_group_label_client = ad_group_label_service.client  # type: ignore
    mock_ad_group_label_client.mutate_ad_group_labels.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_label_service.apply_labels_to_ad_groups(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_label_pairs=ad_group_label_pairs,
    )

    # Assert
    assert len(result) == 3
    assert result[0]["ad_group_id"] == "111"
    assert result[0]["label_id"] == "100"
    assert result[1]["ad_group_id"] == "222"
    assert result[1]["label_id"] == "100"
    assert result[2]["ad_group_id"] == "333"
    assert result[2]["label_id"] == "200"

    # Verify the API call
    mock_ad_group_label_client.mutate_ad_group_labels.assert_called_once()  # type: ignore
    call_args = mock_ad_group_label_client.mutate_ad_group_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Verify each operation
    for i, operation in enumerate(request.operations):
        pair = ad_group_label_pairs[i]
        assert (
            operation.create.ad_group
            == f"customers/{customer_id}/adGroups/{pair['ad_group_id']}"
        )
        assert (
            operation.create.label
            == f"customers/{customer_id}/labels/{pair['label_id']}"
        )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Applied 3 labels to ad groups",
    )


@pytest.mark.asyncio
async def test_remove_label_from_ad_group(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a label from an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    label_id = "999"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupLabelsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked ad group label service client
    mock_ad_group_label_client = ad_group_label_service.client  # type: ignore
    mock_ad_group_label_client.mutate_ad_group_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_label_service.remove_label_from_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            label_id=label_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_label_client.mutate_ad_group_labels.assert_called_once()  # type: ignore
    call_args = mock_ad_group_label_client.mutate_ad_group_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.remove
        == f"customers/{customer_id}/adGroupLabels/{ad_group_id}~{label_id}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed label {label_id} from ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_list_ad_group_labels(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group labels."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    label_info = [
        {
            "ad_group_id": "111",
            "ad_group_name": "Test Ad Group 1",
            "label_id": "100",
            "label_name": "Summer Sale",
            "label_status": LabelStatusEnum.LabelStatus.ENABLED,
            "background_color": "#FF0000",
            "description": "Summer campaign label",
        },
        {
            "ad_group_id": "111",
            "ad_group_name": "Test Ad Group 1",
            "label_id": "200",
            "label_name": "High Priority",
            "label_status": LabelStatusEnum.LabelStatus.ENABLED,
            "background_color": "#0000FF",
            "description": "High priority ad groups",
        },
    ]

    for info in label_info:
        row = Mock()
        # Mock ad group label
        row.ad_group_label = Mock()
        row.ad_group_label.resource_name = f"customers/{customer_id}/adGroupLabels/{info['ad_group_id']}~{info['label_id']}"
        row.ad_group_label.ad_group = (
            f"customers/{customer_id}/adGroups/{info['ad_group_id']}"
        )
        row.ad_group_label.label = f"customers/{customer_id}/labels/{info['label_id']}"

        # Mock ad group
        row.ad_group = Mock()
        row.ad_group.id = info["ad_group_id"]
        row.ad_group.name = info["ad_group_name"]
        row.ad_group.campaign = "customers/1234567890/campaigns/222"

        # Mock campaign
        row.campaign = Mock()
        row.campaign.id = "222"
        row.campaign.name = "Test Campaign"

        # Mock label
        row.label = Mock()
        row.label.id = info["label_id"]
        row.label.name = info["label_name"]
        row.label.status = info["label_status"]
        row.label.text_label = Mock()
        row.label.text_label.background_color = info["background_color"]
        row.label.text_label.description = info["description"]

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_label_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_label_service.list_ad_group_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
        )

    # Assert
    assert len(result) == 2
    assert result[0]["ad_group_id"] == "111"
    assert result[0]["label_id"] == "100"
    assert result[0]["label_name"] == "Summer Sale"
    assert result[0]["label_status"] == "ENABLED"
    assert result[0]["background_color"] == "#FF0000"
    assert result[0]["description"] == "Summer campaign label"

    assert result[1]["label_id"] == "200"
    assert result[1]["label_name"] == "High Priority"
    assert result[1]["background_color"] == "#0000FF"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"ad_group.id = {ad_group_id}" in query
    assert "FROM ad_group_label" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 ad group labels",
    )


@pytest.mark.asyncio
async def test_list_ad_group_labels_with_filters(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group labels with multiple filters."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "222"
    label_id = "100"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_label_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_label_service.list_ad_group_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            label_id=label_id,
        )

    # Assert
    assert result == []

    # Verify the search call with filters
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert f"label.id = {label_id}" in query


@pytest.mark.asyncio
async def test_error_handling(
    ad_group_label_service: AdGroupLabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked ad group label service client and make it raise exception
    mock_ad_group_label_client = ad_group_label_service.client  # type: ignore
    mock_ad_group_label_client.mutate_ad_group_labels.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_label_service.apply_label_to_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id="111",
            label_id="999",
        )

    assert "Failed to apply label to ad group" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to apply label to ad group: Test Google Ads Exception",
    )


def test_register_ad_group_label_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_label_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupLabelService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "apply_label_to_ad_group",
        "apply_labels_to_ad_groups",
        "remove_label_from_ad_group",
        "list_ad_group_labels",
    ]

    assert set(tool_names) == set(expected_tools)
