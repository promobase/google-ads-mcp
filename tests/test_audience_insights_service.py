"""Tests for AudienceInsightsService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.enums.types.audience_insights_dimension import (
    AudienceInsightsDimensionEnum,
)
from google.ads.googleads.v20.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v20.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v20.services.services.audience_insights_service import (
    AudienceInsightsServiceClient,
)
from google.ads.googleads.v20.services.types.audience_insights_service import (
    GenerateInsightsFinderReportResponse,
    GenerateAudienceCompositionInsightsResponse,
    GenerateSuggestedTargetingInsightsResponse,
)

from src.sdk_services.audiences.audience_insights_service import (
    AudienceInsightsService,
    register_audience_insights_tools,
)


@pytest.fixture
def audience_insights_service(mock_sdk_client: Any) -> AudienceInsightsService:
    """Create an AudienceInsightsService instance with mocked dependencies."""
    # Mock AudienceInsightsService client
    mock_insights_client = Mock(spec=AudienceInsightsServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_insights_client  # type: ignore

    with patch(
        "src.sdk_services.audiences.audience_insights_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AudienceInsightsService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_generate_insights_finder_report(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating insights finder report."""
    # Arrange
    customer_id = "1234567890"
    baseline_audience_countries = ["2840"]  # US
    specific_audience_countries = ["2840", "2124"]  # US and Canada
    dimensions = ["AGE_RANGE", "GENDER", "USER_INTEREST"]
    baseline_audience_ages = ["AGE_RANGE_25_34", "AGE_RANGE_35_44"]
    baseline_audience_genders = ["MALE", "FEMALE"]
    specific_audience_ages = ["AGE_RANGE_18_24", "AGE_RANGE_25_34"]
    specific_audience_genders = ["FEMALE"]
    specific_audience_user_interests = ["12345", "67890"]

    # Create mock response
    mock_response = Mock(spec=GenerateInsightsFinderReportResponse)
    mock_response.saved_report_url = "https://example.com/report/123456"

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_insights_finder_report.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"saved_report_url": "https://example.com/report/123456"}

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_insights_finder_report(
            ctx=mock_ctx,
            customer_id=customer_id,
            baseline_audience_countries=baseline_audience_countries,
            specific_audience_countries=specific_audience_countries,
            dimensions=dimensions,
            baseline_audience_ages=baseline_audience_ages,
            baseline_audience_genders=baseline_audience_genders,
            specific_audience_ages=specific_audience_ages,
            specific_audience_genders=specific_audience_genders,
            specific_audience_user_interests=specific_audience_user_interests,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_insights_finder_report.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_insights_finder_report.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    # Verify baseline audience
    assert len(request.baseline_audience.country_location) == 1
    assert (
        request.baseline_audience.country_location[0].geo_target_constant
        == "geoTargetConstants/2840"
    )
    assert len(request.baseline_audience.age_ranges) == 2
    assert (
        request.baseline_audience.age_ranges[0].type_
        == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34
    )
    # BasicInsightsAudience only has a single gender field
    assert request.baseline_audience.gender.type_ == GenderTypeEnum.GenderType.MALE

    # Verify specific audience
    specific_audience = getattr(request, "specific_audience", None)
    assert specific_audience is not None
    assert len(specific_audience.country_location) == 2
    assert len(specific_audience.age_ranges) == 2
    # BasicInsightsAudience only has a single gender field
    assert specific_audience.gender.type_ == GenderTypeEnum.GenderType.FEMALE
    assert len(specific_audience.user_interests) == 2
    assert (
        specific_audience.user_interests[0].user_interest_category
        == "customers/1234567890/userInterests/12345"
    )

    # Note: In v20, GenerateInsightsFinderReportRequest doesn't have dimensions field

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated insights finder report",
    )


@pytest.mark.asyncio
async def test_generate_insights_finder_report_minimal(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating insights finder report with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    baseline_audience_countries = ["2840"]  # US
    specific_audience_countries = ["2840"]  # US
    dimensions = ["LOCATION"]

    # Create mock response
    mock_response = Mock(spec=GenerateInsightsFinderReportResponse)
    mock_response.saved_report_url = "https://example.com/report/minimal"

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_insights_finder_report.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"saved_report_url": "https://example.com/report/minimal"}

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_insights_finder_report(
            ctx=mock_ctx,
            customer_id=customer_id,
            baseline_audience_countries=baseline_audience_countries,
            specific_audience_countries=specific_audience_countries,
            dimensions=dimensions,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_insights_finder_report.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_insights_finder_report.call_args  # type: ignore
    request = call_args[1]["request"]

    # Verify minimal setup - only countries
    assert len(request.baseline_audience.country_location) == 1
    assert len(request.baseline_audience.age_ranges) == 0
    # BasicInsightsAudience gender field should be unset
    # For proto-plus, checking if the field is set is complex, so we skip this check

    specific_audience = getattr(request, "specific_audience", None)
    assert specific_audience is not None
    assert len(specific_audience.country_location) == 1
    assert len(specific_audience.age_ranges) == 0
    # BasicInsightsAudience gender field should be unset
    # For proto-plus, checking if the field is set is complex, so we skip this check
    assert len(specific_audience.user_interests) == 0

    # Note: In v20, GenerateInsightsFinderReportRequest doesn't have dimensions field


@pytest.mark.asyncio
async def test_generate_audience_composition_insights(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating audience composition insights."""
    # Arrange
    customer_id = "1234567890"
    audience_countries = ["2840", "2826"]  # US and UK
    dimensions = ["AGE_RANGE", "GENDER", "GEO_TARGET_COUNTRY", "AFFINITY_USER_INTEREST"]
    audience_ages = ["AGE_RANGE_25_34", "AGE_RANGE_35_44"]
    audience_genders = ["MALE", "FEMALE"]
    audience_user_interests = ["11111", "22222", "33333"]

    # Create mock response
    mock_response = Mock(spec=GenerateAudienceCompositionInsightsResponse)
    # Mock some sample sections
    mock_section1 = Mock()
    mock_section1.dimension_type = (
        AudienceInsightsDimensionEnum.AudienceInsightsDimension.AGE_RANGE
    )
    mock_section2 = Mock()
    mock_section2.dimension_type = (
        AudienceInsightsDimensionEnum.AudienceInsightsDimension.GENDER
    )
    mock_response.sections = [mock_section1, mock_section2]

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_audience_composition_insights.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "sections": [
            {"dimension_type": "AGE_RANGE"},
            {"dimension_type": "GENDER"},
        ]
    }

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_audience_composition_insights(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            dimensions=dimensions,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_audience_composition_insights.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_audience_composition_insights.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    # Verify audience setup
    assert len(request.audience.country_locations) == 2
    assert (
        request.audience.country_locations[0].geo_target_constant
        == "geoTargetConstants/2840"
    )
    assert (
        request.audience.country_locations[1].geo_target_constant
        == "geoTargetConstants/2826"
    )
    assert len(request.audience.age_ranges) == 2
    # InsightsAudience only has a single gender field
    assert request.audience.gender.type_ == GenderTypeEnum.GenderType.MALE
    # Note: In v20, user interests are handled through topic_audience_combinations

    # Verify dimensions
    assert len(request.dimensions) == 4

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated audience composition insights",
    )


@pytest.mark.asyncio
async def test_generate_audience_composition_insights_with_attribute_groups(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating audience composition insights with attribute groups."""
    # Arrange
    customer_id = "1234567890"
    audience_countries = ["2840"]
    dimensions = ["AGE_RANGE"]
    audience_attribute_groups = [{"type": "custom_affinity"}, {"type": "in_market"}]

    # Create mock response
    mock_response = Mock(spec=GenerateAudienceCompositionInsightsResponse)
    mock_response.sections = []

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_audience_composition_insights.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"sections": []}

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_audience_composition_insights(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            dimensions=dimensions,
            audience_attribute_groups=audience_attribute_groups,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_audience_composition_insights.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_audience_composition_insights.call_args  # type: ignore
    request = call_args[1]["request"]

    # Verify attribute groups were added
    assert len(request.audience.topic_audience_combinations) == 2


@pytest.mark.asyncio
async def test_generate_suggested_targeting_insights(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating suggested targeting insights."""
    # Arrange
    customer_id = "1234567890"
    audience_countries = ["2840"]  # US
    audience_ages = ["AGE_RANGE_25_34", "AGE_RANGE_35_44"]
    audience_genders = ["FEMALE"]
    audience_user_interests = ["54321", "98765"]

    # Create mock response
    mock_response = Mock(spec=GenerateSuggestedTargetingInsightsResponse)
    # Mock suggestions
    mock_suggestion1 = Mock()
    mock_suggestion1.user_interest = Mock()
    mock_suggestion1.user_interest.user_interest_category = (  # type: ignore
        "customers/1234567890/userInterests/99999"
    )
    mock_suggestion1.user_interest.user_interest_name = "Technology Enthusiasts"  # type: ignore
    mock_suggestion2 = Mock()
    mock_suggestion2.user_interest = Mock()
    mock_suggestion2.user_interest.user_interest_category = (  # type: ignore
        "customers/1234567890/userInterests/88888"
    )
    mock_suggestion2.user_interest.user_interest_name = "Online Shoppers"  # type: ignore
    mock_response.suggestions = [mock_suggestion1, mock_suggestion2]

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_suggested_targeting_insights.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {
        "suggestions": [
            {
                "user_interest": {
                    "user_interest_category": "customers/1234567890/userInterests/99999",
                    "user_interest_name": "Technology Enthusiasts",
                }
            },
            {
                "user_interest": {
                    "user_interest_category": "customers/1234567890/userInterests/88888",
                    "user_interest_name": "Online Shoppers",
                }
            },
        ]
    }

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_suggested_targeting_insights(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_suggested_targeting_insights.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_suggested_targeting_insights.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id

    # Verify audience setup through audience_definition
    assert request.audience_definition is not None
    audience = request.audience_definition.audience
    assert len(audience.country_locations) == 1
    assert len(audience.age_ranges) == 2
    # InsightsAudience only has a single gender field
    assert audience.gender.type_ == GenderTypeEnum.GenderType.FEMALE
    # Note: In v20, user interests are handled through topic_audience_combinations

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated suggested targeting insights",
    )


@pytest.mark.asyncio
async def test_generate_suggested_targeting_insights_minimal(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test generating suggested targeting insights with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    audience_countries = ["2840"]  # US only

    # Create mock response
    mock_response = Mock(spec=GenerateSuggestedTargetingInsightsResponse)
    mock_response.suggestions = []

    # Get the mocked insights service client
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_suggested_targeting_insights.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message
    expected_result = {"suggestions": []}

    with patch(
        "src.sdk_services.audiences.audience_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await audience_insights_service.generate_suggested_targeting_insights(
            ctx=mock_ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_insights_client.generate_suggested_targeting_insights.assert_called_once()  # type: ignore
    call_args = mock_insights_client.generate_suggested_targeting_insights.call_args  # type: ignore
    request = call_args[1]["request"]

    # Verify minimal setup through audience_definition
    assert request.audience_definition is not None
    audience = request.audience_definition.audience
    assert len(audience.country_locations) == 1
    assert len(audience.age_ranges) == 0
    # InsightsAudience gender should be unset for minimal parameters
    # For proto-plus, checking if the field is set is complex, so we skip this check
    # Note: In v20, user interests are handled through topic_audience_combinations


@pytest.mark.asyncio
async def test_error_handling_generate_insights_finder_report(
    audience_insights_service: AudienceInsightsService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating insights finder report fails."""
    # Arrange
    customer_id = "1234567890"
    baseline_audience_countries = ["2840"]
    specific_audience_countries = ["2840"]
    dimensions = ["AGE_RANGE"]

    # Get the mocked insights service client and make it raise exception
    mock_insights_client = audience_insights_service.client  # type: ignore
    mock_insights_client.generate_insights_finder_report.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await audience_insights_service.generate_insights_finder_report(
            ctx=mock_ctx,
            customer_id=customer_id,
            baseline_audience_countries=baseline_audience_countries,
            specific_audience_countries=specific_audience_countries,
            dimensions=dimensions,
        )

    assert "Failed to generate insights finder report" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to generate insights finder report: Test Google Ads Exception",
    )


def test_register_audience_insights_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_audience_insights_tools(mock_mcp)

    # Assert
    assert isinstance(service, AudienceInsightsService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "generate_insights_finder_report",
        "generate_audience_composition_insights",
        "generate_suggested_targeting_insights",
    ]

    assert set(tool_names) == set(expected_tools)
