"""Tests for CustomerUserAccessService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.access_role import AccessRoleEnum
from google.ads.googleads.v20.services.services.customer_user_access_service import (
    CustomerUserAccessServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.customer_user_access_service import (
    MutateCustomerUserAccessResponse,
)

from src.sdk_services.account.customer_user_access_service import (
    CustomerUserAccessService,
    register_customer_user_access_tools,
)


@pytest.fixture
def customer_user_access_service(mock_sdk_client: Any) -> CustomerUserAccessService:
    """Create a CustomerUserAccessService instance with mocked dependencies."""
    # Mock CustomerUserAccessService client
    mock_customer_user_access_client = Mock(spec=CustomerUserAccessServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_customer_user_access_client  # type: ignore

    with patch(
        "src.sdk_services.account.customer_user_access_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CustomerUserAccessService()
        # Force client initialization
        _ = service.client
        return service


# Note: test_grant_user_access and test_grant_user_access_admin_role have been removed
# because CustomerUserAccessService does not support creating new access.
# To grant access to new users, use CustomerUserAccessInvitationService instead.


@pytest.mark.asyncio
async def test_update_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating user access permissions."""
    # Arrange
    customer_id = "1234567890"
    user_access_resource_name = "customers/1234567890/customerUserAccesses/111222333"
    new_access_role = AccessRoleEnum.AccessRole.READ_ONLY

    # Create mock response
    mock_response = Mock(spec=MutateCustomerUserAccessResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = user_access_resource_name  # type: ignore

    # Get the mocked customer user access service client
    mock_customer_user_access_client = customer_user_access_service.client  # type: ignore
    mock_customer_user_access_client.mutate_customer_user_access.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": user_access_resource_name}}

    with patch(
        "src.sdk_services.account.customer_user_access_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_user_access_service.update_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
            access_role=new_access_role,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_customer_user_access_client.mutate_customer_user_access.assert_called_once()  # type: ignore
    call_args = mock_customer_user_access_client.mutate_customer_user_access.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.update.resource_name == user_access_resource_name
    assert operation.update.access_role == new_access_role
    assert operation.update_mask.paths == ["access_role"]

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Updated user access permissions",
    )


@pytest.mark.asyncio
async def test_update_user_access_no_changes(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating user access with no changes."""
    # Arrange
    customer_id = "1234567890"
    user_access_resource_name = "customers/1234567890/customerUserAccesses/111222333"

    # Create mock response
    mock_response = Mock(spec=MutateCustomerUserAccessResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = user_access_resource_name  # type: ignore

    # Get the mocked customer user access service client
    mock_customer_user_access_client = customer_user_access_service.client  # type: ignore
    mock_customer_user_access_client.mutate_customer_user_access.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": user_access_resource_name}}

    with patch(
        "src.sdk_services.account.customer_user_access_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_user_access_service.update_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
            access_role=None,
        )

    # Assert
    assert result == expected_result

    # Verify the update mask is empty when no fields are updated
    call_args = mock_customer_user_access_client.mutate_customer_user_access.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operation
    assert len(operation.update_mask.paths) == 0


@pytest.mark.asyncio
async def test_list_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing user access permissions."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    roles = [
        AccessRoleEnum.AccessRole.ADMIN,
        AccessRoleEnum.AccessRole.STANDARD,
        AccessRoleEnum.AccessRole.READ_ONLY,
    ]
    for i in range(3):
        row = Mock()
        row.customer_user_access = Mock()
        row.customer_user_access.resource_name = (
            f"customers/{customer_id}/customerUserAccesses/{i + 100}"
        )
        row.customer_user_access.user_id = i + 100
        row.customer_user_access.email_address = f"user{i}@example.com"
        row.customer_user_access.access_role = Mock()
        row.customer_user_access.access_role.name = roles[i].name
        row.customer_user_access.access_creation_date_time = (
            f"2024-01-{i + 1:02d} 10:00:00"
        )
        row.customer_user_access.inviter_user_email_address = "admin@example.com"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return customer_user_access_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message for each user access
    def serialize_side_effect(obj: Any):
        return {
            "resource_name": obj.resource_name,
            "user_id": obj.user_id,
            "email_address": obj.email_address,
            "access_role": obj.access_role.name,
            "access_creation_date_time": obj.access_creation_date_time,
            "inviter_user_email_address": obj.inviter_user_email_address,
        }

    with (
        patch(
            "src.sdk_services.account.customer_user_access_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.customer_user_access_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await customer_user_access_service.list_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Check first result (admin)
    first_result = result[0]
    assert first_result["user_id"] == 100
    assert first_result["email_address"] == "user0@example.com"
    assert first_result["access_role"] == "ADMIN"
    assert first_result["inviter_user_email_address"] == "admin@example.com"

    # Check second result (standard)
    second_result = result[1]
    assert second_result["access_role"] == "STANDARD"

    # Check third result (read-only)
    third_result = result[2]
    assert third_result["access_role"] == "READ_ONLY"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM customer_user_access" in query
    assert "ORDER BY customer_user_access.email_address" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 user access permissions",
    )


@pytest.mark.asyncio
async def test_revoke_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test revoking user access."""
    # Arrange
    customer_id = "1234567890"
    user_access_resource_name = "customers/1234567890/customerUserAccesses/111222333"

    # Create mock response
    mock_response = Mock(spec=MutateCustomerUserAccessResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = user_access_resource_name  # type: ignore

    # Get the mocked customer user access service client
    mock_customer_user_access_client = customer_user_access_service.client  # type: ignore
    mock_customer_user_access_client.mutate_customer_user_access.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": user_access_resource_name}}

    with patch(
        "src.sdk_services.account.customer_user_access_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await customer_user_access_service.revoke_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_customer_user_access_client.mutate_customer_user_access.assert_called_once()  # type: ignore
    call_args = mock_customer_user_access_client.mutate_customer_user_access.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.remove == user_access_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Revoked user access",
    )


# Note: test_error_handling_grant_user_access has been removed
# because CustomerUserAccessService does not support creating new access.


@pytest.mark.asyncio
async def test_error_handling_update_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating user access fails."""
    # Arrange
    customer_id = "1234567890"
    user_access_resource_name = "customers/1234567890/customerUserAccesses/111222333"

    # Get the mocked customer user access service client and make it raise exception
    mock_customer_user_access_client = customer_user_access_service.client  # type: ignore
    mock_customer_user_access_client.mutate_customer_user_access.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await customer_user_access_service.update_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
            access_role=AccessRoleEnum.AccessRole.READ_ONLY,
        )

    assert "Failed to update user access" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update user access: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing user access fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return customer_user_access_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.account.customer_user_access_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await customer_user_access_service.list_user_access(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list user access" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list user access: Search failed",
    )


@pytest.mark.asyncio
async def test_error_handling_revoke_user_access(
    customer_user_access_service: CustomerUserAccessService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when revoking user access fails."""
    # Arrange
    customer_id = "1234567890"
    user_access_resource_name = "customers/1234567890/customerUserAccesses/111222333"

    # Get the mocked customer user access service client and make it raise exception
    mock_customer_user_access_client = customer_user_access_service.client  # type: ignore
    mock_customer_user_access_client.mutate_customer_user_access.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await customer_user_access_service.revoke_user_access(
            ctx=mock_ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
        )

    assert "Failed to revoke user access" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to revoke user access: Test Google Ads Exception",
    )


def test_register_customer_user_access_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_customer_user_access_tools(mock_mcp)

    # Assert
    assert isinstance(service, CustomerUserAccessService)

    # Verify that tools were registered
    assert (
        mock_mcp.tool.call_count == 3
    )  # 3 tools registered (no grant_user_access)  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "update_user_access",
        "list_user_access",
        "revoke_user_access",
    ]

    assert set(tool_names) == set(expected_tools)
