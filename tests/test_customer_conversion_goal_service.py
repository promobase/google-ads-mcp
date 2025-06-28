"""Tests for customer conversion goal service."""

import pytest
from typing import Any
from unittest.mock import Mock, AsyncMock
from fastmcp import Context

from src.sdk_services.conversions.customer_conversion_goal_service import (
    CustomerConversionGoalService,
    create_customer_conversion_goal_tools,
)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    context = Mock(spec=Context)
    context.log = AsyncMock()
    return context


@pytest.fixture
def mock_client():
    """Create a mock customer conversion goal service client."""
    return Mock()


@pytest.fixture
def service(mock_client: Any) -> Any:
    """Create a customer conversion goal service with mocked client."""
    service = CustomerConversionGoalService()
    service._client = mock_client  # type: ignore # Need to set private attribute for testing
    return service


class TestCustomerConversionGoalService:
    """Test cases for CustomerConversionGoalService."""

    @pytest.mark.asyncio
    async def test_mutate_customer_conversion_goals_update(
        self, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test updating customer conversion goals."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/customerConversionGoals/PURCHASE~WEBSITE"
        )

        mock_response = Mock()
        mock_response.results = [mock_result]

        mock_client.mutate_customer_conversion_goals.return_value = mock_response  # type: ignore

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/PURCHASE~WEBSITE",
                    "biddable": True,
                }
            }
        ]

        # Call the method
        result = await service.mutate_customer_conversion_goals(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/customerConversionGoals/PURCHASE~WEBSITE"
        )

        # Verify the API call
        mock_client.mutate_customer_conversion_goals.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_customer_conversion_goals.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.customer_id == "123"
        assert len(request.operations) == 1
        assert (
            request.operations[0].update.resource_name
            == "customers/123/customerConversionGoals/PURCHASE~WEBSITE"
        )
        assert request.operations[0].update.biddable == True
        assert "biddable" in request.operations[0].update_mask.paths

    @pytest.mark.asyncio
    async def test_mutate_customer_conversion_goals_disable_biddable(
        self, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test disabling biddability for customer conversion goals."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = "customers/123/customerConversionGoals/LEAD~WEBSITE"

        mock_response = Mock()
        mock_response.results = [mock_result]

        mock_client.mutate_customer_conversion_goals.return_value = mock_response  # type: ignore

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/LEAD~WEBSITE",
                    "biddable": False,
                }
            }
        ]

        # Call the method
        result = await service.mutate_customer_conversion_goals(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/customerConversionGoals/LEAD~WEBSITE"
        )

        # Verify the API call
        mock_client.mutate_customer_conversion_goals.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_customer_conversion_goals.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.operations[0].update.biddable == False

    @pytest.mark.asyncio
    async def test_mutate_customer_conversion_goals_with_category_and_origin(
        self, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test updating customer conversion goals with category and origin."""
        # Mock response
        mock_result = Mock()
        mock_result.resource_name = (
            "customers/123/customerConversionGoals/SIGNUP~WEBSITE"
        )

        mock_response = Mock()
        mock_response.results = [mock_result]

        mock_client.mutate_customer_conversion_goals.return_value = mock_response  # type: ignore

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/SIGNUP~WEBSITE",
                    "category": "SIGNUP",
                    "origin": "WEBSITE",
                    "biddable": True,
                }
            }
        ]

        # Call the method
        _ = await service.mutate_customer_conversion_goals(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the API call
        mock_client.mutate_customer_conversion_goals.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_customer_conversion_goals.call_args[1]  # type: ignore
        request = call_args["request"]

        # Note: category and origin are typically immutable, but we include them for completeness
        assert request.operations[0].update.biddable == True

    @pytest.mark.asyncio
    async def test_mutate_customer_conversion_goals_multiple_operations(
        self, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test updating multiple customer conversion goals."""
        # Mock response
        mock_result1 = Mock()
        mock_result1.resource_name = (
            "customers/123/customerConversionGoals/PURCHASE~WEBSITE"
        )
        mock_result2 = Mock()
        mock_result2.resource_name = (
            "customers/123/customerConversionGoals/LEAD~WEBSITE"
        )

        mock_response = Mock()
        mock_response.results = [mock_result1, mock_result2]

        mock_client.mutate_customer_conversion_goals.return_value = mock_response  # type: ignore

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/PURCHASE~WEBSITE",
                    "biddable": True,
                }
            },
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/LEAD~WEBSITE",
                    "biddable": False,
                }
            },
        ]

        # Call the method
        result = await service.mutate_customer_conversion_goals(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
        )

        # Verify the result
        assert len(result["results"]) == 2
        assert (
            result["results"][0]["resource_name"]
            == "customers/123/customerConversionGoals/PURCHASE~WEBSITE"
        )
        assert (
            result["results"][1]["resource_name"]
            == "customers/123/customerConversionGoals/LEAD~WEBSITE"
        )

        # Verify the API call
        mock_client.mutate_customer_conversion_goals.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_customer_conversion_goals.call_args[1]  # type: ignore
        request = call_args["request"]

        assert len(request.operations) == 2
        assert request.operations[0].update.biddable == True
        assert request.operations[1].update.biddable == False

    @pytest.mark.asyncio
    async def test_mutate_customer_conversion_goals_validate_only(
        self, service: Any, mock_context: Any, mock_client: Any
    ):
        """Test validating customer conversion goals without executing."""
        # Mock response
        mock_response = Mock()
        mock_response.results = []

        mock_client.mutate_customer_conversion_goals.return_value = mock_response  # type: ignore

        # Test data
        operations = [
            {
                "update": {
                    "resource_name": "customers/123/customerConversionGoals/PURCHASE~WEBSITE",
                    "biddable": True,
                }
            }
        ]

        # Call the method
        _ = await service.mutate_customer_conversion_goals(
            ctx=mock_context,
            customer_id="123",
            operations=operations,
            validate_only=True,
        )

        # Verify the API call
        mock_client.mutate_customer_conversion_goals.assert_called_once()  # type: ignore
        call_args = mock_client.mutate_customer_conversion_goals.call_args[1]  # type: ignore
        request = call_args["request"]

        assert request.validate_only == True


class TestCustomerConversionGoalTools:
    """Test cases for customer conversion goal tools."""

    @pytest.mark.asyncio
    async def test_create_tools(self, mock_context: Any):
        """Test creating customer conversion goal tools."""
        service = Mock()
        service.mutate_customer_conversion_goals = AsyncMock(
            return_value={"results": []}
        )

        tools = create_customer_conversion_goal_tools(service)

        # Should have one tool
        assert len(tools) == 1

        # Test the mutate tool
        mutate_tool = tools[0]
        await mutate_tool(
            ctx=mock_context,
            customer_id="123",
            operations=[],
        )

        service.mutate_customer_conversion_goals.assert_called_once_with(  # type: ignore
            ctx=mock_context,
            customer_id="123",
            operations=[],
            validate_only=False,
        )
