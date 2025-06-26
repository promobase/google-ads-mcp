"""Customizer attribute service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.customizer_attribute_status import (
    CustomizerAttributeStatusEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.resources.types.customizer_attribute import (
    CustomizerAttribute,
)
from google.ads.googleads.v20.services.services.customizer_attribute_service import (
    CustomizerAttributeServiceClient,
)
from google.ads.googleads.v20.services.types.customizer_attribute_service import (
    CustomizerAttributeOperation,
    MutateCustomizerAttributesRequest,
    MutateCustomizerAttributesResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomizerAttributeService:
    """Customizer attribute service for managing ad customizers."""

    def __init__(self) -> None:
        """Initialize the customizer attribute service."""
        self._client: Optional[CustomizerAttributeServiceClient] = None

    @property
    def client(self) -> CustomizerAttributeServiceClient:
        """Get the customizer attribute service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomizerAttributeService")
        assert self._client is not None
        return self._client

    async def create_customizer_attribute(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        attribute_type: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a customizer attribute.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name of the customizer attribute
            attribute_type: Type of attribute (TEXT, NUMBER, PRICE, PERCENT)
            status: Attribute status (ENABLED, REMOVED)

        Returns:
            Created customizer attribute details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customizer attribute
            attribute = CustomizerAttribute()
            attribute.name = name
            attribute.type_ = getattr(
                CustomizerAttributeTypeEnum.CustomizerAttributeType, attribute_type
            )
            attribute.status = getattr(
                CustomizerAttributeStatusEnum.CustomizerAttributeStatus, status
            )

            # Create operation
            operation = CustomizerAttributeOperation()
            operation.create = attribute

            # Create request
            request = MutateCustomizerAttributesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCustomizerAttributesResponse = (
                self.client.mutate_customizer_attributes(request=request)
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customizer attribute: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_customizer_attribute(
        self,
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a customizer attribute.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to update
            status: Optional new status (ENABLED, REMOVED)

        Returns:
            Updated customizer attribute details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customizer attribute with resource name
            attribute = CustomizerAttribute()
            attribute.resource_name = attribute_resource_name

            # Build update mask
            update_mask_paths = []

            if status is not None:
                attribute.status = getattr(
                    CustomizerAttributeStatusEnum.CustomizerAttributeStatus, status
                )
                update_mask_paths.append("status")

            # Create operation
            operation = CustomizerAttributeOperation()
            operation.update = attribute
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateCustomizerAttributesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_customizer_attributes(request=request)

            await ctx.log(
                level="info",
                message="Updated customizer attribute",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update customizer attribute: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_customizer_attributes(
        self,
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List customizer attributes.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            include_removed: Whether to include removed attributes

        Returns:
            List of customizer attributes
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    customizer_attribute.resource_name,
                    customizer_attribute.id,
                    customizer_attribute.name,
                    customizer_attribute.type,
                    customizer_attribute.status
                FROM customizer_attribute
            """

            if not include_removed:
                query += " WHERE customizer_attribute.status != 'REMOVED'"

            query += " ORDER BY customizer_attribute.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            attributes = []
            for row in response:
                attribute = row.customizer_attribute

                attribute_dict = {
                    "resource_name": attribute.resource_name,
                    "id": str(attribute.id),
                    "name": attribute.name,
                    "type": attribute.type_.name if attribute.type_ else "UNKNOWN",
                    "status": attribute.status.name if attribute.status else "UNKNOWN",
                }

                attributes.append(attribute_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(attributes)} customizer attributes",
            )

            return attributes

        except Exception as e:
            error_msg = f"Failed to list customizer attributes: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_customizer_attribute(
        self,
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a customizer attribute.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CustomizerAttributeOperation()
            operation.remove = attribute_resource_name

            # Create request
            request = MutateCustomizerAttributesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_customizer_attributes(request=request)

            await ctx.log(
                level="info",
                message="Removed customizer attribute",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove customizer attribute: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customizer_attribute_tools(
    service: CustomizerAttributeService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customizer attribute service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customizer_attribute(
        ctx: Context,
        customer_id: str,
        name: str,
        attribute_type: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a customizer attribute for ad customization.

        Args:
            customer_id: The customer ID
            name: Name of the customizer attribute (will be used in ad text placeholders)
            attribute_type: Type of attribute - TEXT, NUMBER, PRICE, or PERCENT
            status: Attribute status - ENABLED or REMOVED

        Returns:
            Created customizer attribute details with resource_name and attribute_id
        """
        return await service.create_customizer_attribute(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            attribute_type=attribute_type,
            status=status,
        )

    async def update_customizer_attribute(
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a customizer attribute.

        Args:
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to update
            status: Optional new status (ENABLED, REMOVED)

        Returns:
            Updated customizer attribute details with list of updated fields
        """
        return await service.update_customizer_attribute(
            ctx=ctx,
            customer_id=customer_id,
            attribute_resource_name=attribute_resource_name,
            status=status,
        )

    async def list_customizer_attributes(
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List customizer attributes.

        Args:
            customer_id: The customer ID
            include_removed: Whether to include removed attributes

        Returns:
            List of customizer attributes with details
        """
        return await service.list_customizer_attributes(
            ctx=ctx,
            customer_id=customer_id,
            include_removed=include_removed,
        )

    async def remove_customizer_attribute(
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a customizer attribute.

        Args:
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to remove

        Returns:
            Removal result with status
        """
        return await service.remove_customizer_attribute(
            ctx=ctx,
            customer_id=customer_id,
            attribute_resource_name=attribute_resource_name,
        )

    tools.extend(
        [
            create_customizer_attribute,
            update_customizer_attribute,
            list_customizer_attributes,
            remove_customizer_attribute,
        ]
    )
    return tools


def register_customizer_attribute_tools(
    mcp: FastMCP[Any],
) -> CustomizerAttributeService:
    """Register customizer attribute tools with the MCP server.

    Returns the CustomizerAttributeService instance for testing purposes.
    """
    service = CustomizerAttributeService()
    tools = create_customizer_attribute_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
