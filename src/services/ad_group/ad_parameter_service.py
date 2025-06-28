"""Ad parameter service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.ad_parameter import (
    AdParameter,
)
from google.ads.googleads.v20.services.services.ad_parameter_service import (
    AdParameterServiceClient,
)
from google.ads.googleads.v20.services.types.ad_parameter_service import (
    AdParameterOperation,
    MutateAdParametersRequest,
    MutateAdParametersResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdParameterService:
    """Ad parameter service for managing dynamic numeric values in ads."""

    def __init__(self) -> None:
        """Initialize the ad parameter service."""
        self._client: Optional[AdParameterServiceClient] = None

    @property
    def client(self) -> AdParameterServiceClient:
        """Get the ad parameter service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdParameterService")
        assert self._client is not None
        return self._client

    async def mutate_ad_parameters(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> Dict[str, Any]:
        """Create, update, or remove ad parameters.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of operations to perform
            partial_failure: Whether to allow partial failures
            validate_only: Whether to only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Mutation results with resource names and any errors
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Convert operations
            mutate_operations = []
            for op in operations:
                operation = AdParameterOperation()

                if "create" in op:
                    create_data = op["create"]
                    ad_parameter = AdParameter()

                    if "ad_group_criterion" in create_data:
                        ad_parameter.ad_group_criterion = create_data[
                            "ad_group_criterion"
                        ]

                    if "parameter_index" in create_data:
                        ad_parameter.parameter_index = int(
                            create_data["parameter_index"]
                        )

                    if "insertion_text" in create_data:
                        ad_parameter.insertion_text = create_data["insertion_text"]

                    operation.create = ad_parameter

                elif "update" in op:
                    update_data = op["update"]
                    ad_parameter = AdParameter()

                    if "resource_name" in update_data:
                        ad_parameter.resource_name = update_data["resource_name"]

                    if "insertion_text" in update_data:
                        ad_parameter.insertion_text = update_data["insertion_text"]

                    # Set update mask for fields that can be updated
                    update_mask = field_mask_pb2.FieldMask()
                    if "insertion_text" in update_data:
                        update_mask.paths.append("insertion_text")
                    operation.update_mask = update_mask

                    operation.update = ad_parameter

                elif "remove" in op:
                    operation.remove = op["remove"]

                mutate_operations.append(operation)

            # Create request
            request = MutateAdParametersRequest()
            request.customer_id = customer_id
            request.operations = mutate_operations
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = getattr(
                ResponseContentTypeEnum.ResponseContentType,
                response_content_type,
            )

            # Make the API call
            response: MutateAdParametersResponse = self.client.mutate_ad_parameters(
                request=request
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate ad parameters: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_parameter_tools(
    service: AdParameterService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad parameter service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def mutate_ad_parameters(
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> Dict[str, Any]:
        """Create, update, or remove ad parameters for dynamic numeric values in ads.

        Args:
            customer_id: The customer ID
            operations: List of operations to perform. Each operation should have either:
                - create: Dict with ad_group_criterion, parameter_index (1 or 2), and insertion_text
                - update: Dict with resource_name and insertion_text
                - remove: Resource name to remove
            partial_failure: Whether to allow partial failures
            validate_only: Whether to only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Mutation results with resource names and any errors
        """
        return await service.mutate_ad_parameters(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([mutate_ad_parameters])
    return tools


def register_ad_parameter_tools(
    mcp: FastMCP[Any],
) -> AdParameterService:
    """Register ad parameter tools with the MCP server.

    Returns the AdParameterService instance for testing purposes.
    """
    service = AdParameterService()
    tools = create_ad_parameter_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
