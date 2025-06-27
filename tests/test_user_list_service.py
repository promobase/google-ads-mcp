"""Tests for UserListService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.customer_match_upload_key_type import (
    CustomerMatchUploadKeyTypeEnum,
)
from google.ads.googleads.v20.enums.types.user_list_logical_rule_operator import (
    UserListLogicalRuleOperatorEnum,
)
from google.ads.googleads.v20.enums.types.user_list_membership_status import (
    UserListMembershipStatusEnum,
)
from google.ads.googleads.v20.services.services.user_list_service import (
    UserListServiceClient,
)
from google.ads.googleads.v20.services.types.user_list_service import (
    MutateUserListsResponse,
)

from src.sdk_services.audiences.user_list_service import (
    UserListService,
    register_user_list_tools,
)


@pytest.fixture
def user_list_service(mock_sdk_client: Any) -> UserListService:
    """Create a UserListService instance with mocked dependencies."""
    # Mock UserListService client
    mock_user_list_client = Mock(spec=UserListServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_user_list_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.user_list_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = UserListService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_basic_user_list(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a basic user list."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Basic User List"
    description = "A test user list"
    membership_life_span = 30
    membership_status = "OPEN"

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/userLists/123"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/userLists/123"}]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.create_basic_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            membership_life_span=membership_life_span,
            membership_status=membership_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert (
        operation.create.membership_status
        == UserListMembershipStatusEnum.UserListMembershipStatus.OPEN
    )
    assert operation.create.membership_life_span == membership_life_span
    assert operation.create.basic_user_list is not None

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created basic user list '{name}' with {membership_life_span} day membership",
    )


@pytest.mark.asyncio
async def test_create_crm_based_user_list(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a CRM-based user list."""
    # Arrange
    customer_id = "1234567890"
    name = "Test CRM User List"
    description = "A test CRM user list"
    membership_life_span = 60
    upload_key_type = "CONTACT_INFO"
    data_source_type = "FIRST_PARTY"

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/userLists/456"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/userLists/456"}]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.create_crm_based_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            membership_life_span=membership_life_span,
            upload_key_type=upload_key_type,
            data_source_type=data_source_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert operation.create.membership_life_span == membership_life_span
    assert operation.create.crm_based_user_list is not None
    assert (
        operation.create.crm_based_user_list.upload_key_type
        == CustomerMatchUploadKeyTypeEnum.CustomerMatchUploadKeyType.CONTACT_INFO
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created CRM-based user list '{name}' for customer match",
    )


@pytest.mark.asyncio
async def test_create_similar_user_list(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a similar user list."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Similar User List"
    seed_user_list_ids = ["100", "200", "300"]
    description = "A test similar user list"

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/userLists/789"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/userLists/789"}]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.create_similar_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            seed_user_list_ids=seed_user_list_ids,
            description=description,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert operation.create.similar_user_list is not None
    # Note: The implementation only uses the first seed list ID
    assert (
        operation.create.similar_user_list.seed_user_list
        == f"customers/{customer_id}/userLists/100"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created similar user list '{name}' based on seed list 100",
    )


@pytest.mark.asyncio
async def test_create_logical_user_list(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a logical user list."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Logical User List"
    rules = [
        {"user_list_ids": ["100", "200"], "operator": "ALL"},
        {"user_list_ids": ["300"], "operator": "NONE"},
    ]
    rule_operator = "ALL"
    description = "A test logical user list"
    membership_life_span = 90

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/userLists/999"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/userLists/999"}]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.create_logical_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            rules=rules,
            rule_operator=rule_operator,
            description=description,
            membership_life_span=membership_life_span,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert operation.create.membership_life_span == membership_life_span
    assert operation.create.logical_user_list is not None

    # Check the rules
    logical_list = operation.create.logical_user_list
    assert len(logical_list.rules) == 2

    # First rule: ALL of user lists 100 and 200
    rule1 = logical_list.rules[0]
    assert (
        rule1.operator
        == UserListLogicalRuleOperatorEnum.UserListLogicalRuleOperator.ALL
    )
    assert len(rule1.rule_operands) == 2
    assert rule1.rule_operands[0].user_list == f"customers/{customer_id}/userLists/100"
    assert rule1.rule_operands[1].user_list == f"customers/{customer_id}/userLists/200"

    # Second rule: NONE of user list 300
    rule2 = logical_list.rules[1]
    assert (
        rule2.operator
        == UserListLogicalRuleOperatorEnum.UserListLogicalRuleOperator.NONE
    )
    assert len(rule2.rule_operands) == 1
    assert rule2.rule_operands[0].user_list == f"customers/{customer_id}/userLists/300"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created logical user list '{name}' with 2 rules",
    )


@pytest.mark.asyncio
async def test_update_user_list(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a user list."""
    # Arrange
    customer_id = "1234567890"
    user_list_id = "123"
    name = "Updated User List"
    description = "Updated description"
    membership_status = "CLOSED"
    membership_life_span = 45

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/userLists/{user_list_id}"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/userLists/{user_list_id}"}
        ]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.update_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            name=name,
            description=description,
            membership_status=membership_status,
            membership_life_span=membership_life_span,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/userLists/{user_list_id}"
    )
    assert operation.update.name == name
    assert operation.update.description == description
    assert (
        operation.update.membership_status
        == UserListMembershipStatusEnum.UserListMembershipStatus.CLOSED
    )
    assert operation.update.membership_life_span == membership_life_span

    # Check update mask
    assert "name" in operation.update_mask.paths
    assert "description" in operation.update_mask.paths
    assert "membership_status" in operation.update_mask.paths
    assert "membership_life_span" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated user list {user_list_id}",
    )


@pytest.mark.asyncio
async def test_update_user_list_partial(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test partially updating a user list."""
    # Arrange
    customer_id = "1234567890"
    user_list_id = "123"
    name = "Updated Name Only"

    # Create mock response
    mock_response = Mock(spec=MutateUserListsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/userLists/{user_list_id}"

    # Get the mocked user list service client
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/userLists/{user_list_id}"}
        ]
    }

    with patch(
        "src.sdk_services.audiences.user_list_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await user_list_service.update_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_user_list_client.mutate_user_lists.assert_called_once()  # type: ignore
    call_args = mock_user_list_client.mutate_user_lists.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Check update mask - only name should be in the mask
    assert "name" in operation.update_mask.paths
    assert "description" not in operation.update_mask.paths
    assert "membership_status" not in operation.update_mask.paths
    assert "membership_life_span" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_error_handling(
    user_list_service: UserListService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked user list service client and make it raise exception
    mock_user_list_client = user_list_service.client  # type: ignore
    mock_user_list_client.mutate_user_lists.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await user_list_service.create_basic_user_list(
            ctx=mock_ctx,
            customer_id=customer_id,
            name="Test User List",
        )

    assert "Failed to create basic user list" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create basic user list: Test Google Ads Exception",
    )


def test_register_user_list_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_user_list_tools(mock_mcp)

    # Assert
    assert isinstance(service, UserListService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_basic_user_list",
        "create_crm_based_user_list",
        "create_similar_user_list",
        "create_logical_user_list",
        "update_user_list",
    ]

    assert set(tool_names) == set(expected_tools)
