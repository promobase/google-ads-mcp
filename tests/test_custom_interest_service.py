"""Tests for CustomInterestService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.custom_interest_member_type import (
    CustomInterestMemberTypeEnum,
)
from google.ads.googleads.v20.enums.types.custom_interest_status import (
    CustomInterestStatusEnum,
)
from google.ads.googleads.v20.enums.types.custom_interest_type import (
    CustomInterestTypeEnum,
)
from google.ads.googleads.v20.services.services.custom_interest_service import (
    CustomInterestServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.custom_interest_service import (
    MutateCustomInterestsResponse,
)

from src.sdk_services.audiences.custom_interest_service import (
    CustomInterestService,
    register_custom_interest_tools,
)


@pytest.fixture
def custom_interest_service(mock_sdk_client: Any) -> CustomInterestService:
    """Create a CustomInterestService instance with mocked dependencies."""
    # Mock CustomInterestService client
    mock_custom_client = Mock(spec=CustomInterestServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_custom_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.custom_interest_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CustomInterestService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_custom_interest(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a custom interest."""
    # Arrange
    customer_id = "1234567890"
    name = "Tech Enthusiasts"
    description = "People interested in technology and gadgets"
    members = [
        {"type": "KEYWORD", "value": "artificial intelligence"},
        {"type": "KEYWORD", "value": "machine learning"},
        {"type": "URL", "value": "techcrunch.com"},
        {"type": "URL", "value": "wired.com"},
    ]
    type_ = "CUSTOM_AFFINITY"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomInterestsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customInterests/12345"
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_interest_service.client  # type: ignore
    mock_custom_client.mutate_custom_interests.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customInterests/12345"}]
    }

    with patch(
        "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_interest_service.create_custom_interest(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
            type_=type_,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_interests.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_interests.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert (
        operation.create.type_
        == CustomInterestTypeEnum.CustomInterestType.CUSTOM_AFFINITY
    )
    assert (
        operation.create.status == CustomInterestStatusEnum.CustomInterestStatus.ENABLED
    )

    # Verify members
    assert len(operation.create.members) == 4
    # First two members - keywords
    assert (
        operation.create.members[0].member_type
        == CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
    )
    assert operation.create.members[0].parameter == "artificial intelligence"
    assert (
        operation.create.members[1].member_type
        == CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
    )
    assert operation.create.members[1].parameter == "machine learning"
    # Last two members - URLs
    assert (
        operation.create.members[2].member_type
        == CustomInterestMemberTypeEnum.CustomInterestMemberType.URL
    )
    assert operation.create.members[2].parameter == "techcrunch.com"
    assert (
        operation.create.members[3].member_type
        == CustomInterestMemberTypeEnum.CustomInterestMemberType.URL
    )
    assert operation.create.members[3].parameter == "wired.com"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created custom interest '{name}'",
    )


@pytest.mark.asyncio
async def test_create_custom_interest_custom_intent(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a custom intent audience."""
    # Arrange
    customer_id = "1234567890"
    name = "Car Buyers"
    description = "People actively researching car purchases"
    members = [
        {"type": "KEYWORD", "value": "buy new car"},
        {"type": "KEYWORD", "value": "car reviews 2024"},
        {"type": "URL", "value": "cars.com"},
    ]
    type_ = "CUSTOM_INTENT"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomInterestsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customInterests/54321"
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_interest_service.client  # type: ignore
    mock_custom_client.mutate_custom_interests.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customInterests/54321"}]
    }

    with patch(
        "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_interest_service.create_custom_interest(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
            type_=type_,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_interests.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_interests.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert (
        operation.create.type_
        == CustomInterestTypeEnum.CustomInterestType.CUSTOM_INTENT
    )


@pytest.mark.asyncio
async def test_update_custom_interest(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a custom interest."""
    # Arrange
    customer_id = "1234567890"
    custom_interest_id = "12345"
    name = "Updated Tech Enthusiasts"
    description = "Updated description"
    members = [
        {"type": "KEYWORD", "value": "blockchain"},
        {"type": "KEYWORD", "value": "cryptocurrency"},
    ]
    status = "REMOVED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomInterestsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/customInterests/{custom_interest_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_interest_service.client  # type: ignore
    mock_custom_client.mutate_custom_interests.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/customInterests/{custom_interest_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_interest_service.update_custom_interest(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_interest_id=custom_interest_id,
            name=name,
            description=description,
            members=members,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_interests.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_interests.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/customInterests/{custom_interest_id}"
    )
    assert operation.update.name == name
    assert operation.update.description == description
    assert (
        operation.update.status == CustomInterestStatusEnum.CustomInterestStatus.REMOVED
    )

    # Verify update mask
    assert set(operation.update_mask.paths) == {
        "name",
        "description",
        "members",
        "status",
    }

    # Verify updated members
    assert len(operation.update.members) == 2
    assert all(
        member.member_type
        == CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
        for member in operation.update.members
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated custom interest {custom_interest_id}",
    )


@pytest.mark.asyncio
async def test_update_custom_interest_partial(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a custom interest with partial fields."""
    # Arrange
    customer_id = "1234567890"
    custom_interest_id = "12345"
    name = "Updated Name Only"

    # Create mock response
    mock_response = Mock(spec=MutateCustomInterestsResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/customInterests/{custom_interest_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_interest_service.client  # type: ignore
    mock_custom_client.mutate_custom_interests.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/customInterests/{custom_interest_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_interest_service.update_custom_interest(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_interest_id=custom_interest_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_interests.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_interests.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.update.name == name
    # Verify only name is in update mask
    assert operation.update_mask.paths == ["name"]


@pytest.mark.asyncio
async def test_list_custom_interests(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing custom interests."""
    # Arrange
    customer_id = "1234567890"
    type_filter = "CUSTOM_AFFINITY"
    status_filter = "ENABLED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    interest_info = [
        {
            "id": "12345",
            "name": "Tech Enthusiasts",
            "description": "Technology interested users",
            "type": CustomInterestTypeEnum.CustomInterestType.CUSTOM_AFFINITY,
            "status": CustomInterestStatusEnum.CustomInterestStatus.ENABLED,
        },
        {
            "id": "54321",
            "name": "Sports Fans",
            "description": "Sports enthusiasts",
            "type": CustomInterestTypeEnum.CustomInterestType.CUSTOM_AFFINITY,
            "status": CustomInterestStatusEnum.CustomInterestStatus.ENABLED,
        },
    ]

    for info in interest_info:
        row = Mock()
        row.custom_interest = Mock()
        row.custom_interest.id = info["id"]
        row.custom_interest.name = info["name"]
        row.custom_interest.description = info["description"]
        row.custom_interest.type = info["type"]
        row.custom_interest.status = info["status"]
        row.custom_interest.resource_name = (
            f"customers/{customer_id}/customInterests/{info['id']}"
        )
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Mock serialize_proto_message
    def mock_serialize(obj):
        return {"custom_interest": {"name": "Test Interest"}}

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return custom_interest_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.custom_interest_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await custom_interest_service.list_custom_interests(
            ctx=mock_ctx,
            customer_id=customer_id,
            type_filter=type_filter,
            status_filter=status_filter,
        )

    # Assert
    assert len(result) == 2

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"custom_interest.type = '{type_filter}'" in query
    assert f"custom_interest.status = '{status_filter}'" in query
    assert "FROM custom_interest" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 custom interests",
    )


@pytest.mark.asyncio
async def test_get_custom_interest_details(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting custom interest details."""
    # Arrange
    customer_id = "1234567890"
    custom_interest_id = "12345"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    mock_row = Mock()
    mock_row.custom_interest = Mock()
    mock_row.custom_interest.id = custom_interest_id  # type: ignore
    mock_row.custom_interest.name = "Tech Enthusiasts"  # type: ignore
    mock_row.custom_interest.description = "Technology interested users"  # type: ignore
    mock_row.custom_interest.type = (  # type: ignore
        CustomInterestTypeEnum.CustomInterestType.CUSTOM_AFFINITY
    )
    mock_row.custom_interest.status = (  # type: ignore
        CustomInterestStatusEnum.CustomInterestStatus.ENABLED
    )
    mock_row.custom_interest.resource_name = (  # type: ignore
        f"customers/{customer_id}/customInterests/{custom_interest_id}"
    )

    # Mock members
    member1 = Mock()
    member1.member_type = CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
    member1.parameter = "artificial intelligence"
    member1.HasField = Mock(side_effect=lambda x: x == "parameter")

    member2 = Mock()
    member2.member_type = CustomInterestMemberTypeEnum.CustomInterestMemberType.URL
    member2.parameter = "techcrunch.com"
    member2.HasField = Mock(side_effect=lambda x: x == "parameter")

    mock_row.custom_interest.members = [member1, member2]  # type: ignore

    mock_response = Mock()
    mock_response.__iter__ = Mock(return_value=iter([mock_row]))
    mock_google_ads_service.search.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "custom_interest": {
            "id": custom_interest_id,
            "name": "Tech Enthusiasts",
            "members": [
                {"type": "KEYWORD", "value": "artificial intelligence"},
                {"type": "URL", "value": "techcrunch.com"},
            ],
        }
    }

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return custom_interest_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.custom_interest_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.custom_interest_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await custom_interest_service.get_custom_interest_details(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_interest_id=custom_interest_id,
        )

    # Assert
    assert result == expected_result

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"custom_interest.id = {custom_interest_id}" in query
    assert "custom_interest.members" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Retrieved details for custom interest {custom_interest_id}",
    )


@pytest.mark.asyncio
async def test_error_handling_create_custom_interest(
    custom_interest_service: CustomInterestService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating custom interest fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Interest"
    description = "Test description"
    members = [{"type": "KEYWORD", "value": "test"}]

    # Get the mocked custom service client and make it raise exception
    mock_custom_client = custom_interest_service.client  # type: ignore
    mock_custom_client.mutate_custom_interests.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await custom_interest_service.create_custom_interest(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
        )

    assert "Failed to create custom interest" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create custom interest: Test Google Ads Exception",
    )


def test_register_custom_interest_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_custom_interest_tools(mock_mcp)

    # Assert
    assert isinstance(service, CustomInterestService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_custom_interest",
        "update_custom_interest",
        "list_custom_interests",
        "get_custom_interest_details",
    ]

    assert set(tool_names) == set(expected_tools)
