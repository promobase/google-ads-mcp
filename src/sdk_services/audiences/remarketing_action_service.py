"""Remarketing action service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.remarketing_action import (
    RemarketingAction,
)
from google.ads.googleads.v20.services.services.remarketing_action_service import (
    RemarketingActionServiceClient,
)
from google.ads.googleads.v20.services.types.remarketing_action_service import (
    MutateRemarketingActionsRequest,
    MutateRemarketingActionsResponse,
    RemarketingActionOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class RemarketingActionService:
    """Remarketing action service for managing remarketing tags and lists."""

    def __init__(self) -> None:
        """Initialize the remarketing action service."""
        self._client: Optional[RemarketingActionServiceClient] = None

    @property
    def client(self) -> RemarketingActionServiceClient:
        """Get the remarketing action service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("RemarketingActionService")
        assert self._client is not None
        return self._client

    async def create_remarketing_action(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
    ) -> Dict[str, Any]:
        """Create a new remarketing action (tag).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The remarketing action name

        Returns:
            Created remarketing action details with tag snippets
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create remarketing action
            remarketing_action = RemarketingAction()
            remarketing_action.name = name

            # Create operation
            operation = RemarketingActionOperation()
            operation.create = remarketing_action

            # Create request
            request = MutateRemarketingActionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateRemarketingActionsResponse = (
                self.client.mutate_remarketing_actions(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created remarketing action '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create remarketing action: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def _get_remarketing_action(
        self,
        ctx: Context,
        customer_id: str,
        remarketing_action_id: str,
    ) -> Dict[str, Any]:
        """Get details of a remarketing action including tag snippets.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            remarketing_action_id: The remarketing action ID

        Returns:
            Remarketing action details with tag snippets
        """
        try:
            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = f"""
                SELECT
                    remarketing_action.id,
                    remarketing_action.name,
                    remarketing_action.tag_snippets,
                    remarketing_action.resource_name
                FROM remarketing_action
                WHERE remarketing_action.id = {remarketing_action_id}
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process result
            for row in response:
                ra = row.remarketing_action

                # Process tag snippets
                tag_snippets = []
                for snippet in ra.tag_snippets:
                    tag_snippets.append(
                        {
                            "type": snippet.type_.name if snippet.type_ else "UNKNOWN",
                            "page_format": snippet.page_format.name
                            if snippet.page_format
                            else "UNKNOWN",
                            "global_site_tag": snippet.global_site_tag,
                            "event_snippet": snippet.event_snippet,
                        }
                    )

            return serialize_proto_message(response)

            raise Exception(f"Remarketing action {remarketing_action_id} not found")

        except Exception as e:
            error_msg = f"Failed to get remarketing action: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_remarketing_action(
        self,
        ctx: Context,
        customer_id: str,
        remarketing_action_id: str,
        name: str,
    ) -> Dict[str, Any]:
        """Update a remarketing action name.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            remarketing_action_id: The remarketing action ID to update
            name: New name

        Returns:
            Updated remarketing action details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/remarketingActions/{remarketing_action_id}"
            )

            # Create remarketing action with resource name
            remarketing_action = RemarketingAction()
            remarketing_action.resource_name = resource_name
            remarketing_action.name = name

            # Create operation
            operation = RemarketingActionOperation()
            operation.update = remarketing_action
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["name"]))

            # Create request
            request = MutateRemarketingActionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_remarketing_actions(request=request)

            await ctx.log(
                level="info",
                message=f"Updated remarketing action {remarketing_action_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update remarketing action: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_remarketing_actions(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List all remarketing actions in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of remarketing actions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    remarketing_action.id,
                    remarketing_action.name,
                    remarketing_action.resource_name
                FROM remarketing_action
                ORDER BY remarketing_action.name
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            remarketing_actions = []
            for row in response:
                ra = row.remarketing_action
                remarketing_actions.append(
                    {
                        "remarketing_action_id": str(ra.id),
                        "name": ra.name,
                        "resource_name": ra.resource_name,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Found {len(remarketing_actions)} remarketing actions",
            )

            return remarketing_actions

        except Exception as e:
            error_msg = f"Failed to list remarketing actions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_remarketing_action_tags(
        self,
        ctx: Context,
        customer_id: str,
        remarketing_action_id: str,
    ) -> Dict[str, Any]:
        """Get tag snippets for a remarketing action.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            remarketing_action_id: The remarketing action ID

        Returns:
            Tag snippets for the remarketing action
        """
        try:
            customer_id = format_customer_id(customer_id)
            return await self._get_remarketing_action(
                ctx, customer_id, remarketing_action_id
            )

        except Exception as e:
            error_msg = f"Failed to get remarketing action tags: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_remarketing_action_tools(
    service: RemarketingActionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the remarketing action service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_remarketing_action(
        ctx: Context,
        customer_id: str,
        name: str,
    ) -> Dict[str, Any]:
        """Create a new remarketing action (tag) for tracking website visitors.

        Args:
            customer_id: The customer ID
            name: The remarketing action name

        Returns:
            Created remarketing action with:
            - resource_name: The resource identifier
            - remarketing_action_id: The numeric ID
            - name: The action name
            - tag_snippets: List of tag snippets including:
                - global_site_tag: The global site tag to add to all pages
                - event_snippet: The event snippet for specific conversions
        """
        return await service.create_remarketing_action(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
        )

    async def update_remarketing_action(
        ctx: Context,
        customer_id: str,
        remarketing_action_id: str,
        name: str,
    ) -> Dict[str, Any]:
        """Update a remarketing action name.

        Args:
            customer_id: The customer ID
            remarketing_action_id: The remarketing action ID to update
            name: New name for the remarketing action

        Returns:
            Updated remarketing action details
        """
        return await service.update_remarketing_action(
            ctx=ctx,
            customer_id=customer_id,
            remarketing_action_id=remarketing_action_id,
            name=name,
        )

    async def list_remarketing_actions(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List all remarketing actions in the account.

        Args:
            customer_id: The customer ID

        Returns:
            List of remarketing actions with basic details
        """
        return await service.list_remarketing_actions(
            ctx=ctx,
            customer_id=customer_id,
        )

    async def get_remarketing_action_tags(
        ctx: Context,
        customer_id: str,
        remarketing_action_id: str,
    ) -> Dict[str, Any]:
        """Get tag snippets for a remarketing action.

        Use this to retrieve the JavaScript tags to add to your website.

        Args:
            customer_id: The customer ID
            remarketing_action_id: The remarketing action ID

        Returns:
            Tag information including:
            - global_site_tag: Add to all pages of your website
            - event_snippet: Add to specific conversion pages
            - Instructions for implementation
        """
        return await service.get_remarketing_action_tags(
            ctx=ctx,
            customer_id=customer_id,
            remarketing_action_id=remarketing_action_id,
        )

    tools.extend(
        [
            create_remarketing_action,
            update_remarketing_action,
            list_remarketing_actions,
            get_remarketing_action_tags,
        ]
    )
    return tools


def register_remarketing_action_tools(mcp: FastMCP[Any]) -> RemarketingActionService:
    """Register remarketing action tools with the MCP server.

    Returns the RemarketingActionService instance for testing purposes.
    """
    service = RemarketingActionService()
    tools = create_remarketing_action_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
