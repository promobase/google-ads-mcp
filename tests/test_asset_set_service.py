"""Tests for AssetSetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.asset_set_status import AssetSetStatusEnum
from google.ads.googleads.v20.enums.types.asset_set_type import AssetSetTypeEnum
from google.ads.googleads.v20.services.services.asset_set_service import (
    AssetSetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.asset_set_service import (
    MutateAssetSetsResponse,
)

from src.sdk_services.assets.asset_set_service import (
    AssetSetService,
    register_asset_set_tools,
)


@pytest.fixture
def asset_set_service(mock_sdk_client: Any) -> AssetSetService:
    """Create an AssetSetService instance with mocked dependencies."""
    # Mock AssetSetService client
    mock_asset_set_client = Mock(spec=AssetSetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_asset_set_client  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AssetSetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_asset_set(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an asset set."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Asset Set"
    asset_set_type = AssetSetTypeEnum.AssetSetType.MERCHANT_CENTER_FEED
    status = AssetSetStatusEnum.AssetSetStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAssetSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetSets/123"
    mock_response.results = [mock_result]

    # Get the mocked asset set service client
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assetSets/123"}]
    }

    with patch(
        "src.sdk_services.assets.asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_set_service.create_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            asset_set_type=asset_set_type,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_set_client.mutate_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_asset_set_client.mutate_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == asset_set_type
    assert operation.create.status == status


@pytest.mark.asyncio
async def test_create_asset_set_dynamic_education(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic education asset set."""
    # Arrange
    customer_id = "1234567890"
    name = "Education Asset Set"
    asset_set_type = AssetSetTypeEnum.AssetSetType.DYNAMIC_EDUCATION

    # Create mock response
    mock_response = Mock(spec=MutateAssetSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetSets/456"
    mock_response.results = [mock_result]

    # Get the mocked asset set service client
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assetSets/456"}]
    }

    with patch(
        "src.sdk_services.assets.asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_set_service.create_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            asset_set_type=asset_set_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_set_client.mutate_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_asset_set_client.mutate_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == asset_set_type
    assert (
        operation.create.status == AssetSetStatusEnum.AssetSetStatus.ENABLED
    )  # Default


@pytest.mark.asyncio
async def test_update_asset_set(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an asset set."""
    # Arrange
    customer_id = "1234567890"
    asset_set_id = "123"
    new_name = "Updated Asset Set"
    new_status = AssetSetStatusEnum.AssetSetStatus.REMOVED

    # Create mock response
    mock_response = Mock(spec=MutateAssetSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"
    mock_response.results = [mock_result]

    # Get the mocked asset set service client
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/assetSets/{asset_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.assets.asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_set_service.update_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            name=new_name,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_set_client.mutate_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_asset_set_client.mutate_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/assetSets/{asset_set_id}"
    )
    assert operation.update.name == new_name
    assert operation.update.status == new_status
    assert set(operation.update_mask.paths) == {"name", "status"}

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated asset set {asset_set_id}",
    )


@pytest.mark.asyncio
async def test_update_asset_set_name_only(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only the name of an asset set."""
    # Arrange
    customer_id = "1234567890"
    asset_set_id = "123"
    new_name = "New Name Only"

    # Create mock response
    mock_response = Mock(spec=MutateAssetSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"
    mock_response.results = [mock_result]

    # Get the mocked asset set service client
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/assetSets/{asset_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.assets.asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_set_service.update_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            name=new_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_set_client.mutate_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_asset_set_client.mutate_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.update.name == new_name
    assert operation.update_mask.paths == ["name"]


@pytest.mark.asyncio
async def test_list_asset_sets(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing asset sets."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    asset_set_info = [
        {
            "id": "123",
            "name": "Merchant Center Asset Set",
            "type": AssetSetTypeEnum.AssetSetType.MERCHANT_CENTER_FEED,
            "status": AssetSetStatusEnum.AssetSetStatus.ENABLED,
        },
        {
            "id": "456",
            "name": "Education Asset Set",
            "type": AssetSetTypeEnum.AssetSetType.DYNAMIC_EDUCATION,
            "status": AssetSetStatusEnum.AssetSetStatus.ENABLED,
        },
    ]

    for info in asset_set_info:
        row = Mock()
        # Mock asset set
        row.asset_set = Mock()
        row.asset_set.id = info["id"]
        row.asset_set.name = info["name"]
        row.asset_set.type_ = info["type"]
        row.asset_set.status = info["status"]
        row.asset_set.resource_name = f"customers/{customer_id}/assetSets/{info['id']}"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await asset_set_service.list_asset_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 2

    # Check first asset set
    assert result[0]["asset_set_id"] == "123"
    assert result[0]["name"] == "Merchant Center Asset Set"
    assert result[0]["type"] == "MERCHANT_CENTER_FEED"
    assert result[0]["status"] == "ENABLED"
    assert result[0]["resource_name"] == f"customers/{customer_id}/assetSets/123"

    # Check second asset set
    assert result[1]["asset_set_id"] == "456"
    assert result[1]["name"] == "Education Asset Set"
    assert result[1]["type"] == "DYNAMIC_EDUCATION"
    assert result[1]["status"] == "ENABLED"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "asset_set.status != 'REMOVED'" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 asset sets",
    )


@pytest.mark.asyncio
async def test_list_asset_sets_with_type_filter(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing asset sets with type filter."""
    # Arrange
    customer_id = "1234567890"
    asset_set_type = "MERCHANT_CENTER_FEED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_set_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await asset_set_service.list_asset_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_type=asset_set_type,
            include_removed=True,
        )

    # Assert
    assert result == []

    # Verify the search call includes type filter but not removed filter
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"asset_set.type = '{asset_set_type}'" in query
    assert "asset_set.status != 'REMOVED'" not in query


@pytest.mark.asyncio
async def test_remove_asset_set(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an asset set."""
    # Arrange
    customer_id = "1234567890"
    asset_set_id = "123"

    # Create mock response
    mock_response = Mock(spec=MutateAssetSetsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"
    mock_response.results = [mock_result]

    # Get the mocked asset set service client
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/assetSets/{asset_set_id}"}
        ]
    }

    with patch(
        "src.sdk_services.assets.asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_set_service.remove_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_set_client.mutate_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_asset_set_client.mutate_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == f"customers/{customer_id}/assetSets/{asset_set_id}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed asset set {asset_set_id}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked asset set service client and make it raise exception
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_set_service.create_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test",
            asset_set_type=AssetSetTypeEnum.AssetSetType.MERCHANT_CENTER_FEED,
        )

    assert "Failed to create asset set" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create asset set: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_update_error_handling(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling for update operation."""
    # Arrange
    customer_id = "1234567890"
    asset_set_id = "123"

    # Get the mocked asset set service client and make it raise exception
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_set_service.update_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            name="Updated Name",
        )

    assert "Failed to update asset set" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_error_handling(
    asset_set_service: AssetSetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling for remove operation."""
    # Arrange
    customer_id = "1234567890"
    asset_set_id = "123"

    # Get the mocked asset set service client and make it raise exception
    mock_asset_set_client = asset_set_service.client  # type: ignore
    mock_asset_set_client.mutate_asset_sets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_set_service.remove_asset_set(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
        )

    assert "Failed to remove asset set" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_asset_set_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_asset_set_tools(mock_mcp)

    # Assert
    assert isinstance(service, AssetSetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_asset_set",
        "update_asset_set",
        "list_asset_sets",
        "remove_asset_set",
    ]

    assert set(tool_names) == set(expected_tools)
