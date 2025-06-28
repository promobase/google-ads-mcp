"""Customer Manager Link service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.manager_link_status import (
    ManagerLinkStatusEnum,
)
from google.ads.googleads.v20.resources.types.customer_manager_link import (
    CustomerManagerLink,
)
from google.ads.googleads.v20.services.services.customer_manager_link_service import (
    CustomerManagerLinkServiceClient,
)
from google.ads.googleads.v20.services.types.customer_manager_link_service import (
    CustomerManagerLinkOperation,
    MoveManagerLinkRequest,
    MoveManagerLinkResponse,
    MutateCustomerManagerLinkRequest,
    MutateCustomerManagerLinkResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerManagerLinkService:
    """Service for managing customer-manager relationships in Google Ads."""

    def __init__(self) -> None:
        """Initialize the customer manager link service."""
        self._client: Optional[CustomerManagerLinkServiceClient] = None

    @property
    def client(self) -> CustomerManagerLinkServiceClient:
        """Get the customer manager link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerManagerLinkService")
        assert self._client is not None
        return self._client

    async def update_manager_link_status(
        self,
        ctx: Context,
        customer_id: str,
        manager_customer_id: str,
        manager_link_id: int,
        status: ManagerLinkStatusEnum.ManagerLinkStatus,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update the status of a customer-manager link.

        This can be used to:
        - Accept a pending invitation (status=ACTIVE)
        - Decline a pending invitation (status=REFUSED)
        - Terminate an existing link (status=INACTIVE)

        Args:
            ctx: FastMCP context
            customer_id: The client customer ID
            manager_customer_id: The manager customer ID
            manager_link_id: The link ID
            status: New status (ACTIVE, REFUSED, INACTIVE)
            validate_only: If true, only validates without executing

        Returns:
            Updated link details
        """
        try:
            customer_id = format_customer_id(customer_id)
            manager_customer_id = format_customer_id(manager_customer_id)

            # Create resource name
            resource_name = (
                f"customers/{customer_id}/customerManagerLinks/"
                f"{manager_customer_id}~{manager_link_id}"
            )

            # Create the link with updated status
            link = CustomerManagerLink()
            link.resource_name = resource_name
            link.status = status

            # Create the operation
            operation = CustomerManagerLinkOperation()
            operation.update = link
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create the request
            request = MutateCustomerManagerLinkRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            # Execute the mutation
            response: MutateCustomerManagerLinkResponse = (
                self.client.mutate_customer_manager_link(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated manager link status to {status.name} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update manager link status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def move_manager_link(
        self,
        ctx: Context,
        customer_id: str,
        previous_manager_customer_id: str,
        previous_manager_link_id: int,
        new_manager_customer_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Move a client from one manager to another.

        Args:
            ctx: FastMCP context
            customer_id: The client customer ID being moved
            previous_manager_customer_id: Current manager's customer ID
            previous_manager_link_id: Current link ID
            new_manager_customer_id: New manager's customer ID
            validate_only: If true, only validates without executing

        Returns:
            New manager link details
        """
        try:
            customer_id = format_customer_id(customer_id)
            previous_manager_customer_id = format_customer_id(
                previous_manager_customer_id
            )
            new_manager_customer_id = format_customer_id(new_manager_customer_id)

            # Create previous link resource name
            previous_link = (
                f"customers/{customer_id}/customerManagerLinks/"
                f"{previous_manager_customer_id}~{previous_manager_link_id}"
            )

            # Create new manager resource name
            new_manager = f"customers/{new_manager_customer_id}"

            # Create the request
            request = MoveManagerLinkRequest()
            request.customer_id = customer_id
            request.previous_customer_manager_link = previous_link
            request.new_manager = new_manager
            request.validate_only = validate_only

            # Execute the move
            response: MoveManagerLinkResponse = self.client.move_manager_link(
                request=request
            )

            await ctx.log(
                level="info",
                message=(
                    f"Moved customer {customer_id} from manager "
                    f"{previous_manager_customer_id} to {new_manager_customer_id}"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to move manager link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_manager_link_tools(
    service: CustomerManagerLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer manager link service."""
    tools = []

    async def accept_manager_invitation(
        ctx: Context,
        customer_id: str,
        manager_customer_id: str,
        manager_link_id: int,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Accept a pending manager invitation.

        Args:
            customer_id: The client customer ID
            manager_customer_id: The manager customer ID
            manager_link_id: The link ID from the invitation
            validate_only: If true, only validates without executing

        Returns:
            Updated link details
        """
        return await service.update_manager_link_status(
            ctx=ctx,
            customer_id=customer_id,
            manager_customer_id=manager_customer_id,
            manager_link_id=manager_link_id,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.ACTIVE,
            validate_only=validate_only,
        )

    async def decline_manager_invitation(
        ctx: Context,
        customer_id: str,
        manager_customer_id: str,
        manager_link_id: int,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Decline a pending manager invitation.

        Args:
            customer_id: The client customer ID
            manager_customer_id: The manager customer ID
            manager_link_id: The link ID from the invitation
            validate_only: If true, only validates without executing

        Returns:
            Updated link details
        """
        return await service.update_manager_link_status(
            ctx=ctx,
            customer_id=customer_id,
            manager_customer_id=manager_customer_id,
            manager_link_id=manager_link_id,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.REFUSED,
            validate_only=validate_only,
        )

    async def terminate_manager_link(
        ctx: Context,
        customer_id: str,
        manager_customer_id: str,
        manager_link_id: int,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Terminate an existing manager-client relationship.

        Args:
            customer_id: The client customer ID
            manager_customer_id: The manager customer ID
            manager_link_id: The link ID
            validate_only: If true, only validates without executing

        Returns:
            Updated link details
        """
        return await service.update_manager_link_status(
            ctx=ctx,
            customer_id=customer_id,
            manager_customer_id=manager_customer_id,
            manager_link_id=manager_link_id,
            status=ManagerLinkStatusEnum.ManagerLinkStatus.INACTIVE,
            validate_only=validate_only,
        )

    async def move_client_to_new_manager(
        ctx: Context,
        customer_id: str,
        previous_manager_customer_id: str,
        previous_manager_link_id: int,
        new_manager_customer_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Move a client from one manager account to another.

        Args:
            customer_id: The client customer ID being moved
            previous_manager_customer_id: Current manager's customer ID
            previous_manager_link_id: Current link ID
            new_manager_customer_id: New manager's customer ID
            validate_only: If true, only validates without executing

        Returns:
            New manager link resource name

        Note:
            The new manager must have already sent an invitation to the client.
        """
        return await service.move_manager_link(
            ctx=ctx,
            customer_id=customer_id,
            previous_manager_customer_id=previous_manager_customer_id,
            previous_manager_link_id=previous_manager_link_id,
            new_manager_customer_id=new_manager_customer_id,
            validate_only=validate_only,
        )

    tools.extend(
        [
            accept_manager_invitation,
            decline_manager_invitation,
            terminate_manager_link,
            move_client_to_new_manager,
        ]
    )
    return tools


def register_customer_manager_link_tools(
    mcp: FastMCP[Any],
) -> CustomerManagerLinkService:
    """Register customer manager link tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = CustomerManagerLinkService()
    tools = create_customer_manager_link_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
