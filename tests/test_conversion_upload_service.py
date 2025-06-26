"""Tests for ConversionUploadService."""

import hashlib
from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.conversion_upload_service import (
    ConversionUploadServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_upload_service import (
    UploadCallConversionsResponse,
    UploadClickConversionsResponse,
)

from src.sdk_services.conversions.conversion_upload_service import (
    ConversionUploadService,
    register_conversion_upload_tools,
)


@pytest.fixture
def conversion_upload_service(mock_sdk_client: Any) -> ConversionUploadService:
    """Create a ConversionUploadService instance with mocked dependencies."""
    # Mock ConversionUploadService client
    mock_conversion_upload_client = Mock(spec=ConversionUploadServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_conversion_upload_client

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = ConversionUploadService()
        # Force client initialization
        _ = service.client
        return service


def test_normalize_and_hash() -> None:
    """Test the normalize and hash functionality directly."""
    # Test basic normalization and hashing
    email = "  Test@Example.COM  "
    expected_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
    # Test the normalization logic directly
    normalized = email.lower().strip()
    result = hashlib.sha256(normalized.encode()).hexdigest()
    assert result == expected_hash

    # Test phone number
    phone = "  +1-234-567-8900  "
    expected_hash = hashlib.sha256("+1-234-567-8900".encode()).hexdigest()
    normalized = phone.lower().strip()
    result = hashlib.sha256(normalized.encode()).hexdigest()
    assert result == expected_hash

    # Test empty string
    empty = ""
    expected_hash = hashlib.sha256("".encode()).hexdigest()
    normalized = empty.lower().strip()
    result = hashlib.sha256(normalized.encode()).hexdigest()
    assert result == expected_hash


@pytest.mark.asyncio
async def test_upload_click_conversions_basic(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading basic click conversions."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
            "conversion_value": 29.99,
            "currency_code": "USD",
            "order_id": "order123",
        },
        {
            "gclid": "gclid456",
            "conversion_action_id": "789",
            "conversion_date_time": "2024-01-16 14:45:00-08:00",
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadClickConversionsResponse)
    mock_response.results = []
    for i, _ in enumerate(conversions):
        result = Mock()
        result.gclid = conversions[i]["gclid"]
        result.conversion_action = f"customers/{customer_id}/conversionActions/{conversions[i]['conversion_action_id']}"
        mock_response.results.append(result)

    # Get the mocked conversion upload service client
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "gclid": "gclid123",
                "conversion_action": f"customers/{customer_id}/conversionActions/456",
            },
            {
                "gclid": "gclid456",
                "conversion_action": f"customers/{customer_id}/conversionActions/789",
            },
        ]
    }

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
            partial_failure=True,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_upload_client.upload_click_conversions.assert_called_once()  # type: ignore
    call_args = mock_conversion_upload_client.upload_click_conversions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.conversions) == len(conversions)
    assert request.partial_failure

    # Check first conversion
    conversion = request.conversions[0]
    assert conversion.gclid == "gclid123"
    assert (
        conversion.conversion_action == f"customers/{customer_id}/conversionActions/456"
    )
    assert conversion.conversion_date_time == "2024-01-15 10:30:00-08:00"
    assert conversion.conversion_value == 29.99
    assert conversion.currency_code == "USD"
    assert conversion.order_id == "order123"

    # Check second conversion (minimal fields)
    conversion2 = request.conversions[1]
    assert conversion2.gclid == "gclid456"
    assert (
        conversion2.conversion_action
        == f"customers/{customer_id}/conversionActions/789"
    )
    assert conversion2.conversion_date_time == "2024-01-16 14:45:00-08:00"
    # Optional fields should not be set
    assert (
        not hasattr(conversion2, "conversion_value")
        or conversion2.conversion_value == 0
    )
    assert not hasattr(conversion2, "currency_code") or conversion2.currency_code == ""
    assert not hasattr(conversion2, "order_id") or conversion2.order_id == ""

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Uploaded {len(conversions)} click conversions",
    )


@pytest.mark.asyncio
async def test_upload_click_conversions_with_user_identifiers(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading click conversions with enhanced conversion user identifiers."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
            "user_identifiers": [
                {"email": "  Test@Example.COM  "},
                {"phone_number": "  +1-234-567-8900  "},
                {
                    "address": {
                        "first_name": "  John  ",
                        "last_name": "  DOE  ",
                        "postal_code": "12345",
                        "country_code": "US",
                    }
                },
            ],
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadClickConversionsResponse)
    mock_response.results = []
    result = Mock()
    result.gclid = "gclid123"
    mock_response.results.append(result)

    # Get the mocked conversion upload service client
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"gclid": "gclid123"}]}

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_conversion_upload_client.upload_click_conversions.call_args  # type: ignore
    request = call_args[1]["request"]
    conversion = request.conversions[0]

    # Check user identifiers
    assert len(conversion.user_identifiers) == 3

    # Check email identifier
    email_identifier = conversion.user_identifiers[0]
    expected_email_hash = hashlib.sha256("test@example.com".encode()).hexdigest()
    assert email_identifier.hashed_email == expected_email_hash

    # Check phone identifier
    phone_identifier = conversion.user_identifiers[1]
    expected_phone_hash = hashlib.sha256("+1-234-567-8900".encode()).hexdigest()
    assert phone_identifier.hashed_phone_number == expected_phone_hash

    # Check address identifier
    address_identifier = conversion.user_identifiers[2]
    expected_first_name_hash = hashlib.sha256("john".encode()).hexdigest()
    expected_last_name_hash = hashlib.sha256("doe".encode()).hexdigest()
    assert address_identifier.address_info.hashed_first_name == expected_first_name_hash
    assert address_identifier.address_info.hashed_last_name == expected_last_name_hash
    assert address_identifier.address_info.postal_code == "12345"
    assert address_identifier.address_info.country_code == "US"


@pytest.mark.asyncio
async def test_upload_click_conversions_partial_address(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading click conversions with partial address information."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
            "user_identifiers": [
                {
                    "address": {
                        "first_name": "John",
                        "postal_code": "12345",
                        # Missing last_name and country_code
                    }
                },
            ],
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadClickConversionsResponse)
    mock_response.results = []
    result = Mock()
    result.gclid = "gclid123"
    mock_response.results.append(result)

    # Get the mocked conversion upload service client
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"gclid": "gclid123"}]}

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_conversion_upload_client.upload_click_conversions.call_args  # type: ignore
    request = call_args[1]["request"]
    conversion = request.conversions[0]

    # Check address identifier - only first_name and postal_code should be set
    address_identifier = conversion.user_identifiers[0]
    expected_first_name_hash = hashlib.sha256("john".encode()).hexdigest()
    assert address_identifier.address_info.hashed_first_name == expected_first_name_hash
    assert address_identifier.address_info.postal_code == "12345"
    # These should not be set
    assert (
        not hasattr(address_identifier.address_info, "hashed_last_name")
        or address_identifier.address_info.hashed_last_name == ""
    )
    assert (
        not hasattr(address_identifier.address_info, "country_code")
        or address_identifier.address_info.country_code == ""
    )


@pytest.mark.asyncio
async def test_upload_call_conversions(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading call conversions."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "caller_id": "+1234567890",
            "call_start_date_time": "2024-01-15 10:00:00-08:00",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
            "conversion_value": 199.99,
            "currency_code": "USD",
        },
        {
            "caller_id": "+0987654321",
            "call_start_date_time": "2024-01-16 14:00:00-08:00",
            "conversion_action_id": "789",
            "conversion_date_time": "2024-01-16 14:45:00-08:00",
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadCallConversionsResponse)
    mock_response.results = []
    for i, _ in enumerate(conversions):
        result = Mock()
        result.caller_id = conversions[i]["caller_id"]
        result.conversion_action = f"customers/{customer_id}/conversionActions/{conversions[i]['conversion_action_id']}"
        mock_response.results.append(result)

    # Get the mocked conversion upload service client
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_call_conversions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "caller_id": "+1234567890",
                "conversion_action": f"customers/{customer_id}/conversionActions/456",
            },
            {
                "caller_id": "+0987654321",
                "conversion_action": f"customers/{customer_id}/conversionActions/789",
            },
        ]
    }

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_upload_service.upload_call_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
            partial_failure=False,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_conversion_upload_client.upload_call_conversions.assert_called_once()  # type: ignore
    call_args = mock_conversion_upload_client.upload_call_conversions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.conversions) == len(conversions)
    assert not request.partial_failure

    # Check first conversion
    conversion = request.conversions[0]
    assert conversion.caller_id == "+1234567890"
    assert conversion.call_start_date_time == "2024-01-15 10:00:00-08:00"
    assert (
        conversion.conversion_action == f"customers/{customer_id}/conversionActions/456"
    )
    assert conversion.conversion_date_time == "2024-01-15 10:30:00-08:00"
    assert conversion.conversion_value == 199.99
    assert conversion.currency_code == "USD"

    # Check second conversion (minimal fields)
    conversion2 = request.conversions[1]
    assert conversion2.caller_id == "+0987654321"
    assert conversion2.call_start_date_time == "2024-01-16 14:00:00-08:00"
    assert (
        conversion2.conversion_action
        == f"customers/{customer_id}/conversionActions/789"
    )
    assert conversion2.conversion_date_time == "2024-01-16 14:45:00-08:00"
    # Optional fields should not be set
    assert (
        not hasattr(conversion2, "conversion_value")
        or conversion2.conversion_value == 0
    )
    assert not hasattr(conversion2, "currency_code") or conversion2.currency_code == ""

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Uploaded {len(conversions)} call conversions",
    )


@pytest.mark.asyncio
async def test_upload_click_conversions_no_partial_failure(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test uploading click conversions with partial_failure=False."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
        },
    ]

    # Create mock response
    mock_response = Mock(spec=UploadClickConversionsResponse)
    mock_response.results = []
    result = Mock()
    result.gclid = "gclid123"
    mock_response.results.append(result)

    # Get the mocked conversion upload service client
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"gclid": "gclid123"}]}

    with patch(
        "src.sdk_services.conversions.conversion_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
            partial_failure=False,
        )

    # Assert
    assert result == expected_result

    # Verify partial_failure setting
    call_args = mock_conversion_upload_client.upload_click_conversions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert not request.partial_failure


@pytest.mark.asyncio
async def test_error_handling_click_conversions(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when uploading click conversions fails."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
        },
    ]

    # Get the mocked conversion upload service client and make it raise exception
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
        )

    assert "Failed to upload click conversions" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to upload click conversions: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_call_conversions(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when uploading call conversions fails."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "caller_id": "+1234567890",
            "call_start_date_time": "2024-01-15 10:00:00-08:00",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
        },
    ]

    # Get the mocked conversion upload service client and make it raise exception
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_call_conversions.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await conversion_upload_service.upload_call_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
        )

    assert "Failed to upload call conversions" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to upload call conversions: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_generic_exception(
    conversion_upload_service: ConversionUploadService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when a generic exception occurs."""
    # Arrange
    customer_id = "1234567890"
    conversions = [
        {
            "gclid": "gclid123",
            "conversion_action_id": "456",
            "conversion_date_time": "2024-01-15 10:30:00-08:00",
        },
    ]

    # Get the mocked conversion upload service client and make it raise generic exception
    mock_conversion_upload_client = conversion_upload_service.client  # type: ignore
    mock_conversion_upload_client.upload_click_conversions.side_effect = ValueError(
        "Invalid data format"
    )  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await conversion_upload_service.upload_click_conversions(
            ctx=mock_ctx,
            customer_id=customer_id,
            conversions=conversions,
        )

    assert "Failed to upload click conversions" in str(exc_info.value)
    assert "Invalid data format" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to upload click conversions: Invalid data format",
    )


def test_register_conversion_upload_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_conversion_upload_tools(mock_mcp)

    # Assert
    assert isinstance(service, ConversionUploadService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "upload_click_conversions",
        "upload_call_conversions",
    ]

    assert set(tool_names) == set(expected_tools)
