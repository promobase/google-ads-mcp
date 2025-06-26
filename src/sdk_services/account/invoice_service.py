"""Invoice service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.month_of_year import MonthOfYearEnum
from google.ads.googleads.v20.services.services.invoice_service import (
    InvoiceServiceClient,
)
from google.ads.googleads.v20.services.types.invoice_service import (
    ListInvoicesRequest,
    ListInvoicesResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class InvoiceService:
    """Invoice service for accessing billing invoices."""

    def __init__(self) -> None:
        """Initialize the invoice service."""
        self._client: Optional[InvoiceServiceClient] = None

    @property
    def client(self) -> InvoiceServiceClient:
        """Get the invoice service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("InvoiceService")
        assert self._client is not None
        return self._client

    async def list_invoices(
        self,
        ctx: Context,
        customer_id: str,
        billing_setup: str,
        issue_year: str,
        issue_month: MonthOfYearEnum.MonthOfYear,
    ) -> Dict[str, Any]:
        """List invoices for a specific billing setup and date range.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            billing_setup: Resource name of the billing setup
            issue_year: Year of invoice issue (YYYY format)
            issue_month: Month of invoice issue enum value

        Returns:
            List of invoices with details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = ListInvoicesRequest()
            request.customer_id = customer_id
            request.billing_setup = billing_setup
            request.issue_year = issue_year
            request.issue_month = issue_month

            # Make the API call
            response: ListInvoicesResponse = self.client.list_invoices(request=request)

            await ctx.log(
                level="info",
                message=f"Found {len(response.invoices)} invoices for {issue_year}-{issue_month}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list invoices: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_invoice_tools(
    service: InvoiceService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the invoice service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def list_invoices(
        ctx: Context,
        customer_id: str,
        billing_setup: str,
        issue_year: str,
        issue_month: str,
    ) -> Dict[str, Any]:
        """List invoices for a specific billing setup and date range.

        Args:
            customer_id: The customer ID
            billing_setup: Resource name of the billing setup (e.g., customers/123/billingSetups/456)
            issue_year: Year of invoice issue (YYYY format, e.g., "2024")
            issue_month: Month of invoice issue (JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER)

        Returns:
            List invoices response with comprehensive details including amounts, dates, and account summaries
        """
        # Convert string enum to proper enum type
        month_enum = MonthOfYearEnum.MonthOfYear[issue_month.upper()]

        return await service.list_invoices(
            ctx=ctx,
            customer_id=customer_id,
            billing_setup=billing_setup,
            issue_year=issue_year,
            issue_month=month_enum,
        )

    tools.extend([list_invoices])
    return tools


def register_invoice_tools(mcp: FastMCP[Any]) -> InvoiceService:
    """Register invoice tools with the MCP server.

    Returns the InvoiceService instance for testing purposes.
    """
    service = InvoiceService()
    tools = create_invoice_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
