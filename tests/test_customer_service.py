"""Tests for the customer service."""

from typing import Any
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.sdk_services.account.customer_service import (
    CustomerService,
    create_customer_tools,
)


@pytest.fixture
def mock_sdk_client() -> Any:
    """Create a mock SDK client."""
    with patch("src.sdk_services.account.customer_service.get_sdk_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def customer_service(mock_sdk_client: Any) -> CustomerService:
    """Create a customer service instance."""
    return CustomerService()


@pytest.fixture
def mock_ctx() -> AsyncMock:
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.mark.asyncio
async def test_create_customer_client(
    customer_service: CustomerService, mock_ctx: AsyncMock, mock_sdk_client: Any
) -> None:
    """Test creating a customer client."""
    # Mock the customer service client
    mock_customer_service = MagicMock()
    mock_sdk_client.client.get_service.return_value = mock_customer_service

    # Mock the response
    mock_response = MagicMock()
    mock_response.resource_name = "customers/1234567890"
    mock_customer_service.create_customer_client.return_value = mock_response

    # Mock serialize_proto_message to return expected data
    expected_result = {
        "resource_name": "customers/1234567890",
        "customer_id": "1234567890",
        "descriptive_name": "Test Client",
        "currency_code": "USD",
        "time_zone": "America/New_York",
    }

    with patch(
        "src.sdk_services.account.customer_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Call the method
        result = await customer_service.create_customer_client(
            ctx=mock_ctx,
            manager_customer_id="123-456-7890",
            descriptive_name="Test Client",
            currency_code="USD",
            time_zone="America/New_York",
        )

    # Verify the result
    assert result == expected_result
    assert result["customer_id"] == "1234567890"
    assert result["descriptive_name"] == "Test Client"

    # Verify the API was called correctly
    mock_customer_service.create_customer_client.assert_called_once()
    call_args = mock_customer_service.create_customer_client.call_args
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert request.customer_client.descriptive_name == "Test Client"

    # Verify logging
    mock_ctx.log.assert_called_with(
        level="info",
        message="Created customer client 1234567890 under manager 1234567890",
    )


@pytest.mark.asyncio
async def test_list_accessible_customers(
    customer_service: CustomerService, mock_ctx: AsyncMock, mock_sdk_client: Any
) -> None:
    """Test listing accessible customers."""
    # Mock the customer service client
    mock_customer_service = MagicMock()
    mock_sdk_client.client.get_service.return_value = mock_customer_service

    # Mock the response
    mock_response = MagicMock()
    mock_response.resource_names = [
        "customers/1111111111",
        "customers/2222222222",
        "customers/3333333333",
    ]
    mock_customer_service.list_accessible_customers.return_value = mock_response

    # Call the method
    result = await customer_service.list_accessible_customers(ctx=mock_ctx)

    # Verify the result
    assert result == ["1111111111", "2222222222", "3333333333"]

    # Verify the API was called correctly
    mock_customer_service.list_accessible_customers.assert_called_once()

    # Verify logging
    mock_ctx.log.assert_called_with(
        level="info", message="Found 3 accessible customers"
    )


def test_create_customer_tools() -> None:
    """Test that tools are created correctly."""
    service = MagicMock()
    tools = create_customer_tools(service)

    # Should have 2 tools
    assert len(tools) == 2

    # Check tool names
    tool_names = [tool.__name__ for tool in tools]
    assert "create_customer_client" in tool_names
    assert "list_accessible_customers" in tool_names
