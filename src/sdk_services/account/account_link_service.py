"""Account link service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.account_link_status import (
    AccountLinkStatusEnum,
)
from google.ads.googleads.v20.enums.types.linked_account_type import (
    LinkedAccountTypeEnum,
)
from google.ads.googleads.v20.resources.types.account_link import AccountLink
from google.ads.googleads.v20.services.services.account_link_service import (
    AccountLinkServiceClient,
)
from google.ads.googleads.v20.services.types.account_link_service import (
    AccountLinkOperation,
    CreateAccountLinkRequest,
    CreateAccountLinkResponse,
    MutateAccountLinkRequest,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AccountLinkService:
    """Account link service for managing account linking."""

    def __init__(self) -> None:
        """Initialize the account link service."""
        self._client: Optional[AccountLinkServiceClient] = None

    @property
    def client(self) -> AccountLinkServiceClient:
        """Get the account link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AccountLinkService")
        assert self._client is not None
        return self._client

    async def create_account_link(
        self,
        ctx: Context,
        customer_id: str,
        linked_account_type: str,
        linked_account_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create an account link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            linked_account_type: Type of linked account (GOOGLE_ADS, HOTEL_CENTER, etc.)
            linked_account_id: ID of the account to link
            status: Link status (ENABLED, REMOVED)

        Returns:
            Created account link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create account link
            account_link = AccountLink()
            account_link.type_ = getattr(
                LinkedAccountTypeEnum.LinkedAccountType, linked_account_type
            )
            account_link.linked_account = linked_account_id
            account_link.status = getattr(
                AccountLinkStatusEnum.AccountLinkStatus, status
            )

            # Create request
            request = CreateAccountLinkRequest()
            request.customer_id = customer_id
            request.account_link = account_link

            # Make the API call
            response: CreateAccountLinkResponse = self.client.create_account_link(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created account link between {customer_id} and {linked_account_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create account link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_account_link(
        self,
        ctx: Context,
        customer_id: str,
        account_link_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an account link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            account_link_resource_name: Resource name of the account link to update
            status: Optional new status (ENABLED, REMOVED)

        Returns:
            Updated account link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create account link with resource name
            account_link = AccountLink()
            account_link.resource_name = account_link_resource_name

            # Build update mask
            update_mask_paths = []

            if status is not None:
                account_link.status = getattr(
                    AccountLinkStatusEnum.AccountLinkStatus, status
                )
                update_mask_paths.append("status")

            # Create operation
            operation = AccountLinkOperation()
            operation.update = account_link
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateAccountLinkRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_account_link(request=request)

            await ctx.log(
                level="info",
                message="Updated account link",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update account link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_account_links(
        self,
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List account links.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            include_removed: Whether to include removed account links

        Returns:
            List of account links
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    account_link.resource_name,
                    account_link.account_link_id,
                    account_link.status,
                    account_link.type,
                    account_link.linked_account
                FROM account_link
            """

            if not include_removed:
                query += " WHERE account_link.status != 'REMOVED'"

            query += " ORDER BY account_link.account_link_id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            account_links = []
            for row in response:
                account_link = row.account_link

                link_dict = {
                    "resource_name": account_link.resource_name,
                    "account_link_id": str(account_link.account_link_id),
                    "status": account_link.status.name
                    if account_link.status
                    else "UNKNOWN",
                    "type": account_link.type_.name
                    if account_link.type_
                    else "UNKNOWN",
                    "linked_account": account_link.linked_account,
                }

                account_links.append(link_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(account_links)} account links",
            )

            return account_links

        except Exception as e:
            error_msg = f"Failed to list account links: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_account_link(
        self,
        ctx: Context,
        customer_id: str,
        account_link_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an account link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            account_link_resource_name: Resource name of the account link to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AccountLinkOperation()
            operation.remove = account_link_resource_name

            # Create request
            request = MutateAccountLinkRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_account_link(request=request)

            await ctx.log(
                level="info",
                message="Removed account link",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove account link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_account_link_tools(
    service: AccountLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the account link service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_account_link(
        ctx: Context,
        customer_id: str,
        linked_account_type: str,
        linked_account_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create an account link to connect accounts.

        Args:
            customer_id: The customer ID
            linked_account_type: Type of linked account (GOOGLE_ADS, HOTEL_CENTER, MERCHANT_CENTER, etc.)
            linked_account_id: ID of the account to link
            status: Link status - ENABLED or REMOVED

        Returns:
            Created account link details with resource_name
        """
        return await service.create_account_link(
            ctx=ctx,
            customer_id=customer_id,
            linked_account_type=linked_account_type,
            linked_account_id=linked_account_id,
            status=status,
        )

    async def update_account_link(
        ctx: Context,
        customer_id: str,
        account_link_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an account link.

        Args:
            customer_id: The customer ID
            account_link_resource_name: Resource name of the account link to update
            status: Optional new status (ENABLED, REMOVED)

        Returns:
            Updated account link details with list of updated fields
        """
        return await service.update_account_link(
            ctx=ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
            status=status,
        )

    async def list_account_links(
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List account links for a customer.

        Args:
            customer_id: The customer ID
            include_removed: Whether to include removed account links

        Returns:
            List of account links with details
        """
        return await service.list_account_links(
            ctx=ctx,
            customer_id=customer_id,
            include_removed=include_removed,
        )

    async def remove_account_link(
        ctx: Context,
        customer_id: str,
        account_link_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an account link.

        Args:
            customer_id: The customer ID
            account_link_resource_name: Resource name of the account link to remove

        Returns:
            Removal result with status
        """
        return await service.remove_account_link(
            ctx=ctx,
            customer_id=customer_id,
            account_link_resource_name=account_link_resource_name,
        )

    tools.extend(
        [
            create_account_link,
            update_account_link,
            list_account_links,
            remove_account_link,
        ]
    )
    return tools


def register_account_link_tools(mcp: FastMCP[Any]) -> AccountLinkService:
    """Register account link tools with the MCP server.

    Returns the AccountLinkService instance for testing purposes.
    """
    service = AccountLinkService()
    tools = create_account_link_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
