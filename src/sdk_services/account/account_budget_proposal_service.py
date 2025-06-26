"""Account budget proposal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.account_budget_proposal_type import (
    AccountBudgetProposalTypeEnum,
)
from google.ads.googleads.v20.enums.types.spending_limit_type import (
    SpendingLimitTypeEnum,
)
from google.ads.googleads.v20.enums.types.time_type import TimeTypeEnum
from google.ads.googleads.v20.resources.types.account_budget_proposal import (
    AccountBudgetProposal,
)
from google.ads.googleads.v20.services.services.account_budget_proposal_service import (
    AccountBudgetProposalServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.account_budget_proposal_service import (
    AccountBudgetProposalOperation,
    MutateAccountBudgetProposalRequest,
    MutateAccountBudgetProposalResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AccountBudgetProposalService:
    """Account budget proposal service for managing account-level budget proposals."""

    def __init__(self) -> None:
        """Initialize the account budget proposal service."""
        self._client: Optional[AccountBudgetProposalServiceClient] = None

    @property
    def client(self) -> AccountBudgetProposalServiceClient:
        """Get the account budget proposal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AccountBudgetProposalService")
        assert self._client is not None
        return self._client

    async def create_account_budget_proposal(
        self,
        ctx: Context,
        customer_id: str,
        proposal_type: AccountBudgetProposalTypeEnum.AccountBudgetProposalType,
        billing_setup: str,
        proposed_name: str,
        proposed_start_time_type: TimeTypeEnum.TimeType,
        proposed_spending_limit_type: SpendingLimitTypeEnum.SpendingLimitType = SpendingLimitTypeEnum.SpendingLimitType.INFINITE,
        proposed_spending_limit_micros: Optional[int] = None,
        proposed_start_date_time: Optional[str] = None,
        proposed_end_date_time: Optional[str] = None,
        proposed_end_time_type: Optional[TimeTypeEnum.TimeType] = None,
    ) -> Dict[str, Any]:
        """Create an account budget proposal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            proposal_type: Type of proposal enum value
            billing_setup: Resource name of the billing setup
            proposed_name: Proposed name for the account budget
            proposed_start_time_type: Start time type enum value
            proposed_spending_limit_type: Spending limit type enum value
            proposed_spending_limit_micros: Spending limit in micros (required if FINITE)
            proposed_start_date_time: Start date/time (YYYY-MM-DD HH:MM:SS)
            proposed_end_date_time: End date/time (YYYY-MM-DD HH:MM:SS)
            proposed_end_time_type: End time type enum value

        Returns:
            Mutation result dictionary
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create account budget proposal
            proposal = AccountBudgetProposal()
            proposal.proposal_type = proposal_type
            proposal.billing_setup = billing_setup
            proposal.proposed_name = proposed_name

            # Set start time
            proposal.proposed_start_time_type = proposed_start_time_type

            if proposed_start_date_time:
                proposal.proposed_start_date_time = proposed_start_date_time

            # Set spending limit (these are mutually exclusive oneof fields)
            if proposed_spending_limit_micros is not None:
                proposal.proposed_spending_limit_micros = proposed_spending_limit_micros
            else:
                proposal.proposed_spending_limit_type = proposed_spending_limit_type

            # Set end time if provided (these are mutually exclusive oneof fields)
            if proposed_end_date_time:
                proposal.proposed_end_date_time = proposed_end_date_time
            elif proposed_end_time_type:
                proposal.proposed_end_time_type = proposed_end_time_type

            # Create operation
            operation = AccountBudgetProposalOperation()
            operation.create = proposal

            # Create request
            request = MutateAccountBudgetProposalRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateAccountBudgetProposalResponse = (
                self.client.mutate_account_budget_proposal(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created account budget proposal: {proposed_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create account budget proposal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_account_budget_proposal(
        self,
        ctx: Context,
        customer_id: str,
        account_budget: str,
        billing_setup: str,
        proposed_name: Optional[str] = None,
        proposed_spending_limit_micros: Optional[int] = None,
        proposed_end_date_time: Optional[str] = None,
        proposed_start_date_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an UPDATE proposal for an existing account budget.

        Note: Account budget proposals work by creating new proposals with UPDATE type,
        not by directly updating existing proposals.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            account_budget: Resource name of the account budget to update
            billing_setup: Resource name of the billing setup
            proposed_name: Optional new name
            proposed_spending_limit_micros: Optional new spending limit in micros
            proposed_end_date_time: Optional new end date/time
            proposed_start_date_time: Optional new start date/time

        Returns:
            Mutation result dictionary
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create account budget proposal for UPDATE
            proposal = AccountBudgetProposal()
            proposal.proposal_type = (
                AccountBudgetProposalTypeEnum.AccountBudgetProposalType.UPDATE
            )
            proposal.account_budget = account_budget
            proposal.billing_setup = billing_setup

            if proposed_name is not None:
                proposal.proposed_name = proposed_name

            if proposed_spending_limit_micros is not None:
                proposal.proposed_spending_limit_micros = proposed_spending_limit_micros

            if proposed_end_date_time is not None:
                proposal.proposed_end_date_time = proposed_end_date_time

            if proposed_start_date_time is not None:
                proposal.proposed_start_date_time = proposed_start_date_time

            # Create operation
            operation = AccountBudgetProposalOperation()
            operation.create = proposal

            # Create request
            request = MutateAccountBudgetProposalRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_account_budget_proposal(request=request)

            await ctx.log(
                level="info",
                message="Created UPDATE proposal for account budget",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create update proposal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_account_budget_proposals(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List account budget proposals for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of account budget proposal dictionaries
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
                    account_budget_proposal.resource_name,
                    account_budget_proposal.id,
                    account_budget_proposal.billing_setup,
                    account_budget_proposal.account_budget,
                    account_budget_proposal.proposal_type,
                    account_budget_proposal.status,
                    account_budget_proposal.proposed_name,
                    account_budget_proposal.proposed_start_date_time,
                    account_budget_proposal.proposed_end_date_time,
                    account_budget_proposal.proposed_spending_limit_type,
                    account_budget_proposal.proposed_spending_limit_micros,
                    account_budget_proposal.creation_date_time,
                    account_budget_proposal.approval_date_time
                FROM account_budget_proposal
                ORDER BY account_budget_proposal.id DESC
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            proposals = []
            for row in response:
                proposal = row.account_budget_proposal
                proposals.append(serialize_proto_message(proposal))

            await ctx.log(
                level="info",
                message=f"Found {len(proposals)} account budget proposals",
            )

            return proposals

        except Exception as e:
            error_msg = f"Failed to list account budget proposals: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_account_budget_proposal(
        self,
        ctx: Context,
        customer_id: str,
        proposal_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an account budget proposal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            proposal_resource_name: Resource name of the proposal to remove

        Returns:
            Mutation result dictionary
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = AccountBudgetProposalOperation()
            operation.remove = proposal_resource_name

            # Create request
            request = MutateAccountBudgetProposalRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response = self.client.mutate_account_budget_proposal(request=request)

            await ctx.log(
                level="info",
                message="Removed account budget proposal",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove account budget proposal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_account_budget_proposal_tools(
    service: AccountBudgetProposalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the account budget proposal service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_account_budget_proposal(
        ctx: Context,
        customer_id: str,
        proposal_type: str,
        billing_setup: str,
        proposed_name: str,
        proposed_start_time_type: str,
        proposed_spending_limit_type: str = "INFINITE",
        proposed_spending_limit_micros: Optional[int] = None,
        proposed_start_date_time: Optional[str] = None,
        proposed_end_date_time: Optional[str] = None,
        proposed_end_time_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an account budget proposal for account-level budget management.

        Args:
            customer_id: The customer ID
            proposal_type: Type of proposal (CREATE, UPDATE, REMOVE)
            billing_setup: Resource name of the billing setup
            proposed_name: Proposed name for the account budget
            proposed_start_time_type: Start time type (IMMEDIATELY, NOW, FOREVER)
            proposed_spending_limit_type: Spending limit type (INFINITE, FINITE)
            proposed_spending_limit_micros: Spending limit in micros (for FINITE limit)
            proposed_start_date_time: Start date/time (YYYY-MM-DD HH:MM:SS format)
            proposed_end_date_time: End date/time (YYYY-MM-DD HH:MM:SS format)
            proposed_end_time_type: End time type (NEVER, FOREVER)

        Returns:
            Created account budget proposal details with resource_name
        """
        # Convert string enums to proper enum types
        proposal_type_enum = getattr(
            AccountBudgetProposalTypeEnum.AccountBudgetProposalType, proposal_type
        )
        start_time_enum = getattr(TimeTypeEnum.TimeType, proposed_start_time_type)
        spending_limit_enum = getattr(
            SpendingLimitTypeEnum.SpendingLimitType, proposed_spending_limit_type
        )
        end_time_enum = (
            getattr(TimeTypeEnum.TimeType, proposed_end_time_type)
            if proposed_end_time_type
            else None
        )

        return await service.create_account_budget_proposal(
            ctx=ctx,
            customer_id=customer_id,
            proposal_type=proposal_type_enum,
            billing_setup=billing_setup,
            proposed_name=proposed_name,
            proposed_start_time_type=start_time_enum,
            proposed_spending_limit_type=spending_limit_enum,
            proposed_spending_limit_micros=proposed_spending_limit_micros,
            proposed_start_date_time=proposed_start_date_time,
            proposed_end_date_time=proposed_end_date_time,
            proposed_end_time_type=end_time_enum,
        )

    async def update_account_budget_proposal(
        ctx: Context,
        customer_id: str,
        account_budget: str,
        billing_setup: str,
        proposed_name: Optional[str] = None,
        proposed_spending_limit_micros: Optional[int] = None,
        proposed_end_date_time: Optional[str] = None,
        proposed_start_date_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an UPDATE proposal for an existing account budget.

        Args:
            customer_id: The customer ID
            account_budget: Resource name of the account budget to update
            billing_setup: Resource name of the billing setup
            proposed_name: Optional new name for the account budget
            proposed_spending_limit_micros: Optional new spending limit in micros
            proposed_end_date_time: Optional new end date/time (YYYY-MM-DD HH:MM:SS)
            proposed_start_date_time: Optional new start date/time (YYYY-MM-DD HH:MM:SS)

        Returns:
            Created update proposal details with resource_name
        """
        return await service.update_account_budget_proposal(
            ctx=ctx,
            customer_id=customer_id,
            account_budget=account_budget,
            billing_setup=billing_setup,
            proposed_name=proposed_name,
            proposed_spending_limit_micros=proposed_spending_limit_micros,
            proposed_end_date_time=proposed_end_date_time,
            proposed_start_date_time=proposed_start_date_time,
        )

    async def list_account_budget_proposals(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List account budget proposals for a customer.

        Args:
            customer_id: The customer ID

        Returns:
            List of account budget proposals with details including status and spending limits
        """
        return await service.list_account_budget_proposals(
            ctx=ctx,
            customer_id=customer_id,
        )

    async def remove_account_budget_proposal(
        ctx: Context,
        customer_id: str,
        proposal_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an account budget proposal.

        Args:
            customer_id: The customer ID
            proposal_resource_name: Resource name of the proposal to remove

        Returns:
            Removal result with status
        """
        return await service.remove_account_budget_proposal(
            ctx=ctx,
            customer_id=customer_id,
            proposal_resource_name=proposal_resource_name,
        )

    tools.extend(
        [
            create_account_budget_proposal,
            update_account_budget_proposal,
            list_account_budget_proposals,
            remove_account_budget_proposal,
        ]
    )
    return tools


def register_account_budget_proposal_tools(
    mcp: FastMCP[Any],
) -> AccountBudgetProposalService:
    """Register account budget proposal tools with the MCP server.

    Returns the AccountBudgetProposalService instance for testing purposes.
    """
    service = AccountBudgetProposalService()
    tools = create_account_budget_proposal_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
