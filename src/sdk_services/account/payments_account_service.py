"""Payments account service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.payments_account_service import (
    PaymentsAccountServiceClient,
)
from google.ads.googleads.v20.services.types.payments_account_service import (
    ListPaymentsAccountsRequest,
    ListPaymentsAccountsResponse,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger

logger = get_logger(__name__)


class PaymentsAccountService:
    """Payments account service for managing payments accounts."""

    def __init__(self) -> None:
        """Initialize the payments account service."""
        self._client: Optional[PaymentsAccountServiceClient] = None

    @property
    def client(self) -> PaymentsAccountServiceClient:
        """Get the payments account service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("PaymentsAccountService")
        assert self._client is not None
        return self._client

    async def list_payments_accounts(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List all accessible payments accounts for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of payments accounts
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = ListPaymentsAccountsRequest()
            request.customer_id = customer_id

            # Make the API call
            response: ListPaymentsAccountsResponse = self.client.list_payments_accounts(
                request=request
            )

            # Process results
            accounts = []
            for account in response.payments_accounts:
                account_dict = {
                    "resource_name": account.resource_name,
                    "payments_account_id": account.payments_account_id
                    if account.payments_account_id
                    else None,
                    "name": account.name if account.name else None,
                    "currency_code": account.currency_code
                    if account.currency_code
                    else None,
                    "payments_profile_id": account.payments_profile_id
                    if account.payments_profile_id
                    else None,
                    "secondary_payments_profile_id": account.secondary_payments_profile_id
                    if account.secondary_payments_profile_id
                    else None,
                    "paying_manager_customer": account.paying_manager_customer
                    if account.paying_manager_customer
                    else None,
                }
                accounts.append(account_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(accounts)} payments accounts",
            )

            return accounts

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list payments accounts: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_payments_account_tools(
    service: PaymentsAccountService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the payments account service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def list_payments_accounts(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List all accessible payments accounts for a customer.

        Args:
            customer_id: The customer ID

        Returns:
            List of payments accounts with details including account ID, name, and currency
        """
        return await service.list_payments_accounts(
            ctx=ctx,
            customer_id=customer_id,
        )

    tools.extend([list_payments_accounts])
    return tools


def register_payments_account_tools(
    mcp: FastMCP[Any],
) -> PaymentsAccountService:
    """Register payments account tools with the MCP server.

    Returns the PaymentsAccountService instance for testing purposes.
    """
    service = PaymentsAccountService()
    tools = create_payments_account_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
