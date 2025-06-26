"""Ad group criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    AgeRangeInfo,
    AudienceInfo,
    GenderInfo,
    IncomeRangeInfo,
    KeywordInfo,
    ParentalStatusInfo,
    UserListInfo,
)
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
from google.ads.googleads.v20.resources.types.ad_group_criterion import AdGroupCriterion
from google.ads.googleads.v20.services.services.ad_group_criterion_service import (
    AdGroupCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_service import (
    AdGroupCriterionOperation,
    MutateAdGroupCriteriaRequest,
    MutateAdGroupCriteriaResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupCriterionService:
    """Ad group criterion service for managing ad group-level targeting."""

    def __init__(self) -> None:
        """Initialize the ad group criterion service."""
        self._client: Optional[AdGroupCriterionServiceClient] = None

    @property
    def client(self) -> AdGroupCriterionServiceClient:
        """Get the ad group criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupCriterionService")
        assert self._client is not None
        return self._client

    async def add_keywords(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        negative: bool = False,
    ) -> Dict[str, Any]:
        """Add keyword criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dicts with 'text', 'match_type', and optional 'cpc_bid_micros'
            negative: Whether these are negative keywords

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for keyword in keywords:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )
                ad_group_criterion.negative = negative

                # Set bid if provided and not negative
                if not negative and "cpc_bid_micros" in keyword:
                    ad_group_criterion.cpc_bid_micros = keyword["cpc_bid_micros"]

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                ad_group_criterion.keyword = keyword_info

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(response.results)} keywords to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_list_ids: List[str],
        bid_modifier: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Add audience (user list) targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_list_ids: List of user list IDs
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for user_list_id in user_list_ids:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )

                if bid_modifier is not None:
                    ad_group_criterion.bid_modifier = bid_modifier

                # Create user list info
                user_list_info = UserListInfo()
                user_list_info.user_list = (
                    f"customers/{customer_id}/userLists/{user_list_id}"
                )
                ad_group_criterion.user_list = user_list_info

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                criterion_resource = result.resource_name
                criterion_id = (
                    criterion_resource.split("/")[-1] if criterion_resource else ""
                )
                results.append(
                    {
                        "resource_name": criterion_resource,
                        "criterion_id": criterion_id,
                        "type": "AUDIENCE",
                        "user_list_id": user_list_ids[i],
                        "bid_modifier": bid_modifier,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} audience criteria to ad group {ad_group_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add audience criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_demographic_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        demographics: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Add demographic targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            demographics: List of demographic dicts with 'type' and 'value'

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for demo in demographics:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )

                # Set bid modifier if provided
                if "bid_modifier" in demo:
                    ad_group_criterion.bid_modifier = demo["bid_modifier"]

                # Set demographic based on type
                demo_type = demo["type"].upper()
                if demo_type == "AGE_RANGE":
                    age_range_info = AgeRangeInfo()
                    age_range_info.type_ = getattr(
                        AgeRangeTypeEnum.AgeRangeType, demo["value"]
                    )
                    ad_group_criterion.age_range = age_range_info
                elif demo_type == "GENDER":
                    gender_info = GenderInfo()
                    gender_info.type_ = getattr(
                        GenderTypeEnum.GenderType, demo["value"]
                    )
                    ad_group_criterion.gender = gender_info
                elif demo_type == "PARENTAL_STATUS":
                    parental_status_info = ParentalStatusInfo()
                    parental_status_info.type_ = getattr(
                        ParentalStatusTypeEnum.ParentalStatusType, demo["value"]
                    )
                    ad_group_criterion.parental_status = parental_status_info
                elif demo_type == "INCOME_RANGE":
                    income_range_info = IncomeRangeInfo()
                    income_range_info.type_ = getattr(
                        IncomeRangeTypeEnum.IncomeRangeType, demo["value"]
                    )
                    ad_group_criterion.income_range = income_range_info
                else:
                    continue  # Skip unknown types

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                criterion_resource = result.resource_name
                criterion_id = (
                    criterion_resource.split("/")[-1] if criterion_resource else ""
                )
                demo = demographics[i]
                results.append(
                    {
                        "resource_name": criterion_resource,
                        "criterion_id": criterion_id,
                        "type": demo["type"],
                        "value": demo["value"],
                        "bid_modifier": demo.get("bid_modifier"),
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} demographic criteria to ad group {ad_group_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add demographic criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_criterion_bid(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        cpc_bid_micros: Optional[int] = None,
        bid_modifier: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Update the bid for an ad group criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_resource_name: The criterion resource name
            cpc_bid_micros: New CPC bid in micros
            bid_modifier: New bid modifier

        Returns:
            Updated criterion details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create ad group criterion
            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.resource_name = criterion_resource_name

            # Create update mask
            update_mask_fields = []

            if cpc_bid_micros is not None:
                ad_group_criterion.cpc_bid_micros = cpc_bid_micros
                update_mask_fields.append("cpc_bid_micros")

            if bid_modifier is not None:
                ad_group_criterion.bid_modifier = bid_modifier
                update_mask_fields.append("bid_modifier")

            # Create operation
            operation = AdGroupCriterionOperation()
            operation.update = ad_group_criterion
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Updated criterion bid: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update criterion bid: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_resource_name: The resource name of the criterion to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AdGroupCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed ad group criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_criterion_tools(
    service: AdGroupCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_keywords(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        negative: bool = False,
    ) -> Dict[str, Any]:
        """Add keyword criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dicts with:
                - text: Keyword text
                - match_type: BROAD, PHRASE, EXACT
                - cpc_bid_micros: Optional CPC bid in micros
            negative: Whether these are negative keywords

        Returns:
            Response with created ad group criteria details
        """
        return await service.add_keywords(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
        )

    async def add_audience_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_list_ids: List[str],
        bid_modifier: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Add audience (user list) targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_list_ids: List of user list IDs for remarketing
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%, 0.8 for -20%)

        Returns:
            List of created ad group criteria with resource names and IDs
        """
        return await service.add_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_list_ids=user_list_ids,
            bid_modifier=bid_modifier,
        )

    async def add_demographic_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        demographics: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Add demographic targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            demographics: List of demographic dicts with:
                - type: AGE_RANGE, GENDER, PARENTAL_STATUS, or INCOME_RANGE
                - value: Specific value for the type (e.g., AGE_RANGE_18_24, MALE, PARENT)
                - bid_modifier: Optional bid modifier

        Returns:
            List of created ad group criteria with resource names and IDs
        """
        return await service.add_demographic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=demographics,
        )

    async def update_criterion_bid(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        cpc_bid_micros: Optional[int] = None,
        bid_modifier: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Update the bid for an ad group criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion
            cpc_bid_micros: New CPC bid in micros (for keywords)
            bid_modifier: New bid modifier (for audiences, demographics)

        Returns:
            Updated criterion details with updated fields
        """
        return await service.update_criterion_bid(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
            bid_modifier=bid_modifier,
        )

    async def remove_ad_group_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an ad group criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_ad_group_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    tools.extend(
        [
            add_keywords,
            add_audience_criteria,
            add_demographic_criteria,
            update_criterion_bid,
            remove_ad_group_criterion,
        ]
    )
    return tools


def register_ad_group_criterion_tools(mcp: FastMCP[Any]) -> AdGroupCriterionService:
    """Register ad group criterion tools with the MCP server.

    Returns the AdGroupCriterionService instance for testing purposes.
    """
    service = AdGroupCriterionService()
    tools = create_ad_group_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
