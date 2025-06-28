"""Tests for ad group criterion customizer service."""

import pytest
from typing import Any
from unittest.mock import Mock, AsyncMock, patch
from fastmcp import Context

from src.services.ad_group.ad_group_criterion_customizer_service import (
    AdGroupCriterionCustomizerService,
    create_ad_group_criterion_customizer_tools,
)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    context = Mock(spec=Context)
    context.log = AsyncMock()
    return context


@pytest.fixture
def mock_client():
    """Create a mock ad group criterion customizer service client."""
    return Mock()


@pytest.fixture
def service(mock_client: Any):
    """Create an ad group criterion customizer service with mocked client."""
    service = AdGroupCriterionCustomizerService()
    service._client = mock_client  # type: ignore[reportPrivateUsage]
    return service


class TestAdGroupCriterionCustomizerService:
    """Test cases for AdGroupCriterionCustomizerService."""

    @pytest.mark.asyncio
    @patch(
        "src.sdk_services.ad_group.ad_group_criterion_customizer_service.serialize_proto_message"
    )
    async def test_mutate_ad_group_criterion_customizers_create(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating ad group criterion customizers."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )
        mock_result.ad_group_criterion_customizer = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_group_criterion_customizers.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [
                {
                    "resource_name": "customers/123/adGroupCriterionCustomizers/456~789~101112"
                }
            ],
            "partial_failure_error": None,
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "customizer_attribute": "customers/123/customizerAttributes/101112",
                    "value": {"type": "TEXT", "value": "Custom Text Value"},
                }
            }
        ]

        # Call the method
        result = await service.mutate_ad_group_criterion_customizers(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )
        assert result["partial_failure_error"] is None

        # Verify the API call
        mock_client.mutate_ad_group_criterion_customizers.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_group_criterion_customizers.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert (
            request.operations[0].create.ad_group_criterion
            == "customers/123/adGroupCriteria/456~789"
        )
        assert (
            request.operations[0].create.customizer_attribute
            == "customers/123/customizerAttributes/101112"
        )
        assert request.operations[0].create.value.string_value == "Custom Text Value"

    @pytest.mark.asyncio
    @patch(
        "src.sdk_services.ad_group.ad_group_criterion_customizer_service.serialize_proto_message"
    )
    async def test_mutate_ad_group_criterion_customizers_remove(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test removing ad group criterion customizers."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )
        mock_result.ad_group_criterion_customizer = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_group_criterion_customizers.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [
                {
                    "resource_name": "customers/123/adGroupCriterionCustomizers/456~789~101112"
                }
            ]
        }

        # Test data
        operations = [
            {"remove": "customers/123/adGroupCriterionCustomizers/456~789~101112"}
        ]

        # Call the method
        result = await service.mutate_ad_group_criterion_customizers(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )

        # Verify the API call
        mock_client.mutate_ad_group_criterion_customizers.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_group_criterion_customizers.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert (
            request.operations[0].remove
            == "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )

    @pytest.mark.asyncio
    @patch(
        "src.sdk_services.ad_group.ad_group_criterion_customizer_service.serialize_proto_message"
    )
    async def test_mutate_ad_group_criterion_customizers_number_value(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating ad group criterion customizers with number value."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )
        mock_result.ad_group_criterion_customizer = None

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = None

        mock_client.mutate_ad_group_criterion_customizers.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [
                {
                    "resource_name": "customers/123/adGroupCriterionCustomizers/456~789~101112"
                }
            ]
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "customizer_attribute": "customers/123/customizerAttributes/101112",
                    "value": {"type": "NUMBER", "value": "99.99"},
                }
            }
        ]

        # Call the method
        _ = await service.mutate_ad_group_criterion_customizers(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the API call
        mock_client.mutate_ad_group_criterion_customizers.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_ad_group_criterion_customizers.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.operations[0].create.value.string_value == "99.99"

    @pytest.mark.asyncio
    @patch(
        "src.sdk_services.ad_group.ad_group_criterion_customizer_service.serialize_proto_message"
    )
    async def test_mutate_ad_group_criterion_customizers_with_partial_failure(
        self, mock_serialize: Any, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test mutating ad group criterion customizers with partial failure."""
        # Mock response with partial failure
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/adGroupCriterionCustomizers/456~789~101112"
        )
        mock_result.ad_group_criterion_customizer = None

        mock_error = Mock()
        mock_error.code = 3
        mock_error.message = "Invalid customizer attribute"
        mock_error.details = []

        mock_response = Mock()
        mock_response.results = [mock_result]
        mock_response.partial_failure_error = mock_error

        mock_client.mutate_ad_group_criterion_customizers.return_value = mock_response  # type: ignore

        # Mock the serialization to return a dict
        mock_serialize.return_value = {
            "results": [
                {
                    "resource_name": "customers/123/adGroupCriterionCustomizers/456~789~101112"
                }
            ],
            "partial_failure_error": {
                "code": 3,
                "message": "Invalid customizer attribute",
                "details": [],
            },
        }

        # Test data
        operations = [
            {
                "create": {
                    "ad_group_criterion": "customers/123/adGroupCriteria/456~789",
                    "customizer_attribute": "customers/123/customizerAttributes/101112",
                    "value": {"type": "TEXT", "value": "Test Value"},
                }
            }
        ]

        # Call the method
        result = await service.mutate_ad_group_criterion_customizers(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
            partial_failure=True,
        )

        # Verify the result includes partial failure error
        assert result["partial_failure_error"]["code"] == 3
        assert (
            result["partial_failure_error"]["message"] == "Invalid customizer attribute"
        )


class TestAdGroupCriterionCustomizerTools:
    """Test cases for ad group criterion customizer tools."""

    @pytest.mark.asyncio
    async def test_create_tools(self, mock_context: Any):
        """Test creating ad group criterion customizer tools."""
        service = Mock()
        service.mutate_ad_group_criterion_customizers = AsyncMock(
            return_value={"results": [], "partial_failure_error": None}
        )

        tools = create_ad_group_criterion_customizer_tools(service)

        # Should have one tool
        assert len(tools) == 1

        # Test the mutate tool
        mutate_tool = tools[0]
        await mutate_tool(
            ctx=mock_context,
            customer_id="123",
            operations=[],
        )

        service.mutate_ad_group_criterion_customizers.assert_called_once_with(  # type: ignore
            ctx=mock_context,
            customer_id="123",
            operations=[],
            partial_failure=False,
            validate_only=False,
            response_content_type="RESOURCE_NAME_ONLY",
        )
