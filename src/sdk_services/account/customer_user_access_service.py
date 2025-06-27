"""Customer user access service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.access_role import AccessRoleEnum
from google.ads.googleads.v20.resources.types.customer_user_access import (
    CustomerUserAccess,
)
from google.ads.googleads.v20.services.services.customer_user_access_service import (
    CustomerUserAccessServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.customer_user_access_service import (
    CustomerUserAccessOperation,
    MutateCustomerUserAccessRequest,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerUserAccessService:
    """Customer user access service for managing user permissions."""

    def __init__(self) -> None:
        """Initialize the customer user access service."""
        self._client: Optional[CustomerUserAccessServiceClient] = None

    @property
    def client(self) -> CustomerUserAccessServiceClient:
        """Get the customer user access service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerUserAccessService")
        assert self._client is not None
        return self._client

    # Note: CustomerUserAccessService does not support creating new access.
    # To grant access to new users, use CustomerUserAccessInvitationService instead.
    # This service only supports updating and removing existing user access.

    async def update_user_access(
        self,
        ctx: Context,
        customer_id: str,
        user_access_resource_name: str,
        access_role: Optional[AccessRoleEnum.AccessRole] = None,
    ) -> Dict[str, Any]:
        """Update user access permissions.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_access_resource_name: Resource name of the user access to update
            access_role: Optional new access role enum value

        Returns:
            Updated user access details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customer user access with resource name
            user_access = CustomerUserAccess()
            user_access.resource_name = user_access_resource_name

            # Build update mask
            update_mask_paths = []

            if access_role is not None:
                user_access.access_role = access_role
                update_mask_paths.append("access_role")

            # Create operation
            operation = CustomerUserAccessOperation()
            operation.update = user_access
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateCustomerUserAccessRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_customer_user_access(request=request)

            await ctx.log(
                level="info",
                message="Updated user access permissions",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update user access: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_user_access(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List user access for a customer account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of user access permissions
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
                    customer_user_access.resource_name,
                    customer_user_access.user_id,
                    customer_user_access.email_address,
                    customer_user_access.access_role,
                    customer_user_access.access_creation_date_time,
                    customer_user_access.inviter_user_email_address
                FROM customer_user_access
                ORDER BY customer_user_access.email_address
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            user_accesses = []
            for row in response:
                user_access = row.customer_user_access
                user_accesses.append(serialize_proto_message(user_access))

            await ctx.log(
                level="info",
                message=f"Found {len(user_accesses)} user access permissions",
            )

            return user_accesses

        except Exception as e:
            error_msg = f"Failed to list user access: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def revoke_user_access(
        self,
        ctx: Context,
        customer_id: str,
        user_access_resource_name: str,
    ) -> Dict[str, Any]:
        """Revoke user access to a customer account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_access_resource_name: Resource name of the user access to revoke

        Returns:
            Revocation result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CustomerUserAccessOperation()
            operation.remove = user_access_resource_name

            # Create request
            request = MutateCustomerUserAccessRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_customer_user_access(request=request)

            await ctx.log(
                level="info",
                message="Revoked user access",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to revoke user access: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_user_access_tools(
    service: CustomerUserAccessService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer user access service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    # Note: grant_user_access is not included because CustomerUserAccessService
    # does not support creating new access. Use CustomerUserAccessInvitationService
    # to send invitations for new user access.

    async def update_user_access(
        ctx: Context,
        customer_id: str,
        user_access_resource_name: str,
        access_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update user access permissions.

        Args:
            customer_id: The customer ID
            user_access_resource_name: Resource name of the user access to update
            access_role: Optional new access role (ADMIN, STANDARD, READ_ONLY, EMAIL_ONLY)

        Returns:
            Updated user access details with list of updated fields
        """
        # Convert string enum to proper enum type if provided
        role_enum = (
            getattr(AccessRoleEnum.AccessRole, access_role) if access_role else None
        )

        return await service.update_user_access(
            ctx=ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
            access_role=role_enum,
        )

    async def list_user_access(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List user access for a customer account.

        Args:
            customer_id: The customer ID

        Returns:
            List of user access permissions with email addresses and roles
        """
        return await service.list_user_access(
            ctx=ctx,
            customer_id=customer_id,
        )

    async def revoke_user_access(
        ctx: Context,
        customer_id: str,
        user_access_resource_name: str,
    ) -> Dict[str, Any]:
        """Revoke user access to a customer account.

        Args:
            customer_id: The customer ID
            user_access_resource_name: Resource name of the user access to revoke

        Returns:
            Revocation result with status
        """
        return await service.revoke_user_access(
            ctx=ctx,
            customer_id=customer_id,
            user_access_resource_name=user_access_resource_name,
        )

    tools.extend(
        [
            update_user_access,
            list_user_access,
            revoke_user_access,
        ]
    )
    return tools


def register_customer_user_access_tools(mcp: FastMCP[Any]) -> CustomerUserAccessService:
    """Register customer user access tools with the MCP server.

    Returns the CustomerUserAccessService instance for testing purposes.
    """
    service = CustomerUserAccessService()
    tools = create_customer_user_access_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
