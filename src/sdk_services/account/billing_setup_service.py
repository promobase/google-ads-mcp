"""Billing setup service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.time_type import TimeTypeEnum
from google.ads.googleads.v20.resources.types.billing_setup import BillingSetup
from google.ads.googleads.v20.services.services.billing_setup_service import (
    BillingSetupServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.billing_setup_service import (
    BillingSetupOperation,
    MutateBillingSetupRequest,
    MutateBillingSetupResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BillingSetupService:
    """Billing setup service for managing billing configurations."""

    def __init__(self) -> None:
        """Initialize the billing setup service."""
        self._client: Optional[BillingSetupServiceClient] = None

    @property
    def client(self) -> BillingSetupServiceClient:
        """Get the billing setup service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BillingSetupService")
        assert self._client is not None
        return self._client

    async def create_billing_setup(
        self,
        ctx: Context,
        customer_id: str,
        payments_account_id: str,
        start_date: str,
        end_date: Optional[str] = None,
        start_time_type: TimeTypeEnum.TimeType = TimeTypeEnum.TimeType.NOW,
        end_time_type: TimeTypeEnum.TimeType = TimeTypeEnum.TimeType.FOREVER,
    ) -> Dict[str, Any]:
        """Create a billing setup for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            payments_account_id: The payments account ID to link
            start_date: Start date in YYYY-MM-DD format (ignored if start_time_type is NOW)
            end_date: End date in YYYY-MM-DD format (optional, ignored if end_time_type is FOREVER)
            start_time_type: Start time type enum value
            end_time_type: End time type enum value

        Returns:
            Created billing setup details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create billing setup
            billing_setup = BillingSetup()

            # Set payments account
            billing_setup.payments_account = (
                f"customers/{customer_id}/paymentsAccounts/{payments_account_id}"
            )

            # Set start date/time (these are mutually exclusive oneof fields)
            if start_time_type == TimeTypeEnum.TimeType.NOW:
                billing_setup.start_time_type = start_time_type
            else:
                billing_setup.start_date_time = start_date

            # Set end date/time if provided
            if end_time_type != TimeTypeEnum.TimeType.FOREVER:
                billing_setup.end_time_type = end_time_type
                if end_date and end_time_type != TimeTypeEnum.TimeType.NOW:
                    billing_setup.end_date_time = end_date

            # Create operation
            operation = BillingSetupOperation()
            operation.create = billing_setup

            # Create request
            request = MutateBillingSetupRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateBillingSetupResponse = self.client.mutate_billing_setup(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created billing setup for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create billing setup: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_billing_setups(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List billing setups for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            status_filter: Optional status filter (UNKNOWN, PENDING, APPROVED, CANCELLED)

        Returns:
            List of billing setups
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
                    billing_setup.resource_name,
                    billing_setup.id,
                    billing_setup.status,
                    billing_setup.payments_account,
                    billing_setup.start_date_time,
                    billing_setup.start_time_type,
                    billing_setup.end_date_time,
                    billing_setup.end_time_type
                FROM billing_setup
            """

            if status_filter:
                query += f" WHERE billing_setup.status = '{status_filter}'"

            query += " ORDER BY billing_setup.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            billing_setups = []
            for row in response:
                billing_setup = row.billing_setup
                billing_setups.append(serialize_proto_message(billing_setup))

            await ctx.log(
                level="info",
                message=f"Found {len(billing_setups)} billing setups",
            )

            return billing_setups

        except Exception as e:
            error_msg = f"Failed to list billing setups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_billing_setup(
        self,
        ctx: Context,
        customer_id: str,
        billing_setup_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific billing setup.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            billing_setup_id: The billing setup ID

        Returns:
            Billing setup details
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
                    billing_setup.resource_name,
                    billing_setup.id,
                    billing_setup.status,
                    billing_setup.payments_account,
                    billing_setup.start_date_time,
                    billing_setup.start_time_type,
                    billing_setup.end_date_time,
                    billing_setup.end_time_type
                FROM billing_setup
                WHERE billing_setup.id = {billing_setup_id}
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process result
            for row in response:
                billing_setup = row.billing_setup

                await ctx.log(
                    level="info",
                    message=f"Found billing setup {billing_setup_id}",
                )

                return serialize_proto_message(billing_setup)

            # If no billing setup found
            raise Exception(f"Billing setup {billing_setup_id} not found")

        except Exception as e:
            error_msg = f"Failed to get billing setup: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_payments_accounts(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List available payments accounts for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of payments accounts
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
                    payments_account.resource_name,
                    payments_account.payments_account_id,
                    payments_account.name,
                    payments_account.currency_code,
                    payments_account.payments_profile_id
                FROM payments_account
                ORDER BY payments_account.name
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            payments_accounts = []
            for row in response:
                payments_account = row.payments_account
                payments_accounts.append(serialize_proto_message(payments_account))

            await ctx.log(
                level="info",
                message=f"Found {len(payments_accounts)} payments accounts",
            )

            return payments_accounts

        except Exception as e:
            error_msg = f"Failed to list payments accounts: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_billing_setup_tools(
    service: BillingSetupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the billing setup service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_billing_setup(
        ctx: Context,
        customer_id: str,
        payments_account_id: str,
        start_date: str,
        end_date: Optional[str] = None,
        start_time_type: str = "NOW",
        end_time_type: str = "FOREVER",
    ) -> Dict[str, Any]:
        """Create a billing setup for a customer.

        Args:
            customer_id: The customer ID
            payments_account_id: The payments account ID to link
            start_date: Start date in YYYY-MM-DD format (ignored if start_time_type is NOW)
            end_date: End date in YYYY-MM-DD format (optional, ignored if end_time_type is FOREVER)
            start_time_type: Start time type - NOW or FOREVER
            end_time_type: End time type - FOREVER, NOW, or specific date

        Returns:
            Created billing setup details
        """
        # Convert string enums to proper enum types
        start_enum = getattr(TimeTypeEnum.TimeType, start_time_type)
        end_enum = getattr(TimeTypeEnum.TimeType, end_time_type)

        return await service.create_billing_setup(
            ctx=ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            start_date=start_date,
            end_date=end_date,
            start_time_type=start_enum,
            end_time_type=end_enum,
        )

    async def list_billing_setups(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List billing setups for a customer.

        Args:
            customer_id: The customer ID
            status_filter: Optional status filter (UNKNOWN, PENDING, APPROVED, CANCELLED)

        Returns:
            List of billing setups with details
        """
        return await service.list_billing_setups(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    async def get_billing_setup(
        ctx: Context,
        customer_id: str,
        billing_setup_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific billing setup.

        Args:
            customer_id: The customer ID
            billing_setup_id: The billing setup ID

        Returns:
            Billing setup details including status and account information
        """
        return await service.get_billing_setup(
            ctx=ctx,
            customer_id=customer_id,
            billing_setup_id=billing_setup_id,
        )

    async def list_payments_accounts(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List available payments accounts for a customer.

        Args:
            customer_id: The customer ID

        Returns:
            List of payments accounts that can be linked to billing setups
        """
        return await service.list_payments_accounts(
            ctx=ctx,
            customer_id=customer_id,
        )

    tools.extend(
        [
            create_billing_setup,
            list_billing_setups,
            get_billing_setup,
            list_payments_accounts,
        ]
    )
    return tools


def register_billing_setup_tools(mcp: FastMCP[Any]) -> BillingSetupService:
    """Register billing setup tools with the MCP server.

    Returns the BillingSetupService instance for testing purposes.
    """
    service = BillingSetupService()
    tools = create_billing_setup_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
