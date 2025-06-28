"""Tests for BillingSetupService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.time_type import TimeTypeEnum
from google.ads.googleads.v20.services.services.billing_setup_service import (
    BillingSetupServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.billing_setup_service import (
    MutateBillingSetupResponse,
)

from src.services.account.billing_setup_service import (
    BillingSetupService,
    register_billing_setup_tools,
)


@pytest.fixture
def billing_setup_service(mock_sdk_client: Any) -> BillingSetupService:
    """Create a BillingSetupService instance with mocked dependencies."""
    # Mock BillingSetupService client
    mock_billing_setup_client = Mock(spec=BillingSetupServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_billing_setup_client  # type: ignore

    with patch(
        "src.sdk_services.account.billing_setup_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = BillingSetupService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_billing_setup(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a billing setup."""
    # Arrange
    customer_id = "1234567890"
    payments_account_id = "987654321"
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    start_time_type = TimeTypeEnum.TimeType.NOW
    end_time_type = TimeTypeEnum.TimeType.FOREVER

    # Create mock response
    mock_response = Mock(spec=MutateBillingSetupResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = "customers/1234567890/billingSetups/111222333"  # type: ignore

    # Get the mocked billing setup service client
    mock_billing_setup_client = billing_setup_service.client  # type: ignore
    mock_billing_setup_client.mutate_billing_setup.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "result": {"resource_name": "customers/1234567890/billingSetups/111222333"}
    }

    with patch(
        "src.sdk_services.account.billing_setup_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await billing_setup_service.create_billing_setup(
            ctx=mock_ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            start_date=start_date,
            end_date=end_date,
            start_time_type=start_time_type,
            end_time_type=end_time_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_billing_setup_client.mutate_billing_setup.assert_called_once()  # type: ignore
    call_args = mock_billing_setup_client.mutate_billing_setup.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    billing_setup = operation.create
    assert (
        billing_setup.payments_account
        == f"customers/{customer_id}/paymentsAccounts/{payments_account_id}"
    )
    # Since start_time_type is NOW, start_date_time should not be set
    assert billing_setup.start_time_type == start_time_type

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created billing setup for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_create_billing_setup_with_specific_start_date(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a billing setup with a specific start date."""
    # Arrange
    customer_id = "1234567890"
    payments_account_id = "987654321"
    start_date = "2024-03-01"
    start_time_type = TimeTypeEnum.TimeType.FOREVER  # Not NOW
    end_time_type = TimeTypeEnum.TimeType.FOREVER

    # Create mock response
    mock_response = Mock(spec=MutateBillingSetupResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = "customers/1234567890/billingSetups/111222333"  # type: ignore

    # Get the mocked billing setup service client
    mock_billing_setup_client = billing_setup_service.client  # type: ignore
    mock_billing_setup_client.mutate_billing_setup.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "result": {"resource_name": "customers/1234567890/billingSetups/111222333"}
    }

    with patch(
        "src.sdk_services.account.billing_setup_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await billing_setup_service.create_billing_setup(
            ctx=mock_ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            start_date=start_date,
            start_time_type=start_time_type,
            end_time_type=end_time_type,
        )

    # Assert
    assert result == expected_result

    # Verify the start date was set (not start_time_type)
    call_args = mock_billing_setup_client.mutate_billing_setup.call_args  # type: ignore
    request = call_args[1]["request"]
    billing_setup = request.operation.create
    assert billing_setup.start_date_time == start_date


@pytest.mark.asyncio
async def test_create_billing_setup_with_end_date(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a billing setup with a specific end date."""
    # Arrange
    customer_id = "1234567890"
    payments_account_id = "987654321"
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    start_time_type = TimeTypeEnum.TimeType.NOW
    end_time_type = TimeTypeEnum.TimeType.NOW  # Not FOREVER

    # Create mock response
    mock_response = Mock(spec=MutateBillingSetupResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = "customers/1234567890/billingSetups/111222333"  # type: ignore

    # Get the mocked billing setup service client
    mock_billing_setup_client = billing_setup_service.client  # type: ignore
    mock_billing_setup_client.mutate_billing_setup.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "result": {"resource_name": "customers/1234567890/billingSetups/111222333"}
    }

    with patch(
        "src.sdk_services.account.billing_setup_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await billing_setup_service.create_billing_setup(
            ctx=mock_ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            start_date=start_date,
            end_date=end_date,
            start_time_type=start_time_type,
            end_time_type=end_time_type,
        )

    # Assert
    assert result == expected_result

    # Verify the end date was set
    call_args = mock_billing_setup_client.mutate_billing_setup.call_args  # type: ignore
    request = call_args[1]["request"]
    billing_setup = request.operation.create
    assert billing_setup.end_time_type == end_time_type


@pytest.mark.asyncio
async def test_list_billing_setups(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing billing setups."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.billing_setup = Mock()
        row.billing_setup.resource_name = (
            f"customers/{customer_id}/billingSetups/{i + 100}"
        )
        row.billing_setup.id = i + 100
        row.billing_setup.status = Mock()
        row.billing_setup.status.name = "APPROVED" if i == 0 else "PENDING"
        row.billing_setup.payments_account = (
            f"customers/{customer_id}/paymentsAccounts/{i + 200}"
        )
        row.billing_setup.start_date_time = f"2024-0{i + 1}-01"
        row.billing_setup.start_time_type = Mock()
        row.billing_setup.start_time_type.name = "NOW"
        row.billing_setup.end_date_time = None
        row.billing_setup.end_time_type = Mock()
        row.billing_setup.end_time_type.name = "FOREVER"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message for each billing setup
    def serialize_side_effect(obj: Any):
        return {
            "resource_name": obj.resource_name,
            "id": obj.id,
            "status": obj.status.name,
            "payments_account": obj.payments_account,
            "start_date_time": obj.start_date_time,
            "start_time_type": obj.start_time_type.name,
            "end_date_time": obj.end_date_time,
            "end_time_type": obj.end_time_type.name,
        }

    with (
        patch(
            "src.sdk_services.account.billing_setup_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.billing_setup_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await billing_setup_service.list_billing_setups(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert first_result["id"] == 100
    assert first_result["status"] == "APPROVED"
    assert first_result["start_date_time"] == "2024-01-01"
    assert first_result["start_time_type"] == "NOW"
    assert first_result["end_time_type"] == "FOREVER"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM billing_setup" in query
    assert "ORDER BY billing_setup.id" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 billing setups",
    )


@pytest.mark.asyncio
async def test_list_billing_setups_with_status_filter(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing billing setups with status filter."""
    # Arrange
    customer_id = "1234567890"
    status_filter = "APPROVED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.billing_setup_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        await billing_setup_service.list_billing_setups(
            ctx=mock_ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    # Verify the search query includes the status filter
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"WHERE billing_setup.status = '{status_filter}'" in query


@pytest.mark.asyncio
async def test_get_billing_setup(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting a specific billing setup."""
    # Arrange
    customer_id = "1234567890"
    billing_setup_id = "111222333"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    row = Mock()
    row.billing_setup = Mock()
    row.billing_setup.resource_name = (
        f"customers/{customer_id}/billingSetups/{billing_setup_id}"
    )
    row.billing_setup.id = int(billing_setup_id)
    row.billing_setup.status = Mock()
    row.billing_setup.status.name = "APPROVED"
    row.billing_setup.payments_account = (
        f"customers/{customer_id}/paymentsAccounts/123456"
    )
    row.billing_setup.start_date_time = "2024-01-01"
    row.billing_setup.start_time_type = Mock()
    row.billing_setup.start_time_type.name = "NOW"
    row.billing_setup.end_date_time = None
    row.billing_setup.end_time_type = Mock()
    row.billing_setup.end_time_type.name = "FOREVER"

    mock_google_ads_service.search.return_value = [row]  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "resource_name": row.billing_setup.resource_name,
        "id": row.billing_setup.id,
        "status": row.billing_setup.status.name,
        "payments_account": row.billing_setup.payments_account,
        "start_date_time": row.billing_setup.start_date_time,
        "start_time_type": row.billing_setup.start_time_type.name,
        "end_date_time": row.billing_setup.end_date_time,
        "end_time_type": row.billing_setup.end_time_type.name,
    }

    with (
        patch(
            "src.sdk_services.account.billing_setup_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.billing_setup_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await billing_setup_service.get_billing_setup(
            ctx=mock_ctx,
            customer_id=customer_id,
            billing_setup_id=billing_setup_id,
        )

    # Assert
    assert result == expected_result

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"WHERE billing_setup.id = {billing_setup_id}" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found billing setup {billing_setup_id}",
    )


@pytest.mark.asyncio
async def test_get_billing_setup_not_found(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting a billing setup that doesn't exist."""
    # Arrange
    customer_id = "1234567890"
    billing_setup_id = "999999999"

    # Mock GoogleAdsService for search with empty results
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.billing_setup_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await billing_setup_service.get_billing_setup(
                ctx=mock_ctx,
                customer_id=customer_id,
                billing_setup_id=billing_setup_id,
            )

    assert f"Billing setup {billing_setup_id} not found" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message=f"Failed to get billing setup: Billing setup {billing_setup_id} not found",
    )


@pytest.mark.asyncio
async def test_list_payments_accounts(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing payments accounts."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(2):
        row = Mock()
        row.payments_account = Mock()
        row.payments_account.resource_name = (
            f"customers/{customer_id}/paymentsAccounts/{i + 100}"
        )
        row.payments_account.payments_account_id = f"PAY{i + 100}"
        row.payments_account.name = f"Payments Account {i + 1}"
        row.payments_account.currency_code = "USD"
        row.payments_account.payments_profile_id = f"PROF{i + 200}"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message for each payments account
    def serialize_side_effect(obj: Any):
        return {
            "resource_name": obj.resource_name,
            "payments_account_id": obj.payments_account_id,
            "name": obj.name,
            "currency_code": obj.currency_code,
            "payments_profile_id": obj.payments_profile_id,
        }

    with (
        patch(
            "src.sdk_services.account.billing_setup_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.billing_setup_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await billing_setup_service.list_payments_accounts(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 2

    # Check first result
    first_result = result[0]
    assert first_result["payments_account_id"] == "PAY100"
    assert first_result["name"] == "Payments Account 1"
    assert first_result["currency_code"] == "USD"
    assert first_result["payments_profile_id"] == "PROF200"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM payments_account" in query
    assert "ORDER BY payments_account.name" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 payments accounts",
    )


@pytest.mark.asyncio
async def test_error_handling_create_billing_setup(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating billing setup fails."""
    # Arrange
    customer_id = "1234567890"
    payments_account_id = "987654321"
    start_date = "2024-01-01"

    # Get the mocked billing setup service client and make it raise exception
    mock_billing_setup_client = billing_setup_service.client  # type: ignore
    mock_billing_setup_client.mutate_billing_setup.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await billing_setup_service.create_billing_setup(
            ctx=mock_ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            start_date=start_date,
        )

    assert "Failed to create billing setup" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create billing setup: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_billing_setups(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing billing setups fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.billing_setup_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await billing_setup_service.list_billing_setups(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list billing setups" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list billing setups: Search failed",
    )


@pytest.mark.asyncio
async def test_error_handling_list_payments_accounts(
    billing_setup_service: BillingSetupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing payments accounts fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return billing_setup_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.billing_setup_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await billing_setup_service.list_payments_accounts(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list payments accounts" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list payments accounts: Search failed",
    )


def test_register_billing_setup_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_billing_setup_tools(mock_mcp)

    # Assert
    assert isinstance(service, BillingSetupService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_billing_setup",
        "list_billing_setups",
        "get_billing_setup",
        "list_payments_accounts",
    ]

    assert set(tool_names) == set(expected_tools)
