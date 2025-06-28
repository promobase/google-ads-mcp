"""Tests for RemarketingActionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.remarketing_action_service import (
    RemarketingActionServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.remarketing_action_service import (
    MutateRemarketingActionsResponse,
)

from src.sdk_services.audiences.remarketing_action_service import (
    RemarketingActionService,
    register_remarketing_action_tools,
)


@pytest.fixture
def remarketing_action_service(mock_sdk_client: Any) -> RemarketingActionService:
    """Create a RemarketingActionService instance with mocked dependencies."""
    # Mock RemarketingActionService client
    mock_remarketing_client = Mock(spec=RemarketingActionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_remarketing_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.remarketing_action_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = RemarketingActionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_remarketing_action(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a remarketing action."""
    # Arrange
    customer_id = "1234567890"
    name = "Website Visitors"

    # Create mock response
    mock_response = Mock(spec=MutateRemarketingActionsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/remarketingActions/12345"
    mock_response.results = [mock_result]

    # Get the mocked remarketing service client
    mock_remarketing_client = remarketing_action_service.client  # type: ignore
    mock_remarketing_client.mutate_remarketing_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/remarketingActions/12345"}]
    }

    with patch(
        "src.sdk_services.audiences.remarketing_action_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await remarketing_action_service.create_remarketing_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_remarketing_client.mutate_remarketing_actions.assert_called_once()  # type: ignore
    call_args = mock_remarketing_client.mutate_remarketing_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created remarketing action '{name}'",
    )


@pytest.mark.asyncio
async def test_update_remarketing_action(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a remarketing action."""
    # Arrange
    customer_id = "1234567890"
    remarketing_action_id = "12345"
    name = "Updated Website Visitors"

    # Create mock response
    mock_response = Mock(spec=MutateRemarketingActionsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/remarketingActions/{remarketing_action_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked remarketing service client
    mock_remarketing_client = remarketing_action_service.client  # type: ignore
    mock_remarketing_client.mutate_remarketing_actions.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/remarketingActions/{remarketing_action_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.audiences.remarketing_action_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await remarketing_action_service.update_remarketing_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            remarketing_action_id=remarketing_action_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_remarketing_client.mutate_remarketing_actions.assert_called_once()  # type: ignore
    call_args = mock_remarketing_client.mutate_remarketing_actions.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/remarketingActions/{remarketing_action_id}"
    )
    assert operation.update.name == name
    assert operation.update_mask.paths == ["name"]

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated remarketing action {remarketing_action_id}",
    )


@pytest.mark.asyncio
async def test_list_remarketing_actions(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing remarketing actions."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    action_info = [
        {"id": "12345", "name": "Website Visitors"},
        {"id": "54321", "name": "Cart Abandoners"},
        {"id": "99999", "name": "Product Page Viewers"},
    ]

    for info in action_info:
        row = Mock()
        row.remarketing_action = Mock()
        row.remarketing_action.id = info["id"]
        row.remarketing_action.name = info["name"]
        row.remarketing_action.resource_name = (
            f"customers/{customer_id}/remarketingActions/{info['id']}"
        )
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Mock serialize_proto_message
    def mock_serialize(obj: Any) -> Any:
        return {"remarketing_action": {"name": "Test Action"}}

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return remarketing_action_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.remarketing_action_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.remarketing_action_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await remarketing_action_service.list_remarketing_actions(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 3

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM remarketing_action" in query
    assert "ORDER BY remarketing_action.name" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 remarketing actions",
    )


@pytest.mark.asyncio
async def test_get_remarketing_action_tags(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting remarketing action tags."""
    # Arrange
    customer_id = "1234567890"
    remarketing_action_id = "12345"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    mock_row = Mock()
    mock_row.remarketing_action = Mock()
    mock_row.remarketing_action.id = remarketing_action_id  # type: ignore
    mock_row.remarketing_action.name = "Website Visitors"  # type: ignore
    mock_row.remarketing_action.resource_name = (  # type: ignore
        f"customers/{customer_id}/remarketingActions/{remarketing_action_id}"
    )

    # Mock tag snippets
    snippet1 = Mock()
    snippet1.type_ = Mock(name="REMARKETING")
    snippet1.page_format = Mock(name="HTML")
    snippet1.global_site_tag = (
        "<!-- Global site tag (gtag.js) - Google Ads: 123456789 -->"
    )
    snippet1.event_snippet = (
        "<!-- Event snippet for Website Visitors conversion page -->"
    )

    snippet2 = Mock()
    snippet2.type_ = Mock(name="REMARKETING")
    snippet2.page_format = Mock(name="AMP")
    snippet2.global_site_tag = "<!-- AMP Global site tag -->"
    snippet2.event_snippet = "<!-- AMP Event snippet -->"

    mock_row.remarketing_action.tag_snippets = [snippet1, snippet2]  # type: ignore

    mock_response = Mock()
    mock_response.__iter__ = Mock(return_value=iter([mock_row]))
    mock_google_ads_service.search.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "remarketing_action": {
            "id": remarketing_action_id,
            "name": "Website Visitors",
            "tag_snippets": [
                {
                    "type": "REMARKETING",
                    "page_format": "HTML",
                    "global_site_tag": "<!-- Global site tag (gtag.js) - Google Ads: 123456789 -->",
                    "event_snippet": "<!-- Event snippet for Website Visitors conversion page -->",
                },
                {
                    "type": "REMARKETING",
                    "page_format": "AMP",
                    "global_site_tag": "<!-- AMP Global site tag -->",
                    "event_snippet": "<!-- AMP Event snippet -->",
                },
            ],
        }
    }

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return remarketing_action_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.remarketing_action_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.remarketing_action_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await remarketing_action_service.get_remarketing_action_tags(
            ctx=mock_ctx,
            customer_id=customer_id,
            remarketing_action_id=remarketing_action_id,
        )

    # Assert
    assert result == expected_result

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"remarketing_action.id = {remarketing_action_id}" in query
    assert "remarketing_action.tag_snippets" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Retrieved remarketing action {remarketing_action_id}",
    )


@pytest.mark.asyncio
async def test_get_remarketing_action_tags_not_found(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting remarketing action tags when action not found."""
    # Arrange
    customer_id = "1234567890"
    remarketing_action_id = "99999"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create empty mock response
    mock_response = Mock()
    mock_response.__iter__ = Mock(return_value=iter([]))
    mock_google_ads_service.search.return_value = mock_response  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return remarketing_action_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.audiences.remarketing_action_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await remarketing_action_service.get_remarketing_action_tags(
                ctx=mock_ctx,
                customer_id=customer_id,
                remarketing_action_id=remarketing_action_id,
            )

        assert f"Remarketing action {remarketing_action_id} not found" in str(
            exc_info.value
        )

    # Verify error logging - should be called twice (once in _get_remarketing_action and once in get_remarketing_action_tags)
    assert mock_ctx.log.call_count == 2  # type: ignore
    # Check the last call
    mock_ctx.log.assert_called_with(  # type: ignore
        level="error",
        message=f"Failed to get remarketing action tags: Failed to get remarketing action: Remarketing action {remarketing_action_id} not found",
    )


@pytest.mark.asyncio
async def test_error_handling_create_remarketing_action(
    remarketing_action_service: RemarketingActionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating remarketing action fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Action"

    # Get the mocked remarketing service client and make it raise exception
    mock_remarketing_client = remarketing_action_service.client  # type: ignore
    mock_remarketing_client.mutate_remarketing_actions.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await remarketing_action_service.create_remarketing_action(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
        )

    assert "Failed to create remarketing action" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create remarketing action: Test Google Ads Exception",
    )


def test_register_remarketing_action_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_remarketing_action_tools(mock_mcp)

    # Assert
    assert isinstance(service, RemarketingActionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_remarketing_action",
        "update_remarketing_action",
        "list_remarketing_actions",
        "get_remarketing_action_tags",
    ]

    assert set(tool_names) == set(expected_tools)
