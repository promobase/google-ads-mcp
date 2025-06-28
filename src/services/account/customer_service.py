"""Customer service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.customer import Customer
from google.ads.googleads.v20.services.services.customer_service import (
    CustomerServiceClient,
)
from google.ads.googleads.v20.services.types.customer_service import (
    CreateCustomerClientRequest,
    CreateCustomerClientResponse,
    ListAccessibleCustomersRequest,
    ListAccessibleCustomersResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerService:
    """Customer service for managing Google Ads customers."""

    def __init__(self) -> None:
        """Initialize the customer service."""
        self._client: Optional[CustomerServiceClient] = None

    @property
    def client(self) -> CustomerServiceClient:
        """Get the customer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerService")
        assert self._client is not None
        return self._client

    async def create_customer_client(
        self,
        ctx: Context,
        manager_customer_id: str,
        descriptive_name: str,
        currency_code: str = "USD",
        time_zone: str = "America/New_York",
    ) -> Dict[str, Any]:
        """Create a new client customer under a manager account.

        Args:
            ctx: FastMCP context
            manager_customer_id: The manager customer ID
            descriptive_name: Name of the new client
            currency_code: Currency code (e.g. USD, EUR)
            time_zone: Time zone ID

        Returns:
            Created customer details
        """
        try:
            manager_customer_id = format_customer_id(manager_customer_id)

            # Create a new customer object
            customer = Customer()
            customer.descriptive_name = descriptive_name
            customer.currency_code = currency_code
            customer.time_zone = time_zone

            # Create the request
            request = CreateCustomerClientRequest()
            request.customer_id = manager_customer_id
            request.customer_client = customer

            # Make the API call
            response: CreateCustomerClientResponse = self.client.create_customer_client(
                request=request
            )

            # Extract customer ID from resource name
            customer_resource = response.resource_name
            customer_id = customer_resource.split("/")[-1] if customer_resource else ""

            await ctx.log(
                level="info",
                message=f"Created customer client {customer_id} under manager {manager_customer_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer client: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_accessible_customers(
        self, ctx: Context
    ) -> ListAccessibleCustomersResponse:
        """List all accessible customers for the authenticated user.

        Args:
            ctx: FastMCP context

        Returns:
            List of accessible customer IDs
        """
        try:
            # Create the request
            request = ListAccessibleCustomersRequest()

            # Make the API call
            response: ListAccessibleCustomersResponse = (
                self.client.list_accessible_customers(request=request)
            )
            await ctx.log(
                level="info",
                message=f"ListAccessibleCustomersResponse: {response.resource_names}",
            )
            return response

            customer_ids = response.resource_names

            await ctx.log(
                level="info",
                message=f"Found {len(customer_ids)} accessible customers",
            )

            # Extract customer IDs from resource names
            return [
                resource_name.split("/")[-1]
                for resource_name in customer_ids
                if resource_name
            ]

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list accessible customers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_tools(
    service: CustomerService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customer_client(
        ctx: Context,
        manager_customer_id: str,
        descriptive_name: str,
        currency_code: str = "USD",
        time_zone: str = "America/New_York",
    ) -> Dict[str, Any]:
        """Create a new client customer under a manager account.

        Args:
            manager_customer_id: The manager customer ID
            descriptive_name: Name of the new client
            currency_code: Currency code (e.g. USD, EUR)
            time_zone: Time zone ID

        Returns:
            Created customer details
        """
        return await service.create_customer_client(
            ctx=ctx,
            manager_customer_id=manager_customer_id,
            descriptive_name=descriptive_name,
            currency_code=currency_code,
            time_zone=time_zone,
        )

    async def list_accessible_customers(ctx: Context) -> Dict[str, Any]:
        """List all accessible customers for the authenticated user.

        Returns:
            List of accessible customer IDs
        """
        response = await service.list_accessible_customers(ctx=ctx)
        return serialize_proto_message(response)

    tools.extend([create_customer_client, list_accessible_customers])
    return tools


def register_customer_tools(mcp: FastMCP[Any]) -> CustomerService:
    """Register customer tools with the MCP server.

    Returns the CustomerService instance for testing purposes.
    """
    service = CustomerService()
    tools = create_customer_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
