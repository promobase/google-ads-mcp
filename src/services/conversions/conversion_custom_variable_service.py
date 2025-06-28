"""Conversion Custom Variable service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.conversion_custom_variable_status import (
    ConversionCustomVariableStatusEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.conversion_custom_variable import (
    ConversionCustomVariable,
)
from google.ads.googleads.v20.services.services.conversion_custom_variable_service import (
    ConversionCustomVariableServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_custom_variable_service import (
    ConversionCustomVariableOperation,
    MutateConversionCustomVariablesRequest,
    MutateConversionCustomVariablesResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ConversionCustomVariableService:
    """Service for managing conversion custom variables in Google Ads.

    Custom variables allow you to track additional information with conversions,
    such as product categories, customer types, or other custom dimensions.
    """

    def __init__(self) -> None:
        """Initialize the conversion custom variable service."""
        self._client: Optional[ConversionCustomVariableServiceClient] = None

    @property
    def client(self) -> ConversionCustomVariableServiceClient:
        """Get the conversion custom variable service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ConversionCustomVariableService"
            )
        assert self._client is not None
        return self._client

    async def create_conversion_custom_variable(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        tag: str,
        status: ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus = ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus.ENABLED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
    ) -> Dict[str, Any]:
        """Create a new conversion custom variable.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name of the custom variable (max 100 chars, must be unique)
            tag: Tag used in event snippets (max 100 bytes, lowercase letters/numbers/underscores)
            status: Status of the variable (ENABLED, PAUSED)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing
            response_content_type: What to return in response

        Returns:
            Created custom variable details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create a new conversion custom variable
            custom_variable = ConversionCustomVariable()
            custom_variable.name = name.strip()
            custom_variable.tag = tag.strip().lower()
            custom_variable.status = status

            # Create the operation
            operation = ConversionCustomVariableOperation()
            operation.create = custom_variable

            # Create the request
            request = MutateConversionCustomVariablesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = response_content_type

            # Execute the mutation
            response: MutateConversionCustomVariablesResponse = (
                self.client.mutate_conversion_custom_variables(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created conversion custom variable '{name}' with tag '{tag}' for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create conversion custom variable: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_conversion_custom_variable(
        self,
        ctx: Context,
        customer_id: str,
        custom_variable_id: int,
        name: Optional[str] = None,
        status: Optional[
            ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus
        ] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
    ) -> Dict[str, Any]:
        """Update an existing conversion custom variable.

        Note: The tag field is immutable and cannot be updated.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            custom_variable_id: ID of the custom variable to update
            name: New name (optional)
            status: New status (optional)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing
            response_content_type: What to return in response

        Returns:
            Updated custom variable details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/conversionCustomVariables/{custom_variable_id}"

            # Create custom variable with resource name
            custom_variable = ConversionCustomVariable()
            custom_variable.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                custom_variable.name = name.strip()
                update_mask_fields.append("name")

            if status is not None:
                custom_variable.status = status
                update_mask_fields.append("status")

            if not update_mask_fields:
                raise ValueError("At least one field must be specified for update")

            # Create the operation
            operation = ConversionCustomVariableOperation()
            operation.update = custom_variable
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateConversionCustomVariablesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = response_content_type

            # Execute the mutation
            response = self.client.mutate_conversion_custom_variables(request=request)

            await ctx.log(
                level="info",
                message=f"Updated conversion custom variable {custom_variable_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update conversion custom variable: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_custom_variable_tools(
    service: ConversionCustomVariableService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion custom variable service."""
    tools = []

    async def create_conversion_custom_variable(
        ctx: Context,
        customer_id: str,
        name: str,
        tag: str,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a new conversion custom variable for tracking additional conversion data.

        Custom variables allow you to segment and analyze conversions with custom dimensions
        like product categories, customer types, or other business-specific attributes.

        Args:
            customer_id: The customer ID
            name: Name of the custom variable (max 100 chars, must be unique)
            tag: Tag used in event snippets (max 100 bytes, lowercase letters/numbers/underscores only)
            status: Status of the variable - ENABLED or PAUSED (default: ENABLED)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created custom variable details including resource_name and id

        Example:
            result = await create_conversion_custom_variable(
                customer_id="1234567890",
                name="Product Category",
                tag="product_category",
                status="ENABLED"
            )
        """
        # Convert string enum to proper enum type
        status_enum = getattr(
            ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus, status
        )

        return await service.create_conversion_custom_variable(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            tag=tag,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def update_conversion_custom_variable(
        ctx: Context,
        customer_id: str,
        custom_variable_id: int,
        name: Optional[str] = None,
        status: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update an existing conversion custom variable.

        Note: The tag field is immutable and cannot be changed after creation.

        Args:
            customer_id: The customer ID
            custom_variable_id: ID of the custom variable to update
            name: New name (optional, max 100 chars)
            status: New status - ENABLED or PAUSED (optional)
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Updated custom variable details

        Example:
            result = await update_conversion_custom_variable(
                customer_id="1234567890",
                custom_variable_id=123456,
                name="Updated Product Category",
                status="PAUSED"
            )
        """
        # Convert string enum to proper enum type if provided
        status_enum = None
        if status is not None:
            status_enum = getattr(
                ConversionCustomVariableStatusEnum.ConversionCustomVariableStatus,
                status,
            )

        return await service.update_conversion_custom_variable(
            ctx=ctx,
            customer_id=customer_id,
            custom_variable_id=custom_variable_id,
            name=name,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.extend([create_conversion_custom_variable, update_conversion_custom_variable])
    return tools


def register_conversion_custom_variable_tools(
    mcp: FastMCP[Any],
) -> ConversionCustomVariableService:
    """Register conversion custom variable tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = ConversionCustomVariableService()
    tools = create_conversion_custom_variable_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
