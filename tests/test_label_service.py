"""Tests for LabelService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.label_status import LabelStatusEnum
from google.ads.googleads.v20.services.services.label_service import (
    LabelServiceClient,
)
from google.ads.googleads.v20.services.types.label_service import (
    MutateLabelsResponse,
)

from src.sdk_services.shared.label_service import (
    LabelService,
    register_label_tools,
)


@pytest.fixture
def label_service(mock_sdk_client: Any) -> LabelService:
    """Create a LabelService instance with mocked dependencies."""
    # Mock LabelService client
    mock_label_service_client = Mock(spec=LabelServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_label_service_client  # type: ignore

    with patch(
        "src.sdk_services.shared.label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = LabelService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_label(
    label_service: LabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a label."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Label"
    description = "This is a test label"
    background_color = "#FF0000"

    # Create mock response
    mock_response = Mock(spec=MutateLabelsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/labels/123"

    # Get the mocked label service client
    mock_label_service_client = label_service.client  # type: ignore
    mock_label_service_client.mutate_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/labels/123"}]
    }

    with patch(
        "src.sdk_services.shared.label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await label_service.create_label(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            background_color=background_color,
            status=LabelStatusEnum.LabelStatus.ENABLED,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_label_service_client.mutate_labels.assert_called_once()  # type: ignore
    call_args = mock_label_service_client.mutate_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.status == LabelStatusEnum.LabelStatus.ENABLED
    assert operation.create.text_label.description == description
    assert operation.create.text_label.background_color == background_color

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created label '{name}'",
    )


@pytest.mark.asyncio
async def test_create_label_minimal(
    label_service: LabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a label with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    name = "Minimal Label"

    # Create mock response
    mock_response = Mock(spec=MutateLabelsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/labels/124"

    # Get the mocked label service client
    mock_label_service_client = label_service.client  # type: ignore
    mock_label_service_client.mutate_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/labels/124"}]
    }

    with patch(
        "src.sdk_services.shared.label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await label_service.create_label(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_label_service_client.mutate_labels.assert_called_once()  # type: ignore
    call_args = mock_label_service_client.mutate_labels.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.status == LabelStatusEnum.LabelStatus.ENABLED  # Default


@pytest.mark.asyncio
async def test_update_label(
    label_service: LabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a label."""
    # Arrange
    customer_id = "1234567890"
    label_id = "123"
    new_name = "Updated Label"
    new_description = "Updated description"
    new_status = LabelStatusEnum.LabelStatus.REMOVED

    # Create mock response
    mock_response = Mock(spec=MutateLabelsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/labels/{label_id}"

    # Get the mocked label service client
    mock_label_service_client = label_service.client  # type: ignore
    mock_label_service_client.mutate_labels.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/labels/{label_id}"}]
    }

    with patch(
        "src.sdk_services.shared.label_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await label_service.update_label(
            ctx=mock_ctx,
            customer_id=customer_id,
            label_id=label_id,
            name=new_name,
            description=new_description,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_label_service_client.mutate_labels.assert_called_once()  # type: ignore
    call_args = mock_label_service_client.mutate_labels.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name == f"customers/{customer_id}/labels/{label_id}"
    )
    assert operation.update.name == new_name
    assert operation.update.status == new_status
    assert operation.update.text_label.description == new_description
    assert "name" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths
    assert "text_label.description" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated label {label_id}",
    )


@pytest.mark.asyncio
async def test_list_labels(
    label_service: LabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing labels."""
    # Arrange
    customer_id = "1234567890"
    status_filter = "ENABLED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock()

    # Create mock search results
    mock_results = []
    for _ in range(3):
        row = Mock()
        # Mock serialize_proto_message to return dict
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return label_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with (
        patch(
            "src.sdk_services.shared.label_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.shared.label_service.serialize_proto_message",
            side_effect=[
                {"label": {"id": f"100{i}", "name": f"Label {i}", "status": "ENABLED"}}
                for i in range(3)
            ],
        ),
    ):
        result = await label_service.list_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    # Assert
    assert len(result) == 3

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"WHERE label.status = '{status_filter}'" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 labels",
    )


@pytest.mark.asyncio
async def test_error_handling(
    label_service: LabelService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked label service client and make it raise exception
    mock_label_service_client = label_service.client  # type: ignore
    mock_label_service_client.mutate_labels.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await label_service.create_label(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Label",
        )

    assert "Failed to create label" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create label: Test Google Ads Exception",
    )


def test_register_label_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_label_tools(mock_mcp)

    # Assert
    assert isinstance(service, LabelService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_label",
        "update_label",
        "list_labels",
        "apply_label_to_campaigns",
        "apply_label_to_ad_groups",
    ]

    assert set(tool_names) == set(expected_tools)
