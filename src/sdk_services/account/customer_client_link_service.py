"""Customer client link service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.manager_link_status import (
    ManagerLinkStatusEnum,
)
from google.ads.googleads.v20.resources.types.customer_client_link import (
    CustomerClientLink,
)
from google.ads.googleads.v20.services.services.customer_client_link_service import (
    CustomerClientLinkServiceClient,
)
from google.ads.googleads.v20.services.types.customer_client_link_service import (
    CustomerClientLinkOperation,
    MutateCustomerClientLinkRequest,
    MutateCustomerClientLinkResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerClientLinkService:
    """Customer client link service for managing links between manager and client accounts."""

    def __init__(self) -> None:
        """Initialize the customer client link service."""
        self._client: Optional[CustomerClientLinkServiceClient] = None

    @property
    def client(self) -> CustomerClientLinkServiceClient:
        """Get the customer client link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerClientLinkService")
        assert self._client is not None
        return self._client

    async def create_customer_client_link(
        self,
        ctx: Context,
        customer_id: str,
        client_customer: str,
        status: str = "PENDING",
        hidden: bool = False,
    ) -> Dict[str, Any]:
        """Create a customer client link between manager and client accounts.

        Args:
            ctx: FastMCP context
            customer_id: The manager customer ID
            client_customer: Resource name of the client customer
            status: Link status (PENDING, ACTIVE, CANCELLED, REJECTED)
            hidden: Whether the link is hidden from the client

        Returns:
            Created customer client link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customer client link
            link = CustomerClientLink()
            link.client_customer = client_customer
            link.status = getattr(ManagerLinkStatusEnum.ManagerLinkStatus, status)
            link.hidden = hidden

            # Create operation
            operation = CustomerClientLinkOperation()
            operation.create = link

            # Create request
            request = MutateCustomerClientLinkRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateCustomerClientLinkResponse = (
                self.client.mutate_customer_client_link(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer client link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_customer_client_link(
        self,
        ctx: Context,
        customer_id: str,
        link_resource_name: str,
        status: Optional[str] = None,
        hidden: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a customer client link.

        Args:
            ctx: FastMCP context
            customer_id: The manager customer ID
            link_resource_name: Resource name of the link to update
            status: Optional new status (PENDING, ACTIVE, CANCELLED, REJECTED)
            hidden: Optional new hidden status

        Returns:
            Updated customer client link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customer client link with resource name
            link = CustomerClientLink()
            link.resource_name = link_resource_name

            # Build update mask
            update_mask_paths = []

            if status is not None:
                link.status = getattr(ManagerLinkStatusEnum.ManagerLinkStatus, status)
                update_mask_paths.append("status")

            if hidden is not None:
                link.hidden = hidden
                update_mask_paths.append("hidden")

            # Create operation
            operation = CustomerClientLinkOperation()
            operation.update = link
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateCustomerClientLinkRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_customer_client_link(request=request)

            await ctx.log(
                level="info",
                message="Updated customer client link",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update customer client link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_customer_client_links(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List customer client links for a manager account.

        Args:
            ctx: FastMCP context
            customer_id: The manager customer ID
            status_filter: Optional status filter (PENDING, ACTIVE, CANCELLED, REJECTED)

        Returns:
            List of customer client links
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    customer_client_link.resource_name,
                    customer_client_link.client_customer,
                    customer_client_link.manager_link_id,
                    customer_client_link.status,
                    customer_client_link.hidden,
                    customer_client.descriptive_name,
                    customer_client.manager,
                    customer_client.test_account,
                    customer_client.auto_tagging_enabled,
                    customer_client.id,
                    customer_client.time_zone,
                    customer_client.currency_code
                FROM customer_client_link
            """

            if status_filter:
                query += f" WHERE customer_client_link.status = '{status_filter}'"

            query += " ORDER BY customer_client_link.manager_link_id DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            links = []
            for row in response:
                link = row.customer_client_link
                client = row.customer_client

                link_dict = {
                    "resource_name": link.resource_name,
                    "client_customer": link.client_customer,
                    "manager_link_id": str(link.manager_link_id),
                    "status": link.status.name if link.status else "UNKNOWN",
                    "hidden": link.hidden,
                    "client_details": {
                        "descriptive_name": client.descriptive_name,
                        "manager": client.manager,
                        "test_account": client.test_account,
                        "auto_tagging_enabled": client.auto_tagging_enabled,
                        "id": str(client.id),
                        "time_zone": client.time_zone,
                        "currency_code": client.currency_code,
                    },
                }

                links.append(link_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(links)} customer client links",
            )

            return links

        except Exception as e:
            error_msg = f"Failed to list customer client links: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_client_link_tools(
    service: CustomerClientLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer client link service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customer_client_link(
        ctx: Context,
        customer_id: str,
        client_customer: str,
        status: str = "PENDING",
        hidden: bool = False,
    ) -> Dict[str, Any]:
        """Create a customer client link between manager and client accounts.

        Args:
            customer_id: The manager customer ID
            client_customer: Resource name of the client customer (e.g., customers/123456789)
            status: Link status (PENDING, ACTIVE, CANCELLED, REJECTED)
            hidden: Whether the link is hidden from the client in their account list

        Returns:
            Created customer client link details with resource_name and status
        """
        return await service.create_customer_client_link(
            ctx=ctx,
            customer_id=customer_id,
            client_customer=client_customer,
            status=status,
            hidden=hidden,
        )

    async def update_customer_client_link(
        ctx: Context,
        customer_id: str,
        link_resource_name: str,
        status: Optional[str] = None,
        hidden: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a customer client link.

        Args:
            customer_id: The manager customer ID
            link_resource_name: Resource name of the link to update
            status: Optional new status (PENDING, ACTIVE, CANCELLED, REJECTED)
            hidden: Optional new hidden status

        Returns:
            Updated customer client link details with list of updated fields
        """
        return await service.update_customer_client_link(
            ctx=ctx,
            customer_id=customer_id,
            link_resource_name=link_resource_name,
            status=status,
            hidden=hidden,
        )

    async def list_customer_client_links(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List customer client links for a manager account.

        Args:
            customer_id: The manager customer ID
            status_filter: Optional status filter (PENDING, ACTIVE, CANCELLED, REJECTED)

        Returns:
            List of customer client links with client account details and link status
        """
        return await service.list_customer_client_links(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    tools.extend(
        [
            create_customer_client_link,
            update_customer_client_link,
            list_customer_client_links,
        ]
    )
    return tools


def register_customer_client_link_tools(mcp: FastMCP[Any]) -> CustomerClientLinkService:
    """Register customer client link tools with the MCP server.

    Returns the CustomerClientLinkService instance for testing purposes.
    """
    service = CustomerClientLinkService()
    tools = create_customer_client_link_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
