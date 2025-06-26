"""Tests for CampaignService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v20.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_service import (
    MutateCampaignsResponse,
)

from src.sdk_services.campaign.campaign_service import (
    CampaignService,
    register_campaign_tools,
)


@pytest.fixture
def campaign_service(mock_sdk_client: Any) -> CampaignService:
    """Create a CampaignService instance with mocked dependencies."""
    # Mock CampaignService client
    mock_campaign_service_client = Mock(spec=CampaignServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_service_client

    with patch(
        "src.sdk_services.campaign.campaign_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/999"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = "customers/1234567890/campaigns/123"

    # Get the mocked campaign service client
    mock_campaign_service_client = campaign_service.client  # type: ignore
    mock_campaign_service_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/123"}]
    }

    with patch(
        "src.sdk_services.campaign.campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
            advertising_channel_type=AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH,
            status=CampaignStatusEnum.CampaignStatus.PAUSED,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_service_client.mutate_campaigns.assert_called_once()  # type: ignore
    call_args = mock_campaign_service_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.campaign_budget == budget_resource_name
    assert (
        operation.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    )
    assert operation.create.status == CampaignStatusEnum.CampaignStatus.PAUSED
    assert operation.create.start_date == "20240101"  # Dates are reformatted
    assert operation.create.end_date == "20241231"


@pytest.mark.asyncio
async def test_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "123"
    new_name = "Updated Campaign"
    new_status = CampaignStatusEnum.CampaignStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

    # Get the mocked campaign service client
    mock_campaign_service_client = campaign_service.client  # type: ignore
    mock_campaign_service_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaigns/{campaign_id}"}
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=new_name,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_service_client.mutate_campaigns.assert_called_once()  # type: ignore
    call_args = mock_campaign_service_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert operation.update.name == new_name
    assert operation.update.status == new_status
    assert "name" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated campaign {campaign_id} for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked campaign service client and make it raise exception
    mock_campaign_service_client = campaign_service.client  # type: ignore
    mock_campaign_service_client.mutate_campaigns.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/999",
        )

    assert "Failed to create campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create campaign: Test Google Ads Exception",
    )


def test_register_campaign_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_campaign",
        "update_campaign",
    ]

    assert set(tool_names) == set(expected_tools)
