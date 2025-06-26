"""Tests for BudgetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.budget_delivery_method import (
    BudgetDeliveryMethodEnum,
)
from google.ads.googleads.v20.services.services.campaign_budget_service import (
    CampaignBudgetServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_budget_service import (
    MutateCampaignBudgetsResponse,
)

from src.sdk_services.bidding.budget_service import (
    BudgetService,
    register_budget_tools,
)


@pytest.fixture
def budget_service(mock_sdk_client: Any) -> BudgetService:
    """Create a BudgetService instance with mocked dependencies."""
    # Mock BudgetService client
    mock_budget_client = Mock(spec=CampaignBudgetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_budget_client

    with patch(
        "src.sdk_services.bidding.budget_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = BudgetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_campaign_budget(
    budget_service: BudgetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign budget."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Budget"
    amount_micros = 10000000  # $10.00
    delivery_method = "STANDARD"
    explicitly_shared = True

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBudgetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/campaignBudgets/123"

    # Get the mocked budget service client
    mock_budget_client = budget_service.client  # type: ignore
    mock_budget_client.mutate_campaign_budgets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/campaignBudgets/123"}]
    }

    with patch(
        "src.sdk_services.bidding.budget_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await budget_service.create_campaign_budget(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            amount_micros=amount_micros,
            delivery_method=delivery_method,
            explicitly_shared=explicitly_shared,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_budget_client.mutate_campaign_budgets.assert_called_once()  # type: ignore
    call_args = mock_budget_client.mutate_campaign_budgets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.amount_micros == amount_micros
    assert (
        operation.create.delivery_method
        == BudgetDeliveryMethodEnum.BudgetDeliveryMethod.STANDARD
    )
    assert operation.create.explicitly_shared is True


@pytest.mark.asyncio
async def test_update_campaign_budget(
    budget_service: BudgetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign budget."""
    # Arrange
    customer_id = "1234567890"
    budget_id = "123"
    name = "Updated Budget"
    amount_micros = 20000000  # $20.00
    delivery_method = "ACCELERATED"

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBudgetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/campaignBudgets/{budget_id}"

    # Get the mocked budget service client
    mock_budget_client = budget_service.client  # type: ignore
    mock_budget_client.mutate_campaign_budgets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignBudgets/{budget_id}"}
        ]
    }

    with patch(
        "src.sdk_services.bidding.budget_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await budget_service.update_campaign_budget(
            ctx=mock_ctx,
            customer_id=customer_id,
            budget_id=budget_id,
            name=name,
            amount_micros=amount_micros,
            delivery_method=delivery_method,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_budget_client.mutate_campaign_budgets.assert_called_once()  # type: ignore
    call_args = mock_budget_client.mutate_campaign_budgets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/campaignBudgets/{budget_id}"
    )
    assert operation.update.name == name
    assert operation.update.amount_micros == amount_micros
    assert (
        operation.update.delivery_method
        == BudgetDeliveryMethodEnum.BudgetDeliveryMethod.ACCELERATED
    )

    # Check update mask
    assert "name" in operation.update_mask.paths
    assert "amount_micros" in operation.update_mask.paths
    assert "delivery_method" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated campaign budget {budget_id} for customer {customer_id}",
    )


@pytest.mark.asyncio
async def test_update_campaign_budget_partial(
    budget_service: BudgetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test partially updating a campaign budget."""
    # Arrange
    customer_id = "1234567890"
    budget_id = "123"
    amount_micros = 15000000  # $15.00

    # Create mock response
    mock_response = Mock(spec=MutateCampaignBudgetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/campaignBudgets/{budget_id}"

    # Get the mocked budget service client
    mock_budget_client = budget_service.client  # type: ignore
    mock_budget_client.mutate_campaign_budgets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/campaignBudgets/{budget_id}"}
        ]
    }

    with patch(
        "src.sdk_services.bidding.budget_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await budget_service.update_campaign_budget(
            ctx=mock_ctx,
            customer_id=customer_id,
            budget_id=budget_id,
            amount_micros=amount_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_budget_client.mutate_campaign_budgets.assert_called_once()  # type: ignore
    call_args = mock_budget_client.mutate_campaign_budgets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/campaignBudgets/{budget_id}"
    )
    assert operation.update.amount_micros == amount_micros

    # Check update mask - only amount_micros should be in the mask
    assert "amount_micros" in operation.update_mask.paths
    assert "name" not in operation.update_mask.paths
    assert "delivery_method" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_error_handling(
    budget_service: BudgetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked budget service client and make it raise exception
    mock_budget_client = budget_service.client  # type: ignore
    mock_budget_client.mutate_campaign_budgets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await budget_service.create_campaign_budget(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test Budget",
            amount_micros=10000000,
        )

    assert "Failed to create campaign budget" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create campaign budget: Test Google Ads Exception",
    )


def test_register_budget_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_budget_tools(mock_mcp)

    # Assert
    assert isinstance(service, BudgetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 2  # 2 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_campaign_budget",
        "update_campaign_budget",
    ]

    assert set(tool_names) == set(expected_tools)
