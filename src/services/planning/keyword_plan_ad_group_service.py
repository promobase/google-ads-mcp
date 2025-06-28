"""Google Ads Keyword Plan Ad Group Service

This module provides functionality for managing keyword plan ad groups in Google Ads.
Keyword plan ad groups organize keywords within keyword plan campaigns for planning purposes.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.resources.types.keyword_plan_ad_group import (
    KeywordPlanAdGroup,
)
from google.ads.googleads.v20.services.services.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupOperation,
    MutateKeywordPlanAdGroupsRequest,
    MutateKeywordPlanAdGroupsResponse,
)

from src.sdk_client import get_sdk_client


class KeywordPlanAdGroupService:
    """Service for managing Google Ads keyword plan ad groups."""

    def __init__(self) -> None:
        """Initialize the keyword plan ad group service."""
        self._client: Optional[KeywordPlanAdGroupServiceClient] = None

    @property
    def client(self) -> KeywordPlanAdGroupServiceClient:
        """Get the keyword plan ad group service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordPlanAdGroupService")
        assert self._client is not None
        return self._client

    def mutate_keyword_plan_ad_groups(  # pyright: ignore[reportUnusedFunction]
        self,
        customer_id: str,
        operations: List[KeywordPlanAdGroupOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateKeywordPlanAdGroupsResponse:
        """Mutate keyword plan ad groups.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateKeywordPlanAdGroupsResponse: The response containing results
        """
        request = MutateKeywordPlanAdGroupsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.client.mutate_keyword_plan_ad_groups(request=request)

    def create_keyword_plan_ad_group_operation(  # pyright: ignore[reportUnusedFunction]
        self,
        keyword_plan_campaign: str,
        name: str,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for creation.

        Args:
            keyword_plan_campaign: The keyword plan campaign resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to create the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(
            keyword_plan_campaign=keyword_plan_campaign,
            name=name,
        )

        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros

        return KeywordPlanAdGroupOperation(create=keyword_plan_ad_group)

    def update_keyword_plan_ad_group_operation(  # pyright: ignore[reportUnusedFunction]
        self,
        resource_name: str,
        name: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for update.

        Args:
            resource_name: The keyword plan ad group resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to update the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(resource_name=resource_name)

        update_mask = []
        if name is not None:
            keyword_plan_ad_group.name = name
            update_mask.append("name")
        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")

        return KeywordPlanAdGroupOperation(
            update=keyword_plan_ad_group,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_ad_group_operation(  # pyright: ignore[reportUnusedFunction]
        self, resource_name: str
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for removal.

        Args:
            resource_name: The keyword plan ad group resource name

        Returns:
            KeywordPlanAdGroupOperation: The operation to remove the keyword plan ad group
        """
        return KeywordPlanAdGroupOperation(remove=resource_name)


def register_keyword_plan_ad_group_tools(mcp: FastMCP[Any]) -> None:
    """Register keyword plan ad group tools with the MCP server."""

    @mcp.tool
    async def mutate_keyword_plan_ad_groups(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> str:
        """Create, update, or remove keyword plan ad groups.

        Args:
            customer_id: The customer ID
            operations: List of keyword plan ad group operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = KeywordPlanAdGroupService()

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_keyword_plan_ad_group_operation(
                    keyword_plan_campaign=op_data["keyword_plan_campaign"],
                    name=op_data["name"],
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                )
            elif op_type == "update":
                operation = service.update_keyword_plan_ad_group_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                )
            elif op_type == "remove":
                operation = service.remove_keyword_plan_ad_group_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_keyword_plan_ad_groups(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

        return f"Successfully processed {len(response.results)} keyword plan ad group operations"

    @mcp.tool
    async def create_keyword_plan_ad_group(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        keyword_plan_campaign: str,
        name: str,
        cpc_bid_micros: Optional[int] = None,
    ) -> str:
        """Create a new keyword plan ad group.

        Args:
            customer_id: The customer ID
            keyword_plan_campaign: The keyword plan campaign resource name
            name: Name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            The created keyword plan ad group resource name
        """
        service = KeywordPlanAdGroupService()

        operation = service.create_keyword_plan_ad_group_operation(
            keyword_plan_campaign=keyword_plan_campaign,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
        )

        response = service.mutate_keyword_plan_ad_groups(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Created keyword plan ad group: {result.resource_name}"

    @mcp.tool
    async def update_keyword_plan_ad_group(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> str:
        """Update an existing keyword plan ad group.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan ad group resource name
            name: Name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            The updated keyword plan ad group resource name
        """
        service = KeywordPlanAdGroupService()

        operation = service.update_keyword_plan_ad_group_operation(
            resource_name=resource_name,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
        )

        response = service.mutate_keyword_plan_ad_groups(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated keyword plan ad group: {result.resource_name}"

    @mcp.tool
    async def remove_keyword_plan_ad_group(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove a keyword plan ad group.

        Args:
            customer_id: The customer ID
            resource_name: The keyword plan ad group resource name

        Returns:
            Success message
        """
        service = KeywordPlanAdGroupService()

        operation = service.remove_keyword_plan_ad_group_operation(
            resource_name=resource_name
        )

        service.mutate_keyword_plan_ad_groups(
            customer_id=customer_id, operations=[operation]
        )

        return f"Removed keyword plan ad group: {resource_name}"
