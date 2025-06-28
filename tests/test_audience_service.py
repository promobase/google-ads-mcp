"""Tests for AudienceService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.audience_status import AudienceStatusEnum
from google.ads.googleads.v20.services.services.audience_service import (
    AudienceServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.audience_service import (
    MutateAudiencesResponse,
)

from src.services.audiences.audience_service import (
    AudienceService,
    register_audience_tools,
)


@pytest.fixture
def audience_service(mock_sdk_client: Any) -> AudienceService:
    """Create an AudienceService instance with mocked dependencies."""
    # Mock AudienceService client
    mock_audience_client = Mock(spec=AudienceServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_audience_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.audience_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AudienceService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_combined_audience_with_age(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a combined audience with age dimension."""
    # Arrange
    customer_id = "1234567890"
    name = "Young Adults Audience"
    description = "Audience targeting 18-34 age range"
    dimensions = [{"type": "AGE", "age_ranges": ["AGE_RANGE_18_24", "AGE_RANGE_25_34"]}]
    status = "ENABLED"

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/audiences/111222333"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/audiences/111222333"}]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.create_combined_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert operation.create.status == AudienceStatusEnum.AudienceStatus.ENABLED
    assert len(operation.create.dimensions) == 1
    assert operation.create.dimensions[0].age is not None
    assert len(operation.create.dimensions[0].age.age_ranges) == 2


@pytest.mark.asyncio
async def test_create_combined_audience_with_multiple_dimensions(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a combined audience with multiple dimensions."""
    # Arrange
    customer_id = "1234567890"
    name = "High Income Parents"
    description = "Targeting high income parents"
    dimensions = [
        {
            "type": "HOUSEHOLD_INCOME",
            "income_ranges": ["INCOME_RANGE_80_90", "INCOME_RANGE_90_UP"],
        },
        {"type": "PARENTAL_STATUS", "parent_types": ["PARENT", "NOT_A_PARENT"]},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/audiences/111222333"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/audiences/111222333"}]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.create_combined_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.description == description
    assert len(operation.create.dimensions) == 2

    # Check first dimension (household income)
    assert operation.create.dimensions[0].household_income is not None
    assert len(operation.create.dimensions[0].household_income.income_ranges) == 2

    # Check second dimension (parental status)
    assert operation.create.dimensions[1].parental_status is not None
    assert len(operation.create.dimensions[1].parental_status.parental_statuses) == 2


@pytest.mark.asyncio
async def test_create_combined_audience_with_user_list(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a combined audience with user list dimension."""
    # Arrange
    customer_id = "1234567890"
    name = "Remarketing Audience"
    description = "Users from remarketing list"
    dimensions = [
        {
            "type": "USER_LIST",
            "user_list_resource": "customers/1234567890/userLists/444555666",
        }
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/audiences/111222333"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/audiences/111222333"}]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.create_combined_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.name == name
    assert len(operation.create.dimensions) == 1
    assert operation.create.dimensions[0].audience_segments is not None
    assert len(operation.create.dimensions[0].audience_segments.segments) == 1
    assert (
        operation.create.dimensions[0].audience_segments.segments[0].user_list.user_list
        == "customers/1234567890/userLists/444555666"
    )


@pytest.mark.asyncio
async def test_create_combined_audience_with_exclusions(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a combined audience with exclusion dimensions."""
    # Arrange
    customer_id = "1234567890"
    name = "Age group excluding converters"
    description = "Target age group excluding recent converters"
    dimensions = [
        {
            "type": "AGE",
            "age_ranges": ["AGE_RANGE_25_34", "AGE_RANGE_35_44", "AGE_RANGE_45_54"],
        }
    ]
    exclusion_dimensions = [
        {
            "type": "USER_LIST",
            "user_list_resource": "customers/1234567890/userLists/777888999",
        }
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/audiences/111222333"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": "customers/1234567890/audiences/111222333"}]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.create_combined_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
            exclusion_dimensions=exclusion_dimensions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    assert operation.create.name == name
    assert len(operation.create.dimensions) == 1
    assert operation.create.exclusion_dimension is not None

    # Check exclusion dimension
    assert operation.create.exclusion_dimension.exclusions is not None
    assert len(operation.create.exclusion_dimension.exclusions) == 1
    assert (
        operation.create.exclusion_dimension.exclusions[0].user_list.user_list
        == "customers/1234567890/userLists/777888999"
    )


@pytest.mark.asyncio
async def test_update_audience(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an audience."""
    # Arrange
    customer_id = "1234567890"
    audience_id = "111222333"
    name = "Updated Audience Name"
    description = "Updated description"
    status = "REMOVED"

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/audiences/{audience_id}"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/audiences/{audience_id}"}
        ]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.update_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_id=audience_id,
            name=name,
            description=description,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/audiences/{audience_id}"
    )
    assert operation.update.name == name
    assert operation.update.description == description
    assert operation.update.status == AudienceStatusEnum.AudienceStatus.REMOVED
    assert "name" in operation.update_mask.paths
    assert "description" in operation.update_mask.paths
    assert "status" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_list_audiences(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing audiences."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    audience_info = [
        {
            "id": "111222333",
            "name": "Audience 1",
            "description": "First audience",
            "status": AudienceStatusEnum.AudienceStatus.ENABLED,
        },
        {
            "id": "444555666",
            "name": "Audience 2",
            "description": "Second audience",
            "status": AudienceStatusEnum.AudienceStatus.REMOVED,
        },
    ]

    for info in audience_info:
        row = Mock()
        row.audience = Mock()
        row.audience.id = info["id"]
        row.audience.name = info["name"]
        row.audience.description = info["description"]
        row.audience.status = info["status"]
        row.audience.resource_name = f"customers/{customer_id}/audiences/{info['id']}"
        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return audience_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.audiences.audience_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await audience_service.list_audiences(
            ctx=mock_ctx,
            customer_id=customer_id,
        )

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == "111222333"
    assert result[0]["name"] == "Audience 1"
    assert result[1]["id"] == "444555666"
    assert result[1]["name"] == "Audience 2"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "FROM audience" in query


@pytest.mark.asyncio
async def test_remove_audience(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an audience."""
    # Arrange
    customer_id = "1234567890"
    audience_id = "111222333"

    # Create mock response
    mock_response = Mock(spec=MutateAudiencesResponse)
    mock_result = Mock()
    mock_result.resource_name = f"customers/{customer_id}/audiences/{audience_id}"
    mock_response.results = [mock_result]

    # Get the mocked audience service client
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/audiences/{audience_id}"}
        ]
    }

    with patch(
        "src.sdk_services.audiences.audience_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_service.remove_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_id=audience_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call (remove_audience uses update with REMOVED status)
    mock_audience_client.mutate_audiences.assert_called_once()  # type: ignore
    call_args = mock_audience_client.mutate_audiences.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/audiences/{audience_id}"
    )
    assert operation.update.status == AudienceStatusEnum.AudienceStatus.REMOVED


@pytest.mark.asyncio
async def test_error_handling_create_audience(
    audience_service: AudienceService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating audience fails."""
    # Arrange
    customer_id = "1234567890"
    name = "Test Audience"
    description = "Test description"
    dimensions = [{"type": "AGE", "age_ranges": ["AGE_RANGE_18_24"]}]

    # Get the mocked audience service client and make it raise exception
    mock_audience_client = audience_service.client  # type: ignore
    mock_audience_client.mutate_audiences.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await audience_service.create_combined_audience(
            ctx=mock_ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
        )

    assert "Failed to create combined audience" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create combined audience: Test Google Ads Exception",
    )


def test_register_audience_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_audience_tools(mock_mcp)

    # Assert
    assert isinstance(service, AudienceService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_combined_audience",
        "update_audience",
        "list_audiences",
        "remove_audience",
    ]

    assert set(tool_names) == set(expected_tools)
