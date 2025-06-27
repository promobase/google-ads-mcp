"""Tests for AdGroupBidModifierService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.day_of_week import DayOfWeekEnum
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.hotel_date_selection_type import (
    HotelDateSelectionTypeEnum,
)
from google.ads.googleads.v20.services.services.ad_group_bid_modifier_service import (
    AdGroupBidModifierServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_bid_modifier_service import (
    MutateAdGroupBidModifiersResponse,
)

from src.sdk_services.ad_group.ad_group_bid_modifier_service import (
    AdGroupBidModifierService,
    register_ad_group_bid_modifier_tools,
)


@pytest.fixture
def ad_group_bid_modifier_service(mock_sdk_client: Any) -> AdGroupBidModifierService:
    """Create an AdGroupBidModifierService instance with mocked dependencies."""
    # Mock AdGroupBidModifierService client
    mock_bid_modifier_client = Mock(spec=AdGroupBidModifierServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_bid_modifier_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupBidModifierService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_device_bid_modifier(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a device bid modifier."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    device_type = "MOBILE"
    bid_modifier = 1.2

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/adGroupBidModifiers/12345"
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupBidModifiers/12345"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_bid_modifier_service.create_device_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            device_type=device_type,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_ad_group_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.bid_modifier == bid_modifier
    assert operation.create.device.type_ == DeviceEnum.Device.MOBILE

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created device bid modifier for ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_hotel_check_in_day_bid_modifier(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a hotel check-in day bid modifier."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    day_of_week = "MONDAY"
    bid_modifier = 1.5

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/adGroupBidModifiers/67890"
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupBidModifiers/67890"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = (
            await ad_group_bid_modifier_service.create_hotel_check_in_day_bid_modifier(
                ctx=mock_ctx,
                customer_id=customer_id,
                ad_group_id=ad_group_id,
                day_of_week=day_of_week,
                bid_modifier=bid_modifier,
            )
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_ad_group_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.bid_modifier == bid_modifier
    assert (
        operation.create.hotel_check_in_day.day_of_week
        == DayOfWeekEnum.DayOfWeek.MONDAY
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created hotel check-in day bid modifier for ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_hotel_date_selection_bid_modifier(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a hotel date selection bid modifier."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"
    date_selection_type = "DEFAULT_SELECTION"
    bid_modifier = 1.3

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/adGroupBidModifiers/11111"
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupBidModifiers/11111"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_bid_modifier_service.create_hotel_date_selection_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            date_selection_type=date_selection_type,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_ad_group_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.bid_modifier == bid_modifier
    assert (
        operation.create.hotel_date_selection_type.type_
        == HotelDateSelectionTypeEnum.HotelDateSelectionType.DEFAULT_SELECTION
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created hotel date selection bid modifier for ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_update_bid_modifier(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a bid modifier."""
    # Arrange
    customer_id = "1234567890"
    bid_modifier_resource_name = f"customers/{customer_id}/adGroupBidModifiers/12345"
    new_bid_modifier = 2.0

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = bid_modifier_resource_name
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": bid_modifier_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_bid_modifier_service.update_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
            new_bid_modifier=new_bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_ad_group_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.update.resource_name == bid_modifier_resource_name
    assert operation.update.bid_modifier == new_bid_modifier
    assert operation.update_mask.paths == ["bid_modifier"]

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated bid modifier to {new_bid_modifier}",
    )


@pytest.mark.asyncio
async def test_list_ad_group_bid_modifiers(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group bid modifiers."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "111"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []

    # Device bid modifier
    row1 = Mock()
    row1.ad_group_bid_modifier = Mock()
    row1.ad_group_bid_modifier.resource_name = (
        f"customers/{customer_id}/adGroupBidModifiers/12345"
    )
    row1.ad_group_bid_modifier.bid_modifier = 1.2
    row1.ad_group_bid_modifier.device = Mock()
    row1.ad_group_bid_modifier.device.type = DeviceEnum.Device.MOBILE
    # Initialize other criterion types to None
    row1.ad_group_bid_modifier.hotel_date_selection_type = Mock(type=None)
    row1.ad_group_bid_modifier.hotel_advance_booking_window = Mock(min_days=None)
    row1.ad_group_bid_modifier.hotel_length_of_stay = Mock(min_nights=None)
    row1.ad_group_bid_modifier.hotel_check_in_day = Mock(day_of_week=None)
    row1.ad_group_bid_modifier.hotel_check_in_date_range = Mock(start_date=None)
    row1.ad_group = Mock(id="111", name="Test Ad Group")
    row1.campaign = Mock(id="222", name="Test Campaign")
    mock_results.append(row1)

    # Hotel check-in day bid modifier
    row2 = Mock()
    row2.ad_group_bid_modifier = Mock()
    row2.ad_group_bid_modifier.resource_name = (
        f"customers/{customer_id}/adGroupBidModifiers/67890"
    )
    row2.ad_group_bid_modifier.bid_modifier = 1.5
    row2.ad_group_bid_modifier.hotel_check_in_day = Mock()
    row2.ad_group_bid_modifier.hotel_check_in_day.day_of_week = (
        DayOfWeekEnum.DayOfWeek.MONDAY
    )
    # Initialize other criterion types to None
    row2.ad_group_bid_modifier.device = Mock(type=None)
    row2.ad_group_bid_modifier.hotel_date_selection_type = Mock(type=None)
    row2.ad_group_bid_modifier.hotel_advance_booking_window = Mock(min_days=None)
    row2.ad_group_bid_modifier.hotel_length_of_stay = Mock(min_nights=None)
    row2.ad_group_bid_modifier.hotel_check_in_date_range = Mock(start_date=None)
    row2.ad_group = Mock(id="111", name="Test Ad Group")
    row2.campaign = Mock(id="222", name="Test Campaign")
    mock_results.append(row2)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_bid_modifier_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_bid_modifier_service.list_ad_group_bid_modifiers(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
        )

    # Assert
    assert len(result) == 2

    # Check device bid modifier
    assert result[0]["ad_group_id"] == "111"
    assert result[0]["bid_modifier"] == 1.2
    assert result[0]["criterion_type"] == "DEVICE"
    assert result[0]["criterion_details"]["device_type"] == "MOBILE"

    # Check hotel check-in day bid modifier
    assert result[1]["bid_modifier"] == 1.5
    assert result[1]["criterion_type"] == "HOTEL_CHECK_IN_DAY"
    assert result[1]["criterion_details"]["day_of_week"] == "MONDAY"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"ad_group.id = {ad_group_id}" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 ad group bid modifiers",
    )


@pytest.mark.asyncio
async def test_remove_bid_modifier(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a bid modifier."""
    # Arrange
    customer_id = "1234567890"
    bid_modifier_resource_name = f"customers/{customer_id}/adGroupBidModifiers/12345"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = bid_modifier_resource_name
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": bid_modifier_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_bid_modifier_service.remove_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_ad_group_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == bid_modifier_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed ad group bid modifier",
    )


@pytest.mark.asyncio
async def test_error_handling(
    ad_group_bid_modifier_service: AdGroupBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked bid modifier service client and make it raise exception
    mock_bid_modifier_client = ad_group_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_ad_group_bid_modifiers.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_bid_modifier_service.create_device_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id="111",
            device_type="MOBILE",
            bid_modifier=1.2,
        )

    assert "Failed to create device bid modifier" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create device bid modifier: Test Google Ads Exception",
    )


def test_register_ad_group_bid_modifier_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_bid_modifier_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupBidModifierService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 6  # 6 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_ad_group_device_bid_modifier",
        "create_ad_group_hotel_check_in_day_bid_modifier",
        "create_ad_group_hotel_date_selection_bid_modifier",
        "update_ad_group_bid_modifier",
        "list_ad_group_bid_modifiers",
        "remove_ad_group_bid_modifier",
    ]

    assert set(tool_names) == set(expected_tools)
