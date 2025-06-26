"""Shared set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.shared_set_status import SharedSetStatusEnum
from google.ads.googleads.v20.enums.types.shared_set_type import SharedSetTypeEnum
from google.ads.googleads.v20.resources.types.shared_set import SharedSet
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.services.shared_set_service import (
    SharedSetServiceClient,
)
from google.ads.googleads.v20.services.services.campaign_shared_set_service import (
    CampaignSharedSetServiceClient,
)
from google.ads.googleads.v20.services.types.shared_set_service import (
    MutateSharedSetsRequest,
    MutateSharedSetsResponse,
    SharedSetOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class SharedSetService:
    """Shared set service for managing shared negative keyword lists."""

    def __init__(self) -> None:
        """Initialize the shared set service."""
        self._client: Optional[SharedSetServiceClient] = None

    @property
    def client(self) -> SharedSetServiceClient:
        """Get the shared set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("SharedSetService")
        assert self._client is not None
        return self._client

    async def create_shared_set(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        type: SharedSetTypeEnum.SharedSetType = SharedSetTypeEnum.SharedSetType.NEGATIVE_KEYWORDS,
        status: SharedSetStatusEnum.SharedSetStatus = SharedSetStatusEnum.SharedSetStatus.ENABLED,
    ) -> Dict[str, Any]:
        """Create a new shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The name of the shared set
            type: Type of shared set (NEGATIVE_KEYWORDS or NEGATIVE_PLACEMENTS)
            status: Status (ENABLED or REMOVED)

        Returns:
            Created shared set details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create shared set
            shared_set = SharedSet()
            shared_set.name = name
            shared_set.type_ = type
            shared_set.status = status

            # Create operation
            operation = SharedSetOperation()
            operation.create = shared_set

            # Create request
            request = MutateSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateSharedSetsResponse = self.client.mutate_shared_sets(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created shared set '{name}' ({type})",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create shared set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_shared_set(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        name: Optional[str] = None,
        status: Optional[SharedSetStatusEnum.SharedSetStatus] = None,
    ) -> Dict[str, Any]:
        """Update an existing shared set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID to update
            name: New name (optional)
            status: New status (optional)

        Returns:
            Updated shared set details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            # Create shared set with resource name
            shared_set = SharedSet()
            shared_set.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                shared_set.name = name
                update_mask_fields.append("name")

            if status is not None:
                shared_set.status = status
                update_mask_fields.append("status")

            # Create operation
            operation = SharedSetOperation()
            operation.update = shared_set
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_shared_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated shared set {shared_set_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update shared set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_shared_sets(
        self,
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List shared sets in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            type_filter: Optional filter by type
            status_filter: Optional filter by status

        Returns:
            List of shared sets
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
                    shared_set.id,
                    shared_set.name,
                    shared_set.type,
                    shared_set.member_count,
                    shared_set.reference_count,
                    shared_set.status,
                    shared_set.resource_name
                FROM shared_set
            """

            # Add filters
            conditions = []
            if type_filter:
                conditions.append(f"shared_set.type = '{type_filter}'")
            if status_filter:
                conditions.append(f"shared_set.status = '{status_filter}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY shared_set.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            shared_sets = []
            for row in response:
                shared_sets.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(shared_sets)} shared sets",
            )

            return shared_sets

        except Exception as e:
            error_msg = f"Failed to list shared sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def attach_shared_set_to_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        campaign_ids: List[str],
    ) -> Dict[str, Any]:
        """Attach a shared set to campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_id: The shared set ID
            campaign_ids: List of campaign IDs to attach

        Returns:
            Attachment result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use CampaignSharedSetService
            sdk_client = get_sdk_client()
            campaign_shared_set_service: CampaignSharedSetServiceClient = (
                sdk_client.client.get_service("CampaignSharedSetService")
            )

            from google.ads.googleads.v20.resources.types.campaign_shared_set import (
                CampaignSharedSet,
            )
            from google.ads.googleads.v20.services.types.campaign_shared_set_service import (
                CampaignSharedSetOperation,
                MutateCampaignSharedSetsRequest,
            )

            raise NotImplementedError

            # Create operations
            operations = []
            shared_set_resource = f"customers/{customer_id}/sharedSets/{shared_set_id}"

            for campaign_id in campaign_ids:
                campaign_shared_set = CampaignSharedSet()
                campaign_shared_set.campaign = (
                    f"customers/{customer_id}/campaigns/{campaign_id}"
                )
                campaign_shared_set.shared_set = shared_set_resource

                operation = CampaignSharedSetOperation()
                operation.create = campaign_shared_set
                operations.append(operation)

            # Create request
            request = MutateCampaignSharedSetsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            campaign_shared_set_service.mutate_campaign_shared_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Attached shared set {shared_set_id} to {len(campaign_ids)} campaigns",
            )

            # Return serialized response
            # return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to attach shared set to campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_shared_set_tools(
    service: SharedSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the shared set service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_shared_set(
        ctx: Context,
        customer_id: str,
        name: str,
        type: str = "NEGATIVE_KEYWORDS",
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new shared set for negative keywords or placements.

        Args:
            customer_id: The customer ID
            name: The name of the shared set
            type: Type of shared set - NEGATIVE_KEYWORDS or NEGATIVE_PLACEMENTS
            status: Status - ENABLED or REMOVED

        Returns:
            Created shared set details with resource_name and shared_set_id
        """
        # Convert string enums to proper enum types
        type_enum = getattr(SharedSetTypeEnum.SharedSetType, type)
        status_enum = getattr(SharedSetStatusEnum.SharedSetStatus, status)

        return await service.create_shared_set(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            type=type_enum,
            status=status_enum,
        )

    async def update_shared_set(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing shared set.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID to update
            name: New name (optional)
            status: New status - ENABLED or REMOVED (optional)

        Returns:
            Updated shared set details with updated_fields list
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(SharedSetStatusEnum.SharedSetStatus, status) if status else None
        )

        return await service.update_shared_set(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            name=name,
            status=status_enum,
        )

    async def list_shared_sets(
        ctx: Context,
        customer_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List shared sets in the account.

        Args:
            customer_id: The customer ID
            type_filter: Optional filter by type - NEGATIVE_KEYWORDS or NEGATIVE_PLACEMENTS
            status_filter: Optional filter by status - ENABLED or REMOVED

        Returns:
            List of shared sets with details including member_count and reference_count
        """
        return await service.list_shared_sets(
            ctx=ctx,
            customer_id=customer_id,
            type_filter=type_filter,
            status_filter=status_filter,
        )

    async def attach_shared_set_to_campaigns(
        ctx: Context,
        customer_id: str,
        shared_set_id: str,
        campaign_ids: List[str],
    ) -> Dict[str, Any]:
        """Attach a shared set to one or more campaigns.

        Args:
            customer_id: The customer ID
            shared_set_id: The shared set ID to attach
            campaign_ids: List of campaign IDs to attach the shared set to

        Returns:
            Attachment result with status
        """
        return await service.attach_shared_set_to_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_id=shared_set_id,
            campaign_ids=campaign_ids,
        )

    tools.extend(
        [
            create_shared_set,
            update_shared_set,
            list_shared_sets,
            attach_shared_set_to_campaigns,
        ]
    )
    return tools


def register_shared_set_tools(mcp: FastMCP[Any]) -> SharedSetService:
    """Register shared set tools with the MCP server.

    Returns the SharedSetService instance for testing purposes.
    """
    service = SharedSetService()
    tools = create_shared_set_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
