"""Tests for AdGroupAdService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
from google.ads.googleads.v20.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_ad_service import (
    MutateAdGroupAdsResponse,
)

from src.services.ad_group.ad_group_ad_service import (
    AdGroupAdService,
    register_ad_group_ad_tools,
)


@pytest.fixture
def ad_group_ad_service(mock_sdk_client: Any) -> AdGroupAdService:
    """Create an AdGroupAdService instance with mocked dependencies."""
    # Mock AdGroupAdService client
    mock_ad_group_ad_client = Mock(spec=AdGroupAdServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_ad_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_ad_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupAdService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_ad_group_ad(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an ad group ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    ad_resource_name = f"customers/{customer_id}/ads/456"
    status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~456"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_group_ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~456"}
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_ad_service.create_ad_group_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_resource_name=ad_resource_name,
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
    assert (
        operation.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation.create.ad.resource_name == ad_resource_name
    assert operation.create.status == status


@pytest.mark.asyncio
async def test_update_ad_group_ad_status(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating ad group ad status."""
    # Arrange
    customer_id = "1234567890"
    ad_group_ad_resource_name = f"customers/{customer_id}/adGroupAds/123~456"
    new_status = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = ad_group_ad_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_group_ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": ad_group_ad_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_ad_service.update_ad_group_ad_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_ad_resource_name=ad_group_ad_resource_name,
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
    assert operation.update.resource_name == ad_group_ad_resource_name
    assert operation.update.status == new_status
    assert "status" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad group ad status to {new_status}",
    )


@pytest.mark.asyncio
async def test_list_ad_group_ads(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group ads."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    include_policy_data = True

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.ad_group_ad = Mock()
        row.ad_group_ad.resource_name = (
            f"customers/{customer_id}/adGroupAds/{ad_group_id}~{i + 100}"
        )
        row.ad_group_ad.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
        row.ad_group_ad.ad = Mock()
        row.ad_group_ad.ad.id = i + 100
        row.ad_group_ad.ad.name = f"Ad {i}"
        row.ad_group_ad.ad.type_ = Mock()
        row.ad_group_ad.ad.type_.name = "RESPONSIVE_SEARCH_AD"
        row.ad_group_ad.status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

        # Add policy data
        row.ad_group_ad.policy_summary = Mock()
        row.ad_group_ad.policy_summary.approval_status = Mock()
        row.ad_group_ad.policy_summary.approval_status.name = "APPROVED"
        row.ad_group_ad.policy_summary.review_status = Mock()
        row.ad_group_ad.policy_summary.review_status.name = "REVIEWED"

        row.ad_group = Mock()
        row.ad_group.id = ad_group_id
        row.ad_group.name = "Test Ad Group"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_ad_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Mock serialize_proto_message
    def serialize_side_effect(obj: Any):
        if hasattr(obj, "ad") and hasattr(obj, "status"):
            # AdGroupAd object (has both ad and status properties)
            return {
                "resource_name": obj.resource_name,
                "ad_group": obj.ad_group,
                "ad": {
                    "id": str(obj.ad.id),
                    "name": obj.ad.name,
                    "type": obj.ad.type_.name,
                },
                "status": obj.status.name,
                "policy_summary": {
                    "approval_status": obj.policy_summary.approval_status.name,
                    "review_status": obj.policy_summary.review_status.name,
                },
            }
        else:
            # AdGroup object
            return {
                "id": str(obj.id),
                "name": obj.name,
            }

    with (
        patch(
            "src.sdk_services.ad_group.ad_group_ad_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.sdk_services.ad_group.ad_group_ad_service.serialize_proto_message",
            side_effect=serialize_side_effect,
        ),
    ):
        # Act
        result = await ad_group_ad_service.list_ad_group_ads(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            include_policy_data=include_policy_data,
            limit=10,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["ad"]["id"] == "100"
    assert result[0]["ad"]["name"] == "Ad 0"
    assert result[0]["status"] == "ENABLED"
    assert result[0]["policy_summary"]["approval_status"] == "APPROVED"
    assert "ad_group_details" in result[0]  # Simplified check for now

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert f"AND ad_group.id = {ad_group_id}" in query
    assert "policy_summary.approval_status" in query
    assert "LIMIT 10" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 ad group ads",
    )


@pytest.mark.asyncio
async def test_list_ad_group_ads_no_filter(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing ad group ads without ad group filter."""
    # Arrange
    customer_id = "1234567890"

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)
    mock_google_ads_service.search.return_value = []  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return ad_group_ad_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_ad_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        # Act
        result = await ad_group_ad_service.list_ad_group_ads(
            ctx=mock_ctx,
            customer_id=customer_id,
            include_policy_data=False,
        )

    # Assert
    assert len(result) == 0

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    query = call_args[1]["query"]
    assert "AND ad_group.id =" not in query
    assert "policy_summary" not in query


@pytest.mark.asyncio
async def test_remove_ad_group_ad(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an ad group ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_ad_resource_name = f"customers/{customer_id}/adGroupAds/123~456"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = ad_group_ad_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_group_ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": ad_group_ad_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_ad_service.remove_ad_group_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_ad_resource_name=ad_group_ad_resource_name,
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
    assert operation.remove == ad_group_ad_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed ad group ad: {ad_group_ad_resource_name}",
    )


@pytest.mark.asyncio
async def test_error_handling(
    ad_group_ad_service: AdGroupAdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_group_ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_ad_service.create_ad_group_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_resource_name="customers/123/ads/456",
        )

    assert "Failed to create ad group ad" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create ad group ad: Test Google Ads Exception",
    )


def test_register_ad_group_ad_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_ad_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupAdService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 4  # 4 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_ad_group_ad",
        "update_ad_group_ad_status",
        "list_ad_group_ads",
        "remove_ad_group_ad",
    ]

    assert set(tool_names) == set(expected_tools)
