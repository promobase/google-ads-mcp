"""Tests for GoogleAdsFieldService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.resources.types.google_ads_field import GoogleAdsField
from google.ads.googleads.v20.services.services.google_ads_field_service import (
    GoogleAdsFieldServiceClient,
)
from google.ads.googleads.v20.services.types.google_ads_field_service import (
    GetGoogleAdsFieldRequest,
    SearchGoogleAdsFieldsRequest,
)

from src.sdk_services.metadata.google_ads_field_service import (
    GoogleAdsFieldService,
    register_google_ads_field_tools,
)


@pytest.fixture
def mock_field_service_client() -> Mock:
    """Create a mock GoogleAdsFieldServiceClient."""
    client = Mock(spec=GoogleAdsFieldServiceClient)
    return client


@pytest.fixture
def google_ads_field_service(
    mock_sdk_client: Any, mock_field_service_client: Mock
) -> GoogleAdsFieldService:
    """Create a GoogleAdsFieldService instance with mocked dependencies."""
    mock_sdk_client.client.get_service.return_value = mock_field_service_client

    with patch(
        "src.sdk_services.metadata.google_ads_field_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = GoogleAdsFieldService()
        # Force client initialization
        _ = service.client
        return service


def create_mock_google_ads_field(
    name: str = "campaign.id",
    category: str = "RESOURCE",
    data_type: str = "INT64",
    is_repeated: bool = False,
    selectable: bool = True,
    filterable: bool = True,
    sortable: bool = True,
) -> Mock:
    """Create a mock GoogleAdsField object."""
    field = Mock(spec=GoogleAdsField)
    field.name = name
    field.resource_name = f"googleAdsFields/{name}"

    # Mock category enum
    field.category = Mock()
    field.category.name = category

    # Mock data type enum
    field.data_type = Mock()
    field.data_type.name = data_type

    field.is_repeated = is_repeated

    # Mock type URL
    field.type_url = f"type.googleapis.com/google.ads.googleads.v20.resources.{name}"

    # Mock selectable_with
    field.selectable_with = ["campaign", "metrics"]

    # Mock attribute resources
    field.attribute_resources = ["Campaign"]

    # Mock metrics
    field.metrics = []

    # Mock segments
    field.segments = []

    # Mock other properties
    field.filterable = filterable
    field.sortable = sortable
    field.selectable = selectable

    # Mock enum values (empty for non-enum fields)
    field.enum_values = []

    return field


@pytest.mark.asyncio
async def test_get_field_metadata(
    google_ads_field_service: GoogleAdsFieldService,
    mock_field_service_client: Mock,
    mock_ctx: Context,
) -> None:
    """Test getting metadata for a specific field."""
    # Arrange
    field_name = "campaign.id"
    mock_field = create_mock_google_ads_field(name=field_name)
    mock_field_service_client.get_google_ads_field.return_value = mock_field

    # Mock serialize_proto_message
    expected_result = {
        "name": field_name,
        "category": "RESOURCE",
        "data_type": "INT64",
        "is_repeated": False,
    }

    with patch(
        "src.sdk_services.metadata.google_ads_field_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await google_ads_field_service.get_field_metadata(
            ctx=mock_ctx,
            field_name=field_name,
        )

    # Assert
    assert result == expected_result

    # Verify the request was made correctly
    mock_field_service_client.get_google_ads_field.assert_called_once()
    call_args = mock_field_service_client.get_google_ads_field.call_args[1]
    assert isinstance(call_args["request"], GetGoogleAdsFieldRequest)
    assert call_args["request"].resource_name == f"googleAdsFields/{field_name}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Retrieved metadata for field: {field_name}",
    )


@pytest.mark.asyncio
async def test_search_fields(
    google_ads_field_service: GoogleAdsFieldService,
    mock_field_service_client: Mock,
    mock_ctx: Context,
) -> None:
    """Test searching for fields with a query."""
    # Arrange
    query = "selectable = true AND name LIKE 'campaign.%'"

    # Create mock fields
    mock_fields = [
        create_mock_google_ads_field(name="campaign.id"),
        create_mock_google_ads_field(name="campaign.name", data_type="STRING"),
        create_mock_google_ads_field(name="campaign.status", data_type="ENUM"),
    ]

    # Mock the search response
    mock_field_service_client.search_google_ads_fields.return_value = mock_fields

    # Mock serialize_proto_message for each field
    expected_results = [
        {"name": "campaign.id", "data_type": "INT64"},
        {"name": "campaign.name", "data_type": "STRING"},
        {"name": "campaign.status", "data_type": "ENUM"},
    ]

    with patch(
        "src.sdk_services.metadata.google_ads_field_service.serialize_proto_message",
        side_effect=expected_results,
    ):
        # Act
        results = await google_ads_field_service.search_fields(
            ctx=mock_ctx,
            query=query,
            limit=10,
        )

    # Assert
    assert len(results) == 3
    assert results == expected_results

    # Verify the request
    mock_field_service_client.search_google_ads_fields.assert_called_once()
    call_args = mock_field_service_client.search_google_ads_fields.call_args[1]
    assert isinstance(call_args["request"], SearchGoogleAdsFieldsRequest)
    # The service adds a LIMIT clause, so check that the query contains our original query
    assert query in call_args["request"].query
    assert "LIMIT" in call_args["request"].query
    # Note: page_size is not used when LIMIT is in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 fields matching criteria",
    )


@pytest.mark.asyncio
async def test_get_resource_fields(
    google_ads_field_service: GoogleAdsFieldService,
    mock_field_service_client: Mock,
    mock_ctx: Context,
) -> None:
    """Test getting comprehensive field information for a resource."""
    # Arrange
    resource_name = "campaign"

    # Create mock fields for different categories
    mock_resource_fields = [
        create_mock_google_ads_field(name="campaign.id"),
        create_mock_google_ads_field(name="campaign.name", data_type="STRING"),
    ]

    # Since get_resource_fields calls search_fields multiple times,
    # we need to mock the responses for each call
    mock_field_service_client.search_google_ads_fields.side_effect = [
        mock_resource_fields,  # First call for resource fields
        [],  # Second call for metrics (empty)
        [],  # Third call for segments (empty)
    ]

    with patch(
        "src.sdk_services.metadata.google_ads_field_service.serialize_proto_message",
        side_effect=[
            {"name": "campaign.id", "data_type": "INT64"},
            {"name": "campaign.name", "data_type": "STRING"},
        ],
    ):
        # Act
        results = await google_ads_field_service.get_resource_fields(
            ctx=mock_ctx,
            resource_name=resource_name,
            include_metrics=True,
            include_segments=True,
        )

    # Assert
    assert "attributes" in results
    assert len(results["attributes"]) == 2
    assert "metrics" in results
    assert len(results["metrics"]) == 0
    assert "segments" in results
    assert len(results["segments"]) == 0

    # Verify logging
    assert mock_ctx.log.call_count >= 1  # type: ignore


@pytest.mark.asyncio
async def test_validate_query_fields(
    google_ads_field_service: GoogleAdsFieldService,
    mock_field_service_client: Mock,
    mock_ctx: Context,
) -> None:
    """Test validating fields used in a query."""
    # Arrange
    resource_name = "campaign"
    field_names = ["campaign.id", "campaign.name", "campaign.status"]

    # Create mock fields
    mock_fields = []
    for field_name in field_names:
        mock_field = create_mock_google_ads_field(name=field_name)
        mock_fields.append(mock_field)

    # Mock the get calls
    mock_field_service_client.get_google_ads_field.side_effect = mock_fields

    with patch(
        "src.sdk_services.metadata.google_ads_field_service.serialize_proto_message",
        side_effect=[{"field": f} for f in field_names],
    ):
        # Act
        results = await google_ads_field_service.validate_query_fields(
            ctx=mock_ctx,
            resource_name=resource_name,
            field_names=field_names,
        )

    # Assert - validate_query_fields returns 'all_compatible' not 'all_valid'
    assert "all_compatible" in results
    assert "fields" in results
    assert len(results["fields"]) == 3
    # Check that all fields were validated
    for field_name in field_names:
        assert field_name in results["fields"]
        assert results["fields"][field_name]["valid"] is True

    # Verify logging
    assert mock_ctx.log.call_count >= 1  # type: ignore


@pytest.mark.asyncio
async def test_error_handling(
    google_ads_field_service: GoogleAdsFieldService,
    mock_field_service_client: Mock,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    field_name = "invalid.field"
    mock_field_service_client.get_google_ads_field.side_effect = google_ads_exception

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await google_ads_field_service.get_field_metadata(
            ctx=mock_ctx,
            field_name=field_name,
        )

    # The service wraps the exception in a generic Exception
    assert "Failed to get field metadata" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to get field metadata: Test Google Ads Exception",
    )


def test_register_google_ads_field_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_google_ads_field_tools(mock_mcp)

    # Assert
    assert isinstance(service, GoogleAdsFieldService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "get_field_metadata",
        "search_fields",
        "get_resource_fields",
        "validate_query_fields",
    ]

    assert set(tool_names) == set(expected_tools)
