"""Tests for AccountBudgetProposalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.account_budget_proposal_type import (
    AccountBudgetProposalTypeEnum,
)
from google.ads.googleads.v20.enums.types.spending_limit_type import (
    SpendingLimitTypeEnum,
)
from google.ads.googleads.v20.enums.types.time_type import TimeTypeEnum
from google.ads.googleads.v20.services.services.account_budget_proposal_service import (
    AccountBudgetProposalServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.account_budget_proposal_service import (
    MutateAccountBudgetProposalResponse,
)

from src.sdk_services.account.account_budget_proposal_service import (
    AccountBudgetProposalService,
    register_account_budget_proposal_tools,
)


@pytest.fixture
def account_budget_proposal_service(
    mock_sdk_client: Any,
) -> AccountBudgetProposalService:
    """Create an AccountBudgetProposalService instance with mocked dependencies."""
    # Mock AccountBudgetProposalService client
    mock_account_budget_proposal_client = Mock(spec=AccountBudgetProposalServiceClient)
    mock_sdk_client.client.get_service.return_value = (
        mock_account_budget_proposal_client
    )

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AccountBudgetProposalService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_account_budget_proposal_basic(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a basic account budget proposal."""
    # Arrange
    customer_id = "1234567890"
    proposal_type = AccountBudgetProposalTypeEnum.AccountBudgetProposalType.CREATE
    billing_setup = "customers/1234567890/billingSetups/123456"
    proposed_name = "Test Account Budget"
    proposed_start_time_type = TimeTypeEnum.TimeType.NOW
    proposed_spending_limit_type = SpendingLimitTypeEnum.SpendingLimitType.INFINITE

    # Create mock response
    mock_response = Mock(spec=MutateAccountBudgetProposalResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (
        "customers/1234567890/accountBudgetProposals/987654321"
    )

    # Get the mocked account budget proposal service client
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.return_value = (
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/accountBudgetProposals/987654321"
        }
    }

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_budget_proposal_service.create_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            proposal_type=proposal_type,
            billing_setup=billing_setup,
            proposed_name=proposed_name,
            proposed_start_time_type=proposed_start_time_type,
            proposed_spending_limit_type=proposed_spending_limit_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_budget_proposal_client.mutate_account_budget_proposal.assert_called_once()  # type: ignore
    call_args = (
        mock_account_budget_proposal_client.mutate_account_budget_proposal.call_args
    )  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    proposal = operation.create
    assert proposal.proposal_type == proposal_type
    assert proposal.billing_setup == billing_setup
    assert proposal.proposed_name == proposed_name
    assert proposal.proposed_start_time_type == proposed_start_time_type
    assert proposal.proposed_spending_limit_type == proposed_spending_limit_type

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created account budget proposal: {proposed_name}",
    )


@pytest.mark.asyncio
async def test_create_account_budget_proposal_with_spending_limit(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an account budget proposal with spending limit."""
    # Arrange
    customer_id = "1234567890"
    proposal_type = AccountBudgetProposalTypeEnum.AccountBudgetProposalType.CREATE
    billing_setup = "customers/1234567890/billingSetups/123456"
    proposed_name = "Limited Budget"
    proposed_start_time_type = TimeTypeEnum.TimeType.NOW
    proposed_spending_limit_type = SpendingLimitTypeEnum.SpendingLimitType.INFINITE
    proposed_spending_limit_micros = 1000000000  # $1000 in micros
    proposed_start_date_time = "2024-01-01 00:00:00"
    proposed_end_date_time = "2024-12-31 23:59:59"
    proposed_end_time_type = TimeTypeEnum.TimeType.FOREVER

    # Create mock response
    mock_response = Mock(spec=MutateAccountBudgetProposalResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (
        "customers/1234567890/accountBudgetProposals/987654321"
    )

    # Get the mocked account budget proposal service client
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.return_value = (
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/accountBudgetProposals/987654321"
        }
    }

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_budget_proposal_service.create_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            proposal_type=proposal_type,
            billing_setup=billing_setup,
            proposed_name=proposed_name,
            proposed_start_time_type=proposed_start_time_type,
            proposed_spending_limit_type=proposed_spending_limit_type,
            proposed_spending_limit_micros=proposed_spending_limit_micros,
            proposed_start_date_time=proposed_start_date_time,
            proposed_end_date_time=proposed_end_date_time,
            proposed_end_time_type=proposed_end_time_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = (
        mock_account_budget_proposal_client.mutate_account_budget_proposal.call_args
    )  # type: ignore
    request = call_args[1]["request"]
    proposal = request.operation.create
    # When specific spending limit micros is set, the type should be inferred
    assert proposal.proposed_spending_limit_micros == proposed_spending_limit_micros
    assert proposal.proposed_start_date_time == proposed_start_date_time
    assert proposal.proposed_end_date_time == proposed_end_date_time
    # Note: proposed_end_time_type and proposed_end_date_time are mutually exclusive (oneof)
    # When we set proposed_end_date_time, proposed_end_time_type should not be set


@pytest.mark.asyncio
async def test_update_account_budget_proposal_name_only(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an UPDATE proposal for account budget with name only."""
    # Arrange
    customer_id = "1234567890"
    account_budget = "customers/1234567890/accountBudgets/987654321"
    billing_setup = "customers/1234567890/billingSetups/123456"
    new_name = "Updated Budget Name"

    # Create mock response
    mock_response = Mock(spec=MutateAccountBudgetProposalResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (
        "customers/1234567890/accountBudgetProposals/111222333"
    )

    # Get the mocked account budget proposal service client
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.return_value = (
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/accountBudgetProposals/111222333"
        }
    }

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_budget_proposal_service.update_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_budget=account_budget,
            billing_setup=billing_setup,
            proposed_name=new_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_budget_proposal_client.mutate_account_budget_proposal.assert_called_once()  # type: ignore
    call_args = (
        mock_account_budget_proposal_client.mutate_account_budget_proposal.call_args
    )  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    proposal = operation.create
    assert (
        proposal.proposal_type
        == AccountBudgetProposalTypeEnum.AccountBudgetProposalType.UPDATE
    )
    assert proposal.account_budget == account_budget
    assert proposal.billing_setup == billing_setup
    assert proposal.proposed_name == new_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Created UPDATE proposal for account budget",
    )


@pytest.mark.asyncio
async def test_update_account_budget_proposal_all_fields(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an UPDATE proposal with all updatable fields."""
    # Arrange
    customer_id = "1234567890"
    account_budget = "customers/1234567890/accountBudgets/987654321"
    billing_setup = "customers/1234567890/billingSetups/123456"
    new_name = "Updated Budget Name"
    new_spending_limit = 2000000000  # $2000 in micros
    new_end_date = "2024-06-30 23:59:59"
    new_start_date = "2024-01-01 00:00:00"

    # Create mock response
    mock_response = Mock(spec=MutateAccountBudgetProposalResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = (
        "customers/1234567890/accountBudgetProposals/111222333"
    )

    # Get the mocked account budget proposal service client
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.return_value = (
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/accountBudgetProposals/111222333"
        }
    }

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_budget_proposal_service.update_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_budget=account_budget,
            billing_setup=billing_setup,
            proposed_name=new_name,
            proposed_spending_limit_micros=new_spending_limit,
            proposed_end_date_time=new_end_date,
            proposed_start_date_time=new_start_date,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = (
        mock_account_budget_proposal_client.mutate_account_budget_proposal.call_args
    )  # type: ignore
    request = call_args[1]["request"]
    operation = request.operation
    proposal = operation.create
    assert (
        proposal.proposal_type
        == AccountBudgetProposalTypeEnum.AccountBudgetProposalType.UPDATE
    )
    assert proposal.account_budget == account_budget
    assert proposal.billing_setup == billing_setup
    assert proposal.proposed_name == new_name
    assert proposal.proposed_spending_limit_micros == new_spending_limit
    assert proposal.proposed_end_date_time == new_end_date
    assert proposal.proposed_start_date_time == new_start_date


@pytest.mark.asyncio
async def test_list_account_budget_proposals(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing account budget proposals."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.account_budget_proposal = Mock()
        row.account_budget_proposal.resource_name = (
            f"customers/{customer_id}/accountBudgetProposals/{i + 100}"
        )
        row.account_budget_proposal.id = i + 100
        row.account_budget_proposal.billing_setup = (
            f"customers/{customer_id}/billingSetups/{i + 200}"
        )
        row.account_budget_proposal.proposed_name = f"Budget Proposal {i}"
        row.account_budget_proposal.proposal_type = Mock()
        row.account_budget_proposal.proposal_type.name = "CREATE"
        row.account_budget_proposal.status = Mock()
        row.account_budget_proposal.status.name = "PENDING"
        row.account_budget_proposal.proposed_spending_limit_type = Mock()
        row.account_budget_proposal.proposed_spending_limit_type.name = "INFINITE"
        row.account_budget_proposal.proposed_spending_limit_micros = 0
        row.account_budget_proposal.creation_date_time = f"2024-01-{i + 1:02d} 10:00:00"
        row.account_budget_proposal.approval_date_time = None
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return account_budget_proposal_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    # Mock serialize_proto_message for each proposal
    def serialize_side_effect(obj: Any):
        return {
            "resource_name": obj.resource_name,
            "id": obj.id,
            "billing_setup": obj.billing_setup,
            "proposed_name": obj.proposed_name,
            "proposal_type": obj.proposal_type.name,
            "status": obj.status.name,
            "proposed_spending_limit_type": obj.proposed_spending_limit_type.name,
            "proposed_spending_limit_micros": obj.proposed_spending_limit_micros,
            "creation_date_time": obj.creation_date_time,
            "approval_date_time": obj.approval_date_time,
        }

    with (
        patch(
            "src.sdk_services.account.account_budget_proposal_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await account_budget_proposal_service.list_account_budget_proposals(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert first_result["id"] == 100
    assert first_result["proposed_name"] == "Budget Proposal 0"
    assert first_result["proposal_type"] == "CREATE"
    assert first_result["status"] == "PENDING"
    assert first_result["proposed_spending_limit_type"] == "INFINITE"
    assert first_result["creation_date_time"] == "2024-01-01 10:00:00"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM account_budget_proposal" in query
    assert "ORDER BY account_budget_proposal.id DESC" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 account budget proposals",
    )


@pytest.mark.asyncio
async def test_remove_account_budget_proposal(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an account budget proposal."""
    # Arrange
    customer_id = "1234567890"
    proposal_resource_name = "customers/1234567890/accountBudgetProposals/987654321"

    # Create mock response
    mock_response = Mock(spec=MutateAccountBudgetProposalResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = proposal_resource_name

    # Get the mocked account budget proposal service client
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.return_value = (
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": proposal_resource_name}}

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_budget_proposal_service.remove_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            proposal_resource_name=proposal_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_budget_proposal_client.mutate_account_budget_proposal.assert_called_once()  # type: ignore
    call_args = (
        mock_account_budget_proposal_client.mutate_account_budget_proposal.call_args
    )  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.remove == proposal_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed account budget proposal",
    )


@pytest.mark.asyncio
async def test_error_handling_create_proposal(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating account budget proposal fails."""
    # Arrange
    customer_id = "1234567890"
    proposal_type = AccountBudgetProposalTypeEnum.AccountBudgetProposalType.CREATE
    billing_setup = "customers/1234567890/billingSetups/123456"
    proposed_name = "Test Budget"

    # Get the mocked account budget proposal service client and make it raise exception
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_budget_proposal_service.create_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            proposal_type=proposal_type,
            billing_setup=billing_setup,
            proposed_name=proposed_name,
            proposed_start_time_type=TimeTypeEnum.TimeType.NOW,
        )

    assert "Failed to create account budget proposal" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create account budget proposal: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_proposal(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating update proposal fails."""
    # Arrange
    customer_id = "1234567890"
    account_budget = "customers/1234567890/accountBudgets/987654321"
    billing_setup = "customers/1234567890/billingSetups/123456"

    # Get the mocked account budget proposal service client and make it raise exception
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_budget_proposal_service.update_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_budget=account_budget,
            billing_setup=billing_setup,
            proposed_name="New Name",
        )

    assert "Failed to create update proposal" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create update proposal: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_proposals(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing account budget proposals fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return account_budget_proposal_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.account.account_budget_proposal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_budget_proposal_service.list_account_budget_proposals(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list account budget proposals" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list account budget proposals: Search failed",
    )


@pytest.mark.asyncio
async def test_error_handling_remove_proposal(
    account_budget_proposal_service: AccountBudgetProposalService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing account budget proposal fails."""
    # Arrange
    customer_id = "1234567890"
    proposal_resource_name = "customers/1234567890/accountBudgetProposals/987654321"

    # Get the mocked account budget proposal service client and make it raise exception
    mock_account_budget_proposal_client = account_budget_proposal_service.client  # type: ignore
    mock_account_budget_proposal_client.mutate_account_budget_proposal.side_effect = (
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_budget_proposal_service.remove_account_budget_proposal(
            ctx=mock_ctx,
            customer_id=customer_id,
            proposal_resource_name=proposal_resource_name,
        )

    assert "Failed to remove account budget proposal" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to remove account budget proposal: Test Google Ads Exception",
    )


def test_register_account_budget_proposal_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_account_budget_proposal_tools(mock_mcp)

    # Assert
    assert isinstance(service, AccountBudgetProposalService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_account_budget_proposal",
        "update_account_budget_proposal",
        "list_account_budget_proposals",
        "remove_account_budget_proposal",
    ]

    assert set(tool_names) == set(expected_tools)
