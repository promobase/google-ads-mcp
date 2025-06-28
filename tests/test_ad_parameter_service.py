"""Tests for ad parameter service."""

import pytest
from typing import Any
from unittest.mock import Mock, AsyncMock, patch
from fastmcp import Context

from src.services.ad_group.ad_parameter_service import (
    AdParameterService,
    create_ad_parameter_tools,
)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    context = Mock(spec=Context)
    context.log = AsyncMock()
    return context


@pytest.fixture
def mock_client():
    """Create a mock ad parameter service client."""
    return Mock()


@pytest.fixture
def service(mock_client: Any):
    """Create an ad parameter service with mocked client."""
    service = AdParameterService()
    service._client = mock_client  # type: ignore[reportPrivateUsage]
    return service


class TestAdParameterService:
    """Test cases for AdParameterService."""

    @pytest.mark.asyncio
    @patch("src.sdk_services.ad_group.ad_parameter_service.serialize_proto_message")
    async def test_mutate_ad_parameters_create(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating ad parameters."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = "customers/123/adParameters/456~789~1"
        mock_result.ad_parameter = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_parameters.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [{"resource_name": "customers/123/adParameters/456~789~1"}],
            "partial_failure_error": None,
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "parameter_index": 1,
                    "insertion_text": "$99.99",
                }
            }
        ]

        # Call the method
        result = await service.mutate_ad_parameters(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/adParameters/456~789~1"
        )
        assert result["partial_failure_error"] is None

        # Verify the API call
        mock_client.mutate_ad_parameters.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_parameters.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert (
            request.operations[0].create.ad_group_criterion
            == "customers/123/adGroupCriteria/456~789"
        )
        assert request.operations[0].create.parameter_index == 1
        assert request.operations[0].create.insertion_text == "$99.99"

    @pytest.mark.asyncio
    @patch("src.sdk_services.ad_group.ad_parameter_service.serialize_proto_message")
    async def test_mutate_ad_parameters_update(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test updating ad parameters."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = "customers/123/adParameters/456~789~1"
        mock_result.ad_parameter = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_parameters.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [{"resource_name": "customers/123/adParameters/456~789~1"}]
        }

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/adParameters/456~789~1",
                    "insertion_text": "$149.99",
                }
            }
        ]

        # Call the method
        result = await service.mutate_ad_parameters(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/adParameters/456~789~1"
        )

        # Verify the API call
        mock_client.mutate_ad_parameters.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_parameters.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert (
            request.operations[0].update.resource_name
            == "customers/123/adParameters/456~789~1"
        )
        assert request.operations[0].update.insertion_text == "$149.99"
        assert "insertion_text" in request.operations[0].update_mask.paths

    @pytest.mark.asyncio
    @patch("src.sdk_services.ad_group.ad_parameter_service.serialize_proto_message")
    async def test_mutate_ad_parameters_remove(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test removing ad parameters."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = "customers/123/adParameters/456~789~1"
        mock_result.ad_parameter = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_parameters.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [{"resource_name": "customers/123/adParameters/456~789~1"}]
        }

        # Test data
        operations = [{"remove": "customers/123/adParameters/456~789~1"}]

        # Call the method
        result = await service.mutate_ad_parameters(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/adParameters/456~789~1"
        )

        # Verify the API call
        mock_client.mutate_ad_parameters.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_parameters.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert request.operations[0].remove == "customers/123/adParameters/456~789~1"

    @pytest.mark.asyncio
    @patch("src.sdk_services.ad_group.ad_parameter_service.serialize_proto_message")
    async def test_mutate_ad_parameters_parameter_index_2(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating ad parameters with parameter index 2."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = "customers/123/adParameters/456~789~2"
        mock_result.ad_parameter = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_parameters.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [{"resource_name": "customers/123/adParameters/456~789~2"}]
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "parameter_index": 2,
                    "insertion_text": "50% off",
                }
            }
        ]

        # Call the method
        _ = await service.mutate_ad_parameters(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the API call
        mock_client.mutate_ad_parameters.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_parameters.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.operations[0].create.parameter_index == 2
        assert request.operations[0].create.insertion_text == "50% off"

    @pytest.mark.asyncio
    @patch("src.sdk_services.ad_group.ad_parameter_service.serialize_proto_message")
    async def test_mutate_ad_parameters_with_partial_failure(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test mutating ad parameters with partial failure."""
        # Mock response with partial failure
        mock_result = Mock()
        mock_result.resource_name = "customers/123/adParameters/456~789~1"
        mock_result.ad_parameter = None

        mock_error = Mock()
        mock_error.code = 3
        mock_error.message = "Invalid parameter index"
        mock_error.details = []

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = mock_error

        mock_client.mutate_ad_parameters.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [{"resource_name": "customers/123/adParameters/456~789~1"}],
            "partial_failure_error": {
                "code": 3,
                "message": "Invalid parameter index",
                "details": [],
            },
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "parameter_index": 1,
                    "insertion_text": "$99.99",
                }
            }
        ]

        # Call the method
        result = await service.mutate_ad_parameters(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
            partial_failure=True,
        )

        # Verify the result includes partial failure error
        assert result["partial_failure_error"]["code"] == 3
        assert result["partial_failure_error"]["message"] == "Invalid parameter index"


class TestAdParameterTools:
    """Test cases for ad parameter tools."""

    @pytest.mark.asyncio
    async def test_create_tools(self, mock_context: Any):
        """Test creating ad parameter tools."""
        service = Mock()
        service.mutate_ad_parameters = AsyncMock(
            return_value={"results": [], "partial_failure_error": None}
        )

        tools = create_ad_parameter_tools(service)

        # Should have one tool
        assert len(tools) == 1

        # Test the mutate tool
        mutate_tool = tools[0]
        await mutate_tool(
            ctx=mock_context,
            customer_id="123",
            operations=[],
        )

        service.mutate_ad_parameters.assert_called_once_with(  # type: ignore
            ctx=mock_context,
            customer_id="123",
            operations=[],
            partial_failure=False,
            validate_only=False,
            response_content_type="RESOURCE_NAME_ONLY",
        )
