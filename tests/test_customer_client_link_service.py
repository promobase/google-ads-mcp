"""Tests for CustomerClientLinkService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.manager_link_status import (
    ManagerLinkStatusEnum,
)
from google.ads.googleads.v20.services.services.customer_client_link_service import (
    CustomerClientLinkServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.customer_client_link_service import (
    MutateCustomerClientLinkResponse,
)

from src.sdk_services.account.customer_client_link_service import (
    CustomerClientLinkService,
    register_customer_client_link_tools,
)


@pytest.fixture
def customer_client_link_service(mock_sdk_client: Any) -> CustomerClientLinkService:
    """Create a CustomerClientLinkService instance with mocked dependencies."""
    # Mock CustomerClientLinkService client
    mock_customer_client_link_client = Mock(spec=CustomerClientLinkServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_customer_client_link_client  # type: ignore

    with patch(
        "src.sdk_services.account.customer_client_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CustomerClientLinkService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_customer_client_link(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a customer client link."""
    # Arrange
    customer_id = "1234567890"
    client_customer = "customers/987654321"
    status = ManagerLinkStatusEnum.ManagerLinkStatus.PENDING
    hidden = False

    # Create mock response
    mock_response = Mock(spec=MutateCustomerClientLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (  # type: ignore
        "customers/1234567890/customerClientLinks/111222333"
    )

    # Get the mocked customer client link service client
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/customerClientLinks/111222333"
        }
    }

    with patch(
        "src.sdk_services.account.customer_client_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_client_link_service.create_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            client_customer=client_customer,
            status=status,
            hidden=hidden,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_customer_client_link_client.mutate_customer_client_link.assert_called_once()  # type: ignore
    call_args = mock_customer_client_link_client.mutate_customer_client_link.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    link = operation.create
    assert link.client_customer == client_customer
    assert link.status == status
    assert link.hidden == hidden


@pytest.mark.asyncio
async def test_create_customer_client_link_with_hidden(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a customer client link with hidden flag."""
    # Arrange
    customer_id = "1234567890"
    client_customer = "customers/987654321"
    status = ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE
    hidden = True

    # Create mock response
    mock_response = Mock(spec=MutateCustomerClientLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (  # type: ignore
        "customers/1234567890/customerClientLinks/111222333"
    )

    # Get the mocked customer client link service client
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/customerClientLinks/111222333"
        }
    }

    with patch(
        "src.sdk_services.account.customer_client_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_client_link_service.create_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            client_customer=client_customer,
            status=status,
            hidden=hidden,
        )

    # Assert
    assert result == expected_result

    # Verify the hidden flag was set
    call_args = mock_customer_client_link_client.mutate_customer_client_link.call_args  # type: ignore
    request = call_args[1]["request"]
    link = request.operation.create
    assert link.hidden == True


@pytest.mark.asyncio
async def test_update_customer_client_link(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a customer client link."""
    # Arrange
    customer_id = "1234567890"
    link_resource_name = "customers/1234567890/customerClientLinks/111222333"
    new_status = ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE
    new_hidden = True

    # Create mock response
    mock_response = Mock(spec=MutateCustomerClientLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = link_resource_name  # type: ignore

    # Get the mocked customer client link service client
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": link_resource_name}}

    with patch(
        "src.sdk_services.account.customer_client_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_client_link_service.update_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            link_resource_name=link_resource_name,
            status=new_status,
            hidden=new_hidden,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_customer_client_link_client.mutate_customer_client_link.assert_called_once()  # type: ignore
    call_args = mock_customer_client_link_client.mutate_customer_client_link.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.update.resource_name == link_resource_name
    assert operation.update.status == new_status
    assert operation.update.hidden == new_hidden
    assert set(operation.update_mask.paths) == {"status", "hidden"}

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Updated customer client link",
    )


@pytest.mark.asyncio
async def test_update_customer_client_link_status_only(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only the status of a customer client link."""
    # Arrange
    customer_id = "1234567890"
    link_resource_name = "customers/1234567890/customerClientLinks/111222333"
    new_status = ManagerLinkStatusEnum.ManagerLinkStatus.CANCELED

    # Create mock response
    mock_response = Mock(spec=MutateCustomerClientLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = link_resource_name  # type: ignore

    # Get the mocked customer client link service client
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": link_resource_name}}

    with patch(
        "src.sdk_services.account.customer_client_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_client_link_service.update_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            link_resource_name=link_resource_name,
            status=new_status,
            hidden=None,
        )

    # Assert
    assert result == expected_result

    # Verify only status is in update mask
    call_args = mock_customer_client_link_client.mutate_customer_client_link.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operation
    assert operation.update.status == new_status
    assert operation.update_mask.paths == ["status"]


@pytest.mark.asyncio
async def test_list_customer_client_links(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing customer client links."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        # Mock customer client link
        row.customer_client_link = Mock()
        row.customer_client_link.resource_name = (
            f"customers/{customer_id}/customerClientLinks/{i + 100}"
        )
        row.customer_client_link.client_customer = f"customers/{i + 200}"
        row.customer_client_link.manager_link_id = i + 100
        row.customer_client_link.status = Mock()
        row.customer_client_link.status.name = "ACTIVE" if i == 0 else "PENDING"
        row.customer_client_link.hidden = i == 2  # Last one is hidden

        # Mock customer client details
        row.customer_client = Mock()
        row.customer_client.descriptive_name = f"Client {i + 1}"
        row.customer_client.manager = False
        row.customer_client.test_account = False
        row.customer_client.auto_tagging_enabled = True
        row.customer_client.id = i + 200
        row.customer_client.time_zone = "America/New_York"
        row.customer_client.currency_code = "USD"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return customer_client_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Create expected results
    expected_links = []
    expected_clients = []

    for i in range(3):
        expected_links.append(
            {
                "resource_name": f"customers/{customer_id}/customerClientLinks/{i + 100}",
                "client_customer": f"customers/{i + 200}",
                "manager_link_id": i + 100,
                "status": "ACTIVE" if i == 0 else "PENDING",
                "hidden": i == 2,
            }
        )
        expected_clients.append(
            {
                "descriptive_name": f"Client {i + 1}",
                "manager": False,
                "test_account": False,
                "auto_tagging_enabled": True,
                "id": i + 200,
                "time_zone": "America/New_York",
                "currency_code": "USD",
            }
        )

    # Mock serialize_proto_message to return expected results
    serialize_call_count = 0

    def serialize_side_effect(obj: Any):
        nonlocal serialize_call_count
        # For each row, we serialize link first, then client
        # So calls 0, 2, 4 are links; calls 1, 3, 5 are clients
        if serialize_call_count % 2 == 0:  # Even calls are links
            result = expected_links[serialize_call_count // 2]
        else:  # Odd calls are clients
            result = expected_clients[serialize_call_count // 2]
        serialize_call_count += 1
        return result

    with (
        patch(
            "src.sdk_services.account.customer_client_link_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.customer_client_link_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await customer_client_link_service.list_customer_client_links(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert first_result["manager_link_id"] == 100
    assert first_result["status"] == "ACTIVE"
    assert first_result["hidden"] == False
    assert "client_details" in first_result
    assert first_result["client_details"]["descriptive_name"] == "Client 1"
    assert first_result["client_details"]["currency_code"] == "USD"

    # Check last result (hidden)
    last_result = result[2]
    assert last_result["hidden"] == True

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM customer_client_link" in query
    assert "ORDER BY customer_client_link.manager_link_id DESC" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 customer client links",
    )


@pytest.mark.asyncio
async def test_list_customer_client_links_with_status_filter(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing customer client links with status filter."""
    # Arrange
    customer_id = "1234567890"
    status_filter = "PENDING"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return customer_client_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.customer_client_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        await customer_client_link_service.list_customer_client_links(
            ctx=mock_ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    # Verify the search query includes the status filter
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert f"WHERE customer_client_link.status = '{status_filter}'" in query


@pytest.mark.asyncio
async def test_error_handling_create_customer_client_link(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating customer client link fails."""
    # Arrange
    customer_id = "1234567890"
    client_customer = "customers/987654321"

    # Get the mocked customer client link service client and make it raise exception
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await customer_client_link_service.create_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            client_customer=client_customer,
        )

    assert "Failed to create customer client link" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create customer client link: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_customer_client_link(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating customer client link fails."""
    # Arrange
    customer_id = "1234567890"
    link_resource_name = "customers/1234567890/customerClientLinks/111222333"

    # Get the mocked customer client link service client and make it raise exception
    mock_customer_client_link_client = customer_client_link_service.client  # type: ignore
    mock_customer_client_link_client.mutate_customer_client_link.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await customer_client_link_service.update_customer_client_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            link_resource_name=link_resource_name,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE,
        )

    assert "Failed to update customer client link" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update customer client link: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_customer_client_links(
    customer_client_link_service: CustomerClientLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing customer client links fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return customer_client_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.customer_client_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await customer_client_link_service.list_customer_client_links(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list customer client links" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list customer client links: Search failed",
    )


def test_register_customer_client_link_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_customer_client_link_tools(mock_mcp)

    # Assert
    assert isinstance(service, CustomerClientLinkService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_customer_client_link",
        "update_customer_client_link",
        "list_customer_client_links",
    ]

    assert set(tool_names) == set(expected_tools)
