"""Tests for AdGroupService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.ad_group_status import AdGroupStatusEnum
from google.ads.googleads.v20.enums.types.ad_group_type import AdGroupTypeEnum
from google.ads.googleads.v20.services.services.ad_group_service import (
    AdGroupServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_service import (
    MutateAdGroupsResponse,
)

from src.sdk_services.ad_group.ad_group_service import (
    AdGroupService,
    register_ad_group_tools,
)


@pytest.fixture
def ad_group_service(mock_sdk_client: Any) -> AdGroupService:
    """Create an AdGroupService instance with mocked dependencies."""
    # Mock AdGroupService client
    mock_ad_group_service_client = Mock(spec=AdGroupServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_service_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_ad_group(
    ad_group_service: AdGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an ad group."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    name = "Test Ad Group"
    cpc_bid_micros = 1000000  # $1.00

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/adGroups/123"

    # Get the mocked ad group service client
    mock_ad_group_service_client = ad_group_service.client  # type: ignore
    mock_ad_group_service_client.mutate_ad_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/adGroups/123"}]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_service.create_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=AdGroupStatusEnum.AdGroupStatus.ENABLED,
            type=AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD,
            cpc_bid_micros=cpc_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_service_client.mutate_ad_groups.assert_called_once()  # type: ignore
    call_args = mock_ad_group_service_client.mutate_ad_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert operation.create.status == AdGroupStatusEnum.AdGroupStatus.ENABLED
    assert operation.create.type_ == AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD
    assert operation.create.cpc_bid_micros == cpc_bid_micros

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created ad group in campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_update_ad_group(
    ad_group_service: AdGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "123"
    new_name = "Updated Ad Group"
    new_status = AdGroupStatusEnum.AdGroupStatus.PAUSED
    new_cpc_bid_micros = 2000000  # $2.00

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

    # Get the mocked ad group service client
    mock_ad_group_service_client = ad_group_service.client  # type: ignore
    mock_ad_group_service_client.mutate_ad_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroups/{ad_group_id}"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_service.update_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            name=new_name,
            status=new_status,
            cpc_bid_micros=new_cpc_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_service_client.mutate_ad_groups.assert_called_once()  # type: ignore
    call_args = mock_ad_group_service_client.mutate_ad_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.update.name == new_name
    assert operation.update.status == new_status
    assert operation.update.cpc_bid_micros == new_cpc_bid_micros
    assert "name" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths
    assert "cpc_bid_micros" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad group {ad_group_id} for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_create_ad_group_with_cpm_bid(
    ad_group_service: AdGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an ad group with CPM bidding."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    name = "Display Ad Group"
    cpm_bid_micros = 5000000  # $5.00 CPM

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/adGroups/456"

    # Get the mocked ad group service client
    mock_ad_group_service_client = ad_group_service.client  # type: ignore
    mock_ad_group_service_client.mutate_ad_groups.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/adGroups/456"}]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_service.create_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=AdGroupStatusEnum.AdGroupStatus.ENABLED,
            type=AdGroupTypeEnum.AdGroupType.DISPLAY_STANDARD,
            cpm_bid_micros=cpm_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_service_client.mutate_ad_groups.assert_called_once()  # type: ignore
    call_args = mock_ad_group_service_client.mutate_ad_groups.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.cpm_bid_micros == cpm_bid_micros
    assert operation.create.type_ == AdGroupTypeEnum.AdGroupType.DISPLAY_STANDARD


@pytest.mark.asyncio
async def test_error_handling(
    ad_group_service: AdGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"

    # Get the mocked ad group service client and make it raise exception
    mock_ad_group_service_client = ad_group_service.client  # type: ignore
    mock_ad_group_service_client.mutate_ad_groups.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_service.create_ad_group(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name="Test Ad Group",
        )

    assert "Failed to create ad group" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create ad group: Test Google Ads Exception",
    )


def test_register_ad_group_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_ad_group",
        "update_ad_group",
    ]

    assert set(tool_names) == set(expected_tools)
