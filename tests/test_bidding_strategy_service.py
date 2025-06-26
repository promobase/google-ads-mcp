"""Tests for BiddingStrategyService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.bidding_strategy_status import (
    BiddingStrategyStatusEnum,
)
from google.ads.googleads.v20.enums.types.bidding_strategy_type import (
    BiddingStrategyTypeEnum,
)
from google.ads.googleads.v20.enums.types.target_impression_share_location import (
    TargetImpressionShareLocationEnum,
)
from google.ads.googleads.v20.services.services.bidding_strategy_service import (
    BiddingStrategyServiceClient,
)
from google.ads.googleads.v20.services.types.bidding_strategy_service import (
    MutateBiddingStrategiesResponse,
)

from src.sdk_services.bidding.bidding_strategy_service import (
    BiddingStrategyService,
    register_bidding_strategy_tools,
)


@pytest.fixture
def bidding_strategy_service(mock_sdk_client: Any) -> BiddingStrategyService:
    """Create a BiddingStrategyService instance with mocked dependencies."""
    # Mock BiddingStrategyService client
    mock_bidding_strategy_client = Mock(spec=BiddingStrategyServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_bidding_strategy_client

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = BiddingStrategyService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_target_cpa_strategy(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Target CPA bidding strategy."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Target CPA Strategy"
    target_cpa_micros = 50000000  # $50.00
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingStrategiesResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/biddingStrategies/123"

    # Get the mocked bidding strategy service client
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/biddingStrategies/123"}]
    }

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_strategy_service.create_target_cpa_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bidding_strategy_client.mutate_bidding_strategies.assert_called_once()  # type: ignore
    call_args = mock_bidding_strategy_client.mutate_bidding_strategies.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.status
        == BiddingStrategyStatusEnum.BiddingStrategyStatus.ENABLED
    )
    assert (
        operation.create.type_ == BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_CPA
    )
    assert operation.create.target_cpa.target_cpa_micros == target_cpa_micros

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created Target CPA strategy '{name}' with target {target_cpa_micros} micros",
    )


@pytest.mark.asyncio
async def test_create_target_roas_strategy(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Target ROAS bidding strategy."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Target ROAS Strategy"
    target_roas = 4.0  # 400% ROAS
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingStrategiesResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/biddingStrategies/456"

    # Get the mocked bidding strategy service client
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/biddingStrategies/456"}]
    }

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_strategy_service.create_target_roas_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            target_roas=target_roas,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bidding_strategy_client.mutate_bidding_strategies.assert_called_once()  # type: ignore
    call_args = mock_bidding_strategy_client.mutate_bidding_strategies.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.status
        == BiddingStrategyStatusEnum.BiddingStrategyStatus.ENABLED
    )
    assert (
        operation.create.type_
        == BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_ROAS
    )
    assert operation.create.target_roas.target_roas == target_roas

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created Target ROAS strategy '{name}' with target {target_roas}",
    )


@pytest.mark.asyncio
async def test_create_maximize_conversions_strategy(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Maximize Conversions bidding strategy."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Maximize Conversions Strategy"
    target_cpa_micros = 30000000  # $30.00
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingStrategiesResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/biddingStrategies/789"

    # Get the mocked bidding strategy service client
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/biddingStrategies/789"}]
    }

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_strategy_service.create_maximize_conversions_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bidding_strategy_client.mutate_bidding_strategies.assert_called_once()  # type: ignore
    call_args = mock_bidding_strategy_client.mutate_bidding_strategies.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.status
        == BiddingStrategyStatusEnum.BiddingStrategyStatus.ENABLED
    )
    assert (
        operation.create.type_
        == BiddingStrategyTypeEnum.BiddingStrategyType.MAXIMIZE_CONVERSIONS
    )
    assert operation.create.maximize_conversions.target_cpa_micros == target_cpa_micros

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created Maximize Conversions strategy '{name}'",
    )


@pytest.mark.asyncio
async def test_create_maximize_conversions_strategy_without_target(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Maximize Conversions strategy without target CPA."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Maximize Conversions No Target"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingStrategiesResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/biddingStrategies/999"

    # Get the mocked bidding strategy service client
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/biddingStrategies/999"}]
    }

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_strategy_service.create_maximize_conversions_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=None,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bidding_strategy_client.mutate_bidding_strategies.assert_called_once()  # type: ignore
    call_args = mock_bidding_strategy_client.mutate_bidding_strategies.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Check that maximize_conversions is set but target_cpa_micros is not
    assert operation.create.maximize_conversions is not None
    # We can't easily check if target_cpa_micros is not set without accessing the proto


@pytest.mark.asyncio
async def test_create_target_impression_share_strategy(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Target Impression Share bidding strategy."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Target Impression Share Strategy"
    location = "TOP_OF_PAGE"
    location_fraction_micros = 650000  # 65%
    max_cpc_bid_ceiling_micros = 2000000  # $2.00
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateBiddingStrategiesResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/biddingStrategies/555"

    # Get the mocked bidding strategy service client
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/biddingStrategies/555"}]
    }

    with patch(
        "src.sdk_services.bidding.bidding_strategy_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await bidding_strategy_service.create_target_impression_share_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            location=location,
            location_fraction_micros=location_fraction_micros,
            max_cpc_bid_ceiling_micros=max_cpc_bid_ceiling_micros,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_bidding_strategy_client.mutate_bidding_strategies.assert_called_once()  # type: ignore
    call_args = mock_bidding_strategy_client.mutate_bidding_strategies.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.status
        == BiddingStrategyStatusEnum.BiddingStrategyStatus.ENABLED
    )
    assert (
        operation.create.type_
        == BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_IMPRESSION_SHARE
    )
    assert (
        operation.create.target_impression_share.location
        == TargetImpressionShareLocationEnum.TargetImpressionShareLocation.TOP_OF_PAGE
    )
    assert (
        operation.create.target_impression_share.location_fraction_micros
        == location_fraction_micros
    )
    assert (
        operation.create.target_impression_share.cpc_bid_ceiling_micros
        == max_cpc_bid_ceiling_micros
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created Target Impression Share strategy '{name}'",
    )


@pytest.mark.asyncio
async def test_error_handling(
    bidding_strategy_service: BiddingStrategyService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked bidding strategy service client and make it raise exception
    mock_bidding_strategy_client = bidding_strategy_service.client  # type: ignore
    mock_bidding_strategy_client.mutate_bidding_strategies.side_effect = (  # pyright: ignore
        google_ads_exception
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await bidding_strategy_service.create_target_cpa_strategy(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Strategy",
            target_cpa_micros=50000000,
        )

    assert "Failed to create Target CPA strategy" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create Target CPA strategy: Test Google Ads Exception",
    )


def test_register_bidding_strategy_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_bidding_strategy_tools(mock_mcp)

    # Assert
    assert isinstance(service, BiddingStrategyService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_target_cpa_strategy",
        "create_target_roas_strategy",
        "create_maximize_conversions_strategy",
        "create_target_impression_share_strategy",
    ]

    assert set(tool_names) == set(expected_tools)
