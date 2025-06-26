"""Tests for AdService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
from google.ads.googleads.v20.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_ad_service import (
    MutateAdGroupAdsResponse,
)

from src.sdk_services.ad_group.ad_service import (
    AdService,
    register_ad_tools,
)


@pytest.fixture
def ad_service(mock_sdk_client: Any) -> AdService:
    """Create an AdService instance with mocked dependencies."""
    # Mock AdGroupAdService client
    mock_ad_group_ad_client = Mock(spec=AdGroupAdServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_ad_client

    with patch(
        "src.sdk_services.ad_group.ad_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_responsive_search_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a responsive search ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headlines = [
        "Best Running Shoes",
        "Premium Athletic Footwear",
        "Top Quality Sports Shoes",
        "Comfortable Running Gear",
    ]
    descriptions = [
        "Discover our premium collection of running shoes with superior comfort.",
        "Get the best performance with our top-rated athletic footwear.",
    ]
    final_urls = ["https://example.com/running-shoes"]
    path1 = "shoes"
    path2 = "running"
    status = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~123"
    mock_response.results.append(result)

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~123"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.create
    assert ad_group_ad.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert ad_group_ad.status == status

    # Check ad details
    ad = ad_group_ad.ad
    assert ad.final_urls[0] == final_urls[0]

    # Check responsive search ad
    responsive_ad = ad.responsive_search_ad
    assert len(responsive_ad.headlines) == len(headlines)
    assert len(responsive_ad.descriptions) == len(descriptions)
    assert responsive_ad.headlines[0].text == headlines[0]
    assert responsive_ad.descriptions[0].text == descriptions[0]
    assert responsive_ad.path1 == path1
    assert responsive_ad.path2 == path2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created responsive search ad in ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_responsive_search_ad_minimal(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a responsive search ad with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headlines = ["Headline 1", "Headline 2", "Headline 3"]
    descriptions = ["Description 1", "Description 2"]
    final_urls = ["https://example.com"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~124"
    mock_response.results.append(result)

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~124"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    ad = operation.create.ad

    # Check that optional paths are not set
    responsive_ad = ad.responsive_search_ad
    assert not hasattr(responsive_ad, "path1") or responsive_ad.path1 == ""
    assert not hasattr(responsive_ad, "path2") or responsive_ad.path2 == ""


@pytest.mark.asyncio
async def test_create_expanded_text_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an expanded text ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headline1 = "Best Running Shoes"
    headline2 = "Premium Athletic Footwear"
    headline3 = "Top Quality Sports"
    description1 = "Discover our premium collection of running shoes with superior comfort and style."
    description2 = "Get the best performance with our top-rated athletic footwear designed for athletes."
    final_urls = ["https://example.com/running-shoes"]
    path1 = "shoes"
    path2 = "running"
    status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~125"
    mock_response.results.append(result)

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~125"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.create
    assert ad_group_ad.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert ad_group_ad.status == status

    # Check ad details
    ad = ad_group_ad.ad
    assert ad.final_urls[0] == final_urls[0]

    # Check expanded text ad
    expanded_ad = ad.expanded_text_ad
    assert expanded_ad.headline_part1 == headline1
    assert expanded_ad.headline_part2 == headline2
    assert expanded_ad.headline_part3 == headline3
    assert expanded_ad.description == description1
    assert expanded_ad.description2 == description2
    assert expanded_ad.path1 == path1
    assert expanded_ad.path2 == path2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created expanded text ad in ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_expanded_text_ad_minimal(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an expanded text ad with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headline1 = "Headline 1"
    headline2 = "Headline 2"
    headline3 = None
    description1 = "Description 1"
    description2 = None
    final_urls = ["https://example.com"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~126"
    mock_response.results.append(result)

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~126"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    expanded_ad = operation.create.ad.expanded_text_ad

    # Check that optional fields are handled correctly
    assert expanded_ad.headline_part1 == headline1
    assert expanded_ad.headline_part2 == headline2
    assert expanded_ad.description == description1
    # headline3 and description2 should not be set if None


@pytest.mark.asyncio
async def test_update_ad_status(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating ad status."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    ad_id = "456"
    new_status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
    mock_response.results.append(result)

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.update_ad_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.update
    assert (
        ad_group_ad.resource_name
        == f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
    )
    assert ad_group_ad.status == new_status
    assert "status" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad {ad_id} status to {new_status}",
    )


@pytest.mark.asyncio
async def test_error_handling_responsive_search_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating responsive search ad fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
        )

    assert "Failed to create responsive search ad" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create responsive search ad: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_expanded_text_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating expanded text ad fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1="H1",
            headline2="H2",
            headline3=None,
            description1="D1",
            description2=None,
            final_urls=["https://example.com"],
        )

    assert "Failed to create expanded text ad" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create expanded text ad: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_status(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating ad status fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    ad_id = "456"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.update_ad_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED,
        )

    assert "Failed to update ad status" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update ad status: Test Google Ads Exception",
    )


def test_register_ad_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_responsive_search_ad",
        "create_expanded_text_ad",
        "update_ad_status",
    ]

    assert set(tool_names) == set(expected_tools)
