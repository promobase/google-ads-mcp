"""Tests for AssetGroupService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.asset_group_status import AssetGroupStatusEnum
from google.ads.googleads.v20.services.services.asset_group_service import (
    AssetGroupServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.asset_group_service import (
    MutateAssetGroupsResponse,
)

from src.sdk_services.assets.asset_group_service import (
    AssetGroupService,
    register_asset_group_tools,
)


@pytest.fixture
def asset_group_service(mock_sdk_client: Any) -> AssetGroupService:
    """Create an AssetGroupService instance with mocked dependencies."""
    # Mock AssetGroupService client
    mock_asset_group_client = Mock(spec=AssetGroupServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_asset_group_client  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AssetGroupService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_asset_group(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an asset group."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111"
    name = "Test Asset Group"
    final_urls = ["https://example.com", "https://example.com/page2"]
    final_mobile_urls = ["https://m.example.com"]
    path1 = "shoes"
    path2 = "running"

    # Create mock response
    mock_response = Mock(spec=MutateAssetGroupsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetGroups/123"
    mock_response.results = [mock_result]

    # Get the mocked asset group service client
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assetGroups/123"}]
    }

    with patch(
        "src.sdk_services.assets.asset_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_group_service.create_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            final_urls=final_urls,
            final_mobile_urls=final_mobile_urls,
            path1=path1,
            path2=path2,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_group_client.mutate_asset_groups.assert_called_once()  # type: ignore
    call_args = mock_asset_group_client.mutate_asset_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert list(operation.create.final_urls) == final_urls
    assert list(operation.create.final_mobile_urls) == final_mobile_urls
    assert operation.create.path1 == path1
    assert operation.create.path2 == path2
    assert operation.create.status == AssetGroupStatusEnum.AssetGroupStatus.ENABLED

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created asset group '{name}'",
    )


@pytest.mark.asyncio
async def test_create_asset_group_minimal(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an asset group with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111"
    name = "Minimal Asset Group"
    final_urls = ["https://example.com"]

    # Create mock response
    mock_response = Mock(spec=MutateAssetGroupsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetGroups/456"
    mock_response.results = [mock_result]

    # Get the mocked asset group service client
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assetGroups/456"}]
    }

    with patch(
        "src.sdk_services.assets.asset_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_group_service.create_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            final_urls=final_urls,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_group_client.mutate_asset_groups.assert_called_once()  # type: ignore
    call_args = mock_asset_group_client.mutate_asset_groups.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.name == name
    assert list(operation.create.final_urls) == final_urls
    assert len(operation.create.final_mobile_urls) == 0
    assert operation.create.path1 == ""
    assert operation.create.path2 == ""


@pytest.mark.asyncio
async def test_update_asset_group(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an asset group."""
    # Arrange
    customer_id = "1234567890"
    asset_group_id = "123"
    new_name = "Updated Asset Group"
    new_final_urls = ["https://newexample.com"]
    new_status = AssetGroupStatusEnum.AssetGroupStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateAssetGroupsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetGroups/{asset_group_id}"
    mock_response.results = [mock_result]

    # Get the mocked asset group service client
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/assetGroups/{asset_group_id}"}
        ]
    }

    with patch(
        "src.sdk_services.assets.asset_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_group_service.update_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            name=new_name,
            final_urls=new_final_urls,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_group_client.mutate_asset_groups.assert_called_once()  # type: ignore
    call_args = mock_asset_group_client.mutate_asset_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/assetGroups/{asset_group_id}"
    )
    assert operation.update.name == new_name
    assert list(operation.update.final_urls) == new_final_urls
    assert operation.update.status == new_status
    assert set(operation.update_mask.paths) == {"name", "final_urls", "status"}

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated asset group {asset_group_id}",
    )


@pytest.mark.asyncio
async def test_list_asset_groups(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing asset groups."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    asset_group_info = [
        {
            "id": "123",
            "name": "Asset Group 1",
            "final_urls": ["https://example1.com"],
            "final_mobile_urls": ["https://m.example1.com"],
            "path1": "shoes",
            "path2": "running",
            "status": AssetGroupStatusEnum.AssetGroupStatus.ENABLED,
        },
        {
            "id": "456",
            "name": "Asset Group 2",
            "final_urls": ["https://example2.com", "https://example2.com/page"],
            "final_mobile_urls": [],
            "path1": "clothing",
            "path2": "",
            "status": AssetGroupStatusEnum.AssetGroupStatus.PAUSED,
        },
    ]

    for info in asset_group_info:
        row = Mock()
        # Mock asset group
        row.asset_group = Mock()
        row.asset_group.id = info["id"]
        row.asset_group.name = info["name"]
        row.asset_group.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        row.asset_group.resource_name = (
            f"customers/{customer_id}/assetGroups/{info['id']}"
        )
        row.asset_group.final_urls = info["final_urls"]
        row.asset_group.final_mobile_urls = info["final_mobile_urls"]
        row.asset_group.path1 = info["path1"]
        row.asset_group.path2 = info["path2"]
        row.asset_group.status = info["status"]

        # Mock campaign
        row.campaign = Mock()
        row.campaign.id = campaign_id
        row.campaign.name = "Test Campaign"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_group_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await asset_group_service.list_asset_groups(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    # Assert
    assert len(result) == 2

    # Check first asset group
    assert result[0]["asset_group_id"] == "123"
    assert result[0]["name"] == "Asset Group 1"
    assert result[0]["campaign_id"] == campaign_id
    assert result[0]["campaign_name"] == "Test Campaign"
    assert result[0]["final_urls"] == ["https://example1.com"]
    assert result[0]["final_mobile_urls"] == ["https://m.example1.com"]
    assert result[0]["path1"] == "shoes"
    assert result[0]["path2"] == "running"
    assert result[0]["status"] == "ENABLED"

    # Check second asset group
    assert result[1]["asset_group_id"] == "456"
    assert result[1]["name"] == "Asset Group 2"
    assert result[1]["status"] == "PAUSED"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert "asset_group.status != 'REMOVED'" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 asset groups",
    )


@pytest.mark.asyncio
async def test_list_asset_groups_include_removed(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing asset groups including removed ones."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_group_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.assets.asset_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await asset_group_service.list_asset_groups(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_removed=True,
        )

    # Assert
    assert result == []

    # Verify the search call doesn't filter removed
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert "asset_group.status != 'REMOVED'" not in query


@pytest.mark.asyncio
async def test_remove_asset_group(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an asset group."""
    # Arrange
    customer_id = "1234567890"
    asset_group_id = "123"

    # Create mock response
    mock_response = Mock(spec=MutateAssetGroupsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/assetGroups/{asset_group_id}"
    mock_response.results = [mock_result]

    # Get the mocked asset group service client
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/assetGroups/{asset_group_id}"}
        ]
    }

    with patch(
        "src.sdk_services.assets.asset_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_group_service.remove_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_group_client.mutate_asset_groups.assert_called_once()  # type: ignore
    call_args = mock_asset_group_client.mutate_asset_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == f"customers/{customer_id}/assetGroups/{asset_group_id}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed asset group {asset_group_id}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked asset group service client and make it raise exception
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_group_service.create_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id="111",
            name="Test",
            final_urls=["https://example.com"],
        )

    assert "Failed to create asset group" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create asset group: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_update_error_handling(
    asset_group_service: AssetGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling for update operation."""
    # Arrange
    customer_id = "1234567890"
    asset_group_id = "123"

    # Get the mocked asset group service client and make it raise exception
    mock_asset_group_client = asset_group_service.client  # type: ignore
    mock_asset_group_client.mutate_asset_groups.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_group_service.update_asset_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_group_id=asset_group_id,
            name="Updated Name",
        )

    assert "Failed to update asset group" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_asset_group_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_asset_group_tools(mock_mcp)

    # Assert
    assert isinstance(service, AssetGroupService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_asset_group",
        "update_asset_group",
        "list_asset_groups",
        "remove_asset_group",
    ]

    assert set(tool_names) == set(expected_tools)
