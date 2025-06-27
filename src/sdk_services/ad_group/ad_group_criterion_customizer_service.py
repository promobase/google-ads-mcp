"""Ad group criterion customizer service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.customizer_value import (
    CustomizerValue,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.ad_group_criterion_customizer import (
    AdGroupCriterionCustomizer,
)
from google.ads.googleads.v20.services.services.ad_group_criterion_customizer_service import (
    AdGroupCriterionCustomizerServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_customizer_service import (
    AdGroupCriterionCustomizerOperation,
    MutateAdGroupCriterionCustomizersRequest,
    MutateAdGroupCriterionCustomizersResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupCriterionCustomizerService:
    """Ad group criterion customizer service for managing customizer values at the criterion level."""

    def __init__(self) -> None:
        """Initialize the ad group criterion customizer service."""
        self._client: Optional[AdGroupCriterionCustomizerServiceClient] = None

    @property
    def client(self) -> AdGroupCriterionCustomizerServiceClient:
        """Get the ad group criterion customizer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "AdGroupCriterionCustomizerService"
            )
        assert self._client is not None
        return self._client

    async def mutate_ad_group_criterion_customizers(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> Dict[str, Any]:
        """Create or remove ad group criterion customizers.

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
                operation = AdGroupCriterionCustomizerOperation()

                if "create" in op:
                    create_data = op["create"]
                    customizer = AdGroupCriterionCustomizer()

                    if "ad_group_criterion" in create_data:
                        customizer.ad_group_criterion = create_data[
                            "ad_group_criterion"
                        ]

                    if "customizer_attribute" in create_data:
                        customizer.customizer_attribute = create_data[
                            "customizer_attribute"
                        ]

                    if "value" in create_data:
                        value_data = create_data["value"]
                        customizer_value = CustomizerValue()

                        if "type" in value_data and "value" in value_data:
                            value_type = value_data["type"].upper()
                            # Set the type enum
                            customizer_value.type_ = getattr(
                                CustomizerAttributeTypeEnum.CustomizerAttributeType,
                                value_type,
                            )
                            # All values are stored as strings
                            customizer_value.string_value = str(value_data["value"])

                        customizer.value = customizer_value

                    operation.create = customizer

                elif "remove" in op:
                    operation.remove = op["remove"]

                mutate_operations.append(operation)

            # Create request
            request = MutateAdGroupCriterionCustomizersRequest()
            request.customer_id = customer_id
            request.operations = mutate_operations
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = getattr(
                ResponseContentTypeEnum.ResponseContentType,
                response_content_type,
            )

            # Make the API call
            response: MutateAdGroupCriterionCustomizersResponse = (
                self.client.mutate_ad_group_criterion_customizers(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate ad group criterion customizers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_criterion_customizer_tools(
    service: AdGroupCriterionCustomizerService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group criterion customizer service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def mutate_ad_group_criterion_customizers(
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> Dict[str, Any]:
        """Create or remove ad group criterion customizers for dynamic ad customization.

        Args:
            customer_id: The customer ID
            operations: List of operations to perform. Each operation should have either:
                - create: Dict with ad_group_criterion, customizer_attribute, and value
                - remove: Resource name to remove
            partial_failure: Whether to allow partial failures
            validate_only: Whether to only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Mutation results with resource names and any errors
        """
        return await service.mutate_ad_group_criterion_customizers(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([mutate_ad_group_criterion_customizers])
    return tools


def register_ad_group_criterion_customizer_tools(
    mcp: FastMCP[Any],
) -> AdGroupCriterionCustomizerService:
    """Register ad group criterion customizer tools with the MCP server.

    Returns the AdGroupCriterionCustomizerService instance for testing purposes.
    """
    service = AdGroupCriterionCustomizerService()
    tools = create_ad_group_criterion_customizer_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
