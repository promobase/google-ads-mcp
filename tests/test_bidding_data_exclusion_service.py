"""Tests for BiddingDataExclusionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.seasonality_event_scope import (
    SeasonalityEventScopeEnum,
)
from google.ads.googleads.v20.enums.types.seasonality_event_status import (
    SeasonalityEventStatusEnum,
)
from google.ads.googleads.v20.services.services.bidding_data_exclusion_service import (
    BiddingDataExclusionServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.bidding_data_exclusion_service import (
    MutateBiddingDataExclusionsResponse,
)

from src.services.bidding.bidding_data_exclusion_service import (
    BiddingDataExclusionService,
    register_bidding_data_exclusion_tools,
)


@pytest.fixture
def bidding_data_exclusion_service(mock_sdk_client: Any) -> BiddingDataExclusionService:
    """Create a BiddingDataExclusionService instance with mocked dependencies."""
    # Mock BiddingDataExclusionService client
    mock_exclusion_client = Mock(spec=BiddingDataExclusionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_exclusion_client  # type: ignore

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = BiddingDataExclusionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_bidding_data_exclusion_customer_scope(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a customer-scoped bidding data exclusion."""
    # Arrange
    customer_id = "1234567890"
    name = "Holiday Exclusion"
    scope = "CUSTOMER"
    start_date_time = "2024-12-24 00:00:00"
    end_date_time = "2024-12-26 23:59:59"
    status = "ENABLED"
    description = "Exclude holiday period from bidding data"
    advertising_channel_types = ["SEARCH", "DISPLAY"]
    devices = ["MOBILE", "DESKTOP"]

    # Create mock response
    mock_response = Mock(spec=MutateBiddingDataExclusionsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/biddingDataExclusions/123"
    mock_response.results = [mock_result]

    # Get the mocked exclusion service client
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/biddingDataExclusions/123"}
        ]
    }

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_data_exclusion_service.create_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            scope=scope,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            status=status,
            description=description,
            advertising_channel_types=advertising_channel_types,
            devices=devices,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_exclusion_client.mutate_bidding_data_exclusions.assert_called_once()  # type: ignore
    call_args = mock_exclusion_client.mutate_bidding_data_exclusions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    exclusion = operation.create
    assert exclusion.name == name
    assert exclusion.scope == SeasonalityEventScopeEnum.SeasonalityEventScope.CUSTOMER
    assert exclusion.status == SeasonalityEventStatusEnum.SeasonalityEventStatus.ENABLED
    assert exclusion.start_date_time == start_date_time
    assert exclusion.end_date_time == end_date_time
    assert exclusion.description == description

    # Check advertising channel types
    assert len(exclusion.advertising_channel_types) == 2
    assert (
        AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
        in exclusion.advertising_channel_types
    )
    assert (
        AdvertisingChannelTypeEnum.AdvertisingChannelType.DISPLAY
        in exclusion.advertising_channel_types
    )

    # Check devices
    assert len(exclusion.devices) == 2
    assert DeviceEnum.Device.MOBILE in exclusion.devices
    assert DeviceEnum.Device.DESKTOP in exclusion.devices

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created bidding data exclusion: {name}",
    )


@pytest.mark.asyncio
async def test_create_bidding_data_exclusion_campaign_scope(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign-scoped bidding data exclusion."""
    # Arrange
    customer_id = "1234567890"
    name = "Campaign Exclusion"
    scope = "CAMPAIGN"
    start_date_time = "2024-11-01 00:00:00"
    end_date_time = "2024-11-03 23:59:59"
    campaigns = [
        f"customers/{customer_id}/campaigns/111",
        f"customers/{customer_id}/campaigns/222",
    ]

    # Create mock response
    mock_response = Mock(spec=MutateBiddingDataExclusionsResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/biddingDataExclusions/456"
    mock_response.results = [mock_result]

    # Get the mocked exclusion service client
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/biddingDataExclusions/456"}
        ]
    }

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_data_exclusion_service.create_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            scope=scope,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            campaigns=campaigns,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_exclusion_client.mutate_bidding_data_exclusions.assert_called_once()  # type: ignore
    call_args = mock_exclusion_client.mutate_bidding_data_exclusions.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    exclusion = operation.create
    assert exclusion.name == name
    assert exclusion.scope == SeasonalityEventScopeEnum.SeasonalityEventScope.CAMPAIGN
    assert (
        exclusion.status == SeasonalityEventStatusEnum.SeasonalityEventStatus.ENABLED
    )  # Default
    assert list(exclusion.campaigns) == campaigns


@pytest.mark.asyncio
async def test_update_bidding_data_exclusion(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a bidding data exclusion."""
    # Arrange
    customer_id = "1234567890"
    exclusion_resource_name = f"customers/{customer_id}/biddingDataExclusions/123"
    new_name = "Updated Exclusion"
    new_status = "REMOVED"
    new_description = "Updated description"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingDataExclusionsResponse)
    mock_result = Mock()
    mock_result.resource_name = exclusion_resource_name
    mock_response.results = [mock_result]

    # Get the mocked exclusion service client
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": exclusion_resource_name}]}

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_data_exclusion_service.update_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            exclusion_resource_name=exclusion_resource_name,
            name=new_name,
            status=new_status,
            description=new_description,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_exclusion_client.mutate_bidding_data_exclusions.assert_called_once()  # type: ignore
    call_args = mock_exclusion_client.mutate_bidding_data_exclusions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    exclusion = operation.update
    assert exclusion.resource_name == exclusion_resource_name
    assert exclusion.name == new_name
    assert exclusion.status == SeasonalityEventStatusEnum.SeasonalityEventStatus.REMOVED
    assert exclusion.description == new_description
    assert set(operation.update_mask.paths) == {"name", "status", "description"}

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Updated bidding data exclusion",
    )


@pytest.mark.asyncio
async def test_update_bidding_data_exclusion_dates_only(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only dates of a bidding data exclusion."""
    # Arrange
    customer_id = "1234567890"
    exclusion_resource_name = f"customers/{customer_id}/biddingDataExclusions/123"
    new_start_date_time = "2024-12-01 00:00:00"
    new_end_date_time = "2024-12-02 23:59:59"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingDataExclusionsResponse)
    mock_result = Mock()
    mock_result.resource_name = exclusion_resource_name
    mock_response.results = [mock_result]

    # Get the mocked exclusion service client
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": exclusion_resource_name}]}

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_data_exclusion_service.update_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            exclusion_resource_name=exclusion_resource_name,
            start_date_time=new_start_date_time,
            end_date_time=new_end_date_time,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_exclusion_client.mutate_bidding_data_exclusions.assert_called_once()  # type: ignore
    call_args = mock_exclusion_client.mutate_bidding_data_exclusions.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    exclusion = operation.update
    assert exclusion.start_date_time == new_start_date_time
    assert exclusion.end_date_time == new_end_date_time
    assert set(operation.update_mask.paths) == {"start_date_time", "end_date_time"}


@pytest.mark.asyncio
async def test_list_bidding_data_exclusions(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing bidding data exclusions."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    exclusion_info = [
        {
            "data_exclusion_id": "123",
            "name": "Holiday Exclusion",
            "scope": SeasonalityEventScopeEnum.SeasonalityEventScope.CUSTOMER,
            "status": SeasonalityEventStatusEnum.SeasonalityEventStatus.ENABLED,
            "start_date_time": "2024-12-24 00:00:00",
            "end_date_time": "2024-12-26 23:59:59",
            "description": "Holiday period exclusion",
            "campaigns": [],
            "advertising_channel_types": [
                AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
            ],
            "devices": [DeviceEnum.Device.MOBILE],
        },
        {
            "data_exclusion_id": "456",
            "name": "Campaign Exclusion",
            "scope": SeasonalityEventScopeEnum.SeasonalityEventScope.CAMPAIGN,
            "status": SeasonalityEventStatusEnum.SeasonalityEventStatus.REMOVED,
            "start_date_time": "2024-11-01 00:00:00",
            "end_date_time": "2024-11-03 23:59:59",
            "description": "",
            "campaigns": [f"customers/{customer_id}/campaigns/111"],
            "advertising_channel_types": [],
            "devices": [],
        },
    ]

    for info in exclusion_info:
        row = Mock()
        # Mock bidding data exclusion
        row.bidding_data_exclusion = Mock()
        row.bidding_data_exclusion.resource_name = (
            f"customers/{customer_id}/biddingDataExclusions/{info['data_exclusion_id']}"
        )
        row.bidding_data_exclusion.data_exclusion_id = info["data_exclusion_id"]
        row.bidding_data_exclusion.name = info["name"]
        row.bidding_data_exclusion.scope = info["scope"]
        row.bidding_data_exclusion.status = info["status"]
        row.bidding_data_exclusion.start_date_time = info["start_date_time"]
        row.bidding_data_exclusion.end_date_time = info["end_date_time"]
        row.bidding_data_exclusion.description = info["description"]
        row.bidding_data_exclusion.campaigns = info["campaigns"]
        row.bidding_data_exclusion.advertising_channel_types = info[
            "advertising_channel_types"
        ]
        row.bidding_data_exclusion.devices = info["devices"]

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return bidding_data_exclusion_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await bidding_data_exclusion_service.list_bidding_data_exclusions(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 2

    # Check first exclusion
    assert result[0]["data_exclusion_id"] == "123"
    assert result[0]["name"] == "Holiday Exclusion"
    assert result[0]["scope"] == "CUSTOMER"
    assert result[0]["status"] == "ENABLED"
    assert result[0]["start_date_time"] == "2024-12-24 00:00:00"
    assert result[0]["end_date_time"] == "2024-12-26 23:59:59"
    assert result[0]["description"] == "Holiday period exclusion"
    assert result[0]["campaigns"] == []
    assert result[0]["advertising_channel_types"] == ["SEARCH"]
    assert result[0]["devices"] == ["MOBILE"]

    # Check second exclusion
    assert result[1]["data_exclusion_id"] == "456"
    assert result[1]["name"] == "Campaign Exclusion"
    assert result[1]["scope"] == "CAMPAIGN"
    assert result[1]["status"] == "REMOVED"
    assert result[1]["campaigns"] == [f"customers/{customer_id}/campaigns/111"]

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM bidding_data_exclusion" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 bidding data exclusions",
    )


@pytest.mark.asyncio
async def test_list_bidding_data_exclusions_with_scope_filter(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing bidding data exclusions with scope filter."""
    # Arrange
    customer_id = "1234567890"
    scope_filter = "CUSTOMER"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return bidding_data_exclusion_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await bidding_data_exclusion_service.list_bidding_data_exclusions(
            ctx=mock_ctx,
            customer_id=customer_id,
            scope_filter=scope_filter,
        )

    # Assert
    assert result == []

    # Verify the search call includes scope filter
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"bidding_data_exclusion.scope = '{scope_filter}'" in query


@pytest.mark.asyncio
async def test_remove_bidding_data_exclusion(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a bidding data exclusion."""
    # Arrange
    customer_id = "1234567890"
    exclusion_resource_name = f"customers/{customer_id}/biddingDataExclusions/123"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingDataExclusionsResponse)
    mock_result = Mock()
    mock_result.resource_name = exclusion_resource_name
    mock_response.results = [mock_result]

    # Get the mocked exclusion service client
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": exclusion_resource_name}]}

    with patch(
        "src.sdk_services.bidding.bidding_data_exclusion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_data_exclusion_service.remove_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            exclusion_resource_name=exclusion_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_exclusion_client.mutate_bidding_data_exclusions.assert_called_once()  # type: ignore
    call_args = mock_exclusion_client.mutate_bidding_data_exclusions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == exclusion_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed bidding data exclusion",
    )


@pytest.mark.asyncio
async def test_error_handling(
    bidding_data_exclusion_service: BiddingDataExclusionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked exclusion service client and make it raise exception
    mock_exclusion_client = bidding_data_exclusion_service.client  # type: ignore
    mock_exclusion_client.mutate_bidding_data_exclusions.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await bidding_data_exclusion_service.create_bidding_data_exclusion(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test",
            scope="CUSTOMER",
            start_date_time="2024-01-01 00:00:00",
            end_date_time="2024-01-02 23:59:59",
        )

    assert "Failed to create bidding data exclusion" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create bidding data exclusion: Test Google Ads Exception",
    )


def test_register_bidding_data_exclusion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_bidding_data_exclusion_tools(mock_mcp)

    # Assert
    assert isinstance(service, BiddingDataExclusionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_bidding_data_exclusion",
        "update_bidding_data_exclusion",
        "list_bidding_data_exclusions",
        "remove_bidding_data_exclusion",
    ]

    assert set(tool_names) == set(expected_tools)
