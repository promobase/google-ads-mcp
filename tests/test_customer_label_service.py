"""Tests for Customer Label service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.customer_label import CustomerLabel
from google.ads.googleads.v20.services.types.customer_label_service import (
    CustomerLabelOperation,
    MutateCustomerLabelsResponse,
    MutateCustomerLabelResult,
)
from google.rpc import status_pb2

from src.sdk_services.account.customer_label_service import (
    CustomerLabelService,
    create_customer_label_tools,
)


@pytest.fixture
def customer_label_service():
    """Create a Customer Label service instance."""
    return CustomerLabelService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Customer Label service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestCustomerLabelService:
    """Test cases for CustomerLabelService."""

    async def test_create_customer_label_success(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test successful creation of a customer label association."""
        # Mock the client
        customer_label_service._client = mock_client

        # Create mock response
        mock_result = MutateCustomerLabelResult()
        mock_result.resource_name = "customers/1234567890/customerLabels/9876543210"

        mock_response = MutateCustomerLabelsResponse()
        mock_response.results.append(mock_result)

        mock_client.mutate_customer_labels.return_value = mock_response

        # Execute
        result = await customer_label_service.create_customer_label(
            ctx=mock_context,
            customer_id="123-456-7890",
            label_id="9876543210",
        )

        # Verify request
        request = mock_client.mutate_customer_labels.call_args[1]["request"]
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.partial_failure is False
        assert request.validate_only is False

        operation = request.operations[0]
        # The label field should be set on the create operation
        assert operation.create.label == "customers/1234567890/labels/9876543210"

        # Verify logging
        mock_context.log.assert_called_with(
            level="info",
            message="Created customer label association: customer 1234567890 with label 9876543210",
        )

    async def test_remove_customer_label_success(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test successful removal of a customer label association."""
        customer_label_service._client = mock_client

        mock_response = MutateCustomerLabelsResponse()
        mock_response.results.append(MutateCustomerLabelResult())
        mock_client.mutate_customer_labels.return_value = mock_response

        # Execute
        result = await customer_label_service.remove_customer_label(
            ctx=mock_context,
            customer_id="1234567890",
            label_id="9876543210",
        )

        # Verify request
        request = mock_client.mutate_customer_labels.call_args[1]["request"]
        operation = request.operations[0]

        # Check resource name format
        assert operation.remove == "customers/1234567890/customerLabels/9876543210"

        # Verify logging
        mock_context.log.assert_called_with(
            level="info",
            message="Removed customer label association: customer 1234567890 from label 9876543210",
        )

    async def test_create_with_partial_failure(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test create with partial failure mode."""
        customer_label_service._client = mock_client

        # Create response with partial failure error
        mock_response = MutateCustomerLabelsResponse()
        mock_response.results.append(MutateCustomerLabelResult())

        partial_error = status_pb2.Status()
        partial_error.code = 3  # INVALID_ARGUMENT
        partial_error.message = "Partial failure occurred"
        mock_response.partial_failure_error.CopyFrom(partial_error)

        mock_client.mutate_customer_labels.return_value = mock_response

        result = await customer_label_service.create_customer_label(
            ctx=mock_context,
            customer_id="1234567890",
            label_id="9876543210",
            partial_failure=True,
        )

        request = mock_client.mutate_customer_labels.call_args[1]["request"]
        assert request.partial_failure is True

    async def test_create_api_error(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test create with API error."""
        customer_label_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()
        error.failure.__str__ = Mock(return_value="Label not found")
        mock_client.mutate_customer_labels.side_effect = error

        with pytest.raises(Exception) as exc_info:
            await customer_label_service.create_customer_label(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="nonexistent",
            )

        assert "Google Ads API error: Label not found" in str(exc_info.value)

    async def test_remove_general_error(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test remove with general error."""
        customer_label_service._client = mock_client
        mock_client.mutate_customer_labels.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await customer_label_service.remove_customer_label(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="9876543210",
            )

        assert "Failed to remove customer label: Network error" in str(exc_info.value)

    async def test_create_with_validate_only(
        self, customer_label_service, mock_context, mock_client
    ):
        """Test create with validate_only flag."""
        customer_label_service._client = mock_client

        mock_response = MutateCustomerLabelsResponse()
        mock_client.mutate_customer_labels.return_value = mock_response

        await customer_label_service.create_customer_label(
            ctx=mock_context,
            customer_id="1234567890",
            label_id="9876543210",
            validate_only=True,
        )

        request = mock_client.mutate_customer_labels.call_args[1]["request"]
        assert request.validate_only is True


@pytest.mark.asyncio
class TestCustomerLabelTools:
    """Test cases for Customer Label tool functions."""

    async def test_create_customer_label_tool(self, mock_context):
        """Test create_customer_label tool function."""
        service = CustomerLabelService()
        tools = create_customer_label_tools(service)
        create_tool = tools[0]  # First tool is create_customer_label

        # Mock the service method
        with patch.object(service, "create_customer_label") as mock_create:
            mock_create.return_value = {
                "results": [{"resource_name": "customers/123/customerLabels/456"}]
            }

            await create_tool(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="9876543210",
            )

            mock_create.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="9876543210",
                partial_failure=False,
                validate_only=False,
            )

    async def test_remove_customer_label_tool(self, mock_context):
        """Test remove_customer_label tool function."""
        service = CustomerLabelService()
        tools = create_customer_label_tools(service)
        remove_tool = tools[1]  # Second tool is remove_customer_label

        with patch.object(service, "remove_customer_label") as mock_remove:
            mock_remove.return_value = {"results": [{"resource_name": "test"}]}

            await remove_tool(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="9876543210",
                validate_only=True,
            )

            mock_remove.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                label_id="9876543210",
                partial_failure=False,
                validate_only=True,
            )

