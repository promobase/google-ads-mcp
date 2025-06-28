"""Tests for ConversionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.attribution_model import (
    AttributionModelEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_category import (
    ConversionActionCategoryEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_counting_type import (
    ConversionActionCountingTypeEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_status import (
    ConversionActionStatusEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_type import (
    ConversionActionTypeEnum,
)
from google.ads.googleads.v20.enums.types.data_driven_model_status import (
    DataDrivenModelStatusEnum,
)
from google.ads.googleads.v20.services.services.conversion_action_service import (
    ConversionActionServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_action_service import (
    MutateConversionActionsResponse,
)

from src.services.conversions.conversion_service import (
    ConversionService,
    register_conversion_tools,
)


@pytest.fixture
def conversion_service(mock_sdk_client: Any) -> ConversionService:
    """Create a ConversionService instance with mocked dependencies."""
    # Mock ConversionActionService client
    mock_conversion_action_client = Mock(spec=ConversionActionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_conversion_action_client  # type: ignore

    with patch(
        "src.sdk_services.conversions.conversion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = ConversionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_conversion_action(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a conversion action."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Conversion Action"
    category = "PURCHASE"
    type = "WEBPAGE"
    status = "ENABLED"
    value_settings = {
        "default_value": 50.0,
        "always_use_default_value": False,
    }
    counting_type = "ONE_PER_CLICK"
    attribution_model = "GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN"
    click_through_lookback_window_days = 30
    view_through_lookback_window_days = 1

    # Create mock response
    mock_response = Mock(spec=MutateConversionActionsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/conversionActions/123"

    # Get the mocked conversion action service client
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/conversionActions/123"}]
    }

    with patch(
        "src.sdk_services.conversions.conversion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_service.create_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            category=category,
            type=type,
            status=status,
            value_settings=value_settings,
            counting_type=counting_type,
            attribution_model=attribution_model,
            click_through_lookback_window_days=click_through_lookback_window_days,
            view_through_lookback_window_days=view_through_lookback_window_days,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_action_client.mutate_conversion_actions.assert_called_once()  # type: ignore
    call_args = mock_conversion_action_client.mutate_conversion_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert (
        operation.create.status
        == ConversionActionStatusEnum.ConversionActionStatus.ENABLED
    )
    assert (
        operation.create.type_ == ConversionActionTypeEnum.ConversionActionType.WEBPAGE
    )
    assert (
        operation.create.category
        == ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE
    )
    assert (
        operation.create.counting_type
        == ConversionActionCountingTypeEnum.ConversionActionCountingType.ONE_PER_CLICK
    )

    # Check value settings
    assert operation.create.value_settings.default_value == 50.0
    assert operation.create.value_settings.always_use_default_value is False

    # Check attribution settings
    assert (
        operation.create.attribution_model_settings.attribution_model
        == AttributionModelEnum.AttributionModel.GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN
    )
    assert (
        operation.create.attribution_model_settings.data_driven_model_status
        == DataDrivenModelStatusEnum.DataDrivenModelStatus.AVAILABLE
    )

    # Check lookback windows
    assert operation.create.click_through_lookback_window_days == 30
    assert operation.create.view_through_lookback_window_days == 1


@pytest.mark.asyncio
async def test_create_conversion_action_with_defaults(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a conversion action with default value settings."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Conversion Action"

    # Create mock response
    mock_response = Mock(spec=MutateConversionActionsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/conversionActions/456"

    # Get the mocked conversion action service client
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/conversionActions/456"}]
    }

    with patch(
        "src.sdk_services.conversions.conversion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_service.create_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_action_client.mutate_conversion_actions.assert_called_once()  # type: ignore
    call_args = mock_conversion_action_client.mutate_conversion_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Check default value settings
    assert operation.create.value_settings.default_value == 0
    assert operation.create.value_settings.always_use_default_value is False


@pytest.mark.asyncio
async def test_update_conversion_action(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a conversion action."""
    # Arrange
    customer_id = "1234567890"
    conversion_action_id = "123"
    name = "Updated Conversion Action"
    status = "REMOVED"
    default_value = 100.0
    always_use_default_value = True
    counting_type = "MANY_PER_CLICK"

    # Create mock response
    mock_response = Mock(spec=MutateConversionActionsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = (
        f"customers/{customer_id}/conversionActions/{conversion_action_id}"
    )

    # Get the mocked conversion action service client
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.conversions.conversion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_service.update_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversion_action_id=conversion_action_id,
            name=name,
            status=status,
            default_value=default_value,
            always_use_default_value=always_use_default_value,
            counting_type=counting_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_action_client.mutate_conversion_actions.assert_called_once()  # type: ignore
    call_args = mock_conversion_action_client.mutate_conversion_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/conversionActions/{conversion_action_id}"
    )
    assert operation.update.name == name
    assert (
        operation.update.status
        == ConversionActionStatusEnum.ConversionActionStatus.REMOVED
    )
    assert (
        operation.update.counting_type
        == ConversionActionCountingTypeEnum.ConversionActionCountingType.MANY_PER_CLICK
    )

    # Check value settings
    assert operation.update.value_settings.default_value == default_value
    assert operation.update.value_settings.always_use_default_value is True

    # Check update mask
    assert "name" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths
    assert "counting_type" in operation.update_mask.paths
    assert "value_settings.default_value" in operation.update_mask.paths
    assert "value_settings.always_use_default_value" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated conversion action {conversion_action_id}",
    )


@pytest.mark.asyncio
async def test_update_conversion_action_partial(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test partially updating a conversion action."""
    # Arrange
    customer_id = "1234567890"
    conversion_action_id = "123"
    name = "Updated Name Only"

    # Create mock response
    mock_response = Mock(spec=MutateConversionActionsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = (
        f"customers/{customer_id}/conversionActions/{conversion_action_id}"
    )

    # Get the mocked conversion action service client
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.conversions.conversion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_service.update_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversion_action_id=conversion_action_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_action_client.mutate_conversion_actions.assert_called_once()  # type: ignore
    call_args = mock_conversion_action_client.mutate_conversion_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Check update mask - only name should be in the mask
    assert "name" in operation.update_mask.paths
    assert "status" not in operation.update_mask.paths
    assert "counting_type" not in operation.update_mask.paths
    assert "value_settings.default_value" not in operation.update_mask.paths
    assert "value_settings.always_use_default_value" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_update_conversion_action_value_settings_only(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only value settings of a conversion action."""
    # Arrange
    customer_id = "1234567890"
    conversion_action_id = "123"
    default_value = 75.0

    # Create mock response
    mock_response = Mock(spec=MutateConversionActionsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = (
        f"customers/{customer_id}/conversionActions/{conversion_action_id}"
    )

    # Get the mocked conversion action service client
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.conversions.conversion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_service.update_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversion_action_id=conversion_action_id,
            default_value=default_value,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_action_client.mutate_conversion_actions.assert_called_once()  # type: ignore
    call_args = mock_conversion_action_client.mutate_conversion_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Check value settings
    assert operation.update.value_settings.default_value == default_value

    # Check update mask - only value_settings.default_value should be in the mask
    assert "value_settings.default_value" in operation.update_mask.paths
    assert "value_settings.always_use_default_value" not in operation.update_mask.paths
    assert "name" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_error_handling(
    conversion_service: ConversionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked conversion action service client and make it raise exception
    mock_conversion_action_client = conversion_service.client  # type: ignore
    mock_conversion_action_client.mutate_conversion_actions.side_effect = (  # pyright: ignore  # type: ignore
        google_ads_exception
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await conversion_service.create_conversion_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Conversion",
        )

    assert "Failed to create conversion action" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create conversion action: Test Google Ads Exception",
    )


def test_register_conversion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_conversion_tools(mock_mcp)

    # Assert
    assert isinstance(service, ConversionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_conversion_action",
        "update_conversion_action",
    ]

    assert set(tool_names) == set(expected_tools)
