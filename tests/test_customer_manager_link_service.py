"""Tests for Customer Manager Link service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.manager_link_status import (
    ManagerLinkStatusEnum,
)
from google.ads.googleads.v20.resources.types.customer_manager_link import (
    CustomerManagerLink,
)
from google.ads.googleads.v20.services.types.customer_manager_link_service import (
    CustomerManagerLinkOperation,
    MoveManagerLinkResponse,
    MutateCustomerManagerLinkResponse,
    MutateCustomerManagerLinkResult,
)

from src.sdk_services.account.customer_manager_link_service import (
    CustomerManagerLinkService,
    create_customer_manager_link_tools,
)


@pytest.fixture
def customer_manager_link_service():
    """Create a Customer Manager Link service instance."""
    return CustomerManagerLinkService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Customer Manager Link service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestCustomerManagerLinkService:
    """Test cases for CustomerManagerLinkService."""

    async def test_update_manager_link_status_accept(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test accepting a manager invitation."""
        # Mock the client
        customer_manager_link_service._client = mock_client

        # Create mock response
        mock_result = MutateCustomerManagerLinkResult()
        mock_result.resource_name = (
            "customers/1234567890/customerManagerLinks/9876543210~123"
        )

        mock_response = MutateCustomerManagerLinkResponse()
        mock_response.results.append(mock_result)

        mock_client.mutate_customer_manager_link.return_value = mock_response

        # Execute
        result = await customer_manager_link_service.update_manager_link_status(
            ctx=mock_context,
            customer_id="123-456-7890",
            manager_customer_id="987-654-3210",
            manager_link_id=123,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE,
        )

        # Verify request
        request = mock_client.mutate_customer_manager_link.call_args[1]["request"]
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.validate_only is False

        operation = request.operations[0]
        assert operation.update.resource_name == (
            "customers/1234567890/customerManagerLinks/9876543210~123"
        )
        assert operation.update.status == ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE
        assert list(operation.update_mask.paths) == ["status"]

        # Verify logging
        mock_context.log.assert_called_with(
            level="info",
            message="Updated manager link status to ACTIVE for customer 1234567890",
        )

    async def test_update_manager_link_status_refuse(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test declining a manager invitation."""
        customer_manager_link_service._client = mock_client

        mock_result = MutateCustomerManagerLinkResult()
        mock_result.resource_name = (
            "customers/1234567890/customerManagerLinks/9876543210~123"
        )

        mock_response = MutateCustomerManagerLinkResponse()
        mock_response.results.append(mock_result)

        mock_client.mutate_customer_manager_link.return_value = mock_response

        result = await customer_manager_link_service.update_manager_link_status(
            ctx=mock_context,
            customer_id="1234567890",
            manager_customer_id="9876543210",
            manager_link_id=123,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.REFUSED,
            validate_only=True,
        )

        request = mock_client.mutate_customer_manager_link.call_args[1]["request"]
        assert request.validate_only is True
        assert request.operations[0].update.status == (
            ManagerLinkStatusEnum.ManagerLinkStatus.REFUSED
        )

    async def test_update_manager_link_status_terminate(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test terminating a manager link."""
        customer_manager_link_service._client = mock_client

        mock_result = MutateCustomerManagerLinkResult()
        mock_result.resource_name = (
            "customers/1234567890/customerManagerLinks/9876543210~123"
        )

        mock_response = MutateCustomerManagerLinkResponse()
        mock_response.results.append(mock_result)

        mock_client.mutate_customer_manager_link.return_value = mock_response

        result = await customer_manager_link_service.update_manager_link_status(
            ctx=mock_context,
            customer_id="1234567890",
            manager_customer_id="9876543210",
            manager_link_id=123,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.INACTIVE,
        )

        request = mock_client.mutate_customer_manager_link.call_args[1]["request"]
        assert request.operations[0].update.status == (
            ManagerLinkStatusEnum.ManagerLinkStatus.INACTIVE
        )

    async def test_move_manager_link_success(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test moving a client to a new manager."""
        customer_manager_link_service._client = mock_client

        # Create mock response
        mock_response = MoveManagerLinkResponse()
        mock_response.resource_name = (
            "customers/1234567890/customerManagerLinks/5555555555~456"
        )

        mock_client.move_manager_link.return_value = mock_response

        # Execute
        result = await customer_manager_link_service.move_manager_link(
            ctx=mock_context,
            customer_id="123-456-7890",
            previous_manager_customer_id="987-654-3210",
            previous_manager_link_id=123,
            new_manager_customer_id="555-555-5555",
        )

        # Verify request
        request = mock_client.move_manager_link.call_args[1]["request"]
        assert request.customer_id == "1234567890"
        assert request.previous_customer_manager_link == (
            "customers/1234567890/customerManagerLinks/9876543210~123"
        )
        assert request.new_manager == "customers/5555555555"
        assert request.validate_only is False

        # Verify logging
        mock_context.log.assert_called_with(
            level="info",
            message=("Moved customer 1234567890 from manager 9876543210 to 5555555555"),
        )

    async def test_update_manager_link_api_error(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test update with API error."""
        customer_manager_link_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()
        error.failure.__str__ = Mock(return_value="Permission denied")
        mock_client.mutate_customer_manager_link.side_effect = error

        with pytest.raises(Exception) as exc_info:
            await customer_manager_link_service.update_manager_link_status(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
                status=ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE,
            )

        assert "Google Ads API error: Permission denied" in str(exc_info.value)

    async def test_move_manager_link_general_error(
        self, customer_manager_link_service, mock_context, mock_client
    ):
        """Test move with general error."""
        customer_manager_link_service._client = mock_client
        mock_client.move_manager_link.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await customer_manager_link_service.move_manager_link(
                ctx=mock_context,
                customer_id="1234567890",
                previous_manager_customer_id="9876543210",
                previous_manager_link_id=123,
                new_manager_customer_id="5555555555",
            )

        assert "Failed to move manager link: Network error" in str(exc_info.value)


@pytest.mark.asyncio
class TestCustomerManagerLinkTools:
    """Test cases for Customer Manager Link tool functions."""

    async def test_accept_manager_invitation_tool(self, mock_context):
        """Test accept_manager_invitation tool function."""
        service = CustomerManagerLinkService()
        tools = create_customer_manager_link_tools(service)
        accept_tool = tools[0]  # First tool is accept_manager_invitation

        # Mock the service method
        with patch.object(service, "update_manager_link_status") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}

            await accept_tool(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
            )

            mock_update.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
                status=ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE,
                validate_only=False,
            )

    async def test_decline_manager_invitation_tool(self, mock_context):
        """Test decline_manager_invitation tool function."""
        service = CustomerManagerLinkService()
        tools = create_customer_manager_link_tools(service)
        decline_tool = tools[1]  # Second tool is decline_manager_invitation

        with patch.object(service, "update_manager_link_status") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}

            await decline_tool(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
                validate_only=True,
            )

            mock_update.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
                status=ManagerLinkStatusEnum.ManagerLinkStatus.REFUSED,
                validate_only=True,
            )

    async def test_terminate_manager_link_tool(self, mock_context):
        """Test terminate_manager_link tool function."""
        service = CustomerManagerLinkService()
        tools = create_customer_manager_link_tools(service)
        terminate_tool = tools[2]  # Third tool is terminate_manager_link

        with patch.object(service, "update_manager_link_status") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}

            await terminate_tool(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
            )

            mock_update.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                manager_customer_id="9876543210",
                manager_link_id=123,
                status=ManagerLinkStatusEnum.ManagerLinkStatus.INACTIVE,
                validate_only=False,
            )

    async def test_move_client_to_new_manager_tool(self, mock_context):
        """Test move_client_to_new_manager tool function."""
        service = CustomerManagerLinkService()
        tools = create_customer_manager_link_tools(service)
        move_tool = tools[3]  # Fourth tool is move_client_to_new_manager

        with patch.object(service, "move_manager_link") as mock_move:
            mock_move.return_value = {"resource_name": "new_link"}

            await move_tool(
                ctx=mock_context,
                customer_id="1234567890",
                previous_manager_customer_id="9876543210",
                previous_manager_link_id=123,
                new_manager_customer_id="5555555555",
            )

            mock_move.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                previous_manager_customer_id="9876543210",
                previous_manager_link_id=123,
                new_manager_customer_id="5555555555",
                validate_only=False,
            )
