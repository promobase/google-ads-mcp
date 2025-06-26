"""Keyword service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import KeywordInfo
from google.ads.googleads.v20.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v20.enums.types.keyword_match_type import (
    KeywordMatchTypeEnum,
)
from google.ads.googleads.v20.resources.types.ad_group_criterion import (
    AdGroupCriterion,
)
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


class KeywordService:
    """Keyword service for managing Google Ads keywords."""

    def __init__(self) -> None:
        """Initialize the keyword service."""
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
        keywords: List[Dict[str, str]],
        default_cpc_bid_micros: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Add keywords to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dictionaries with 'text' and 'match_type' fields
            default_cpc_bid_micros: Default CPC bid for keywords in micros

        Returns:
            List of created keyword details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []

            for keyword_data in keywords:
                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword_data["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType,
                    keyword_data.get("match_type", "BROAD"),
                )

                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource_name
                ad_group_criterion.keyword = keyword_info
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )

                # Set CPC bid if provided
                if (
                    default_cpc_bid_micros is not None
                    or "cpc_bid_micros" in keyword_data
                ):
                    cpc_bid = keyword_data.get("cpc_bid_micros", default_cpc_bid_micros)
                    if cpc_bid is not None:
                        ad_group_criterion.cpc_bid_micros = int(cpc_bid)

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create the request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            # Extract results
            results = []
            for result in response.results:
                resource_name = result.resource_name
                criterion_id = resource_name.split("~")[-1] if resource_name else ""
                results.append(
                    {
                        "resource_name": resource_name,
                        "criterion_id": criterion_id,
                        "ad_group_id": ad_group_id,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} keywords to ad group {ad_group_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_keyword_bid(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_id: str,
        cpc_bid_micros: int,
    ) -> Dict[str, Any]:
        """Update the bid for a keyword.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_id: The criterion ID
            cpc_bid_micros: New CPC bid in micros

        Returns:
            Updated keyword details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
            )

            # Create ad group criterion with resource name
            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.resource_name = resource_name
            ad_group_criterion.cpc_bid_micros = cpc_bid_micros

            # Create the operation
            operation = AdGroupCriterionOperation()
            operation.update = ad_group_criterion
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=["cpc_bid_micros"])
            )

            # Create the request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Updated bid for keyword {criterion_id} to {cpc_bid_micros} micros",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update keyword bid: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_keyword(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_id: str,
    ) -> Dict[str, Any]:
        """Remove a keyword from an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_id: The criterion ID

        Returns:
            Removed keyword details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"
            )

            # Create the operation
            operation = AdGroupCriterionOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed keyword {criterion_id} from ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove keyword: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_keyword_tools(
    service: KeywordService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the keyword service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_keywords(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, str]],
        default_cpc_bid_micros: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Add keywords to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dictionaries, each with:
                - text: The keyword text
                - match_type: EXACT, PHRASE, or BROAD (default: BROAD)
                - cpc_bid_micros: Optional CPC bid for this keyword
            default_cpc_bid_micros: Default CPC bid for keywords without individual bids

        Returns:
            List of created keyword details
        """
        return await service.add_keywords(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            default_cpc_bid_micros=default_cpc_bid_micros,
        )

    async def update_keyword_bid(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_id: str,
        cpc_bid_micros: int,
    ) -> Dict[str, Any]:
        """Update the bid for a keyword.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_id: The criterion ID of the keyword
            cpc_bid_micros: New CPC bid in micros (1 million micros = 1 unit)

        Returns:
            Updated keyword details
        """
        return await service.update_keyword_bid(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
            cpc_bid_micros=cpc_bid_micros,
        )

    async def remove_keyword(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_id: str,
    ) -> Dict[str, Any]:
        """Remove a keyword from an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_id: The criterion ID of the keyword to remove

        Returns:
            Removed keyword details
        """
        return await service.remove_keyword(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_id=criterion_id,
        )

    tools.extend([add_keywords, update_keyword_bid, remove_keyword])
    return tools


def register_keyword_tools(mcp: FastMCP[Any]) -> KeywordService:
    """Register keyword tools with the MCP server.

    Returns the KeywordService instance for testing purposes.
    """
    service = KeywordService()
    tools = create_keyword_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
