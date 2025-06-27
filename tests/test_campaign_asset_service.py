"""Tests for CampaignAssetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v20.services.services.campaign_asset_service import (
    CampaignAssetServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_asset_service import (
    MutateCampaignAssetsResponse,
)

from src.sdk_services.campaign.campaign_asset_service import (
    CampaignAssetService,
    register_campaign_asset_tools,
)


@pytest.fixture
def campaign_asset_service(mock_sdk_client: Any) -> CampaignAssetService:
    """Create a CampaignAssetService instance with mocked dependencies."""
    # Mock CampaignAssetService client
    mock_campaign_asset_client = Mock(spec=CampaignAssetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_asset_client  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignAssetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_link_asset_to_campaign(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test linking an asset to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    asset_id = "555666777"
    field_type = AssetFieldTypeEnum.AssetFieldType.SITELINK

    # Create mock response
    mock_response = Mock(spec=MutateCampaignAssetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = (
        f"customers/{customer_id}/campaignAssets/{campaign_id}~{asset_id}~SITELINK"
    )
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign asset service client
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignAssets/{campaign_id}~{asset_id}~SITELINK"
            }
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_asset_service.link_asset_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=field_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_asset_client.mutate_campaign_assets.assert_called_once()  # type: ignore
    call_args = mock_campaign_asset_client.mutate_campaign_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    campaign_asset = operation.create
    assert campaign_asset.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert campaign_asset.asset == f"customers/{customer_id}/assets/{asset_id}"
    assert campaign_asset.field_type == field_type

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Linked asset {asset_id} to campaign {campaign_id} for field type {field_type}",
    )


@pytest.mark.asyncio
async def test_link_multiple_assets_to_campaign(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test linking multiple assets to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    asset_links = [
        {"asset_id": "111", "field_type": "SITELINK"},
        {"asset_id": "222", "field_type": "CALLOUT"},
        {"asset_id": "333", "field_type": "HEADLINE"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignAssetsResponse)
    mock_response.results = []
    for i, link in enumerate(asset_links):
        result = Mock()
        result.resource_name = f"customers/{customer_id}/campaignAssets/{campaign_id}~{link['asset_id']}~{link['field_type']}"
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign asset service client
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.return_value = mock_response  # type: ignore

    # Act
    result = await campaign_asset_service.link_multiple_assets_to_campaign(
        ctx=mock_ctx,
        customer_id=customer_id,
        campaign_id=campaign_id,
        asset_links=asset_links,
    )

    # Assert
    assert len(result) == len(asset_links)

    # Check results
    for i, link in enumerate(asset_links):
        asset_result = result[i]
        assert (
            asset_result["resource_name"]
            == f"customers/{customer_id}/campaignAssets/{campaign_id}~{link['asset_id']}~{link['field_type']}"
        )
        assert asset_result["campaign_id"] == campaign_id
        assert asset_result["asset_id"] == link["asset_id"]
        assert asset_result["field_type"] == link["field_type"]

    # Verify the API call
    mock_campaign_asset_client.mutate_campaign_assets.assert_called_once()  # type: ignore
    call_args = mock_campaign_asset_client.mutate_campaign_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(asset_links)

    # Check operations
    for i, link in enumerate(asset_links):
        operation = request.operations[i]
        campaign_asset = operation.create
        assert (
            campaign_asset.campaign
            == f"customers/{customer_id}/campaigns/{campaign_id}"
        )
        assert (
            campaign_asset.asset == f"customers/{customer_id}/assets/{link['asset_id']}"
        )
        assert campaign_asset.field_type == getattr(
            AssetFieldTypeEnum.AssetFieldType, link["field_type"]
        )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Linked {len(asset_links)} assets to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_list_campaign_assets(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign assets."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    field_type = AssetFieldTypeEnum.AssetFieldType.SITELINK
    include_system_managed = False

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()

        # Mock campaign_asset
        row.campaign_asset = Mock()
        row.campaign_asset.resource_name = (
            f"customers/{customer_id}/campaignAssets/{campaign_id}~{i + 100}~SITELINK"
        )
        row.campaign_asset.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        row.campaign_asset.asset = f"customers/{customer_id}/assets/{i + 100}"
        row.campaign_asset.field_type = Mock()
        row.campaign_asset.field_type.name = "SITELINK"
        row.campaign_asset.status = Mock()
        row.campaign_asset.status.name = "ENABLED"

        # Mock campaign
        row.campaign = Mock()
        row.campaign.id = campaign_id
        row.campaign.name = "Test Campaign"

        # Mock asset
        row.asset = Mock()
        row.asset.id = i + 100
        row.asset.name = f"Test Asset {i}"
        row.asset.type_ = Mock()
        row.asset.type_.name = "SITELINK"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_asset_service.list_campaign_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            field_type=field_type,
            include_system_managed=include_system_managed,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert (
        first_result["resource_name"]
        == f"customers/{customer_id}/campaignAssets/{campaign_id}~100~SITELINK"
    )
    assert first_result["campaign_id"] == campaign_id
    assert first_result["campaign_name"] == "Test Campaign"
    assert first_result["asset_id"] == "100"
    assert first_result["asset_name"] == "Test Asset 0"
    assert first_result["asset_type"] == "SITELINK"
    assert first_result["field_type"] == "SITELINK"
    assert first_result["status"] == "ENABLED"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert f"campaign_asset.field_type = '{field_type.name}'" in query
    assert "campaign_asset.source = 'ADVERTISER'" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 campaign assets",
    )


@pytest.mark.asyncio
async def test_list_campaign_assets_no_filters(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign assets without filters."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_asset_service.list_campaign_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 0

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    # Should not have campaign_id or field_type filters
    assert "campaign.id =" not in query
    assert "campaign_asset.field_type =" not in query
    # Should still have system managed filter by default
    assert "campaign_asset.source = 'ADVERTISER'" in query


@pytest.mark.asyncio
async def test_list_campaign_assets_include_system_managed(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign assets including system managed."""
    # Arrange
    customer_id = "1234567890"
    include_system_managed = True

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_asset_service.list_campaign_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_system_managed=include_system_managed,
        )

    # Assert
    assert len(result) == 0

    # Verify the search call
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    # Should not have system managed filter
    assert "campaign_asset.source = 'ADVERTISER'" not in query


@pytest.mark.asyncio
async def test_list_campaign_assets_with_none_values(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign assets with None enum values."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result with None values
    mock_results = []
    row = Mock()

    # Mock campaign_asset with None values
    row.campaign_asset = Mock()
    row.campaign_asset.resource_name = (
        f"customers/{customer_id}/campaignAssets/123~100~SITELINK"
    )
    row.campaign_asset.campaign = f"customers/{customer_id}/campaigns/123"
    row.campaign_asset.asset = f"customers/{customer_id}/assets/100"
    row.campaign_asset.field_type = None
    row.campaign_asset.status = None

    # Mock campaign
    row.campaign = Mock()
    row.campaign.id = "123"
    row.campaign.name = "Test Campaign"

    # Mock asset with None type
    row.asset = Mock()
    row.asset.id = 100
    row.asset.name = "Test Asset"
    row.asset.type_ = None

    mock_results.append(row)
    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_asset_service.list_campaign_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 1

    # Check result with None values
    first_result = result[0]
    assert first_result["asset_type"] == "UNKNOWN"
    assert first_result["field_type"] == "UNKNOWN"
    assert first_result["status"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_remove_asset_from_campaign(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an asset from a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    asset_id = "555666777"
    field_type = AssetFieldTypeEnum.AssetFieldType.SITELINK
    campaign_asset_resource = (
        f"customers/{customer_id}/campaignAssets/{campaign_id}~{asset_id}~{field_type}"
    )

    # Create mock response
    mock_response = Mock(spec=MutateCampaignAssetsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = campaign_asset_resource
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign asset service client
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": campaign_asset_resource}]}

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_asset_service.remove_asset_from_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=field_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_asset_client.mutate_campaign_assets.assert_called_once()  # type: ignore
    call_args = mock_campaign_asset_client.mutate_campaign_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == campaign_asset_resource

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed asset {asset_id} from campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_error_handling_link_asset(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when linking asset fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    asset_id = "555666777"

    # Get the mocked campaign asset service client and make it raise exception
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_asset_service.link_asset_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=AssetFieldTypeEnum.AssetFieldType.SITELINK,
        )

    assert "Failed to link asset to campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to link asset to campaign: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_link_multiple_assets(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when linking multiple assets fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"

    # Get the mocked campaign asset service client and make it raise exception
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_asset_service.link_multiple_assets_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_links=[{"asset_id": "123", "field_type": "SITELINK"}],
        )

    assert "Failed to link assets to campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to link assets to campaign: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_assets(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing assets fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await campaign_asset_service.list_campaign_assets(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list campaign assets" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list campaign assets: Search failed",
    )


@pytest.mark.asyncio
async def test_error_handling_remove_asset(
    campaign_asset_service: CampaignAssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing asset fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    asset_id = "555666777"

    # Get the mocked campaign asset service client and make it raise exception
    mock_campaign_asset_client = campaign_asset_service.client  # type: ignore
    mock_campaign_asset_client.mutate_campaign_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_asset_service.remove_asset_from_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            asset_id=asset_id,
            field_type=AssetFieldTypeEnum.AssetFieldType.SITELINK,
        )

    assert "Failed to remove asset from campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to remove asset from campaign: Test Google Ads Exception",
    )


def test_register_campaign_asset_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_asset_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignAssetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "link_asset_to_campaign",
        "link_multiple_assets_to_campaign",
        "list_campaign_assets",
        "remove_asset_from_campaign",
    ]

    assert set(tool_names) == set(expected_tools)
