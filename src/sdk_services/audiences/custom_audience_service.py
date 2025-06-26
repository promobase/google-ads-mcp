"""Custom audience service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.custom_audience_member_type import (
    CustomAudienceMemberTypeEnum,
)
from google.ads.googleads.v20.enums.types.custom_audience_status import (
    CustomAudienceStatusEnum,
)
from google.ads.googleads.v20.enums.types.custom_audience_type import (
    CustomAudienceTypeEnum,
)
from google.ads.googleads.v20.resources.types.custom_audience import (
    CustomAudience,
    CustomAudienceMember,
)
from google.ads.googleads.v20.services.services.custom_audience_service import (
    CustomAudienceServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.custom_audience_service import (
    CustomAudienceOperation,
    MutateCustomAudiencesRequest,
    MutateCustomAudiencesResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomAudienceService:
    """Custom audience service for managing custom segments."""

    def __init__(self) -> None:
        """Initialize the custom audience service."""
        self._client: Optional[CustomAudienceServiceClient] = None

    @property
    def client(self) -> CustomAudienceServiceClient:
        """Get the custom audience service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomAudienceService")
        assert self._client is not None
        return self._client

    async def create_custom_audience(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        members: List[Dict[str, Any]],
        type_: str = "CUSTOM",
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new custom audience (custom segment).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The custom audience name
            description: Description of the custom audience
            members: List of members with type and parameters
                Example: [
                    {"type": "KEYWORD", "keyword": "running shoes"},
                    {"type": "URL", "url": "example.com/shoes"},
                    {"type": "APP", "app": "com.example.app"}
                ]
            type_: Type - CUSTOM, INTEREST, PURCHASE_INTENT, or SEARCH
            status: Status - ENABLED or REMOVED

        Returns:
            Created custom audience details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create custom audience
            custom_audience = CustomAudience()
            custom_audience.name = name
            custom_audience.description = description
            custom_audience.type_ = getattr(
                CustomAudienceTypeEnum.CustomAudienceType, type_
            )
            custom_audience.status = getattr(
                CustomAudienceStatusEnum.CustomAudienceStatus, status
            )

            # Add members
            for member_data in members:
                member = CustomAudienceMember()
                member_type = getattr(
                    CustomAudienceMemberTypeEnum.CustomAudienceMemberType,
                    member_data["type"],
                )
                member.member_type = member_type

                if (
                    member_type
                    == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
                ):
                    member.keyword = member_data.get("keyword", "")
                elif (
                    member_type
                    == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.URL
                ):
                    member.url = member_data.get("url", "")
                elif (
                    member_type
                    == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.PLACE_CATEGORY
                ):
                    member.place_category = member_data.get("place_category", 0)
                elif (
                    member_type
                    == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.APP
                ):
                    member.app = member_data.get("app", "")

                custom_audience.members.append(member)

            # Create operation
            operation = CustomAudienceOperation()
            operation.create = custom_audience

            # Create request
            request = MutateCustomAudiencesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCustomAudiencesResponse = (
                self.client.mutate_custom_audiences(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created custom audience '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create custom audience: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_custom_audience(
        self,
        ctx: Context,
        customer_id: str,
        custom_audience_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[Dict[str, Any]]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing custom audience.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            custom_audience_id: The custom audience ID to update
            name: New name (optional)
            description: New description (optional)
            members: New list of members (optional, replaces existing)
            status: New status (optional)

        Returns:
            Updated custom audience details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/customAudiences/{custom_audience_id}"
            )

            # Create custom audience with resource name
            custom_audience = CustomAudience()
            custom_audience.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                custom_audience.name = name
                update_mask_fields.append("name")

            if description is not None:
                custom_audience.description = description
                update_mask_fields.append("description")

            if status is not None:
                custom_audience.status = getattr(
                    CustomAudienceStatusEnum.CustomAudienceStatus, status
                )
                update_mask_fields.append("status")

            if members is not None:
                # Clear and add new members
                custom_audience.members.clear()
                for member_data in members:
                    member = CustomAudienceMember()
                    member_type = getattr(
                        CustomAudienceMemberTypeEnum.CustomAudienceMemberType,
                        member_data["type"],
                    )
                    member.member_type = member_type

                    if (
                        member_type
                        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.KEYWORD
                    ):
                        member.keyword = member_data.get("keyword", "")
                    elif (
                        member_type
                        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.URL
                    ):
                        member.url = member_data.get("url", "")
                    elif (
                        member_type
                        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.PLACE_CATEGORY
                    ):
                        member.place_category = member_data.get("place_category", 0)
                    elif (
                        member_type
                        == CustomAudienceMemberTypeEnum.CustomAudienceMemberType.APP
                    ):
                        member.app = member_data.get("app", "")

                    custom_audience.members.append(member)
                update_mask_fields.append("members")

            # Create operation
            operation = CustomAudienceOperation()
            operation.update = custom_audience
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateCustomAudiencesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_custom_audiences(request=request)

            await ctx.log(
                level="info",
                message=f"Updated custom audience {custom_audience_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update custom audience: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_custom_audiences(
        self,
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all custom audiences in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            type_filter: Optional filter by type
            status_filter: Optional filter by status (ENABLED or REMOVED)

        Returns:
            List of custom audiences
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    custom_audience.id,
                    custom_audience.name,
                    custom_audience.description,
                    custom_audience.type,
                    custom_audience.status,
                    custom_audience.resource_name
                FROM custom_audience
            """

            conditions = []
            if type_filter:
                conditions.append(f"custom_audience.type = '{type_filter}'")
            if status_filter:
                conditions.append(f"custom_audience.status = '{status_filter}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY custom_audience.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            custom_audiences = []
            for row in response:
                custom_audiences.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(custom_audiences)} custom audiences",
            )

            return custom_audiences

        except Exception as e:
            error_msg = f"Failed to list custom audiences: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_custom_audience_details(
        self,
        ctx: Context,
        customer_id: str,
        custom_audience_id: str,
    ) -> Dict[str, Any]:
        """Get detailed information about a custom audience including members.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            custom_audience_id: The custom audience ID

        Returns:
            Custom audience details with members
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = f"""
                SELECT
                    custom_audience.id,
                    custom_audience.name,
                    custom_audience.description,
                    custom_audience.type,
                    custom_audience.status,
                    custom_audience.members,
                    custom_audience.resource_name
                FROM custom_audience
                WHERE custom_audience.id = {custom_audience_id}
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            return serialize_proto_message(response)

            raise Exception(f"Custom audience {custom_audience_id} not found")

        except Exception as e:
            error_msg = f"Failed to get custom audience details: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_custom_audience_tools(
    service: CustomAudienceService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the custom audience service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_custom_audience(
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        members: List[Dict[str, Any]],
        type_: str = "CUSTOM",
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new custom audience (custom segment).

        Args:
            customer_id: The customer ID
            name: The custom audience name
            description: Description of the custom audience
            members: List of audience members with type-specific parameters
                Examples:
                - {"type": "KEYWORD", "keyword": "running shoes"}
                - {"type": "URL", "url": "example.com/shoes"}
                - {"type": "PLACE_CATEGORY", "place_category": 1234}
                - {"type": "APP", "app": "com.example.app"}
            type_: Type of custom audience:
                - CUSTOM: Standard custom segment
                - INTEREST: Interest-based segment
                - PURCHASE_INTENT: Purchase intent segment
                - SEARCH: Search-based segment
            status: Status - ENABLED or REMOVED

        Returns:
            Created custom audience details with resource_name and custom_audience_id
        """
        return await service.create_custom_audience(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
            type_=type_,
            status=status,
        )

    async def update_custom_audience(
        ctx: Context,
        customer_id: str,
        custom_audience_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[Dict[str, Any]]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing custom audience.

        Args:
            customer_id: The customer ID
            custom_audience_id: The custom audience ID to update
            name: New name (optional)
            description: New description (optional)
            members: New list of members - replaces existing (optional)
            status: New status - ENABLED or REMOVED (optional)

        Returns:
            Updated custom audience details with updated_fields list
        """
        return await service.update_custom_audience(
            ctx=ctx,
            customer_id=customer_id,
            custom_audience_id=custom_audience_id,
            name=name,
            description=description,
            members=members,
            status=status,
        )

    async def list_custom_audiences(
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all custom audiences in the account.

        Args:
            customer_id: The customer ID
            type_filter: Optional filter by type
            status_filter: Optional filter - ENABLED or REMOVED

        Returns:
            List of custom audiences with basic details
        """
        return await service.list_custom_audiences(
            ctx=ctx,
            customer_id=customer_id,
            type_filter=type_filter,
            status_filter=status_filter,
        )

    async def get_custom_audience_details(
        ctx: Context,
        customer_id: str,
        custom_audience_id: str,
    ) -> Dict[str, Any]:
        """Get detailed information about a custom audience including all members.

        Args:
            customer_id: The customer ID
            custom_audience_id: The custom audience ID

        Returns:
            Complete custom audience details including all members
        """
        return await service.get_custom_audience_details(
            ctx=ctx,
            customer_id=customer_id,
            custom_audience_id=custom_audience_id,
        )

    tools.extend(
        [
            create_custom_audience,
            update_custom_audience,
            list_custom_audiences,
            get_custom_audience_details,
        ]
    )
    return tools


def register_custom_audience_tools(mcp: FastMCP[Any]) -> CustomAudienceService:
    """Register custom audience tools with the MCP server.

    Returns the CustomAudienceService instance for testing purposes.
    """
    service = CustomAudienceService()
    tools = create_custom_audience_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
