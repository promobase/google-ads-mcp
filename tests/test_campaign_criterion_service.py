"""Tests for CampaignCriterionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.device import DeviceEnum
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.services.services.campaign_criterion_service import (
    CampaignCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_criterion_service import (
    MutateCampaignCriteriaResponse,
)

from src.sdk_services.campaign.campaign_criterion_service import (
    CampaignCriterionService,
    register_campaign_criterion_tools,
)


@pytest.fixture
def campaign_criterion_service(mock_sdk_client: Any) -> CampaignCriterionService:
    """Create a CampaignCriterionService instance with mocked dependencies."""
    # Mock CampaignCriterionService client
    mock_campaign_criterion_client = Mock(spec=CampaignCriterionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_criterion_client

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignCriterionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_add_location_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding location criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    location_ids = ["1014044", "1007734"]  # California, Arizona
    negative = False
    bid_modifier = 1.2

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(location_ids):
        result = Mock()
        result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 100}"
        mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 100}"}
            for i in range(len(location_ids))
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(location_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == negative
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert criterion.location.geo_target_constant == f"geoTargetConstants/{location_ids[0]}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(location_ids)} location criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_location_criteria_negative(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative location criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    location_ids = ["1014045"]  # Florida
    negative = True

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~101"
    mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~101"}
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=1.5,  # Should be ignored for negative criteria
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.negative == negative
    # Bid modifier should not be set for negative criteria
    assert not hasattr(criterion, 'bid_modifier') or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_language_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding language criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    language_ids = ["1000", "1003"]  # English, Spanish

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(language_ids):
        result = Mock()
        result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 200}"
        mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 200}"}
            for i in range(len(language_ids))
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_language_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            language_ids=language_ids,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(language_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.language.language_constant == f"languageConstants/{language_ids[0]}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(language_ids)} language criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_device_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding device criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    device_types = [DeviceEnum.Device.MOBILE, DeviceEnum.Device.DESKTOP]
    bid_modifiers = {"MOBILE": 1.3, "DESKTOP": 0.9}

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(device_types):
        result = Mock()
        result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 300}"
        mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 300}"}
            for i in range(len(device_types))
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_device_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_types,
            bid_modifiers=bid_modifiers,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(device_types)

    # Check operations
    mobile_operation = request.operations[0]
    mobile_criterion = mobile_operation.create
    assert mobile_criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert mobile_criterion.negative == False
    assert mobile_criterion.device.type_ == DeviceEnum.Device.MOBILE
    assert abs(mobile_criterion.bid_modifier - 1.3) < 0.001

    desktop_operation = request.operations[1]
    desktop_criterion = desktop_operation.create
    assert desktop_criterion.device.type_ == DeviceEnum.Device.DESKTOP
    assert abs(desktop_criterion.bid_modifier - 0.9) < 0.001

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(device_types)} device criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_device_criteria_no_bid_modifiers(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding device criteria without bid modifiers."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    device_types = [DeviceEnum.Device.TABLET]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~301"
    mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~301"}
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_device_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_types,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.device.type_ == DeviceEnum.Device.TABLET
    # No bid modifier should be set
    assert not hasattr(criterion, 'bid_modifier') or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_negative_keyword_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative keyword criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    keywords = [
        {"text": "free", "match_type": "BROAD"},
        {"text": "cheap", "match_type": "PHRASE"},
        {"text": "discount", "match_type": "EXACT"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, keyword in enumerate(keywords):
        result = Mock()
        result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 400}"
        mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 400}"}
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_negative_keyword_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keywords=keywords,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(keywords)

    # Check operations
    for i, keyword in enumerate(keywords):
        operation = request.operations[i]
        criterion = operation.create
        assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
        assert criterion.negative == True
        assert criterion.keyword.text == keyword["text"]
        assert criterion.keyword.match_type == getattr(
            KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
        )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(keywords)} negative keywords to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_remove_campaign_criterion(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a campaign criterion."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    criterion_resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~500"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.sdk_services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.remove_campaign_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == criterion_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed campaign criterion: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"

    # Get the mocked campaign criterion service client and make it raise exception
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=["1014044"],
        )

    assert "Failed to add location criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add location criteria: Test Google Ads Exception",
    )


def test_register_campaign_criterion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_criterion_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignCriterionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "add_location_criteria",
        "add_language_criteria",
        "add_device_criteria",
        "add_negative_keyword_criteria",
        "remove_campaign_criterion",
    ]

    assert set(tool_names) == set(expected_tools)