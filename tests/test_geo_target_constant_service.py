"""Tests for GeoTargetConstantService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.geo_target_constant_service import (
    GeoTargetConstantServiceClient,
)
from google.ads.googleads.v20.services.types.geo_target_constant_service import (
    SuggestGeoTargetConstantsResponse,
)

from src.sdk_services.targeting.geo_target_constant_service import (
    GeoTargetConstantService,
    register_geo_target_constant_tools,
)


@pytest.fixture
def geo_target_constant_service(mock_sdk_client: Any) -> GeoTargetConstantService:
    """Create a GeoTargetConstantService instance with mocked dependencies."""
    # Mock GeoTargetConstantService client
    mock_geo_target_client = Mock(spec=GeoTargetConstantServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_geo_target_client

    with patch(
        "src.sdk_services.targeting.geo_target_constant_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = GeoTargetConstantService()
        # Force client initialization
        _ = service.client
        return service


def create_mock_geo_target_suggestion(
    resource_name: str,
    geo_id: str,
    name: str,
    country_code: str,
    target_type: str = "State",
    canonical_name: str = "",
    parent_geo_target: str = "",
    locale: str = "en",
    reach: int = 1000000,
    search_term: str = "",
) -> Mock:
    """Create a mock geo target constant suggestion."""
    suggestion = Mock()
    
    # Mock geo target constant
    geo_target = Mock()
    geo_target.resource_name = resource_name
    geo_target.id = geo_id
    geo_target.name = name
    geo_target.country_code = country_code
    geo_target.target_type = target_type
    geo_target.status = Mock()
    geo_target.status.name = "ENABLED"
    geo_target.canonical_name = canonical_name
    geo_target.parent_geo_target = parent_geo_target
    
    suggestion.geo_target_constant = geo_target
    suggestion.locale = locale
    suggestion.reach = reach
    suggestion.search_term = search_term
    
    return suggestion


@pytest.mark.asyncio
async def test_suggest_geo_targets_by_location(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting geo targets by location names."""
    # Arrange
    location_names = ["New York", "California"]
    locale = "en"
    country_code = "US"

    # Create mock response
    mock_response = Mock(spec=SuggestGeoTargetConstantsResponse)
    mock_response.geo_target_constant_suggestions = [
        create_mock_geo_target_suggestion(
            resource_name="geoTargetConstants/1023191",
            geo_id="1023191",
            name="New York",
            country_code="US",
            target_type="State",
            canonical_name="New York, United States",
            parent_geo_target="geoTargetConstants/2840",
            locale="en",
            reach=19500000,
            search_term="New York",
        ),
        create_mock_geo_target_suggestion(
            resource_name="geoTargetConstants/1014044",
            geo_id="1014044", 
            name="California",
            country_code="US",
            target_type="State",
            canonical_name="California, United States",
            parent_geo_target="geoTargetConstants/2840",
            locale="en",
            reach=39500000,
            search_term="California",
        ),
    ]

    # Get the mocked geo target constant service client
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.return_value = mock_response  # type: ignore

    # Act
    result = await geo_target_constant_service.suggest_geo_targets_by_location(
        ctx=mock_ctx,
        location_names=location_names,
        locale=locale,
        country_code=country_code,
    )

    # Assert
    assert len(result) == 2
    
    # Check first result (New York)
    ny_result = result[0]
    assert ny_result["resource_name"] == "geoTargetConstants/1023191"
    assert ny_result["id"] == "1023191"
    assert ny_result["name"] == "New York"
    assert ny_result["country_code"] == "US"
    assert ny_result["target_type"] == "State"
    assert ny_result["status"] == "ENABLED"
    assert ny_result["canonical_name"] == "New York, United States"
    assert ny_result["parent_geo_target"] == "geoTargetConstants/2840"
    assert ny_result["locale"] == "en"
    assert ny_result["reach"] == 19500000
    assert ny_result["search_term"] == "New York"

    # Check second result (California)
    ca_result = result[1]
    assert ca_result["resource_name"] == "geoTargetConstants/1014044"
    assert ca_result["id"] == "1014044"
    assert ca_result["name"] == "California"
    assert ca_result["reach"] == 39500000

    # Verify the API call
    mock_geo_target_client.suggest_geo_target_constants.assert_called_once()  # type: ignore
    call_args = mock_geo_target_client.suggest_geo_target_constants.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.locale == locale
    assert request.country_code == country_code
    assert list(request.location_names.names) == location_names

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found 2 geo target suggestions for {location_names}",
    )


@pytest.mark.asyncio
async def test_suggest_geo_targets_by_location_no_country_code(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting geo targets without country code filter."""
    # Arrange
    location_names = ["London"]
    locale = "en"

    # Create mock response
    mock_response = Mock(spec=SuggestGeoTargetConstantsResponse)
    mock_response.geo_target_constant_suggestions = [
        create_mock_geo_target_suggestion(
            resource_name="geoTargetConstants/1006886",
            geo_id="1006886",
            name="London",
            country_code="GB",
            target_type="City",
            canonical_name="London, United Kingdom",
            parent_geo_target="geoTargetConstants/2826",
            locale="en",
            reach=9000000,
            search_term="London",
        ),
    ]

    # Get the mocked geo target constant service client
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.return_value = mock_response  # type: ignore

    # Act
    result = await geo_target_constant_service.suggest_geo_targets_by_location(
        ctx=mock_ctx,
        location_names=location_names,
        locale=locale,
    )

    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "London"
    assert result[0]["country_code"] == "GB"

    # Verify the API call - should not have country_code set
    call_args = mock_geo_target_client.suggest_geo_target_constants.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.locale == locale
    assert not hasattr(request, 'country_code') or request.country_code == ""


@pytest.mark.asyncio
async def test_suggest_geo_targets_by_address(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting geo targets by address."""
    # Arrange
    address_text = "1600 Amphitheatre Parkway, Mountain View, CA"
    locale = "en"
    country_code = "US"

    # Create mock response
    mock_response = Mock(spec=SuggestGeoTargetConstantsResponse)
    mock_response.geo_target_constant_suggestions = [
        create_mock_geo_target_suggestion(
            resource_name="geoTargetConstants/1014221",
            geo_id="1014221",
            name="Mountain View",
            country_code="US",
            target_type="City",
            canonical_name="Mountain View, CA, United States",
            parent_geo_target="geoTargetConstants/1014044",
            locale="en",
            reach=82000,
            search_term=address_text,
        ),
    ]

    # Get the mocked geo target constant service client
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.return_value = mock_response  # type: ignore

    # Act
    result = await geo_target_constant_service.suggest_geo_targets_by_address(
        ctx=mock_ctx,
        address_text=address_text,
        locale=locale,
        country_code=country_code,
    )

    # Assert
    assert len(result) == 1
    mv_result = result[0]
    assert mv_result["resource_name"] == "geoTargetConstants/1014221"
    assert mv_result["id"] == "1014221"
    assert mv_result["name"] == "Mountain View"
    assert mv_result["country_code"] == "US"
    assert mv_result["target_type"] == "City"
    assert mv_result["canonical_name"] == "Mountain View, CA, United States"
    assert mv_result["reach"] == 82000

    # Verify the API call
    mock_geo_target_client.suggest_geo_target_constants.assert_called_once()  # type: ignore
    call_args = mock_geo_target_client.suggest_geo_target_constants.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.locale == locale
    assert request.country_code == country_code
    # Check that geo_targets was set (this will contain the address)
    assert hasattr(request, 'geo_targets')

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Found 1 geo target suggestions for address: {address_text}",
    )


@pytest.mark.asyncio
async def test_search_geo_targets(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching geo targets."""
    # Arrange
    query = "Texas"
    locale = "en"
    limit = 50

    # Create mock response
    mock_response = Mock(spec=SuggestGeoTargetConstantsResponse)
    mock_response.geo_target_constant_suggestions = [
        create_mock_geo_target_suggestion(
            resource_name="geoTargetConstants/1014221",
            geo_id="1014221",
            name="Texas",
            country_code="US",
            target_type="State",
            canonical_name="Texas, United States",
            parent_geo_target="geoTargetConstants/2840",
            locale="en",
            reach=29000000,
            search_term="Texas",
        ),
    ]

    # Get the mocked geo target constant service client
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.return_value = mock_response  # type: ignore

    # Act
    result = await geo_target_constant_service.search_geo_targets(
        ctx=mock_ctx,
        query=query,
        locale=locale,
        limit=limit,
    )

    # Assert
    assert len(result) == 1
    tx_result = result[0]
    assert tx_result["name"] == "Texas"
    assert tx_result["country_code"] == "US"
    assert tx_result["target_type"] == "State"
    assert tx_result["reach"] == 29000000

    # Verify logging was called twice (once for search info, once for suggest info)
    assert mock_ctx.log.call_count == 2  # type: ignore
    first_call = mock_ctx.log.call_args_list[0]  # type: ignore
    assert first_call[1]["message"] == f"Searching for geo targets matching: {query}"


@pytest.mark.asyncio
async def test_suggest_geo_targets_with_no_status(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting geo targets when status is None."""
    # Arrange
    location_names = ["Test Location"]

    # Create mock response with no status
    mock_response = Mock(spec=SuggestGeoTargetConstantsResponse)
    suggestion = Mock()
    geo_target = Mock()
    geo_target.resource_name = "geoTargetConstants/123"
    geo_target.id = "123"
    geo_target.name = "Test Location"
    geo_target.country_code = "US"
    geo_target.target_type = "City"
    geo_target.status = None  # No status
    geo_target.canonical_name = "Test Location, US"
    geo_target.parent_geo_target = "geoTargetConstants/2840"
    
    suggestion.geo_target_constant = geo_target
    suggestion.locale = "en"
    suggestion.reach = 50000
    suggestion.search_term = "Test Location"
    
    mock_response.geo_target_constant_suggestions = [suggestion]

    # Get the mocked geo target constant service client
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.return_value = mock_response  # type: ignore

    # Act
    result = await geo_target_constant_service.suggest_geo_targets_by_location(
        ctx=mock_ctx,
        location_names=location_names,
    )

    # Assert
    assert len(result) == 1
    assert result[0]["status"] == "UNKNOWN"  # Should default to UNKNOWN when status is None


@pytest.mark.asyncio
async def test_error_handling_location(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when suggesting by location fails."""
    # Arrange
    location_names = ["Invalid Location"]

    # Get the mocked geo target constant service client and make it raise exception
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await geo_target_constant_service.suggest_geo_targets_by_location(
            ctx=mock_ctx,
            location_names=location_names,
        )

    assert "Failed to suggest geo targets by location" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to suggest geo targets by location: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_address(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when suggesting by address fails."""
    # Arrange
    address_text = "Invalid Address"

    # Get the mocked geo target constant service client and make it raise exception
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await geo_target_constant_service.suggest_geo_targets_by_address(
            ctx=mock_ctx,
            address_text=address_text,
        )

    assert "Failed to suggest geo targets by address" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to suggest geo targets by address: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_search(
    geo_target_constant_service: GeoTargetConstantService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when search fails."""
    # Arrange
    query = "Invalid Query"

    # Get the mocked geo target constant service client and make it raise exception
    mock_geo_target_client = geo_target_constant_service.client  # type: ignore
    mock_geo_target_client.suggest_geo_target_constants.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await geo_target_constant_service.search_geo_targets(
            ctx=mock_ctx,
            query=query,
        )

    assert "Failed to search geo targets" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging - should be called twice (once for search, once for underlying suggest)
    assert mock_ctx.log.call_count >= 1  # type: ignore


def test_register_geo_target_constant_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_geo_target_constant_tools(mock_mcp)

    # Assert
    assert isinstance(service, GeoTargetConstantService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "suggest_geo_targets_by_location",
        "suggest_geo_targets_by_address", 
        "search_geo_targets",
    ]

    assert set(tool_names) == set(expected_tools)