"""Tests for AdGroupCriterionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v20.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v20.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v20.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.enums.types.parental_status_type import (
    ParentalStatusTypeEnum,
)
from google.ads.googleads.v20.services.services.ad_group_criterion_service import (
    AdGroupCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_service import (
    MutateAdGroupCriteriaResponse,
)

from src.sdk_services.ad_group.ad_group_criterion_service import (
    AdGroupCriterionService,
    register_ad_group_criterion_tools,
)


@pytest.fixture
def ad_group_criterion_service(mock_sdk_client: Any) -> AdGroupCriterionService:
    """Create an AdGroupCriterionService instance with mocked dependencies."""
    # Mock AdGroupCriterionService client
    mock_ad_group_criterion_client = Mock(spec=AdGroupCriterionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_criterion_client  # type: ignore

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupCriterionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_add_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keyword criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords = [
        {"text": "running shoes", "match_type": "EXACT", "cpc_bid_micros": 1000000},
        {"text": "athletic footwear", "match_type": "PHRASE", "cpc_bid_micros": 800000},
        {"text": "sports shoes", "match_type": "BROAD"},
    ]
    negative = False

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(keywords):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 100}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 100}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(keywords)

    # Check first operation (with bid)
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert criterion.status == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    assert criterion.negative == negative
    assert criterion.cpc_bid_micros == 1000000
    assert criterion.keyword.text == "running shoes"
    assert criterion.keyword.match_type == KeywordMatchTypeEnum.KeywordMatchType.EXACT

    # Check third operation (without bid)
    operation = request.operations[2]
    criterion = operation.create
    assert criterion.keyword.text == "sports shoes"
    assert criterion.keyword.match_type == KeywordMatchTypeEnum.KeywordMatchType.BROAD
    assert not hasattr(criterion, "cpc_bid_micros") or criterion.cpc_bid_micros == 0

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(keywords)} keywords to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_negative_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative keyword criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords = [
        {"text": "free", "match_type": "BROAD"},
        {"text": "cheap", "match_type": "PHRASE"},
    ]
    negative = True

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(keywords):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 200}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 200}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.negative == negative
    # Negative keywords should not have bid
    assert not hasattr(criterion, "cpc_bid_micros") or criterion.cpc_bid_micros == 0


@pytest.mark.asyncio
async def test_add_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding audience (user list) criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    user_list_ids = ["123456", "789012"]
    bid_modifier = 1.2

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(user_list_ids):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 300}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_audience_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        user_list_ids=user_list_ids,
        bid_modifier=bid_modifier,
    )

    # Assert
    assert len(result) == len(user_list_ids)

    # Check first result
    first_result = result[0]
    assert (
        first_result["resource_name"]
        == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~300"
    )
    assert first_result["criterion_id"] == f"{ad_group_id}~300"
    assert first_result["type"] == "AUDIENCE"
    assert first_result["user_list_id"] == user_list_ids[0]
    assert first_result["bid_modifier"] == bid_modifier

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(user_list_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert criterion.status == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert (
        criterion.user_list.user_list
        == f"customers/{customer_id}/userLists/{user_list_ids[0]}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(user_list_ids)} audience criteria to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_audience_criteria_no_bid_modifier(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding audience criteria without bid modifier."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    user_list_ids = ["123456"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~301"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_audience_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        user_list_ids=user_list_ids,
    )

    # Assert
    assert len(result) == 1
    assert result[0]["bid_modifier"] is None

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    # No bid modifier should be set
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_demographic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding demographic criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    demographics = [
        {"type": "AGE_RANGE", "value": "AGE_RANGE_25_34", "bid_modifier": 1.1},
        {"type": "GENDER", "value": "MALE", "bid_modifier": 0.9},
        {"type": "PARENTAL_STATUS", "value": "PARENT"},
        {"type": "INCOME_RANGE", "value": "INCOME_RANGE_50_60"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(demographics):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 400}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 400}",
                "type": demo["type"],
                "value": demo["value"],
                "bid_modifier": demo.get("bid_modifier"),
            }
            for i, demo in enumerate(demographics)
        ]
    }

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=demographics,
        )

    # Assert
    assert len(result["results"]) == len(demographics)

    # Check results
    for i, demo in enumerate(demographics):
        criterion_result = result["results"][i]
        assert (
            criterion_result["resource_name"]
            == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 400}"
        )
        assert criterion_result["type"] == demo["type"]
        assert criterion_result["value"] == demo["value"]
        assert criterion_result["bid_modifier"] == demo.get("bid_modifier")

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(demographics)

    # Check operations
    age_operation = request.operations[0]
    age_criterion = age_operation.create
    assert age_criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert (
        age_criterion.status
        == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    )
    assert abs(age_criterion.bid_modifier - 1.1) < 0.001
    assert (
        age_criterion.age_range.type_ == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34
    )

    gender_operation = request.operations[1]
    gender_criterion = gender_operation.create
    assert abs(gender_criterion.bid_modifier - 0.9) < 0.001
    assert gender_criterion.gender.type_ == GenderTypeEnum.GenderType.MALE

    parental_operation = request.operations[2]
    parental_criterion = parental_operation.create
    assert (
        not hasattr(parental_criterion, "bid_modifier")
        or parental_criterion.bid_modifier == 0
    )
    assert (
        parental_criterion.parental_status.type_
        == ParentalStatusTypeEnum.ParentalStatusType.PARENT
    )

    income_operation = request.operations[3]
    income_criterion = income_operation.create
    assert (
        income_criterion.income_range.type_
        == IncomeRangeTypeEnum.IncomeRangeType.INCOME_RANGE_50_60
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(demographics)} demographic criteria to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_demographic_criteria_unknown_type(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding demographic criteria with unknown type (should be skipped)."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    demographics = [
        {"type": "UNKNOWN_TYPE", "value": "UNKNOWN_VALUE"},
        {"type": "AGE_RANGE", "value": "AGE_RANGE_25_34"},
    ]

    # Create mock response - only one result since unknown type is skipped
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~401"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_demographic_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        demographics=demographics,
    )

    # Assert - only 1 result since unknown type was skipped
    assert len(result) == 1

    # Verify the API call - only 1 operation since unknown type was skipped
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 1
    assert (
        request.operations[0].create.age_range.type_
        == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34
    )


@pytest.mark.asyncio
async def test_update_criterion_bid(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating criterion bid."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"
    cpc_bid_micros = 1500000
    bid_modifier = 1.3

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    criterion = operation.update
    assert criterion.resource_name == criterion_resource_name
    assert criterion.cpc_bid_micros == cpc_bid_micros
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert "cpc_bid_micros" in operation.update_mask.paths
    assert "bid_modifier" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated criterion bid: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_update_criterion_bid_partial(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating criterion bid with only one field."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"
    cpc_bid_micros = 2000000

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.update
    assert criterion.cpc_bid_micros == cpc_bid_micros
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0
    assert "cpc_bid_micros" in operation.update_mask.paths
    assert "bid_modifier" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_remove_ad_group_criterion(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an ad group criterion."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.sdk_services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.remove_ad_group_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == criterion_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed ad group criterion: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_error_handling_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding keywords fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=[{"text": "test", "match_type": "BROAD"}],
        )

    assert "Failed to add keywords" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add keywords: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding audience criteria fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_list_ids=["123"],
        )

    assert "Failed to add audience criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add audience criteria: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_demographic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding demographic criteria fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=[{"type": "AGE_RANGE", "value": "AGE_RANGE_25_34"}],
        )

    assert "Failed to add demographic criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add demographic criteria: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_criterion_bid(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating criterion bid fails."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=1000000,
        )

    assert "Failed to update criterion bid" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update criterion bid: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_remove_criterion(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing criterion fails."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.remove_ad_group_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    assert "Failed to remove ad group criterion" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to remove ad group criterion: Test Google Ads Exception",
    )


def test_register_ad_group_criterion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_criterion_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupCriterionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 5  # 5 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "add_keywords",
        "add_audience_criteria",
        "add_demographic_criteria",
        "update_criterion_bid",
        "remove_ad_group_criterion",
    ]

    assert set(tool_names) == set(expected_tools)
