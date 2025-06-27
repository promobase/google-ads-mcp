"""Customer Label service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.customer_label import CustomerLabel
from google.ads.googleads.v20.services.services.customer_label_service import (
    CustomerLabelServiceClient,
)
from google.ads.googleads.v20.services.types.customer_label_service import (
    CustomerLabelOperation,
    MutateCustomerLabelsRequest,
    MutateCustomerLabelsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerLabelService:
    """Service for managing customer labels in Google Ads.

    Customer labels allow you to organize and categorize Google Ads accounts
    by associating them with labels. This is especially useful for agencies
    managing multiple customer accounts.
    """

    def __init__(self) -> None:
        """Initialize the customer label service."""
        self._client: Optional[CustomerLabelServiceClient] = None

    @property
    def client(self) -> CustomerLabelServiceClient:
        """Get the customer label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerLabelService")
        assert self._client is not None
        return self._client

    async def create_customer_label(
        self,
        ctx: Context,
        customer_id: str,
        label_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a new customer label association.

        Associates a label with a customer account for organization purposes.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID to associate with the label
            label_id: The label ID to associate with the customer
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created customer label details
        """
        try:
            customer_id = format_customer_id(customer_id)
            label_resource = f"customers/{customer_id}/labels/{label_id}"

            # Create a new customer label
            # Note: We only need to provide the label resource
            # The customer is inferred from the request's customer_id
            customer_label = CustomerLabel()
            customer_label.label = label_resource

            # Create the operation
            operation = CustomerLabelOperation()
            operation.create = customer_label

            # Create the request
            request = MutateCustomerLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response: MutateCustomerLabelsResponse = self.client.mutate_customer_labels(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created customer label association: customer {customer_id} with label {label_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_customer_label(
        self,
        ctx: Context,
        customer_id: str,
        label_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a customer label association.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            label_id: The label ID to remove from the customer
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Construct resource name
            resource_name = f"customers/{customer_id}/customerLabels/{label_id}"

            # Create the operation
            operation = CustomerLabelOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateCustomerLabelsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            request.partial_failure = partial_failure
            request.validate_only = validate_only

            # Execute the mutation
            response = self.client.mutate_customer_labels(request=request)

            await ctx.log(
                level="info",
                message=f"Removed customer label association: customer {customer_id} from label {label_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove customer label: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_label_tools(
    service: CustomerLabelService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer label service."""
    tools = []

    async def create_customer_label(
        ctx: Context,
        customer_id: str,
        label_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Associate a label with a customer account for organization.

        Customer labels help organize and categorize Google Ads accounts,
        making it easier to manage multiple accounts, apply bulk changes,
        and generate reports across specific account groups.

        Args:
            customer_id: The customer ID to label
            label_id: The label ID to associate with the customer
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Created customer label association details

        Example:
            # Label a customer account as "Premium"
            result = await create_customer_label(
                customer_id="1234567890",
                label_id="9876543210"
            )

            # Label multiple customers with the same label for bulk operations
            for customer in premium_customers:
                await create_customer_label(
                    customer_id=customer,
                    label_id="9876543210"
                )
        """
        return await service.create_customer_label(
            ctx=ctx,
            customer_id=customer_id,
            label_id=label_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def remove_customer_label(
        ctx: Context,
        customer_id: str,
        label_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a label association from a customer account.

        Args:
            customer_id: The customer ID
            label_id: The label ID to remove from the customer
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing

        Returns:
            Removal result details

        Example:
            result = await remove_customer_label(
                customer_id="1234567890",
                label_id="9876543210"
            )
        """
        return await service.remove_customer_label(
            ctx=ctx,
            customer_id=customer_id,
            label_id=label_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.extend([create_customer_label, remove_customer_label])
    return tools


def register_customer_label_tools(
    mcp: FastMCP[Any],
) -> CustomerLabelService:
    """Register customer label tools with the MCP server.

    Returns the service instance for testing purposes.
    """
    service = CustomerLabelService()
    tools = create_customer_label_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
