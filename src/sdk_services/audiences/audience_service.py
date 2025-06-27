"""Audience service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.audiences import (
    AgeDimension,
    AudienceDimension,
    AudienceExclusionDimension,
    AudienceSegmentDimension,
    CustomAudienceSegment,
    DetailedDemographicSegment,
    GenderDimension,
    HouseholdIncomeDimension,
    LifeEventSegment,
    ParentalStatusDimension,
    UserInterestSegment,
    UserListSegment,
)
from google.ads.googleads.v20.enums.types.audience_status import AudienceStatusEnum
from google.ads.googleads.v20.resources.types.audience import Audience
from google.ads.googleads.v20.services.services.audience_service import (
    AudienceServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.audience_service import (
    AudienceOperation,
    MutateAudiencesRequest,
    MutateAudiencesResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AudienceService:
    """Audience service for managing combined audiences."""

    def __init__(self) -> None:
        """Initialize the audience service."""
        self._client: Optional[AudienceServiceClient] = None

    @property
    def client(self) -> AudienceServiceClient:
        """Get the audience service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AudienceService")
        assert self._client is not None
        return self._client

    async def create_combined_audience(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        dimensions: List[Dict[str, Any]],
        exclusion_dimensions: Optional[List[Dict[str, Any]]] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a combined audience with multiple targeting dimensions.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Audience name
            description: Audience description
            dimensions: List of audience dimensions to include
            exclusion_dimensions: Optional list of dimensions to exclude
            status: Audience status (ENABLED, REMOVED)

        Returns:
            Created audience details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create audience
            audience = Audience()
            audience.name = name
            audience.description = description
            audience.status = getattr(AudienceStatusEnum.AudienceStatus, status)

            # Add dimensions
            for dim_config in dimensions:
                dimension = self._create_audience_dimension(dim_config)
                audience.dimensions.append(dimension)

            # Add exclusion dimension if provided
            # Note: In v20, only one exclusion dimension is supported
            if exclusion_dimensions and len(exclusion_dimensions) > 0:
                exclusion = self._create_audience_exclusion_dimension(
                    exclusion_dimensions[0]
                )
                audience.exclusion_dimension = exclusion

            # Create operation
            operation = AudienceOperation()
            operation.create = audience

            # Create request
            request = MutateAudiencesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateAudiencesResponse = self.client.mutate_audiences(
                request=request
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create combined audience: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def _create_audience_dimension(self, config: Dict[str, Any]) -> AudienceDimension:
        """Create an audience dimension from configuration."""
        dimension = AudienceDimension()

        dimension_type = config.get("type")

        if dimension_type == "AGE":
            age_dim = AgeDimension()
            age_ranges = config.get("age_ranges", [])
            for age_range in age_ranges:
                # Create AgeSegment from age range specification
                from google.ads.googleads.v20.common.types.audiences import AgeSegment

                age_segment = AgeSegment()

                # Handle different age range formats
                if isinstance(age_range, dict):
                    if "min_age" in age_range:
                        age_segment.min_age = age_range["min_age"]
                    if "max_age" in age_range:
                        age_segment.max_age = age_range["max_age"]
                elif isinstance(age_range, str):
                    # Handle predefined age ranges
                    if age_range == "AGE_RANGE_18_24":
                        age_segment.min_age = 18
                        age_segment.max_age = 24
                    elif age_range == "AGE_RANGE_25_34":
                        age_segment.min_age = 25
                        age_segment.max_age = 34
                    elif age_range == "AGE_RANGE_35_44":
                        age_segment.min_age = 35
                        age_segment.max_age = 44
                    elif age_range == "AGE_RANGE_45_54":
                        age_segment.min_age = 45
                        age_segment.max_age = 54
                    elif age_range == "AGE_RANGE_55_64":
                        age_segment.min_age = 55
                        age_segment.max_age = 64
                    elif age_range == "AGE_RANGE_65_UP":
                        age_segment.min_age = 65
                        # No max_age for 65+

                age_dim.age_ranges.append(age_segment)
            dimension.age = age_dim

        elif dimension_type == "GENDER":
            gender_dim = GenderDimension()
            genders = config.get("genders", [])

            # Import enum for gender
            from google.ads.googleads.v20.enums.types.gender_type import GenderTypeEnum

            for gender in genders:
                if isinstance(gender, str):
                    gender_dim.genders.append(
                        getattr(GenderTypeEnum.GenderType, gender)
                    )
                else:
                    gender_dim.genders.append(gender)
            dimension.gender = gender_dim

        elif dimension_type == "HOUSEHOLD_INCOME":
            income_dim = HouseholdIncomeDimension()
            income_ranges = config.get("income_ranges", [])

            # Import enum for income range
            from google.ads.googleads.v20.enums.types.income_range_type import (
                IncomeRangeTypeEnum,
            )

            for income_range in income_ranges:
                if isinstance(income_range, str):
                    income_dim.income_ranges.append(
                        getattr(IncomeRangeTypeEnum.IncomeRangeType, income_range)
                    )
                else:
                    income_dim.income_ranges.append(income_range)
            dimension.household_income = income_dim

        elif dimension_type == "PARENTAL_STATUS":
            parental_dim = ParentalStatusDimension()
            parent_types = config.get("parent_types", [])

            # Import enum for parental status
            from google.ads.googleads.v20.enums.types.parental_status_type import (
                ParentalStatusTypeEnum,
            )

            for parent_type in parent_types:
                if isinstance(parent_type, str):
                    parental_dim.parental_statuses.append(
                        getattr(ParentalStatusTypeEnum.ParentalStatusType, parent_type)
                    )
                else:
                    parental_dim.parental_statuses.append(parent_type)
            dimension.parental_status = parental_dim

        elif dimension_type == "USER_LIST":
            segment_dim = AudienceSegmentDimension()
            user_list_segment = UserListSegment()
            user_list_segment.user_list = config.get("user_list_resource")  # type: ignore

            # Create audience segment manually
            from google.ads.googleads.v20.common.types.audiences import AudienceSegment

            audience_segment = AudienceSegment()
            audience_segment.user_list = user_list_segment  # type: ignore
            segment_dim.segments.append(audience_segment)
            dimension.audience_segments = segment_dim

        elif dimension_type == "USER_INTEREST":
            segment_dim = AudienceSegmentDimension()
            interest_segment = UserInterestSegment()
            interest_segment.user_interest_category = config.get("interest_resource")  # type: ignore

            # Create audience segment manually
            from google.ads.googleads.v20.common.types.audiences import AudienceSegment

            audience_segment = AudienceSegment()
            audience_segment.user_interest = interest_segment  # type: ignore
            segment_dim.segments.append(audience_segment)
            dimension.audience_segments = segment_dim

        elif dimension_type == "CUSTOM_AUDIENCE":
            segment_dim = AudienceSegmentDimension()
            custom_segment = CustomAudienceSegment()
            custom_segment.custom_audience = config.get("custom_audience_resource")  # type: ignore

            # Create audience segment manually
            from google.ads.googleads.v20.common.types.audiences import AudienceSegment

            audience_segment = AudienceSegment()
            audience_segment.custom_audience = custom_segment  # type: ignore
            segment_dim.segments.append(audience_segment)
            dimension.audience_segments = segment_dim

        elif dimension_type == "LIFE_EVENT":
            segment_dim = AudienceSegmentDimension()
            life_event_segment = LifeEventSegment()
            life_event_segment.life_event = config.get("life_event_resource")  # type: ignore

            # Create audience segment manually
            from google.ads.googleads.v20.common.types.audiences import AudienceSegment

            audience_segment = AudienceSegment()
            audience_segment.life_event = life_event_segment  # type: ignore
            segment_dim.segments.append(audience_segment)
            dimension.audience_segments = segment_dim

        elif dimension_type == "DETAILED_DEMOGRAPHIC":
            segment_dim = AudienceSegmentDimension()
            demographic_segment = DetailedDemographicSegment()
            demographic_segment.detailed_demographic = config.get(
                "demographic_resource"
            )  # type: ignore
            # Create audience segment manually since direct construction may not work
            from google.ads.googleads.v20.common.types.audiences import AudienceSegment

            audience_segment = AudienceSegment()
            audience_segment.detailed_demographic = demographic_segment  # type: ignore
            segment_dim.segments.append(audience_segment)
            dimension.audience_segments = segment_dim

        return dimension

    def _create_audience_exclusion_dimension(
        self, config: Dict[str, Any]
    ) -> AudienceExclusionDimension:
        """Create an audience exclusion dimension from configuration.

        Note: In v20, exclusions only support audience segments (user lists).
        """
        exclusion = AudienceExclusionDimension()

        dimension_type = config.get("type")

        if dimension_type == "USER_LIST":
            from google.ads.googleads.v20.common.types.audiences import ExclusionSegment

            exclusion_segment = ExclusionSegment()
            user_list_segment = UserListSegment()
            user_list_segment.user_list = config.get("user_list_resource")  # type: ignore
            exclusion_segment.user_list = user_list_segment
            exclusion.exclusions.append(exclusion_segment)
        else:
            # Other dimension types are not supported for exclusions in v20
            logger.warning(f"Exclusion type {dimension_type} is not supported in v20")

        return exclusion

    async def update_audience(
        self,
        ctx: Context,
        customer_id: str,
        audience_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an audience.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_id: The audience ID to update
            name: Optional new name
            description: Optional new description
            status: Optional new status

        Returns:
            Updated audience details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/audiences/{audience_id}"

            # Create audience with resource name
            audience = Audience()
            audience.resource_name = resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                audience.name = name
                update_mask_paths.append("name")

            if description is not None:
                audience.description = description
                update_mask_paths.append("description")

            if status is not None:
                audience.status = getattr(AudienceStatusEnum.AudienceStatus, status)
                update_mask_paths.append("status")

            # Create operation
            operation = AudienceOperation()
            operation.update = audience
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateAudiencesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_audiences(request=request)

            await ctx.log(
                level="info",
                message=f"Updated audience {audience_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update audience: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_audiences(
        self,
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            include_removed: Whether to include removed audiences
            limit: Maximum number of results

        Returns:
            List of audiences
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    audience.id,
                    audience.name,
                    audience.status,
                    audience.description,
                    audience.resource_name
                FROM audience
            """

            if not include_removed:
                query += " WHERE audience.status != 'REMOVED'"

            query += f" ORDER BY audience.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            audiences = []
            for row in response:
                audience = row.audience

                audience_dict = {
                    "id": str(audience.id),
                    "name": audience.name,
                    "description": audience.description,
                    "status": audience.status.name if audience.status else "UNKNOWN",
                    "resource_name": audience.resource_name,
                }

                audiences.append(audience_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(audiences)} audiences",
            )

            return audiences

        except Exception as e:
            error_msg = f"Failed to list audiences: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_audience(
        self,
        ctx: Context,
        customer_id: str,
        audience_id: str,
    ) -> Dict[str, Any]:
        """Remove an audience.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_id: The audience ID to remove

        Returns:
            Removal result
        """
        # Since there's no remove operation, update status to REMOVED
        return await self.update_audience(
            ctx=ctx,
            customer_id=customer_id,
            audience_id=audience_id,
            status="REMOVED",
        )


def create_audience_tools(
    service: AudienceService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the audience service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_combined_audience(
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        dimensions: List[Dict[str, Any]],
        exclusion_dimensions: Optional[List[Dict[str, Any]]] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a combined audience with multiple targeting dimensions.

        Args:
            customer_id: The customer ID
            name: Audience name
            description: Audience description
            dimensions: List of audience dimensions to include. Each dimension dict should have:
                - type: Dimension type (AGE, GENDER, HOUSEHOLD_INCOME, PARENTAL_STATUS,
                        USER_LIST, USER_INTEREST, CUSTOM_AUDIENCE, LIFE_EVENT, DETAILED_DEMOGRAPHIC)
                - Additional fields based on type:
                    - AGE: age_ranges (list of age range enums)
                    - GENDER: genders (list of gender enums)
                    - HOUSEHOLD_INCOME: income_ranges (list of income range enums)
                    - PARENTAL_STATUS: parent_types (list of parental status enums)
                    - USER_LIST: user_list_resource (resource name)
                    - USER_INTEREST: interest_resource (resource name)
                    - CUSTOM_AUDIENCE: custom_audience_resource (resource name)
                    - LIFE_EVENT: life_event_resource (resource name)
                    - DETAILED_DEMOGRAPHIC: demographic_resource (resource name)
            exclusion_dimensions: Optional list of dimensions to exclude (same format as dimensions)
            status: Audience status - ENABLED or REMOVED

        Returns:
            Created audience details including resource_name and audience_id
        """
        return await service.create_combined_audience(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            dimensions=dimensions,
            exclusion_dimensions=exclusion_dimensions,
            status=status,
        )

    async def update_audience(
        ctx: Context,
        customer_id: str,
        audience_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an audience.

        Args:
            customer_id: The customer ID
            audience_id: The audience ID to update
            name: Optional new name
            description: Optional new description
            status: Optional new status - ENABLED or REMOVED

        Returns:
            Updated audience details with list of updated fields
        """
        return await service.update_audience(
            ctx=ctx,
            customer_id=customer_id,
            audience_id=audience_id,
            name=name,
            description=description,
            status=status,
        )

    async def list_audiences(
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List audiences.

        Args:
            customer_id: The customer ID
            include_removed: Whether to include removed audiences
            limit: Maximum number of results

        Returns:
            List of audiences with details
        """
        return await service.list_audiences(
            ctx=ctx,
            customer_id=customer_id,
            include_removed=include_removed,
            limit=limit,
        )

    async def remove_audience(
        ctx: Context,
        customer_id: str,
        audience_id: str,
    ) -> Dict[str, Any]:
        """Remove an audience.

        Args:
            customer_id: The customer ID
            audience_id: The audience ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_audience(
            ctx=ctx,
            customer_id=customer_id,
            audience_id=audience_id,
        )

    tools.extend(
        [
            create_combined_audience,
            update_audience,
            list_audiences,
            remove_audience,
        ]
    )
    return tools


def register_audience_tools(mcp: FastMCP[Any]) -> AudienceService:
    """Register audience tools with the MCP server.

    Returns the AudienceService instance for testing purposes.
    """
    service = AudienceService()
    tools = create_audience_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
