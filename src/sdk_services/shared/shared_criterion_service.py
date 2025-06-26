"""Shared criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import (
    KeywordInfo,
    PlacementInfo,
)
from google.ads.googleads.v20.enums.types.criterion_type import CriterionTypeEnum
from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.resources.types.shared_criterion import SharedCriterion
from google.ads.googleads.v20.services.services.shared_criterion_service import (
    SharedCriterionServiceClient,
)
from google.ads.googleads.v20.services.types.shared_criterion_service import (
    MutateSharedCriteriaRequest,
    MutateSharedCriteriaResponse,
    SharedCriterionOperation,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class SharedCriterionService:
    """Shared criterion service for managing items in shared sets."""

    def __init__(self) -> None:
        """Initialize the shared criterion service."""
        self._client: Optional[SharedCriterionServiceClient] = None

    @property
    def client(self) -> SharedCriterionServiceClient:
        """Get the shared criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("SharedCriterionService")
        assert self._client is not None
        return self._client

    async def add_keywords_to_shared_set(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        keywords: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Add negative keywords to a shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID
            keywords: List of dicts with 'text' and 'match_type' keys

        Returns:
            List of created shared criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            shared_set_resource = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            # Create operations
            operations = []
            for keyword in keywords:
                # Create shared criterion
                shared_criterion = SharedCriterion()
                shared_criterion.shared_set = shared_set_resource
                shared_criterion.type_ = CriterionTypeEnum.CriterionType.KEYWORD

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                shared_criterion.keyword = keyword_info

                # Create operation
                operation = SharedCriterionOperation()
                operation.create = shared_criterion
                operations.append(operation)

            # Create request
            request = MutateSharedCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateSharedCriteriaResponse = self.client.mutate_shared_criteria(
                request=request
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
                        "shared_criterion_id": criterion_id,
                        "type": "KEYWORD",
                        "keyword_text": keyword["text"],
                        "match_type": keyword["match_type"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} keywords to shared set {shared_set_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add keywords to shared set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placements_to_shared_set(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        placement_urls: List[str],
    ) -> List[Dict[str, Any]]:
        """Add placement exclusions to a shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID
            placement_urls: List of website URLs

        Returns:
            List of created shared criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            shared_set_resource = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            # Create operations
            operations = []
            for url in placement_urls:
                # Create shared criterion
                shared_criterion = SharedCriterion()
                shared_criterion.shared_set = shared_set_resource
                shared_criterion.type_ = CriterionTypeEnum.CriterionType.PLACEMENT

                # Create placement info
                placement_info = PlacementInfo()
                placement_info.url = url
                shared_criterion.placement = placement_info

                # Create operation
                operation = SharedCriterionOperation()
                operation.create = shared_criterion
                operations.append(operation)

            # Create request
            request = MutateSharedCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: MutateSharedCriteriaResponse = self.client.mutate_shared_criteria(
                request=request
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
                        "shared_criterion_id": criterion_id,
                        "type": "PLACEMENT",
                        "url": placement_urls[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} placements to shared set {shared_set_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add placements to shared set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_shared_criteria(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List criteria in a shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID
            criterion_type: Optional filter by type

        Returns:
            List of shared criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            shared_set_resource = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = f"""
                SELECT
                    shared_criterion.resource_name,
                    shared_criterion.criterion_id,
                    shared_criterion.type,
                    shared_criterion.keyword.text,
                    shared_criterion.keyword.match_type,
                    shared_criterion.placement.url
                FROM shared_criterion
                WHERE shared_criterion.shared_set = '{shared_set_resource}'
            """

            if criterion_type:
                query += f" AND shared_criterion.type = '{criterion_type}'"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            criteria = []
            for row in response:
                criterion = row.shared_criterion
                criterion_dict = {
                    "resource_name": criterion.resource_name,
                    "shared_criterion_id": str(criterion.criterion_id),
                    "type": criterion.type_.name if criterion.type_ else "UNKNOWN",
                }

                # Add type-specific fields
                if criterion.keyword:
                    criterion_dict["keyword_text"] = criterion.keyword.text
                    criterion_dict["match_type"] = criterion.keyword.match_type.name
                elif criterion.placement:
                    criterion_dict["url"] = criterion.placement.url

                criteria.append(criterion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(criteria)} criteria in shared set {shared_set_id}",
            )

            return criteria

        except Exception as e:
            error_msg = f"Failed to list shared criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_shared_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a criterion from a shared set.

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
            operation = SharedCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateSharedCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_shared_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed shared criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove shared criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_shared_criterion_tools(
    service: SharedCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the shared criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_keywords_to_shared_set(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        keywords: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Add negative keywords to a shared set.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID
            keywords: List of keyword dicts with:
                - text: Keyword text
                - match_type: BROAD, PHRASE, or EXACT

        Returns:
            List of created shared criteria with resource names and IDs
        """
        return await service.add_keywords_to_shared_set(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            keywords=keywords,
        )

    async def add_placements_to_shared_set(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        placement_urls: List[str],
    ) -> List[Dict[str, Any]]:
        """Add placement exclusions to a shared set.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID
            placement_urls: List of website URLs to exclude

        Returns:
            List of created shared criteria with resource names and IDs
        """
        return await service.add_placements_to_shared_set(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            placement_urls=placement_urls,
        )

    async def list_shared_criteria(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List criteria in a shared set.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID
            criterion_type: Optional filter by type - KEYWORD or PLACEMENT

        Returns:
            List of shared criteria with details
        """
        return await service.list_shared_criteria(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            criterion_type=criterion_type,
        )

    async def remove_shared_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a criterion from a shared set.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_shared_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    tools.extend(
        [
            add_keywords_to_shared_set,
            add_placements_to_shared_set,
            list_shared_criteria,
            remove_shared_criterion,
        ]
    )
    return tools


def register_shared_criterion_tools(mcp: FastMCP[Any]) -> SharedCriterionService:
    """Register shared criterion tools with the MCP server.

    Returns the SharedCriterionService instance for testing purposes.
    """
    service = SharedCriterionService()
    tools = create_shared_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
