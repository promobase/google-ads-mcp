"""Audience insights service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.audience_insights_service import (
    AudienceInsightsServiceClient,
)
from google.ads.googleads.v20.services.types.audience_insights_service import (
    GenerateInsightsFinderReportRequest,
    GenerateInsightsFinderReportResponse,
    GenerateAudienceCompositionInsightsRequest,
    GenerateAudienceCompositionInsightsResponse,
    GenerateSuggestedTargetingInsightsRequest,
    GenerateSuggestedTargetingInsightsResponse,
    BasicInsightsAudience,
    InsightsAudience,
    InsightsAudienceAttributeGroup,
    InsightsAudienceDefinition,
)
from google.ads.googleads.v20.common.types.criteria import (
    AgeRangeInfo,
    GenderInfo,
    LocationInfo,
    UserInterestInfo,
)
from google.ads.googleads.v20.enums.types.audience_insights_dimension import (
    AudienceInsightsDimensionEnum,
)
from google.ads.googleads.v20.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v20.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AudienceInsightsService:
    """Audience insights service for analyzing audience data and getting recommendations."""

    def __init__(self) -> None:
        """Initialize the audience insights service."""
        self._client: Optional[AudienceInsightsServiceClient] = None

    @property
    def client(self) -> AudienceInsightsServiceClient:
        """Get the audience insights service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AudienceInsightsService")
        assert self._client is not None
        return self._client

    async def generate_insights_finder_report(
        self,
        ctx: Context,
        customer_id: str,
        baseline_audience_countries: List[str],
        specific_audience_countries: List[str],
        dimensions: List[str],
        baseline_audience_ages: Optional[List[str]] = None,
        baseline_audience_genders: Optional[List[str]] = None,
        specific_audience_ages: Optional[List[str]] = None,
        specific_audience_genders: Optional[List[str]] = None,
        specific_audience_user_interests: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate insights finder report comparing two audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            baseline_audience_countries: List of country location IDs for baseline audience
            specific_audience_countries: List of country location IDs for specific audience
            dimensions: List of dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, etc.)
            baseline_audience_ages: Optional age ranges for baseline (AGE_RANGE_18_24, etc.)
            baseline_audience_genders: Optional genders for baseline (MALE, FEMALE, UNDETERMINED)
            specific_audience_ages: Optional age ranges for specific audience
            specific_audience_genders: Optional genders for specific audience
            specific_audience_user_interests: Optional user interest IDs for specific audience

        Returns:
            Insights report with audience comparisons
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create baseline audience
            baseline_audience = BasicInsightsAudience()

            # Add countries
            for country_id in baseline_audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                baseline_audience.country_location.append(location)

            # Add age ranges if provided
            if baseline_audience_ages:
                for age_range in baseline_audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    baseline_audience.age_ranges.append(age_info)

            # Add gender if provided (BasicInsightsAudience only supports one gender)
            if baseline_audience_genders and len(baseline_audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, baseline_audience_genders[0]
                )
                baseline_audience.gender = gender_info

            # Create specific audience (also BasicInsightsAudience)
            specific_audience = BasicInsightsAudience()

            # Add countries
            for country_id in specific_audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                specific_audience.country_location.append(location)

            # Add age ranges if provided
            if specific_audience_ages:
                for age_range in specific_audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    specific_audience.age_ranges.append(age_info)

            # Add gender if provided (BasicInsightsAudience only supports one gender)
            if specific_audience_genders and len(specific_audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, specific_audience_genders[0]
                )
                specific_audience.gender = gender_info

            # Add user interests if provided
            if specific_audience_user_interests:
                for interest_id in specific_audience_user_interests:
                    interest_info = UserInterestInfo()
                    interest_info.user_interest_category = (
                        f"customers/{customer_id}/userInterests/{interest_id}"
                    )
                    specific_audience.user_interests.append(interest_info)

            # Create request
            request = GenerateInsightsFinderReportRequest()
            request.customer_id = customer_id
            request.baseline_audience = baseline_audience
            request.specific_audience = specific_audience

            # Note: In v20, GenerateInsightsFinderReportRequest doesn't have dimensions field
            # The dimensions parameter is kept for API compatibility but not used

            # Make the API call
            response: GenerateInsightsFinderReportResponse = (
                self.client.generate_insights_finder_report(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated insights finder report",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate insights finder report: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_audience_composition_insights(
        self,
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        dimensions: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        audience_attribute_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate audience composition insights for a specific audience.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_countries: List of country location IDs
            dimensions: List of dimensions to analyze
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            audience_attribute_groups: Optional custom attribute groups

        Returns:
            Audience composition insights
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create audience
            audience = InsightsAudience()

            # Add countries
            for country_id in audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                audience.country_locations.append(location)

            # Add demographics and interests
            if audience_ages:
                for age_range in audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    audience.age_ranges.append(age_info)

            if audience_genders and len(audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, audience_genders[0]
                )
                audience.gender = gender_info

            # Note: In v20, user interests should be provided through topic_audience_combinations
            # For simplicity, we skip user interests handling in this implementation

            # Add attribute groups if provided
            if audience_attribute_groups:
                for _ in (
                    audience_attribute_groups
                ):  # group_data will be used when fully implemented
                    attr_group = InsightsAudienceAttributeGroup()
                    # Process attributes based on group_data structure
                    # This is a simplified implementation
                    audience.topic_audience_combinations.append(attr_group)

            # Create request
            request = GenerateAudienceCompositionInsightsRequest()
            request.customer_id = customer_id
            request.audience = audience

            # Add dimensions
            for dimension in dimensions:
                request.dimensions.append(
                    getattr(
                        AudienceInsightsDimensionEnum.AudienceInsightsDimension,
                        dimension,
                    )
                )

            # Make the API call
            response: GenerateAudienceCompositionInsightsResponse = (
                self.client.generate_audience_composition_insights(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated audience composition insights",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate audience composition insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_suggested_targeting_insights(
        self,
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate suggested targeting insights for reaching similar audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_countries: List of country location IDs
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs

        Returns:
            Suggested targeting insights
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create audience
            audience = InsightsAudience()

            # Add countries
            for country_id in audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                audience.country_locations.append(location)

            # Add demographics and interests
            if audience_ages:
                for age_range in audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    audience.age_ranges.append(age_info)

            if audience_genders and len(audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, audience_genders[0]
                )
                audience.gender = gender_info

            # Note: In v20, user interests should be provided through topic_audience_combinations
            # For simplicity, we skip user interests handling in this implementation

            # Create audience definition
            audience_definition = InsightsAudienceDefinition()
            audience_definition.audience = audience

            # Create request
            request = GenerateSuggestedTargetingInsightsRequest()
            request.customer_id = customer_id
            request.audience_definition = audience_definition

            # Make the API call
            response: GenerateSuggestedTargetingInsightsResponse = (
                self.client.generate_suggested_targeting_insights(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated suggested targeting insights",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate suggested targeting insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_audience_insights_tools(
    service: AudienceInsightsService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the audience insights service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def generate_insights_finder_report(
        ctx: Context,
        customer_id: str,
        baseline_audience_countries: List[str],
        specific_audience_countries: List[str],
        dimensions: List[str],
        baseline_audience_ages: Optional[List[str]] = None,
        baseline_audience_genders: Optional[List[str]] = None,
        specific_audience_ages: Optional[List[str]] = None,
        specific_audience_genders: Optional[List[str]] = None,
        specific_audience_user_interests: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate insights finder report comparing baseline and specific audiences.

        Args:
            customer_id: The customer ID
            baseline_audience_countries: Country location IDs for baseline audience (e.g., ["2840"] for US)
            specific_audience_countries: Country location IDs for specific audience
            dimensions: Dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, TOPIC, etc.)
            baseline_audience_ages: Age ranges (AGE_RANGE_18_24, AGE_RANGE_25_34, etc.)
            baseline_audience_genders: Genders (MALE, FEMALE, UNDETERMINED)
            specific_audience_ages: Age ranges for specific audience
            specific_audience_genders: Genders for specific audience
            specific_audience_user_interests: User interest IDs for specific audience

        Returns:
            Insights report with saved_report_url for downloading results
        """
        return await service.generate_insights_finder_report(
            ctx=ctx,
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

    async def generate_audience_composition_insights(
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        dimensions: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        audience_attribute_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate detailed composition insights for a specific audience.

        Args:
            customer_id: The customer ID
            audience_countries: Country location IDs (e.g., ["2840"] for US)
            dimensions: Dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, etc.)
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            audience_attribute_groups: Optional custom attribute groups

        Returns:
            Detailed audience composition with affinity scores and demographic breakdowns
        """
        return await service.generate_audience_composition_insights(
            ctx=ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            dimensions=dimensions,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
            audience_attribute_groups=audience_attribute_groups,
        )

    async def generate_suggested_targeting_insights(
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate targeting suggestions for reaching similar audiences.

        Args:
            customer_id: The customer ID
            audience_countries: Country location IDs (e.g., ["2840"] for US)
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs

        Returns:
            Suggested user interests and targeting options for similar audiences
        """
        return await service.generate_suggested_targeting_insights(
            ctx=ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
        )

    tools.extend(
        [
            generate_insights_finder_report,
            generate_audience_composition_insights,
            generate_suggested_targeting_insights,
        ]
    )
    return tools


def register_audience_insights_tools(
    mcp: FastMCP[Any],
) -> AudienceInsightsService:
    """Register audience insights tools with the MCP server.

    Returns the AudienceInsightsService instance for testing purposes.
    """
    service = AudienceInsightsService()
    tools = create_audience_insights_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
