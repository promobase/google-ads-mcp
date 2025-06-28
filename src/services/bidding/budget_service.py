"""Budget service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.budget_delivery_method import (
    BudgetDeliveryMethodEnum,
)
from google.ads.googleads.v20.resources.types.campaign_budget import CampaignBudget
from google.ads.googleads.v20.services.services.campaign_budget_service import (
    CampaignBudgetServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_budget_service import (
    CampaignBudgetOperation,
    MutateCampaignBudgetsRequest,
    MutateCampaignBudgetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BudgetService:
    """Budget service for managing Google Ads campaign budgets."""

    def __init__(self) -> None:
        """Initialize the budget service."""
        self._client: Optional[CampaignBudgetServiceClient] = None

    @property
    def client(self) -> CampaignBudgetServiceClient:
        """Get the campaign budget service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignBudgetService")
        assert self._client is not None
        return self._client

    async def create_campaign_budget(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        amount_micros: int,
        delivery_method: str = "STANDARD",
        explicitly_shared: bool = False,
    ) -> Dict[str, Any]:
        """Create a new campaign budget.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Budget name
            amount_micros: Budget amount in micros (1 million micros = 1 unit)
            delivery_method: STANDARD or ACCELERATED (default: STANDARD)
            explicitly_shared: Whether the budget can be shared across campaigns

        Returns:
            Created budget details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create a new campaign budget
            campaign_budget = CampaignBudget()
            campaign_budget.name = name
            campaign_budget.amount_micros = amount_micros
            campaign_budget.explicitly_shared = explicitly_shared

            # Set delivery method
            campaign_budget.delivery_method = getattr(
                BudgetDeliveryMethodEnum.BudgetDeliveryMethod, delivery_method
            )

            # Create the operation
            operation = CampaignBudgetOperation()
            operation.create = campaign_budget

            # Create the request
            request = MutateCampaignBudgetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateCampaignBudgetsResponse = (
                self.client.mutate_campaign_budgets(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign budget: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign_budget(
        self,
        ctx: Context,
        customer_id: str,
        budget_id: str,
        name: Optional[str] = None,
        amount_micros: Optional[int] = None,
        delivery_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign budget.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            budget_id: The budget ID to update
            name: New budget name (optional)
            amount_micros: New budget amount in micros (optional)
            delivery_method: New delivery method (optional)

        Returns:
            Updated budget details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/campaignBudgets/{budget_id}"

            # Create budget with resource name
            campaign_budget = CampaignBudget()
            campaign_budget.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                campaign_budget.name = name
                update_mask_fields.append("name")

            if amount_micros is not None:
                campaign_budget.amount_micros = amount_micros
                update_mask_fields.append("amount_micros")

            if delivery_method is not None:
                campaign_budget.delivery_method = getattr(
                    BudgetDeliveryMethodEnum.BudgetDeliveryMethod, delivery_method
                )
                update_mask_fields.append("delivery_method")

            # Create the operation
            operation = CampaignBudgetOperation()
            operation.update = campaign_budget
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateCampaignBudgetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_campaign_budgets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated campaign budget {budget_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign budget: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_budget_tools(service: BudgetService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the budget service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_campaign_budget(
        ctx: Context,
        customer_id: str,
        name: str,
        amount_micros: int,
        delivery_method: str = "STANDARD",
        explicitly_shared: bool = False,
    ) -> Dict[str, Any]:
        """Create a new campaign budget.

        Args:
            customer_id: The customer ID
            name: Budget name
            amount_micros: Budget amount in micros (1 million micros = 1 unit)
            delivery_method: STANDARD or ACCELERATED (default: STANDARD)
            explicitly_shared: Whether the budget can be shared across campaigns

        Returns:
            Created budget details including resource_name and budget_id
        """
        return await service.create_campaign_budget(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            amount_micros=amount_micros,
            delivery_method=delivery_method,
            explicitly_shared=explicitly_shared,
        )

    async def update_campaign_budget(
        ctx: Context,
        customer_id: str,
        budget_id: str,
        name: Optional[str] = None,
        amount_micros: Optional[int] = None,
        delivery_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign budget.

        Args:
            customer_id: The customer ID
            budget_id: The budget ID to update
            name: New budget name (optional)
            amount_micros: New budget amount in micros (optional)
            delivery_method: New delivery method - STANDARD or ACCELERATED (optional)

        Returns:
            Updated budget details
        """
        return await service.update_campaign_budget(
            ctx=ctx,
            customer_id=customer_id,
            budget_id=budget_id,
            name=name,
            amount_micros=amount_micros,
            delivery_method=delivery_method,
        )

    tools.extend([create_campaign_budget, update_campaign_budget])
    return tools


def register_budget_tools(mcp: FastMCP[Any]) -> BudgetService:
    """Register budget tools with the MCP server.

    Returns the BudgetService instance for testing purposes.
    """
    service = BudgetService()
    tools = create_budget_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
