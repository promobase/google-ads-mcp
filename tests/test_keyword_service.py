"""Tests for KeywordService."""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v20.enums.types.keyword_match_type import (
    KeywordMatchTypeEnum,
)
from google.ads.googleads.v20.services.services.ad_group_criterion_service import (
    AdGroupCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_service import (
    MutateAdGroupCriteriaResponse,
)

from src.sdk_services.ad_group.keyword_service import (
    KeywordService,
    register_keyword_tools,
)


@pytest.fixture
def keyword_service(mock_sdk_client: Any) -> KeywordService:
    """Create a KeywordService instance with mocked dependencies."""
    # Mock AdGroupCriterionService client
    mock_criterion_service_client = Mock(spec=AdGroupCriterionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_criterion_service_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.keyword_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = KeywordService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_add_keywords(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keywords to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords: List[Dict[str, Any]] = [
        {"text": "running shoes", "match_type": "EXACT"},
        {"text": "athletic footwear", "match_type": "PHRASE"},
        {"text": "sports shoes", "match_type": "BROAD", "cpc_bid_micros": 1500000},
    ]
    default_cpc_bid_micros = 1000000  # $1.00

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i in range(len(keywords)):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 1000}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked criterion service client
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 1000}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.sdk_services.ad_group.keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            default_cpc_bid_micros=default_cpc_bid_micros,
        )

    # Assert
    assert result == expected_result
    assert len(result["results"]) == 3

    # Verify the API call
    mock_criterion_service_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_criterion_service_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 3

    # Check first keyword (EXACT match)
    operation1 = request.operations[0]
    assert (
        operation1.create.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    )
    assert operation1.create.keyword.text == "running shoes"
    assert (
        operation1.create.keyword.match_type
        == KeywordMatchTypeEnum.KeywordMatchType.EXACT
    )
    assert (
        operation1.create.status
        == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    )
    assert operation1.create.cpc_bid_micros == default_cpc_bid_micros

    # Check second keyword (PHRASE match)
    operation2 = request.operations[1]
    assert operation2.create.keyword.text == "athletic footwear"
    assert (
        operation2.create.keyword.match_type
        == KeywordMatchTypeEnum.KeywordMatchType.PHRASE
    )
    assert operation2.create.cpc_bid_micros == default_cpc_bid_micros

    # Check third keyword (BROAD match with custom bid)
    operation3 = request.operations[2]
    assert operation3.create.keyword.text == "sports shoes"
    assert (
        operation3.create.keyword.match_type
        == KeywordMatchTypeEnum.KeywordMatchType.BROAD
    )
    assert operation3.create.cpc_bid_micros == 1500000  # Custom bid

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added 3 keywords to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_update_keyword_bid(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a keyword bid."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    criterion_id = "123456"
    new_cpc_bid_micros = 2000000  # $2.00

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = (
        f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
    )

    # Get the mocked criterion service client
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_service.update_keyword_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
            cpc_bid_micros=new_cpc_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_criterion_service_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_criterion_service_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.update.resource_name
        == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
    )
    assert operation.update.cpc_bid_micros == new_cpc_bid_micros
    assert "cpc_bid_micros" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated bid for keyword {criterion_id} to {new_cpc_bid_micros} micros",
    )


@pytest.mark.asyncio
async def test_remove_keyword(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a keyword from an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    criterion_id = "123"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = (
        f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
    )

    # Get the mocked criterion service client
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_service.remove_keyword(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_criterion_service_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_criterion_service_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert (
        operation.remove
        == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed keyword {criterion_id} from ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_keywords_without_bids(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keywords without any bids specified."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords: List[Dict[str, Any]] = [
        {"text": "running shoes", "match_type": "EXACT"},
        {"text": "athletic footwear", "match_type": "PHRASE"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i in range(len(keywords)):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 1000}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked criterion service client
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 1000}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.sdk_services.ad_group.keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
        )

    # Assert
    assert result == expected_result
    assert len(result["results"]) == 2

    # Verify the API call
    mock_criterion_service_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_criterion_service_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 2

    # Check that no bids were set
    for operation in request.operations:
        assert (
            not hasattr(operation.create, "cpc_bid_micros")
            or operation.create.cpc_bid_micros == 0
        )


@pytest.mark.asyncio
async def test_add_keywords_with_default_match_type(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keywords with default match type when not specified."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords: List[Dict[str, Any]] = [
        {"text": "running shoes"},  # No match_type specified
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_result = Mock()
    mock_result.resource_name = (
        f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~1000"
    )
    mock_response.results = [mock_result]

    # Get the mocked criterion service client
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~1000"
            }
        ]
    }

    with patch(
        "src.sdk_services.ad_group.keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await keyword_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_criterion_service_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_criterion_service_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]

    # Should default to BROAD match type
    assert (
        operation.create.keyword.match_type
        == KeywordMatchTypeEnum.KeywordMatchType.BROAD
    )


@pytest.mark.asyncio
async def test_error_handling(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked criterion service client and make it raise exception
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.side_effect = (  # pyright: ignore  # type: ignore
        google_ads_exception
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await keyword_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=[{"text": "test", "match_type": "EXACT"}],
        )

    assert "Failed to add keywords" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add keywords: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_update_keyword_bid_error_handling(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling for update keyword bid."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    criterion_id = "123456"

    # Get the mocked criterion service client and make it raise exception
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.side_effect = (  # pyright: ignore  # type: ignore
        google_ads_exception
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await keyword_service.update_keyword_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
            cpc_bid_micros=2000000,
        )

    assert "Failed to update keyword bid" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_keyword_error_handling(
    keyword_service: KeywordService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling for remove keyword."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    criterion_id = "123"

    # Get the mocked criterion service client and make it raise exception
    mock_criterion_service_client = keyword_service.client  # type: ignore
    mock_criterion_service_client.mutate_ad_group_criteria.side_effect = (  # pyright: ignore  # type: ignore
        google_ads_exception
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await keyword_service.remove_keyword(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
        )

    assert "Failed to remove keyword" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_keyword_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_keyword_tools(mock_mcp)

    # Assert
    assert isinstance(service, KeywordService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "add_keywords",
        "update_keyword_bid",
        "remove_keyword",
    ]

    assert set(tool_names) == set(expected_tools)
