"""Tests for UserDataService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.user_data_service import (
    UserDataServiceClient,
)
from google.ads.googleads.v20.services.types.user_data_service import (
    UploadUserDataResponse,
)

from src.sdk_services.data_import.user_data_service import (
    UserDataService,
    register_user_data_tools,
)


@pytest.fixture
def user_data_service(mock_sdk_client: Any) -> UserDataService:
    """Create a UserDataService instance with mocked dependencies."""
    # Mock UserDataService client
    mock_user_data_client = Mock(spec=UserDataServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_user_data_client  # type: ignore

    with patch(
        "src.sdk_services.data_import.user_data_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = UserDataService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_upload_enhanced_conversions(
    user_data_service: UserDataService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading enhanced conversions."""
    # Arrange
    customer_id = "1234567890"
    conversion_adjustments = [
        {
            "user_identifiers": [
                {"hashed_email": "a1b2c3d4e5f6"},
                {"hashed_phone_number": "123456789"},
            ],
            "transaction_attribute": {
                "conversion_action": f"customers/{customer_id}/conversionActions/456",
                "currency_code": "USD",
                "transaction_amount_micros": 50000000,  # $50
                "transaction_date_time": "2024-01-15 10:30:00",
                "order_id": "ORDER123",
            },
        },
        {
            "user_identifiers": [
                {
                    "address_info": {
                        "hashed_first_name": "john123",
                        "hashed_last_name": "doe456",
                        "country_code": "US",
                        "postal_code": "12345",
                    }
                }
            ],
            "transaction_attribute": {
                "conversion_action": f"customers/{customer_id}/conversionActions/456",
                "currency_code": "USD",
                "transaction_amount_micros": 100000000,  # $100
                "transaction_date_time": "2024-01-16 14:20:00",
                "order_id": "ORDER456",
            },
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadUserDataResponse)
    mock_response.received_operations_count = 2
    mock_response.upload_date_time = "2024-01-20 12:00:00"
    mock_response.partial_failure_error = None

    # Get the mocked user data service client
    mock_user_data_client = user_data_service.client  # type: ignore
    mock_user_data_client.upload_user_data.return_value = mock_response  # type: ignore

    # Act
    result = await user_data_service.upload_enhanced_conversions(
        ctx=mock_ctx,
        customer_id=customer_id,
        conversion_adjustments=conversion_adjustments,
    )

    # Assert
    assert result["received_operations_count"] == 2
    assert result["upload_date_time"] == "2024-01-20 12:00:00"
    assert result["partial_failure_error"] is None

    # Verify the API call
    mock_user_data_client.upload_user_data.assert_called_once()  # type: ignore
    call_args = mock_user_data_client.upload_user_data.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 2

    # Check first operation
    op1 = request.operations[0]
    assert len(op1.create.user_identifiers) == 2
    assert op1.create.user_identifiers[0].hashed_email == "a1b2c3d4e5f6"
    assert op1.create.user_identifiers[1].hashed_phone_number == "123456789"
    assert (
        op1.create.transaction_attribute.conversion_action
        == f"customers/{customer_id}/conversionActions/456"
    )
    assert op1.create.transaction_attribute.transaction_amount_micros == 50000000

    # Check second operation
    op2 = request.operations[1]
    assert len(op2.create.user_identifiers) == 1
    assert op2.create.user_identifiers[0].address_info.hashed_first_name == "john123"
    assert op2.create.user_identifiers[0].address_info.country_code == "US"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Uploaded 2 enhanced conversion operations",
    )


@pytest.mark.asyncio
async def test_upload_customer_match_data(
    user_data_service: UserDataService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading customer match data."""
    # Arrange
    customer_id = "1234567890"
    user_list_id = "789"
    user_data_list = [
        {
            "user_identifiers": [
                {"hashed_email": "user1@example.com"},
                {"hashed_phone_number": "1234567890"},
            ],
            "user_attribute": {
                "lifetime_value_micros": 5000000000,  # $5000
                "shopping_loyalty": {"loyalty_tier": "GOLD"},
            },
        },
        {
            "user_identifiers": [
                {"mobile_id": "IDFA123456"},
                {"third_party_user_id": "USER789"},
            ],
        },
        {
            "user_identifiers": [
                {
                    "address_info": {
                        "hashed_first_name": "jane123",
                        "hashed_last_name": "smith456",
                        "country_code": "CA",
                        "postal_code": "M5V 3A8",
                        "hashed_street_address": "123mainst",
                    }
                }
            ],
            "user_attribute": {
                "lifetime_value_bucket": 5,
            },
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadUserDataResponse)
    mock_response.received_operations_count = 3
    mock_response.upload_date_time = "2024-01-20 13:00:00"
    mock_response.partial_failure_error = None

    # Get the mocked user data service client
    mock_user_data_client = user_data_service.client  # type: ignore
    mock_user_data_client.upload_user_data.return_value = mock_response  # type: ignore

    # Act
    result = await user_data_service.upload_customer_match_data(
        ctx=mock_ctx,
        customer_id=customer_id,
        user_list_id=user_list_id,
        user_data_list=user_data_list,
    )

    # Assert
    assert result["received_operations_count"] == 3
    assert result["upload_date_time"] == "2024-01-20 13:00:00"
    assert result["partial_failure_error"] is None

    # Verify the API call
    mock_user_data_client.upload_user_data.assert_called_once()  # type: ignore
    call_args = mock_user_data_client.upload_user_data.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Check customer match metadata
    assert (
        request.customer_match_user_list_metadata.user_list
        == f"customers/{customer_id}/userLists/{user_list_id}"
    )

    # Check first operation
    op1 = request.operations[0]
    assert len(op1.create.user_identifiers) == 2
    assert op1.create.user_identifiers[0].hashed_email == "user1@example.com"
    assert op1.create.user_attribute.lifetime_value_micros == 5000000000
    assert op1.create.user_attribute.shopping_loyalty.loyalty_tier == "GOLD"

    # Check second operation
    op2 = request.operations[1]
    assert len(op2.create.user_identifiers) == 2
    assert op2.create.user_identifiers[0].mobile_id == "IDFA123456"
    assert op2.create.user_identifiers[1].third_party_user_id == "USER789"

    # Check third operation
    op3 = request.operations[2]
    assert len(op3.create.user_identifiers) == 1
    assert op3.create.user_identifiers[0].address_info.country_code == "CA"
    assert op3.create.user_attribute.lifetime_value_bucket == 5

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Uploaded 3 customer match operations to user list {user_list_id}",
    )


@pytest.mark.asyncio
async def test_upload_store_sales_data(
    user_data_service: UserDataService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading store sales data."""
    # Arrange
    customer_id = "1234567890"
    conversion_action = f"customers/{customer_id}/conversionActions/456"
    store_sales_data = [
        {
            "user_identifiers": [
                {"hashed_email": "customer1@example.com"},
            ],
            "transaction_attribute": {
                "currency_code": "USD",
                "transaction_amount_micros": 150000000,  # $150
                "transaction_date_time": "2024-01-18 15:45:00",
                "order_id": "STORE-ORDER-001",
                "store_code": "STORE123",
            },
        },
        {
            "user_identifiers": [
                {"hashed_phone_number": "9876543210"},
            ],
            "transaction_attribute": {
                "currency_code": "USD",
                "transaction_amount_micros": 75000000,  # $75
                "transaction_date_time": "2024-01-19 10:15:00",
                "order_id": "STORE-ORDER-002",
                "store_code": "STORE456",
            },
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadUserDataResponse)
    mock_response.received_operations_count = 2
    mock_response.upload_date_time = "2024-01-20 14:00:00"
    mock_response.partial_failure_error = None

    # Get the mocked user data service client
    mock_user_data_client = user_data_service.client  # type: ignore
    mock_user_data_client.upload_user_data.return_value = mock_response  # type: ignore

    # Act
    result = await user_data_service.upload_store_sales_data(
        ctx=mock_ctx,
        customer_id=customer_id,
        conversion_action=conversion_action,
        store_sales_data=store_sales_data,
    )

    # Assert
    assert result["received_operations_count"] == 2
    assert result["upload_date_time"] == "2024-01-20 14:00:00"
    assert result["partial_failure_error"] is None

    # Verify the API call
    mock_user_data_client.upload_user_data.assert_called_once()  # type: ignore
    call_args = mock_user_data_client.upload_user_data.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 2

    # Note: store_sales_metadata is not available in v20 API
    # Store sales are identified by store_code in transaction_attribute

    # Check first operation
    op1 = request.operations[0]
    assert len(op1.create.user_identifiers) == 1
    assert op1.create.user_identifiers[0].hashed_email == "customer1@example.com"
    assert op1.create.transaction_attribute.conversion_action == conversion_action
    assert op1.create.transaction_attribute.transaction_amount_micros == 150000000
    assert op1.create.transaction_attribute.store_attribute.store_code == "STORE123"

    # Check second operation
    op2 = request.operations[1]
    assert len(op2.create.user_identifiers) == 1
    assert op2.create.user_identifiers[0].hashed_phone_number == "9876543210"
    assert op2.create.transaction_attribute.store_attribute.store_code == "STORE456"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Uploaded 2 store sales operations",
    )


@pytest.mark.asyncio
async def test_partial_failure_error(
    user_data_service: UserDataService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test handling partial failure errors."""
    # Arrange
    customer_id = "1234567890"
    conversion_adjustments = [
        {
            "user_identifiers": [{"hashed_email": "test@example.com"}],
            "transaction_attribute": {
                "conversion_action": f"customers/{customer_id}/conversionActions/456",
                "currency_code": "USD",
                "transaction_amount_micros": 10000000,
                "transaction_date_time": "2024-01-20 10:00:00",
            },
        }
    ]

    # Create mock response with partial failure
    mock_response = Mock(spec=UploadUserDataResponse)
    mock_response.received_operations_count = 1
    mock_response.upload_date_time = "2024-01-20 15:00:00"
    mock_response.partial_failure_error = Mock()
    mock_response.partial_failure_error.__str__ = Mock(  # type: ignore
        return_value="Partial failure: Invalid email format"
    )

    # Get the mocked user data service client
    mock_user_data_client = user_data_service.client  # type: ignore
    mock_user_data_client.upload_user_data.return_value = mock_response  # type: ignore

    # Act
    result = await user_data_service.upload_enhanced_conversions(
        ctx=mock_ctx,
        customer_id=customer_id,
        conversion_adjustments=conversion_adjustments,
    )

    # Assert
    assert result["received_operations_count"] == 1
    assert result["partial_failure_error"] == "Partial failure: Invalid email format"


@pytest.mark.asyncio
async def test_error_handling(
    user_data_service: UserDataService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked user data service client and make it raise exception
    mock_user_data_client = user_data_service.client  # type: ignore
    mock_user_data_client.upload_user_data.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await user_data_service.upload_enhanced_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversion_adjustments=[],
        )

    assert "Failed to upload enhanced conversions" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to upload enhanced conversions: Test Google Ads Exception",
    )


def test_register_user_data_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_user_data_tools(mock_mcp)

    # Assert
    assert isinstance(service, UserDataService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "upload_enhanced_conversions",
        "upload_customer_match_data",
        "upload_store_sales_data",
    ]

    assert set(tool_names) == set(expected_tools)
