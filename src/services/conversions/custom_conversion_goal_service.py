"""Google Ads Custom Conversion Goal Service

This module provides functionality for managing custom conversion goals in Google Ads.
Custom conversion goals allow making arbitrary conversion actions biddable.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.enums.types.custom_conversion_goal_status import (
    CustomConversionGoalStatusEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.custom_conversion_goal import (
    CustomConversionGoal,
)
from google.ads.googleads.v20.services.services.custom_conversion_goal_service import (
    CustomConversionGoalServiceClient,
)
from google.ads.googleads.v20.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
    MutateCustomConversionGoalsRequest,
    MutateCustomConversionGoalsResponse,
)

from src.sdk_client import get_sdk_client


class CustomConversionGoalService:
    """Service for managing Google Ads custom conversion goals."""

    def __init__(self) -> None:
        """Initialize the custom conversion goal service."""
        self._client: Optional[CustomConversionGoalServiceClient] = None

    @property
    def client(self) -> CustomConversionGoalServiceClient:
        """Get the custom conversion goal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomConversionGoalService")
        assert self._client is not None
        return self._client

    def mutate_custom_conversion_goals(
        self,
        customer_id: str,
        operations: List[CustomConversionGoalOperation],
        validate_only: bool = False,
        response_content_type: Optional[
            ResponseContentTypeEnum.ResponseContentType
        ] = None,
    ) -> MutateCustomConversionGoalsResponse:
        """Mutate custom conversion goals.

        Args:
            customer_id: The customer ID
            operations: List of custom conversion goal operations
            validate_only: Whether to only validate the request
            response_content_type: The response content type setting

        Returns:
            MutateCustomConversionGoalsResponse: The response containing results
        """
        request = MutateCustomConversionGoalsRequest(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

        if response_content_type is not None:
            request.response_content_type = response_content_type

        return self.client.mutate_custom_conversion_goals(request=request)

    def create_custom_conversion_goal_operation(
        self,
        name: str,
        conversion_actions: List[str],
        status: CustomConversionGoalStatusEnum.CustomConversionGoalStatus = CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for creation.

        Args:
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to create the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(
            name=name,
            conversion_actions=conversion_actions,
            status=status,
        )

        return CustomConversionGoalOperation(create=custom_conversion_goal)

    def update_custom_conversion_goal_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        conversion_actions: Optional[List[str]] = None,
        status: Optional[
            CustomConversionGoalStatusEnum.CustomConversionGoalStatus
        ] = None,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for update.

        Args:
            resource_name: The custom conversion goal resource name
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to update the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(resource_name=resource_name)

        update_mask = []
        if name is not None:
            custom_conversion_goal.name = name
            update_mask.append("name")
        if conversion_actions is not None:
            custom_conversion_goal.conversion_actions = conversion_actions
            update_mask.append("conversion_actions")
        if status is not None:
            custom_conversion_goal.status = status
            update_mask.append("status")

        return CustomConversionGoalOperation(
            update=custom_conversion_goal,
            update_mask={"paths": update_mask},
        )

    def remove_custom_conversion_goal_operation(
        self, resource_name: str
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for removal.

        Args:
            resource_name: The custom conversion goal resource name

        Returns:
            CustomConversionGoalOperation: The operation to remove the custom conversion goal
        """
        return CustomConversionGoalOperation(remove=resource_name)


def register_custom_conversion_goal_tools(mcp: FastMCP[Any]) -> None:
    """Register custom conversion goal tools with the MCP server."""

    @mcp.tool
    async def mutate_custom_conversion_goals(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        validate_only: bool = False,
    ) -> str:
        """Create, update, or remove custom conversion goals.

        Args:
            customer_id: The customer ID
            operations: List of custom conversion goal operations
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = CustomConversionGoalService()

        def _get_status_enum(
            status_str: str,
        ) -> CustomConversionGoalStatusEnum.CustomConversionGoalStatus:
            """Convert string to custom conversion goal status enum."""
            if status_str == "ENABLED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
            elif status_str == "REMOVED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.REMOVED
            else:
                raise ValueError(f"Invalid custom conversion goal status: {status_str}")

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                status = (
                    CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
                )
                if "status" in op_data:
                    status = _get_status_enum(op_data["status"])

                operation = service.create_custom_conversion_goal_operation(
                    name=op_data["name"],
                    conversion_actions=op_data["conversion_actions"],
                    status=status,
                )
            elif op_type == "update":
                status = None
                if "status" in op_data:
                    status = _get_status_enum(op_data["status"])

                operation = service.update_custom_conversion_goal_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    conversion_actions=op_data.get("conversion_actions"),
                    status=status,
                )
            elif op_type == "remove":
                operation = service.remove_custom_conversion_goal_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_custom_conversion_goals(
            customer_id=customer_id,
            operations=ops,
            validate_only=validate_only,
        )

        return f"Successfully processed {len(response.results)} custom conversion goal operations"

    @mcp.tool
    async def create_custom_conversion_goal(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        name: str,
        conversion_actions: list[str],
        status: str = "ENABLED",
    ) -> str:
        """Create a new custom conversion goal.

        Args:
            customer_id: The customer ID
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status (ENABLED or REMOVED)

        Returns:
            The created custom conversion goal resource name
        """
        service = CustomConversionGoalService()

        def _get_status_enum(
            status_str: str,
        ) -> CustomConversionGoalStatusEnum.CustomConversionGoalStatus:
            """Convert string to custom conversion goal status enum."""
            if status_str == "ENABLED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
            elif status_str == "REMOVED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.REMOVED
            else:
                raise ValueError(f"Invalid custom conversion goal status: {status_str}")

        operation = service.create_custom_conversion_goal_operation(
            name=name,
            conversion_actions=conversion_actions,
            status=_get_status_enum(status),
        )

        response = service.mutate_custom_conversion_goals(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Created custom conversion goal: {result.resource_name}"

    @mcp.tool
    async def update_custom_conversion_goal(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        conversion_actions: Optional[list[str]] = None,
        status: Optional[str] = None,
    ) -> str:
        """Update an existing custom conversion goal.

        Args:
            customer_id: The customer ID
            resource_name: The custom conversion goal resource name
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status (ENABLED or REMOVED)

        Returns:
            The updated custom conversion goal resource name
        """
        service = CustomConversionGoalService()

        def _get_status_enum(
            status_str: str,
        ) -> CustomConversionGoalStatusEnum.CustomConversionGoalStatus:
            """Convert string to custom conversion goal status enum."""
            if status_str == "ENABLED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
            elif status_str == "REMOVED":
                return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.REMOVED
            else:
                raise ValueError(f"Invalid custom conversion goal status: {status_str}")

        status_enum = None
        if status is not None:
            status_enum = _get_status_enum(status)

        operation = service.update_custom_conversion_goal_operation(
            resource_name=resource_name,
            name=name,
            conversion_actions=conversion_actions,
            status=status_enum,
        )

        response = service.mutate_custom_conversion_goals(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated custom conversion goal: {result.resource_name}"

    @mcp.tool
    async def remove_custom_conversion_goal(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove a custom conversion goal.

        Args:
            customer_id: The customer ID
            resource_name: The custom conversion goal resource name

        Returns:
            Success message
        """
        service = CustomConversionGoalService()

        operation = service.remove_custom_conversion_goal_operation(
            resource_name=resource_name
        )

        service.mutate_custom_conversion_goals(
            customer_id=customer_id, operations=[operation]
        )

        return f"Removed custom conversion goal: {resource_name}"
