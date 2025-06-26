"""Customer negative criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    ContentLabelInfo,
    KeywordInfo,
    PlacementInfo,
)
from google.ads.googleads.v20.enums.types.content_label_type import ContentLabelTypeEnum
from google.ads.googleads.v20.enums.types.criterion_type import CriterionTypeEnum
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.customer_negative_criterion import (
    CustomerNegativeCriterion,
)
from google.ads.googleads.v20.services.services.customer_negative_criterion_service import (
    CustomerNegativeCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.customer_negative_criterion_service import (
    CustomerNegativeCriterionOperation,
    MutateCustomerNegativeCriteriaRequest,
    MutateCustomerNegativeCriteriaResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerNegativeCriterionService:
    """Customer negative criterion service for account-level exclusions."""

    def __init__(self) -> None:
        """Initialize the customer negative criterion service."""
        self._client: Optional[CustomerNegativeCriterionServiceClient] = None

    @property
    def client(self) -> CustomerNegativeCriterionServiceClient:
        """Get the customer negative criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CustomerNegativeCriterionService"
            )
        assert self._client is not None
        return self._client

    async def add_negative_keywords(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Add negative keywords at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of dicts with 'text' and 'match_type' keys

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for keyword in keywords:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                customer_negative_criterion.keyword = keyword_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.KEYWORD
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                criterion_resource = result.resource_name
                criterion_id = (
                    criterion_resource.split("/")[-1] if criterion_resource else ""
                )
                keyword = keywords[i]
                results.append(
                    {
                        "resource_name": criterion_resource,
                        "criterion_id": criterion_id,
                        "type": "KEYWORD",
                        "keyword_text": keyword["text"],
                        "match_type": keyword["match_type"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} negative keywords at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add negative keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placement_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        placement_urls: List[str],
    ) -> List[Dict[str, Any]]:
        """Add placement (website) exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            placement_urls: List of website URLs to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for url in placement_urls:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create placement info
                placement_info = PlacementInfo()
                placement_info.url = url
                customer_negative_criterion.placement = placement_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.PLACEMENT
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
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
                        "type": "PLACEMENT",
                        "url": placement_urls[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} placement exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add placement exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_content_label_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        content_labels: List[str],
    ) -> List[Dict[str, Any]]:
        """Add content label exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            content_labels: List of content label types to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for label in content_labels:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create content label info
                content_label_info = ContentLabelInfo()
                content_label_info.type_ = getattr(
                    ContentLabelTypeEnum.ContentLabelType, label
                )
                customer_negative_criterion.content_label = content_label_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.CONTENT_LABEL
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
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
                        "type": "CONTENT_LABEL",
                        "content_label": content_labels[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} content label exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add content label exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_negative_criteria(
        self,
        ctx: Context,
        customer_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all customer negative criteria.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_type: Optional filter by type (KEYWORD, PLACEMENT, CONTENT_LABEL)

        Returns:
            List of customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    customer_negative_criterion.resource_name,
                    customer_negative_criterion.id,
                    customer_negative_criterion.type,
                    customer_negative_criterion.keyword.text,
                    customer_negative_criterion.keyword.match_type,
                    customer_negative_criterion.placement.url,
                    customer_negative_criterion.content_label.type
                FROM customer_negative_criterion
            """

            if criterion_type:
                query += f" WHERE customer_negative_criterion.type = '{criterion_type}'"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            criteria = []
            for row in response:
                criterion = row.customer_negative_criterion
                criterion_dict = {
                    "resource_name": criterion.resource_name,
                    "criterion_id": str(criterion.id),
                    "type": criterion.type_.name if criterion.type_ else "UNKNOWN",
                }

                # Add type-specific fields
                if criterion.keyword:
                    criterion_dict["keyword_text"] = criterion.keyword.text
                    criterion_dict["match_type"] = criterion.keyword.match_type.name
                elif criterion.placement:
                    criterion_dict["url"] = criterion.placement.url
                elif criterion.content_label:
                    criterion_dict["content_label"] = criterion.content_label.type_.name

                criteria.append(criterion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(criteria)} customer negative criteria",
            )

            return criteria

        except Exception as e:
            error_msg = f"Failed to list negative criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_negative_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a customer negative criterion.

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
            operation = CustomerNegativeCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_customer_negative_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed customer negative criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove negative criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_negative_criterion_tools(
    service: CustomerNegativeCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer negative criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_negative_keywords(
        ctx: Context,
        customer_id: str,
        keywords: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Add negative keywords at the account level.

        Args:
            customer_id: The customer ID
            keywords: List of keyword dicts with:
                - text: Keyword text
                - match_type: BROAD, PHRASE, or EXACT

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_negative_keywords(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
        )

    async def add_placement_exclusions(
        ctx: Context,
        customer_id: str,
        placement_urls: List[str],
    ) -> List[Dict[str, Any]]:
        """Add placement (website) exclusions at the account level.

        Args:
            customer_id: The customer ID
            placement_urls: List of website URLs to exclude (e.g., ["example.com", "site.com"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_placement_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            placement_urls=placement_urls,
        )

    async def add_content_label_exclusions(
        ctx: Context,
        customer_id: str,
        content_labels: List[str],
    ) -> List[Dict[str, Any]]:
        """Add content label exclusions at the account level.

        Args:
            customer_id: The customer ID
            content_labels: List of content label types to exclude:
                - JUVENILE
                - PROFANITY
                - TRAGEDY
                - VIDEO
                - VIDEO_RATING_DV_G
                - VIDEO_RATING_DV_PG
                - VIDEO_RATING_DV_T
                - VIDEO_RATING_DV_MA
                - VIDEO_NOT_YET_RATED
                - EMBEDDED_VIDEO
                - LIVE_STREAMING_VIDEO
                - SOCIAL_ISSUES

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_content_label_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            content_labels=content_labels,
        )

    async def list_negative_criteria(
        ctx: Context,
        customer_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all customer negative criteria.

        Args:
            customer_id: The customer ID
            criterion_type: Optional filter by type - KEYWORD, PLACEMENT, or CONTENT_LABEL

        Returns:
            List of customer negative criteria with details
        """
        return await service.list_negative_criteria(
            ctx=ctx,
            customer_id=customer_id,
            criterion_type=criterion_type,
        )

    async def remove_negative_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a customer negative criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_negative_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    tools.extend(
        [
            add_negative_keywords,
            add_placement_exclusions,
            add_content_label_exclusions,
            list_negative_criteria,
            remove_negative_criterion,
        ]
    )
    return tools


def register_customer_negative_criterion_tools(
    mcp: FastMCP[Any],
) -> CustomerNegativeCriterionService:
    """Register customer negative criterion tools with the MCP server.

    Returns the CustomerNegativeCriterionService instance for testing purposes.
    """
    service = CustomerNegativeCriterionService()
    tools = create_customer_negative_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
