"""Tests for AccountLinkService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.account_link_status import (
    AccountLinkStatusEnum,
)
from google.ads.googleads.v20.enums.types.linked_account_type import (
    LinkedAccountTypeEnum,
)
from google.ads.googleads.v20.enums.types.mobile_app_vendor import (
    MobileAppVendorEnum,
)
from google.ads.googleads.v20.services.services.account_link_service import (
    AccountLinkServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.account_link_service import (
    CreateAccountLinkResponse,
    MutateAccountLinkResponse,
)

from src.sdk_services.account.account_link_service import (
    AccountLinkService,
    register_account_link_tools,
)


@pytest.fixture
def account_link_service(mock_sdk_client: Any) -> AccountLinkService:
    """Create an AccountLinkService instance with mocked dependencies."""
    # Mock AccountLinkService client
    mock_account_link_client = Mock(spec=AccountLinkServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_account_link_client

    with patch(
        "src.sdk_services.account.account_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AccountLinkService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an account link."""
    # Arrange
    customer_id = "1234567890"
    app_analytics_provider_id = 123456
    app_id = "com.example.app"
    app_vendor = MobileAppVendorEnum.MobileAppVendor.GOOGLE_APP_STORE
    status = AccountLinkStatusEnum.AccountLinkStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=CreateAccountLinkResponse)
    mock_response.resource_name = "customers/1234567890/accountLinks/111222333"

    # Get the mocked account link service client
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.create_account_link.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"resource_name": "customers/1234567890/accountLinks/111222333"}

    with patch(
        "src.sdk_services.account.account_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_link_service.create_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            app_analytics_provider_id=app_analytics_provider_id,
            app_id=app_id,
            app_vendor=app_vendor,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_link_client.create_account_link.assert_called_once()  # type: ignore
    call_args = mock_account_link_client.create_account_link.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert (
        request.account_link.type_
        == LinkedAccountTypeEnum.LinkedAccountType.THIRD_PARTY_APP_ANALYTICS
    )
    assert (
        request.account_link.third_party_app_analytics.app_analytics_provider_id
        == app_analytics_provider_id
    )
    assert request.account_link.third_party_app_analytics.app_id == app_id
    assert request.account_link.third_party_app_analytics.app_vendor == app_vendor
    assert request.account_link.status == status

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created account link for app {app_id}",
    )


@pytest.mark.asyncio
async def test_update_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an account link."""
    # Arrange
    customer_id = "1234567890"
    account_link_resource_name = "customers/1234567890/accountLinks/111222333"
    new_status = AccountLinkStatusEnum.AccountLinkStatus.REMOVED

    # Create mock response
    mock_response = Mock(spec=MutateAccountLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = account_link_resource_name

    # Get the mocked account link service client
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.mutate_account_link.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": account_link_resource_name}}

    with patch(
        "src.sdk_services.account.account_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_link_service.update_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_link_client.mutate_account_link.assert_called_once()  # type: ignore
    call_args = mock_account_link_client.mutate_account_link.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.update.resource_name == account_link_resource_name
    assert operation.update.status == new_status
    assert "status" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Updated account link",
    )


@pytest.mark.asyncio
async def test_update_account_link_no_changes(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an account link with no changes."""
    # Arrange
    customer_id = "1234567890"
    account_link_resource_name = "customers/1234567890/accountLinks/111222333"

    # Create mock response
    mock_response = Mock(spec=MutateAccountLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = account_link_resource_name

    # Get the mocked account link service client
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.mutate_account_link.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": account_link_resource_name}}

    with patch(
        "src.sdk_services.account.account_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_link_service.update_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
            status=None,
        )

    # Assert
    assert result == expected_result

    # Verify the update mask is empty when no fields are updated
    call_args = mock_account_link_client.mutate_account_link.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operation
    assert len(operation.update_mask.paths) == 0


@pytest.mark.asyncio
async def test_list_account_links(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing account links."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.account_link = Mock()
        row.account_link.resource_name = (
            f"customers/{customer_id}/accountLinks/{i + 100}"
        )
        row.account_link.account_link_id = i + 100
        row.account_link.status = Mock()
        row.account_link.status.name = "ENABLED"
        row.account_link.type = Mock()
        row.account_link.type.name = "THIRD_PARTY_APP_ANALYTICS"
        row.account_link.third_party_app_analytics = Mock()
        row.account_link.third_party_app_analytics.app_analytics_provider_id = 123456
        row.account_link.third_party_app_analytics.app_id = f"com.example.app{i}"
        row.account_link.third_party_app_analytics.app_vendor = Mock()
        row.account_link.third_party_app_analytics.app_vendor.name = "GOOGLE_APP_STORE"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return account_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    # Mock serialize_proto_message for each account link
    def serialize_side_effect(obj: Any):
        result = {
            "resource_name": obj.resource_name,
            "account_link_id": obj.account_link_id,
            "status": obj.status.name,
            "type": obj.type.name,
        }
        if hasattr(obj, "third_party_app_analytics") and obj.third_party_app_analytics:
            result["third_party_app_analytics"] = {
                "app_analytics_provider_id": obj.third_party_app_analytics.app_analytics_provider_id,
                "app_id": obj.third_party_app_analytics.app_id,
                "app_vendor": obj.third_party_app_analytics.app_vendor.name,
            }
        return result

    with (
        patch(
            "src.sdk_services.account.account_link_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.account.account_link_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await account_link_service.list_account_links(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_removed=False,
        )

    # Assert
    assert len(result) == 3

    # Check first result
    first_result = result[0]
    assert first_result["account_link_id"] == 100
    assert first_result["status"] == "ENABLED"
    assert first_result["type"] == "THIRD_PARTY_APP_ANALYTICS"
    assert (
        first_result["third_party_app_analytics"]["app_analytics_provider_id"] == 123456
    )
    assert first_result["third_party_app_analytics"]["app_id"] == "com.example.app0"
    assert first_result["third_party_app_analytics"]["app_vendor"] == "GOOGLE_APP_STORE"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM account_link" in query
    assert "WHERE account_link.status != 'REMOVED'" in query
    assert "ORDER BY account_link.account_link_id" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 account links",
    )


@pytest.mark.asyncio
async def test_list_account_links_include_removed(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing account links including removed ones."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return account_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.account.account_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        await account_link_service.list_account_links(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_removed=True,
        )

    # Verify the search query doesn't filter removed links
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert "WHERE account_link.status != 'REMOVED'" not in query


@pytest.mark.asyncio
async def test_remove_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an account link."""
    # Arrange
    customer_id = "1234567890"
    account_link_resource_name = "customers/1234567890/accountLinks/111222333"

    # Create mock response
    mock_response = Mock(spec=MutateAccountLinkResponse)
    mock_response.result = Mock()
    mock_response.result.resource_name = account_link_resource_name

    # Get the mocked account link service client
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.mutate_account_link.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"result": {"resource_name": account_link_resource_name}}

    with patch(
        "src.sdk_services.account.account_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await account_link_service.remove_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_account_link_client.mutate_account_link.assert_called_once()  # type: ignore
    call_args = mock_account_link_client.mutate_account_link.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    operation = request.operation
    assert operation.remove == account_link_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Removed account link",
    )


@pytest.mark.asyncio
async def test_error_handling_create_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating account link fails."""
    # Arrange
    customer_id = "1234567890"
    app_analytics_provider_id = 123456
    app_id = "com.example.app"
    app_vendor = MobileAppVendorEnum.MobileAppVendor.GOOGLE_APP_STORE

    # Get the mocked account link service client and make it raise exception
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.create_account_link.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_link_service.create_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            app_analytics_provider_id=app_analytics_provider_id,
            app_id=app_id,
            app_vendor=app_vendor,
        )

    assert "Failed to create account link" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create account link: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating account link fails."""
    # Arrange
    customer_id = "1234567890"
    account_link_resource_name = "customers/1234567890/accountLinks/111222333"

    # Get the mocked account link service client and make it raise exception
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.mutate_account_link.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_link_service.update_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
            status=AccountLinkStatusEnum.AccountLinkStatus.REMOVED,
        )

    assert "Failed to update account link" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update account link: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_list_account_links(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing account links fails."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search and make it raise exception
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.side_effect = Exception("Search failed")

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return account_link_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.sdk_services.account.account_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_link_service.list_account_links(
                ctx=mock_ctx,
                customer_id=customer_id,
            )

    assert "Failed to list account links" in str(exc_info.value)
    assert "Search failed" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to list account links: Search failed",
    )


@pytest.mark.asyncio
async def test_error_handling_remove_account_link(
    account_link_service: AccountLinkService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing account link fails."""
    # Arrange
    customer_id = "1234567890"
    account_link_resource_name = "customers/1234567890/accountLinks/111222333"

    # Get the mocked account link service client and make it raise exception
    mock_account_link_client = account_link_service.client  # type: ignore
    mock_account_link_client.mutate_account_link.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await account_link_service.remove_account_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
        )

    assert "Failed to remove account link" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to remove account link: Test Google Ads Exception",
    )


def test_register_account_link_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_account_link_tools(mock_mcp)

    # Assert
    assert isinstance(service, AccountLinkService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_account_link",
        "update_account_link",
        "list_account_links",
        "remove_account_link",
    ]

    assert set(tool_names) == set(expected_tools)
