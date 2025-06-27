"""Tests for CustomAudienceService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.custom_audience_member_type import (
    CustomAudienceMemberTypeEnum,
)
from google.ads.googleads.v20.enums.types.custom_audience_status import (
    CustomAudienceStatusEnum,
)
from google.ads.googleads.v20.enums.types.custom_audience_type import (
    CustomAudienceTypeEnum,
)
from google.ads.googleads.v20.services.services.custom_audience_service import (
    CustomAudienceServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.custom_audience_service import (
    MutateCustomAudiencesResponse,
)

from src.sdk_services.audiences.custom_audience_service import (
    CustomAudienceService,
    register_custom_audience_tools,
)


@pytest.fixture
def custom_audience_service(mock_sdk_client: Any) -> CustomAudienceService:
    """Create a CustomAudienceService instance with mocked dependencies."""
    # Mock CustomAudienceService client
    mock_custom_client = Mock(spec=CustomAudienceServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_custom_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.custom_audience_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CustomAudienceService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_custom_audience(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a custom audience."""
    # Arrange
    customer_id = "1234567890"
    name = "Technology Enthusiasts"
    description = "People interested in tech products and innovations"
    members = [
        {"type": "KEYWORD", "keyword": "artificial intelligence"},
        {"type": "KEYWORD", "keyword": "machine learning"},
        {"type": "URL", "url": "techcrunch.com"},
        {"type": "APP", "app": "com.example.techapp"},
    ]
    type_ = "AUTO"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customAudiences/12345"
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_audience_service.client  # type: ignore
    mock_custom_client.mutate_custom_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customAudiences/12345"}]
    }

    with patch(
        "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_audience_service.create_custom_audience(
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
    mock_custom_client.mutate_custom_audiences.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert operation.create.type_ == CustomAudienceTypeEnum.CustomAudienceType.AUTO
    assert (
        operation.create.status == CustomAudienceStatusEnum.CustomAudienceStatus.ENABLED
    )

    # Verify members
    assert len(operation.create.members) == 4
    # First member - keyword
    assert (
        operation.create.members[0].member_type
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
    )
    assert operation.create.members[0].keyword == "artificial intelligence"
    # Second member - keyword
    assert (
        operation.create.members[1].member_type
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
    )
    assert operation.create.members[1].keyword == "machine learning"
    # Third member - URL
    assert (
        operation.create.members[2].member_type
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.URL
    )
    assert operation.create.members[2].url == "techcrunch.com"
    # Fourth member - app
    assert (
        operation.create.members[3].member_type
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.APP
    )
    assert operation.create.members[3].app == "com.example.techapp"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created custom audience '{name}'",
    )


@pytest.mark.asyncio
async def test_create_custom_audience_with_place_category(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a custom audience with place category member."""
    # Arrange
    customer_id = "1234567890"
    name = "Local Restaurant Visitors"
    description = "People who visit restaurants"
    members = [
        {"type": "PLACE_CATEGORY", "place_category": 13000},  # Restaurant category
    ]
    type_ = "PURCHASE_INTENT"
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customAudiences/54321"
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_audience_service.client  # type: ignore
    mock_custom_client.mutate_custom_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customAudiences/54321"}]
    }

    with patch(
        "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_audience_service.create_custom_audience(
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
    mock_custom_client.mutate_custom_audiences.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_audiences.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert (
        operation.create.type_
        == CustomAudienceTypeEnum.CustomAudienceType.PURCHASE_INTENT
    )

    # Verify place category member
    assert len(operation.create.members) == 1
    assert (
        operation.create.members[0].member_type
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.PLACE_CATEGORY
    )
    assert operation.create.members[0].place_category == 13000


@pytest.mark.asyncio
async def test_update_custom_audience(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a custom audience."""
    # Arrange
    customer_id = "1234567890"
    custom_audience_id = "12345"
    name = "Updated Tech Enthusiasts"
    description = "Updated description"
    members = [
        {"type": "KEYWORD", "keyword": "blockchain"},
        {"type": "KEYWORD", "keyword": "cryptocurrency"},
    ]
    status = "REMOVED"

    # Create mock response
    mock_response = Mock(spec=MutateCustomAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/customAudiences/{custom_audience_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_audience_service.client  # type: ignore
    mock_custom_client.mutate_custom_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/customAudiences/{custom_audience_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_audience_service.update_custom_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_audience_id=custom_audience_id,
            name=name,
            description=description,
            members=members,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_audiences.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/customAudiences/{custom_audience_id}"
    )
    assert operation.update.name == name
    assert operation.update.description == description
    assert (
        operation.update.status == CustomAudienceStatusEnum.CustomAudienceStatus.REMOVED
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
        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
        for member in operation.update.members
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated custom audience {custom_audience_id}",
    )


@pytest.mark.asyncio
async def test_update_custom_audience_partial(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a custom audience with partial fields."""
    # Arrange
    customer_id = "1234567890"
    custom_audience_id = "12345"
    name = "Updated Name Only"

    # Create mock response
    mock_response = Mock(spec=MutateCustomAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/customAudiences/{custom_audience_id}"
    )
    mock_response.results = [mock_result]

    # Get the mocked custom service client
    mock_custom_client = custom_audience_service.client  # type: ignore
    mock_custom_client.mutate_custom_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/customAudiences/{custom_audience_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await custom_audience_service.update_custom_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_audience_id=custom_audience_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_custom_client.mutate_custom_audiences.assert_called_once()  # type: ignore
    call_args = mock_custom_client.mutate_custom_audiences.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.update.name == name
    # Verify only name is in update mask
    assert operation.update_mask.paths == ["name"]


@pytest.mark.asyncio
async def test_list_custom_audiences(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing custom audiences."""
    # Arrange
    customer_id = "1234567890"
    type_filter = "AUTO"
    status_filter = "ENABLED"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    audience_info = [
        {
            "id": "12345",
            "name": "Tech Enthusiasts",
            "description": "Technology interested users",
            "type": CustomAudienceTypeEnum.CustomAudienceType.AUTO,
            "status": CustomAudienceStatusEnum.CustomAudienceStatus.ENABLED,
        },
        {
            "id": "54321",
            "name": "Sports Fans",
            "description": "Sports enthusiasts",
            "type": CustomAudienceTypeEnum.CustomAudienceType.AUTO,
            "status": CustomAudienceStatusEnum.CustomAudienceStatus.ENABLED,
        },
    ]

    for info in audience_info:
        row = Mock()
        row.custom_audience = Mock()
        row.custom_audience.id = info["id"]
        row.custom_audience.name = info["name"]
        row.custom_audience.description = info["description"]
        row.custom_audience.type = info["type"]
        row.custom_audience.status = info["status"]
        row.custom_audience.resource_name = (
            f"customers/{customer_id}/customAudiences/{info['id']}"
        )
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Mock serialize_proto_message
    def mock_serialize(obj):
        return {"custom_audience": {"name": "Test Audience"}}

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return custom_audience_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.custom_audience_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
            side_effect=mock_serialize,
        ),
    ):
        # Act
        result = await custom_audience_service.list_custom_audiences(
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
    assert f"custom_audience.type = '{type_filter}'" in query
    assert f"custom_audience.status = '{status_filter}'" in query
    assert "FROM custom_audience" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 2 custom audiences",
    )


@pytest.mark.asyncio
async def test_get_custom_audience_details(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test getting custom audience details."""
    # Arrange
    customer_id = "1234567890"
    custom_audience_id = "12345"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    mock_row = Mock()
    mock_row.custom_audience = Mock()
    mock_row.custom_audience.id = custom_audience_id  # type: ignore
    mock_row.custom_audience.name = "Tech Enthusiasts"  # type: ignore
    mock_row.custom_audience.description = "Technology interested users"  # type: ignore
    mock_row.custom_audience.type = CustomAudienceTypeEnum.CustomAudienceType.AUTO  # type: ignore
    mock_row.custom_audience.status = (  # type: ignore
        CustomAudienceStatusEnum.CustomAudienceStatus.ENABLED
    )
    mock_row.custom_audience.resource_name = (  # type: ignore
        f"customers/{customer_id}/customAudiences/{custom_audience_id}"
    )

    # Mock members
    member1 = Mock()
    member1.member_type = CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
    member1.keyword = "artificial intelligence"

    member2 = Mock()
    member2.member_type = CustomAudienceMemberTypeEnum.CustomAudienceMemberType.URL
    member2.url = "techcrunch.com"

    mock_row.custom_audience.members = [member1, member2]  # type: ignore

    mock_response = Mock()
    mock_response.__iter__ = Mock(return_value=iter([mock_row]))
    mock_google_ads_service.search.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "custom_audience": {
            "id": custom_audience_id,
            "name": "Tech Enthusiasts",
            "members": [
                {"member_type": "KEYWORD", "keyword": "artificial intelligence"},
                {"member_type": "URL", "url": "techcrunch.com"},
            ],
        }
    }

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return custom_audience_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with (
        patch(
            "src.sdk_services.audiences.custom_audience_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.audiences.custom_audience_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        # Act
        result = await custom_audience_service.get_custom_audience_details(
            ctx=mock_ctx,
            customer_id=customer_id,
            custom_audience_id=custom_audience_id,
        )

    # Assert
    assert result == expected_result

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"custom_audience.id = {custom_audience_id}" in query
    assert "custom_audience.members" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found custom audience {custom_audience_id}",
    )


@pytest.mark.asyncio
async def test_error_handling_create_custom_audience(
    custom_audience_service: CustomAudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating custom audience fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Audience"
    description = "Test description"
    members = [{"type": "KEYWORD", "keyword": "test"}]

    # Get the mocked custom service client and make it raise exception
    mock_custom_client = custom_audience_service.client  # type: ignore
    mock_custom_client.mutate_custom_audiences.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await custom_audience_service.create_custom_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
        )

    assert "Failed to create custom audience" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create custom audience: Test Google Ads Exception",
    )


def test_register_custom_audience_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_custom_audience_tools(mock_mcp)

    # Assert
    assert isinstance(service, CustomAudienceService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_custom_audience",
        "update_custom_audience",
        "list_custom_audiences",
        "get_custom_audience_details",
    ]

    assert set(tool_names) == set(expected_tools)
