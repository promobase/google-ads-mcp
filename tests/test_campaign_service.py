"""Tests for CampaignService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_experiment_type import (
    CampaignExperimentTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v20.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_service import (
    MutateCampaignsResponse,
)

from src.services.campaign.campaign_service import (
    CampaignService,
    register_campaign_tools,
)


@pytest.fixture
def campaign_service(mock_sdk_client: Any) -> CampaignService:
    """Create a CampaignService instance with mocked dependencies."""
    # Mock CampaignService client
    mock_campaign_client = Mock(spec=CampaignServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_client  # type: ignore

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
    name = "Test Search Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/987654321"
    advertising_channel_type = AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    status = CampaignStatusEnum.CampaignStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
            advertising_channel_type=advertising_channel_type,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_client.mutate_campaigns.assert_called_once()  # type: ignore
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.campaign_budget == budget_resource_name
    assert operation.create.advertising_channel_type == advertising_channel_type
    assert operation.create.status == status
    assert (
        operation.create.experiment_type
        == CampaignExperimentTypeEnum.CampaignExperimentType.BASE
    )


@pytest.mark.asyncio
async def test_create_campaign_with_dates(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign with start and end dates."""
    # Arrange
    customer_id = "1234567890"
    name = "Limited Time Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/987654321"
    advertising_channel_type = AdvertisingChannelTypeEnum.AdvertisingChannelType.DISPLAY
    status = CampaignStatusEnum.CampaignStatus.ENABLED
    start_date = "2024-03-01"
    end_date = "2024-03-31"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
            advertising_channel_type=advertising_channel_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

    # Assert
    assert result == expected_result

    # Verify the dates were formatted correctly (removing dashes)
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.create.start_date == "20240301"
    assert operation.create.end_date == "20240331"


@pytest.mark.asyncio
async def test_create_campaign_shopping_channel(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a shopping campaign."""
    # Arrange
    customer_id = "1234567890"
    name = "Shopping Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/987654321"
    advertising_channel_type = (
        AdvertisingChannelTypeEnum.AdvertisingChannelType.SHOPPING
    )
    status = CampaignStatusEnum.CampaignStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
            advertising_channel_type=advertising_channel_type,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify shopping channel type was set
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert (
        operation.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.SHOPPING
    )


@pytest.mark.asyncio
async def test_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    new_name = "Updated Campaign Name"
    new_status = CampaignStatusEnum.CampaignStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
    mock_campaign_client.mutate_campaigns.assert_called_once()  # type: ignore
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
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
    assert set(operation.update_mask.paths) == {"name", "status"}

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated campaign {campaign_id} for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_update_campaign_dates_only(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only campaign dates."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    new_start_date = "2024-04-01"
    new_end_date = "2024-04-30"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
            start_date=new_start_date,
            end_date=new_end_date,
        )

    # Assert
    assert result == expected_result

    # Verify only dates were updated
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.update.start_date == "20240401"
    assert operation.update.end_date == "20240430"
    assert set(operation.update_mask.paths) == {"start_date", "end_date"}


@pytest.mark.asyncio
async def test_update_campaign_no_changes(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating campaign with no changes."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
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
        )

    # Assert
    assert result == expected_result

    # Verify update mask is empty
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert len(operation.update_mask.paths) == 0


@pytest.mark.asyncio
async def test_error_handling_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating campaign fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/987654321"

    # Get the mocked campaign service client and make it raise exception
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
        )

    assert "Failed to create campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create campaign: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating campaign fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    new_name = "Updated Name"

    # Get the mocked campaign service client and make it raise exception
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=new_name,
        )

    assert "Failed to update campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update campaign: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_tool_wrapper_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper for create_campaign with string enum conversion."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Campaign"
    budget_resource_name = "customers/1234567890/campaignBudgets/987654321"
    advertising_channel_type_str = "SEARCH"  # String input from tool
    status_str = "PAUSED"  # String input from tool

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
    }

    # Import the tool function
    from src.services.campaign.campaign_service import create_campaign_tools

    tools = create_campaign_tools(campaign_service)
    create_campaign_tool = tools[0]  # First tool

    with patch(
        "src.sdk_services.campaign.campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await create_campaign_tool(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
            advertising_channel_type=advertising_channel_type_str,
            status=status_str,
        )

    # Assert
    assert result == expected_result

    # Verify the enum conversions worked correctly
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert (
        operation.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    )
    assert operation.create.status == CampaignStatusEnum.CampaignStatus.PAUSED


@pytest.mark.asyncio
async def test_tool_wrapper_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper for update_campaign with string enum conversion."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    status_str = "ENABLED"  # String input from tool

    # Create mock response
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    # Get the mocked campaign service client
    mock_campaign_client = campaign_service.client  # type: ignore
    mock_campaign_client.mutate_campaigns.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
    }

    # Import the tool function
    from src.services.campaign.campaign_service import create_campaign_tools

    tools = create_campaign_tools(campaign_service)
    update_campaign_tool = tools[1]  # Second tool

    with patch(
        "src.sdk_services.campaign.campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await update_campaign_tool(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            status=status_str,
        )

    # Assert
    assert result == expected_result

    # Verify the enum conversion worked correctly
    call_args = mock_campaign_client.mutate_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.update.status == CampaignStatusEnum.CampaignStatus.ENABLED


def test_register_campaign_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = ["create_campaign", "update_campaign"]

    assert set(tool_names) == set(expected_tools)
