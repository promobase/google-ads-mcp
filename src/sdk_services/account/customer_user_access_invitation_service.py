"""Customer user access invitation service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.customer_user_access_invitation_service import (
    CustomerUserAccessInvitationServiceClient,
)
from google.ads.googleads.v20.services.types.customer_user_access_invitation_service import (
    MutateCustomerUserAccessInvitationRequest,
    MutateCustomerUserAccessInvitationResponse,
    CustomerUserAccessInvitationOperation,
)
from google.ads.googleads.v20.resources.types.customer_user_access_invitation import (
    CustomerUserAccessInvitation,
)
from google.ads.googleads.v20.enums.types.access_role import (
    AccessRoleEnum,
)

from google.ads.googleads.errors import GoogleAdsException

from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerUserAccessInvitationService:
    """Customer user access invitation service for managing user access invitations."""

    def __init__(self) -> None:
        """Initialize the customer user access invitation service."""
        self._client: Optional[CustomerUserAccessInvitationServiceClient] = None

    @property
    def client(self) -> CustomerUserAccessInvitationServiceClient:
        """Get the customer user access invitation service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CustomerUserAccessInvitationService"
            )
        assert self._client is not None
        return self._client

    async def create_customer_user_access_invitation(
        self,
        ctx: Context,
        customer_id: str,
        email_address: str,
        access_role: str,
    ) -> Dict[str, Any]:
        """Create a customer user access invitation to invite a new user.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            email_address: Email address to send the invitation to
            access_role: Access role for the user (ADMIN, STANDARD, READ_ONLY, EMAIL_ONLY)

        Returns:
            Created customer user access invitation details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customer user access invitation
            invitation = CustomerUserAccessInvitation()
            invitation.email_address = email_address
            invitation.access_role = getattr(AccessRoleEnum.AccessRole, access_role)

            # Create operation
            operation = CustomerUserAccessInvitationOperation()
            operation.create = invitation

            # Create request
            request = MutateCustomerUserAccessInvitationRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateCustomerUserAccessInvitationResponse = (
                self.client.mutate_customer_user_access_invitation(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created customer user access invitation for: {email_address}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer user access invitation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_customer_user_access_invitations(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List customer user access invitations for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            status_filter: Optional status filter (PENDING, DECLINED, EXPIRED)

        Returns:
            List of customer user access invitations
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
                    customer_user_access_invitation.resource_name,
                    customer_user_access_invitation.invitation_id,
                    customer_user_access_invitation.access_role,
                    customer_user_access_invitation.email_address,
                    customer_user_access_invitation.creation_date_time,
                    customer_user_access_invitation.invitation_status
                FROM customer_user_access_invitation
            """

            if status_filter:
                query += f" WHERE customer_user_access_invitation.invitation_status = '{status_filter}'"

            query += " ORDER BY customer_user_access_invitation.creation_date_time DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            invitations = []
            for row in response:
                invitation = row.customer_user_access_invitation

                invitation_dict = {
                    "resource_name": invitation.resource_name,
                    "invitation_id": str(invitation.invitation_id),
                    "access_role": invitation.access_role.name
                    if invitation.access_role
                    else "UNKNOWN",
                    "email_address": invitation.email_address,
                    "creation_date_time": invitation.creation_date_time,
                    "invitation_status": invitation.invitation_status.name
                    if invitation.invitation_status
                    else "UNKNOWN",
                }

                invitations.append(invitation_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(invitations)} customer user access invitations",
            )

            return invitations

        except Exception as e:
            error_msg = f"Failed to list customer user access invitations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_customer_user_access_invitation(
        self,
        ctx: Context,
        customer_id: str,
        invitation_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove (revoke) a customer user access invitation.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            invitation_resource_name: Resource name of the invitation to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CustomerUserAccessInvitationOperation()
            operation.remove = invitation_resource_name

            # Create request
            request = MutateCustomerUserAccessInvitationRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_customer_user_access_invitation(
                request=request
            )

            await ctx.log(
                level="info",
                message="Removed customer user access invitation",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove customer user access invitation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_user_access_invitation_tools(
    service: CustomerUserAccessInvitationService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer user access invitation service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customer_user_access_invitation(
        ctx: Context,
        customer_id: str,
        email_address: str,
        access_role: str,
    ) -> Dict[str, Any]:
        """Create a customer user access invitation to invite a new user to the account.

        Args:
            customer_id: The customer ID
            email_address: Email address to send the invitation to
            access_role: Access role for the user (ADMIN, STANDARD, READ_ONLY, EMAIL_ONLY)

        Returns:
            Created customer user access invitation details with resource_name
        """
        return await service.create_customer_user_access_invitation(
            ctx=ctx,
            customer_id=customer_id,
            email_address=email_address,
            access_role=access_role,
        )

    async def list_customer_user_access_invitations(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List customer user access invitations for a customer.

        Args:
            customer_id: The customer ID
            status_filter: Optional status filter (PENDING, DECLINED, EXPIRED)

        Returns:
            List of customer user access invitations with details including status and email
        """
        return await service.list_customer_user_access_invitations(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    async def remove_customer_user_access_invitation(
        ctx: Context,
        customer_id: str,
        invitation_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove (revoke) a customer user access invitation.

        Args:
            customer_id: The customer ID
            invitation_resource_name: Resource name of the invitation to remove

        Returns:
            Removal result with status
        """
        return await service.remove_customer_user_access_invitation(
            ctx=ctx,
            customer_id=customer_id,
            invitation_resource_name=invitation_resource_name,
        )

    tools.extend(
        [
            create_customer_user_access_invitation,
            list_customer_user_access_invitations,
            remove_customer_user_access_invitation,
        ]
    )
    return tools


def register_customer_user_access_invitation_tools(
    mcp: FastMCP[Any],
) -> CustomerUserAccessInvitationService:
    """Register customer user access invitation tools with the MCP server.

    Returns the CustomerUserAccessInvitationService instance for testing purposes.
    """
    service = CustomerUserAccessInvitationService()
    tools = create_customer_user_access_invitation_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
