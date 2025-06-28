"""Customer conversion goal service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.customer_conversion_goal_service import (
    CustomerConversionGoalServiceClient,
)
from google.ads.googleads.v20.services.types.customer_conversion_goal_service import (
    MutateCustomerConversionGoalsRequest,
    CustomerConversionGoalOperation,
    MutateCustomerConversionGoalsResponse,
)
from google.ads.googleads.v20.resources.types.customer_conversion_goal import (
    CustomerConversionGoal,
)
from google.ads.googleads.v20.enums.types.conversion_action_category import (
    ConversionActionCategoryEnum,
)
from google.ads.googleads.v20.enums.types.conversion_origin import (
    ConversionOriginEnum,
)
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger

logger = get_logger(__name__)


class CustomerConversionGoalService:
    """Customer conversion goal service for managing customer-level conversion goal biddability."""

    def __init__(self) -> None:
        """Initialize the customer conversion goal service."""
        self._client: Optional[CustomerConversionGoalServiceClient] = None

    @property
    def client(self) -> CustomerConversionGoalServiceClient:
        """Get the customer conversion goal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CustomerConversionGoalService"
            )
        assert self._client is not None
        return self._client

    async def mutate_customer_conversion_goals(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update customer conversion goals.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of update operations to perform
            validate_only: Whether to only validate the request

        Returns:
            Mutation results with resource names
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Convert operations
            mutate_operations = []
            for op in operations:
                operation = CustomerConversionGoalOperation()

                if "update" in op:
                    update_data = op["update"]
                    conversion_goal = CustomerConversionGoal()

                    if "resource_name" in update_data:
                        conversion_goal.resource_name = update_data["resource_name"]

                    if "category" in update_data:
                        conversion_goal.category = getattr(
                            ConversionActionCategoryEnum.ConversionActionCategory,
                            update_data["category"],
                        )

                    if "origin" in update_data:
                        conversion_goal.origin = getattr(
                            ConversionOriginEnum.ConversionOrigin,
                            update_data["origin"],
                        )

                    if "biddable" in update_data:
                        conversion_goal.biddable = bool(update_data["biddable"])

                    # Set update mask for fields that can be updated
                    update_mask = field_mask_pb2.FieldMask()
                    if "biddable" in update_data:
                        update_mask.paths.append("biddable")
                    operation.update_mask = update_mask

                    operation.update = conversion_goal

                mutate_operations.append(operation)

            # Create request
            request = MutateCustomerConversionGoalsRequest()
            request.customer_id = customer_id
            request.operations = mutate_operations
            request.validate_only = validate_only

            # Make the API call
            response: MutateCustomerConversionGoalsResponse = (
                self.client.mutate_customer_conversion_goals(request=request)
            )

            # Process results
            results = []
            for result in response.results:
                result_dict = {
                    "resource_name": result.resource_name,
                }
                results.append(result_dict)

            await ctx.log(
                level="info",
                message=f"Mutated {len(results)} customer conversion goals",
            )

            return {
                "results": results,
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate customer conversion goals: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_conversion_goal_tools(
    service: CustomerConversionGoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer conversion goal service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def mutate_customer_conversion_goals(
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update customer conversion goals to control biddability at the customer level.

        Args:
            customer_id: The customer ID
            operations: List of update operations. Each operation should have:
                - update: Dict with resource_name and biddable (true/false)
            validate_only: Whether to only validate the request

        Returns:
            Mutation results with resource names
        """
        return await service.mutate_customer_conversion_goals(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

    tools.extend([mutate_customer_conversion_goals])
    return tools


def register_customer_conversion_goal_tools(
    mcp: FastMCP[Any],
) -> CustomerConversionGoalService:
    """Register customer conversion goal tools with the MCP server.

    Returns the CustomerConversionGoalService instance for testing purposes.
    """
    service = CustomerConversionGoalService()
    tools = create_customer_conversion_goal_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
