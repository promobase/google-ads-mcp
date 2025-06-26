"""Custom interest service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.custom_interest_member_type import (
    CustomInterestMemberTypeEnum,
)
from google.ads.googleads.v20.enums.types.custom_interest_status import (
    CustomInterestStatusEnum,
)
from google.ads.googleads.v20.enums.types.custom_interest_type import (
    CustomInterestTypeEnum,
)
from google.ads.googleads.v20.resources.types.custom_interest import (
    CustomInterest,
    CustomInterestMember,
)
from google.ads.googleads.v20.services.services.custom_interest_service import (
    CustomInterestServiceClient,
)
from google.ads.googleads.v20.services.types.custom_interest_service import (
    CustomInterestOperation,
    MutateCustomInterestsRequest,
    MutateCustomInterestsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomInterestService:
    """Custom interest service for managing custom affinity audiences."""

    def __init__(self) -> None:
        """Initialize the custom interest service."""
        self._client: Optional[CustomInterestServiceClient] = None

    @property
    def client(self) -> CustomInterestServiceClient:
        """Get the custom interest service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomInterestService")
        assert self._client is not None
        return self._client

    async def create_custom_interest(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        members: List[Dict[str, str]],
        type_: str = "CUSTOM_AFFINITY",
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new custom interest (custom affinity audience).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The custom interest name
            description: Description of the custom interest
            members: List of members with type and value
                Example: [
                    {"type": "KEYWORD", "value": "running shoes"},
                    {"type": "URL", "value": "example.com/shoes"}
                ]
            type_: Type - CUSTOM_AFFINITY or CUSTOM_INTENT
            status: Status - ENABLED or REMOVED

        Returns:
            Created custom interest details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create custom interest
            custom_interest = CustomInterest()
            custom_interest.name = name
            custom_interest.description = description
            custom_interest.type_ = getattr(
                CustomInterestTypeEnum.CustomInterestType, type_
            )
            custom_interest.status = getattr(
                CustomInterestStatusEnum.CustomInterestStatus, status
            )

            # Add members
            for member in members:
                member_type = getattr(
                    CustomInterestMemberTypeEnum.CustomInterestMemberType,
                    member["type"],
                )

                ci_member = CustomInterestMember()
                ci_member.member_type = member_type

                if (
                    member_type
                    == CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
                ):
                    ci_member.keyword = member["value"]
                elif (
                    member_type
                    == CustomInterestMemberTypeEnum.CustomInterestMemberType.URL
                ):
                    ci_member.url = member["value"]

                custom_interest.members.append(ci_member)

            # Create operation
            operation = CustomInterestOperation()
            operation.create = custom_interest

            # Create request
            request = MutateCustomInterestsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCustomInterestsResponse = (
                self.client.mutate_custom_interests(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created custom interest '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create custom interest: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_custom_interest(
        self,
        ctx: Context,
        customer_id: str,
        custom_interest_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[Dict[str, str]]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing custom interest.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            custom_interest_id: The custom interest ID to update
            name: New name (optional)
            description: New description (optional)
            members: New list of members (optional, replaces existing)
            status: New status (optional)

        Returns:
            Updated custom interest details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/customInterests/{custom_interest_id}"
            )

            # Create custom interest with resource name
            custom_interest = CustomInterest()
            custom_interest.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                custom_interest.name = name
                update_mask_fields.append("name")

            if description is not None:
                custom_interest.description = description
                update_mask_fields.append("description")

            if status is not None:
                custom_interest.status = getattr(
                    CustomInterestStatusEnum.CustomInterestStatus, status
                )
                update_mask_fields.append("status")

            if members is not None:
                # Clear and add new members
                custom_interest.members.clear()
                for member in members:
                    member_type = getattr(
                        CustomInterestMemberTypeEnum.CustomInterestMemberType,
                        member["type"],
                    )

                    ci_member = CustomInterestMember()
                    ci_member.member_type = member_type

                    if (
                        member_type
                        == CustomInterestMemberTypeEnum.CustomInterestMemberType.KEYWORD
                    ):
                        ci_member.keyword = member["value"]
                    elif (
                        member_type
                        == CustomInterestMemberTypeEnum.CustomInterestMemberType.URL
                    ):
                        ci_member.url = member["value"]

                    custom_interest.members.append(ci_member)
                update_mask_fields.append("members")

            # Create operation
            operation = CustomInterestOperation()
            operation.update = custom_interest
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateCustomInterestsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_custom_interests(request=request)

            await ctx.log(
                level="info",
                message=f"Updated custom interest {custom_interest_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update custom interest: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_custom_interests(
        self,
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all custom interests in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            type_filter: Optional filter by type (CUSTOM_AFFINITY or CUSTOM_INTENT)
            status_filter: Optional filter by status (ENABLED or REMOVED)

        Returns:
            List of custom interests
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    custom_interest.id,
                    custom_interest.name,
                    custom_interest.description,
                    custom_interest.type,
                    custom_interest.status,
                    custom_interest.resource_name
                FROM custom_interest
            """

            conditions = []
            if type_filter:
                conditions.append(f"custom_interest.type = '{type_filter}'")
            if status_filter:
                conditions.append(f"custom_interest.status = '{status_filter}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY custom_interest.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            custom_interests = []
            for row in response:
                ci = row.custom_interest
                custom_interests.append(
                    {
                        "custom_interest_id": str(ci.id),
                        "name": ci.name,
                        "description": ci.description,
                        "type": ci.type_.name if ci.type_ else "UNKNOWN",
                        "status": ci.status.name if ci.status else "UNKNOWN",
                        "resource_name": ci.resource_name,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Found {len(custom_interests)} custom interests",
            )

            return custom_interests

        except Exception as e:
            error_msg = f"Failed to list custom interests: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_custom_interest_details(
        self,
        ctx: Context,
        customer_id: str,
        custom_interest_id: str,
    ) -> Dict[str, Any]:
        """Get detailed information about a custom interest including members.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            custom_interest_id: The custom interest ID

        Returns:
            Custom interest details with members
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = f"""
                SELECT
                    custom_interest.id,
                    custom_interest.name,
                    custom_interest.description,
                    custom_interest.type,
                    custom_interest.status,
                    custom_interest.members,
                    custom_interest.resource_name
                FROM custom_interest
                WHERE custom_interest.id = {custom_interest_id}
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process result
            for row in response:
                ci = row.custom_interest

                # Process members
                members = []
                for member in ci.members:
                    member_dict = {
                        "type": member.member_type.name
                        if member.member_type
                        else "UNKNOWN"
                    }
                    if member.HasField("keyword"):
                        member_dict["value"] = member.keyword
                    elif member.HasField("url"):
                        member_dict["value"] = member.url
                    members.append(member_dict)

                await ctx.log(
                    level="info",
                    message=f"Retrieved details for custom interest {custom_interest_id}",
                )

            return serialize_proto_message(response)

        except Exception as e:
            error_msg = f"Failed to get custom interest details: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_custom_interest_tools(
    service: CustomInterestService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the custom interest service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_custom_interest(
        ctx: Context,
        customer_id: str,
        name: str,
        description: str,
        members: List[Dict[str, str]],
        type_: str = "CUSTOM_AFFINITY",
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new custom interest (custom affinity/intent audience).

        Args:
            customer_id: The customer ID
            name: The custom interest name
            description: Description of the custom interest
            members: List of audience members, each with type and value
                Example: [
                    {"type": "KEYWORD", "value": "running shoes"},
                    {"type": "URL", "value": "example.com/shoes"}
                ]
            type_: Type of custom interest:
                - CUSTOM_AFFINITY: For reaching users with specific interests
                - CUSTOM_INTENT: For reaching users actively researching
            status: Status - ENABLED or REMOVED

        Returns:
            Created custom interest details with resource_name and custom_interest_id
        """
        return await service.create_custom_interest(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            members=members,
            type_=type_,
            status=status,
        )

    async def update_custom_interest(
        ctx: Context,
        customer_id: str,
        custom_interest_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        members: Optional[List[Dict[str, str]]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing custom interest.

        Args:
            customer_id: The customer ID
            custom_interest_id: The custom interest ID to update
            name: New name (optional)
            description: New description (optional)
            members: New list of members - replaces existing (optional)
            status: New status - ENABLED or REMOVED (optional)

        Returns:
            Updated custom interest details with updated_fields list
        """
        return await service.update_custom_interest(
            ctx=ctx,
            customer_id=customer_id,
            custom_interest_id=custom_interest_id,
            name=name,
            description=description,
            members=members,
            status=status,
        )

    async def list_custom_interests(
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all custom interests in the account.

        Args:
            customer_id: The customer ID
            type_filter: Optional filter - CUSTOM_AFFINITY or CUSTOM_INTENT
            status_filter: Optional filter - ENABLED or REMOVED

        Returns:
            List of custom interests with basic details
        """
        return await service.list_custom_interests(
            ctx=ctx,
            customer_id=customer_id,
            type_filter=type_filter,
            status_filter=status_filter,
        )

    async def get_custom_interest_details(
        ctx: Context,
        customer_id: str,
        custom_interest_id: str,
    ) -> Dict[str, Any]:
        """Get detailed information about a custom interest including all members.

        Args:
            customer_id: The customer ID
            custom_interest_id: The custom interest ID

        Returns:
            Complete custom interest details including all members
        """
        return await service.get_custom_interest_details(
            ctx=ctx,
            customer_id=customer_id,
            custom_interest_id=custom_interest_id,
        )

    tools.extend(
        [
            create_custom_interest,
            update_custom_interest,
            list_custom_interests,
            get_custom_interest_details,
        ]
    )
    return tools


def register_custom_interest_tools(mcp: FastMCP[Any]) -> CustomInterestService:
    """Register custom interest tools with the MCP server.

    Returns the CustomInterestService instance for testing purposes.
    """
    service = CustomInterestService()
    tools = create_custom_interest_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
