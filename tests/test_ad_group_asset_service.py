"""Tests for AdGroupAssetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.enums.types.asset_link_status import AssetLinkStatusEnum
from google.ads.googleads.v20.services.services.ad_group_asset_service import (
    AdGroupAssetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_asset_service import (
    MutateAdGroupAssetsResponse,
)

from src.sdk_services.ad_group.ad_group_asset_service import (
    AdGroupAssetService,
    register_ad_group_asset_tools,
)


@pytest.fixture
def ad_group_asset_service(mock_sdk_client: Any) -> AdGroupAssetService:
    """Create an AdGroupAssetService instance with mocked dependencies."""
    # Mock AdGroupAssetService client
    mock_ad_group_asset_client = Mock(spec=AdGroupAssetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_asset_client

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupAssetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_link_asset_to_ad_group(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test linking an asset to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    asset_id = "999"
    field_type = "HEADLINE"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAssetsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
    )
    mock_response.results = [mock_result]

    # Get the mocked ad group asset service client
    mock_ad_group_asset_client = ad_group_asset_service.client  # type: ignore
    mock_ad_group_asset_client.mutate_ad_group_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_asset_service.link_asset_to_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_asset_client.mutate_ad_group_assets.assert_called_once()  # type: ignore
    call_args = mock_ad_group_asset_client.mutate_ad_group_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.asset == f"customers/{customer_id}/assets/{asset_id}"
    assert operation.create.field_type == AssetFieldTypeEnum.AssetFieldType.HEADLINE
    assert operation.create.status == AssetLinkStatusEnum.AssetLinkStatus.ENABLED

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Linked asset {asset_id} to ad group {ad_group_id} for field type {field_type}",
    )


@pytest.mark.asyncio
async def test_link_multiple_assets_to_ad_group(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test linking multiple assets to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    asset_links = [
        {"asset_id": "100", "field_type": "HEADLINE", "status": "ENABLED"},
        {"asset_id": "200", "field_type": "DESCRIPTION"},
        {"asset_id": "300", "field_type": "SITELINK", "status": "PAUSED"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAssetsResponse)
    mock_results = []
    for link in asset_links:
        mock_result = Mock()
        mock_result.resource_name = f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{link['asset_id']}~{link['field_type']}"
        mock_results.append(mock_result)
    mock_response.results = mock_results

    # Get the mocked ad group asset service client
    mock_ad_group_asset_client = ad_group_asset_service.client  # type: ignore
    mock_ad_group_asset_client.mutate_ad_group_assets.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_asset_service.link_multiple_assets_to_ad_group(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        asset_links=asset_links,
    )

    # Assert
    assert len(result) == 3
    assert result[0]["ad_group_id"] == ad_group_id
    assert result[0]["asset_id"] == "100"
    assert result[0]["field_type"] == "HEADLINE"
    assert result[0]["status"] == "ENABLED"

    assert result[1]["asset_id"] == "200"
    assert result[1]["field_type"] == "DESCRIPTION"
    assert result[1]["status"] == "ENABLED"  # Default

    assert result[2]["asset_id"] == "300"
    assert result[2]["field_type"] == "SITELINK"
    assert result[2]["status"] == "PAUSED"

    # Verify the API call
    mock_ad_group_asset_client.mutate_ad_group_assets.assert_called_once()  # type: ignore
    call_args = mock_ad_group_asset_client.mutate_ad_group_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Verify first operation
    operation1 = request.operations[0]
    assert (
        operation1.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation1.create.asset == f"customers/{customer_id}/assets/100"
    assert operation1.create.field_type == AssetFieldTypeEnum.AssetFieldType.HEADLINE
    assert operation1.create.status == AssetLinkStatusEnum.AssetLinkStatus.ENABLED

    # Verify third operation with PAUSED status
    operation3 = request.operations[2]
    assert operation3.create.asset == f"customers/{customer_id}/assets/300"
    assert operation3.create.field_type == AssetFieldTypeEnum.AssetFieldType.SITELINK
    assert operation3.create.status == AssetLinkStatusEnum.AssetLinkStatus.PAUSED

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Linked {len(result)} assets to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_update_ad_group_asset_status(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating the status of an ad group asset link."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    asset_id = "999"
    field_type = "HEADLINE"
    status = "PAUSED"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAssetsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
    )
    mock_response.results = [mock_result]

    # Get the mocked ad group asset service client
    mock_ad_group_asset_client = ad_group_asset_service.client  # type: ignore
    mock_ad_group_asset_client.mutate_ad_group_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_asset_service.update_ad_group_asset_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_asset_client.mutate_ad_group_assets.assert_called_once()  # type: ignore
    call_args = mock_ad_group_asset_client.mutate_ad_group_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
    )
    assert operation.update.status == AssetLinkStatusEnum.AssetLinkStatus.PAUSED
    assert operation.update_mask.paths == ["status"]

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad group asset status to {status}",
    )


@pytest.mark.asyncio
async def test_list_ad_group_assets(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group assets."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    field_type = "HEADLINE"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    asset_info = [
        {
            "ad_group_id": "111",
            "ad_group_name": "Test Ad Group",
            "asset_id": "100",
            "asset_name": "Headline 1",
            "field_type": AssetFieldTypeEnum.AssetFieldType.HEADLINE,
            "status": AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
        },
        {
            "ad_group_id": "111",
            "ad_group_name": "Test Ad Group",
            "asset_id": "200",
            "asset_name": "Headline 2",
            "field_type": AssetFieldTypeEnum.AssetFieldType.HEADLINE,
            "status": AssetLinkStatusEnum.AssetLinkStatus.PAUSED,
        },
    ]

    for info in asset_info:
        row = Mock()
        # Mock ad group asset
        row.ad_group_asset = Mock()
        row.ad_group_asset.resource_name = f"customers/{customer_id}/adGroupAssets/{info['ad_group_id']}~{info['asset_id']}~HEADLINE"
        row.ad_group_asset.ad_group = (
            f"customers/{customer_id}/adGroups/{info['ad_group_id']}"
        )
        row.ad_group_asset.asset = f"customers/{customer_id}/assets/{info['asset_id']}"
        row.ad_group_asset.field_type = info["field_type"]
        row.ad_group_asset.status = info["status"]

        # Mock ad group
        row.ad_group = Mock()
        row.ad_group.id = info["ad_group_id"]
        row.ad_group.name = info["ad_group_name"]
        row.ad_group.campaign = "customers/1234567890/campaigns/222"

        # Mock campaign
        row.campaign = Mock()
        row.campaign.id = "222"
        row.campaign.name = "Test Campaign"

        # Mock asset
        row.asset = Mock()
        row.asset.id = info["asset_id"]
        row.asset.name = info["asset_name"]
        row.asset.type_ = Mock(name="TEXT")

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_asset_service.list_ad_group_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            field_type=field_type,
        )

    # Assert
    assert len(result) == 2
    assert result[0]["ad_group_id"] == "111"
    assert result[0]["asset_id"] == "100"
    assert result[0]["asset_name"] == "Headline 1"
    assert result[0]["field_type"] == "HEADLINE"
    assert result[0]["status"] == "ENABLED"

    assert result[1]["asset_id"] == "200"
    assert result[1]["status"] == "PAUSED"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"ad_group.id = {ad_group_id}" in query
    assert f"ad_group_asset.field_type = '{field_type}'" in query
    assert "ad_group_asset.source = 'ADVERTISER'" in query  # Default filter

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 ad group assets",
    )


@pytest.mark.asyncio
async def test_list_ad_group_assets_with_campaign_filter(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group assets with campaign filter."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "222"
    include_system_managed = True

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_asset_service.list_ad_group_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            include_system_managed=include_system_managed,
        )

    # Assert
    assert result == []

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert "ad_group_asset.source = 'ADVERTISER'" not in query  # Should not be included


@pytest.mark.asyncio
async def test_remove_asset_from_ad_group(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an asset from an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    asset_id = "999"
    field_type = "HEADLINE"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAssetsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
    )
    mock_response.results = [mock_result]

    # Get the mocked ad group asset service client
    mock_ad_group_asset_client = ad_group_asset_service.client  # type: ignore
    mock_ad_group_asset_client.mutate_ad_group_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_asset_service.remove_asset_from_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            asset_id=asset_id,
            field_type=field_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_asset_client.mutate_ad_group_assets.assert_called_once()  # type: ignore
    call_args = mock_ad_group_asset_client.mutate_ad_group_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.remove
        == f"customers/{customer_id}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed asset {asset_id} from ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    ad_group_asset_service: AdGroupAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked ad group asset service client and make it raise exception
    mock_ad_group_asset_client = ad_group_asset_service.client  # type: ignore
    mock_ad_group_asset_client.mutate_ad_group_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_asset_service.link_asset_to_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id="111",
            asset_id="999",
            field_type="HEADLINE",
        )

    assert "Failed to link asset to ad group" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to link asset to ad group: Test Google Ads Exception",
    )


def test_register_ad_group_asset_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_asset_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupAssetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "link_asset_to_ad_group",
        "link_multiple_assets_to_ad_group",
        "update_ad_group_asset_status",
        "list_ad_group_assets",
        "remove_asset_from_ad_group",
    ]

    assert set(tool_names) == set(expected_tools)
