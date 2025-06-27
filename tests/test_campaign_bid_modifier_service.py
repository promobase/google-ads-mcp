"""Tests for CampaignBidModifierService.

Note: In Google Ads API v20, CampaignBidModifier is only for interaction type bid modifiers.
For device, location, demographic, and ad schedule bid modifiers, use CampaignCriterion.
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.interaction_type import InteractionTypeEnum
from google.ads.googleads.v20.services.services.campaign_bid_modifier_service import (
    CampaignBidModifierServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_bid_modifier_service import (
    MutateCampaignBidModifiersResponse,
)

from src.sdk_services.campaign.campaign_bid_modifier_service import (
    CampaignBidModifierService,
    register_campaign_bid_modifier_tools,
)


@pytest.fixture
def campaign_bid_modifier_service(mock_sdk_client: Any) -> CampaignBidModifierService:
    """Create a CampaignBidModifierService instance with mocked dependencies."""
    # Mock CampaignBidModifierService client
    mock_bid_modifier_client = Mock(spec=CampaignBidModifierServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_bid_modifier_client  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignBidModifierService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_interaction_type_bid_modifier(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an interaction type bid modifier."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    interaction_type = InteractionTypeEnum.InteractionType.CALLS
    bid_modifier = 1.25

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        "customers/1234567890/campaignBidModifiers/111222333~12345"
    )
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = campaign_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": "customers/1234567890/campaignBidModifiers/111222333~12345"
            }
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = (
            await campaign_bid_modifier_service.create_interaction_type_bid_modifier(
                ctx=mock_ctx,
                customer_id=customer_id,
                campaign_id=campaign_id,
                interaction_type=interaction_type,
                bid_modifier=bid_modifier,
            )
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_campaign_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.create.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert operation.create.bid_modifier == bid_modifier
    assert operation.create.interaction_type.type_ == interaction_type

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created interaction type bid modifier for campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_update_bid_modifier(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an existing bid modifier."""
    # Arrange
    customer_id = "1234567890"
    bid_modifier_resource_name = (
        "customers/1234567890/campaignBidModifiers/111222333~12345"
    )
    new_bid_modifier = 1.75

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = bid_modifier_resource_name
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = campaign_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": bid_modifier_resource_name}]}

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_bid_modifier_service.update_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
            new_bid_modifier=new_bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_campaign_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.update.resource_name == bid_modifier_resource_name
    assert operation.update.bid_modifier == new_bid_modifier
    assert "bid_modifier" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated bid modifier to {new_bid_modifier}",
    )


@pytest.mark.asyncio
async def test_list_campaign_bid_modifiers(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign bid modifiers."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []

    # Add interaction type bid modifier
    interaction_row = Mock()
    interaction_row.campaign_bid_modifier = Mock()
    interaction_row.campaign_bid_modifier.resource_name = (
        "customers/1234567890/campaignBidModifiers/111222333~12345"
    )
    interaction_row.campaign_bid_modifier.bid_modifier = 1.25
    interaction_row.campaign_bid_modifier.criterion_id = 12345
    interaction_row.campaign_bid_modifier.interaction_type = Mock()
    interaction_row.campaign_bid_modifier.interaction_type.type_ = (
        InteractionTypeEnum.InteractionType.CALLS
    )
    interaction_row.campaign = Mock()
    interaction_row.campaign.id = campaign_id
    interaction_row.campaign.name = "Test Campaign"
    mock_results.append(interaction_row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_bid_modifier_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_bid_modifier_service.list_campaign_bid_modifiers(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    # Assert
    assert len(result) == 1

    # Check interaction type bid modifier
    assert result[0]["campaign_id"] == campaign_id
    assert result[0]["campaign_name"] == "Test Campaign"
    assert result[0]["bid_modifier"] == 1.25
    assert result[0]["criterion_id"] == "12345"
    assert result[0]["interaction_type"] == "CALLS"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"campaign.id = {campaign_id}" in query
    assert "FROM campaign_bid_modifier" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 1 campaign bid modifiers",
    )


@pytest.mark.asyncio
async def test_list_campaign_bid_modifiers_no_interaction_type(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign bid modifiers when interaction type is not set."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result with no interaction type
    mock_results = []
    row = Mock()
    row.campaign_bid_modifier = Mock()
    row.campaign_bid_modifier.resource_name = (
        "customers/1234567890/campaignBidModifiers/111222333~12345"
    )
    row.campaign_bid_modifier.bid_modifier = 1.5
    row.campaign_bid_modifier.criterion_id = None
    row.campaign_bid_modifier.interaction_type = None
    row.campaign = Mock()
    row.campaign.id = "111222333"
    row.campaign.name = "Test Campaign"
    mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_bid_modifier_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await campaign_bid_modifier_service.list_campaign_bid_modifiers(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 1
    assert result[0]["interaction_type"] is None


@pytest.mark.asyncio
async def test_remove_bid_modifier(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a campaign bid modifier."""
    # Arrange
    customer_id = "1234567890"
    bid_modifier_resource_name = (
        "customers/1234567890/campaignBidModifiers/111222333~12345"
    )

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBidModifiersResponse)
    mock_result = Mock()
    mock_result.resource_name = bid_modifier_resource_name
    mock_response.results = [mock_result]

    # Get the mocked bid modifier service client
    mock_bid_modifier_client = campaign_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": bid_modifier_resource_name}]}

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_bid_modifier_service.remove_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            bid_modifier_resource_name=bid_modifier_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.assert_called_once()  # type: ignore
    call_args = mock_bid_modifier_client.mutate_campaign_bid_modifiers.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == bid_modifier_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed campaign bid modifier",
    )


@pytest.mark.asyncio
async def test_error_handling_create_interaction_type_bid_modifier(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating interaction type bid modifier fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"
    interaction_type = InteractionTypeEnum.InteractionType.CALLS
    bid_modifier = 1.25

    # Get the mocked bid modifier service client and make it raise exception
    mock_bid_modifier_client = campaign_bid_modifier_service.client  # type: ignore
    mock_bid_modifier_client.mutate_campaign_bid_modifiers.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_bid_modifier_service.create_interaction_type_bid_modifier(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            interaction_type=interaction_type,
            bid_modifier=bid_modifier,
        )

    assert "Failed to create interaction type bid modifier" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create interaction type bid modifier: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_bid_modifiers(
    campaign_bid_modifier_service: CampaignBidModifierService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing bid modifiers fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return campaign_bid_modifier_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.campaign.campaign_bid_modifier_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await campaign_bid_modifier_service.list_campaign_bid_modifiers(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list campaign bid modifiers" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list campaign bid modifiers: Search failed",
    )


def test_register_campaign_bid_modifier_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_bid_modifier_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignBidModifierService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_interaction_type_bid_modifier",
        "update_bid_modifier",
        "list_campaign_bid_modifiers",
        "remove_bid_modifier",
    ]

    assert set(tool_names) == set(expected_tools)
