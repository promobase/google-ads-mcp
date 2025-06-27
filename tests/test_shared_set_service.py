"""Tests for SharedSetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.shared_set_status import SharedSetStatusEnum
from google.ads.googleads.v20.enums.types.shared_set_type import SharedSetTypeEnum
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.services.shared_set_service import (
    SharedSetServiceClient,
)
from google.ads.googleads.v20.services.types.shared_set_service import (
    MutateSharedSetsResponse,
)

from src.sdk_services.shared.shared_set_service import (
    SharedSetService,
    register_shared_set_tools,
)


@pytest.fixture
def shared_set_service(mock_sdk_client: Any) -> SharedSetService:
    """Create a SharedSetService instance with mocked dependencies."""
    # Mock SharedSetService client
    mock_shared_set_client = Mock(spec=SharedSetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_shared_set_client  # type: ignore

    with patch(
        "src.sdk_services.shared.shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = SharedSetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_shared_set(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a shared set."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Negative Keywords"
    type_enum = SharedSetTypeEnum.SharedSetType.NEGATIVE_KEYWORDS
    status_enum = SharedSetStatusEnum.SharedSetStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateSharedSetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/sharedSets/123456"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked shared set service client
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/sharedSets/123456"}]
    }

    with patch(
        "src.sdk_services.shared.shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await shared_set_service.create_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            type=type_enum,
            status=status_enum,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    shared_set = operation.create
    assert shared_set.name == name
    assert shared_set.type_ == type_enum
    assert shared_set.status == status_enum

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created shared set '{name}' ({type_enum})",
    )


@pytest.mark.asyncio
async def test_create_shared_set_negative_placements(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a shared set for negative placements."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Negative Placements"
    type_enum = SharedSetTypeEnum.SharedSetType.NEGATIVE_PLACEMENTS
    status_enum = SharedSetStatusEnum.SharedSetStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateSharedSetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/sharedSets/654321"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked shared set service client
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/sharedSets/654321"}]
    }

    with patch(
        "src.sdk_services.shared.shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await shared_set_service.create_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            type=type_enum,
            status=status_enum,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_shared_set_client.mutate_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    shared_set = operation.create
    assert shared_set.name == name
    assert shared_set.type_ == type_enum
    assert shared_set.status == status_enum


@pytest.mark.asyncio
async def test_update_shared_set_name_only(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating shared set name only."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "123456"
    new_name = "Updated Negative Keywords List"

    # Create mock response
    mock_response = Mock(spec=MutateSharedSetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/sharedSets/{shared_set_id}"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked shared set service client
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/sharedSets/{shared_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.shared.shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await shared_set_service.update_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            name=new_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_shared_set_client.mutate_shared_sets.assert_called_once()  # type: ignore
    call_args = mock_shared_set_client.mutate_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    shared_set = operation.update
    assert (
        shared_set.resource_name
        == f"customers/{customer_id}/sharedSets/{shared_set_id}"
    )
    assert shared_set.name == new_name
    assert "name" in operation.update_mask.paths
    assert "status" not in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated shared set {shared_set_id}",
    )


@pytest.mark.asyncio
async def test_update_shared_set_status_only(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating shared set status only."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "123456"
    new_status = SharedSetStatusEnum.SharedSetStatus.REMOVED

    # Create mock response
    mock_response = Mock(spec=MutateSharedSetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/sharedSets/{shared_set_id}"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked shared set service client
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/sharedSets/{shared_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.shared.shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await shared_set_service.update_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_shared_set_client.mutate_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    shared_set = operation.update
    assert (
        shared_set.resource_name
        == f"customers/{customer_id}/sharedSets/{shared_set_id}"
    )
    assert shared_set.status == new_status
    assert "status" in operation.update_mask.paths
    assert "name" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_update_shared_set_both_fields(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating both name and status of shared set."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "123456"
    new_name = "Updated List"
    new_status = SharedSetStatusEnum.SharedSetStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateSharedSetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/sharedSets/{shared_set_id}"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked shared set service client
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/sharedSets/{shared_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.shared.shared_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await shared_set_service.update_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            name=new_name,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_shared_set_client.mutate_shared_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    shared_set = operation.update
    assert (
        shared_set.resource_name
        == f"customers/{customer_id}/sharedSets/{shared_set_id}"
    )
    assert shared_set.name == new_name
    assert shared_set.status == new_status
    assert "name" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_list_shared_sets_no_filters(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing shared sets without filters."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.shared_set = Mock()
        row.shared_set.id = f"{i + 100}"
        row.shared_set.name = f"Shared Set {i}"
        row.shared_set.type = Mock()
        row.shared_set.type.name = "NEGATIVE_KEYWORDS"
        row.shared_set.member_count = i + 5
        row.shared_set.reference_count = i + 2
        row.shared_set.status = Mock()
        row.shared_set.status.name = "ENABLED"
        row.shared_set.resource_name = f"customers/{customer_id}/sharedSets/{i + 100}"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message for each row
    def serialize_side_effect(obj: Any):
        return {
            "shared_set": {
                "id": obj.shared_set.id,
                "name": obj.shared_set.name,
                "type": obj.shared_set.type.name,
                "member_count": obj.shared_set.member_count,
                "reference_count": obj.shared_set.reference_count,
                "status": obj.shared_set.status.name,
                "resource_name": obj.shared_set.resource_name,
            }
        }

    with (
        patch(
            "src.sdk_services.shared.shared_set_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.shared.shared_set_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await shared_set_service.list_shared_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert first_result["shared_set"]["id"] == "100"
    assert first_result["shared_set"]["name"] == "Shared Set 0"
    assert first_result["shared_set"]["type"] == "NEGATIVE_KEYWORDS"
    assert first_result["shared_set"]["member_count"] == 5
    assert first_result["shared_set"]["reference_count"] == 2
    assert first_result["shared_set"]["status"] == "ENABLED"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    # Should not have WHERE clause
    assert "WHERE" not in query
    assert "ORDER BY shared_set.name" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 shared sets",
    )


@pytest.mark.asyncio
async def test_list_shared_sets_with_filters(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing shared sets with type and status filters."""
    # Arrange
    customer_id = "1234567890"
    type_filter = "NEGATIVE_KEYWORDS"
    status_filter = "ENABLED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.shared.shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await shared_set_service.list_shared_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            type_filter=type_filter,
            status_filter=status_filter,
        )

    # Assert
    assert len(result) == 0

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    # Should have WHERE clause with both filters
    assert "WHERE" in query
    assert f"shared_set.type = '{type_filter}'" in query
    assert f"shared_set.status = '{status_filter}'" in query
    assert "AND" in query


@pytest.mark.asyncio
async def test_list_shared_sets_type_filter_only(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing shared sets with type filter only."""
    # Arrange
    customer_id = "1234567890"
    type_filter = "NEGATIVE_PLACEMENTS"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.shared.shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await shared_set_service.list_shared_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            type_filter=type_filter,
        )

    # Assert
    assert len(result) == 0

    # Verify the search call
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    # Should have WHERE clause with type filter only
    assert "WHERE" in query
    assert f"shared_set.type = '{type_filter}'" in query
    assert "shared_set.status =" not in query


@pytest.mark.asyncio
async def test_attach_shared_set_to_campaigns_not_implemented(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test that attach_shared_set_to_campaigns raises NotImplementedError."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "123456"
    campaign_ids = ["111", "222"]

    # Mock the get_sdk_client call within the method
    with patch(
        "src.sdk_services.shared.shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await shared_set_service.attach_shared_set_to_campaigns(
                ctx=mock_ctx,
                customer_id=customer_id,
                shared_set_id=shared_set_id,
                campaign_ids=campaign_ids,
            )

        # The NotImplementedError gets wrapped, so check that the method failed appropriately
        assert "Failed to attach shared set to campaigns" in str(exc_info.value)


@pytest.mark.asyncio
async def test_error_handling_create_shared_set(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating shared set fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test List"

    # Get the mocked shared set service client and make it raise exception
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await shared_set_service.create_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    assert "Failed to create shared set" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create shared set: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_shared_set(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating shared set fails."""
    # Arrange
    customer_id = "1234567890"
    shared_set_id = "123456"

    # Get the mocked shared set service client and make it raise exception
    mock_shared_set_client = shared_set_service.client  # type: ignore
    mock_shared_set_client.mutate_shared_sets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await shared_set_service.update_shared_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            name="New Name",
        )

    assert "Failed to update shared set" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update shared set: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_shared_sets(
    shared_set_service: SharedSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing shared sets fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return shared_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.shared.shared_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await shared_set_service.list_shared_sets(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list shared sets" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list shared sets: Search failed",
    )


def test_register_shared_set_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_shared_set_tools(mock_mcp)

    # Assert
    assert isinstance(service, SharedSetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_shared_set",
        "update_shared_set",
        "list_shared_sets",
        "attach_shared_set_to_campaigns",
    ]

    assert set(tool_names) == set(expected_tools)
