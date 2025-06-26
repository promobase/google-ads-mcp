"""User list service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.user_lists import (
    BasicUserListInfo,
    CrmBasedUserListInfo,
    LogicalUserListInfo,
    LogicalUserListOperandInfo,
    SimilarUserListInfo,
    UserListLogicalRuleInfo,
)
from google.ads.googleads.v20.enums.types.user_list_logical_rule_operator import (
    UserListLogicalRuleOperatorEnum,
)
from google.ads.googleads.v20.enums.types.user_list_membership_status import (
    UserListMembershipStatusEnum,
)
from google.ads.googleads.v20.resources.types.user_list import UserList
from google.ads.googleads.v20.services.services.user_list_service import (
    UserListServiceClient,
)
from google.ads.googleads.v20.services.types.user_list_service import (
    MutateUserListsRequest,
    MutateUserListsResponse,
    UserListOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class UserListService:
    """User list service for managing Google Ads remarketing lists."""

    def __init__(self) -> None:
        """Initialize the user list service."""
        self._client: Optional[UserListServiceClient] = None

    @property
    def client(self) -> UserListServiceClient:
        """Get the user list service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("UserListService")
        assert self._client is not None
        return self._client

    async def create_basic_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: int = 30,
        membership_status: str = "OPEN",
    ) -> Dict[str, Any]:
        """Create a basic remarketing user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days)
            membership_status: OPEN or CLOSED

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            user_list.membership_status = getattr(
                UserListMembershipStatusEnum.UserListMembershipStatus, membership_status
            )
            user_list.membership_life_span = membership_life_span

            # Create basic user list info
            basic_user_list = BasicUserListInfo()
            user_list.basic_user_list = basic_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created basic user list '{name}' with {membership_life_span} day membership",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create basic user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_crm_based_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: int = 30,
        upload_key_type: str = "CONTACT_INFO",
        data_source_type: str = "FIRST_PARTY",
    ) -> Dict[str, Any]:
        """Create a CRM-based user list for customer match.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days)
            upload_key_type: CONTACT_INFO, CRM_ID, or MOBILE_ADVERTISING_ID
            data_source_type: FIRST_PARTY or THIRD_PARTY

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            user_list.membership_status = (
                UserListMembershipStatusEnum.UserListMembershipStatus.OPEN
            )
            user_list.membership_life_span = membership_life_span

            # Create CRM-based user list info
            crm_user_list = CrmBasedUserListInfo()
            # Set upload key type using enum
            from google.ads.googleads.v20.enums.types.customer_match_upload_key_type import (
                CustomerMatchUploadKeyTypeEnum,
            )

            crm_user_list.upload_key_type = getattr(
                CustomerMatchUploadKeyTypeEnum.CustomerMatchUploadKeyType,
                upload_key_type,
            )

            user_list.crm_based_user_list = crm_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created CRM-based user list '{name}' for customer match",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create CRM-based user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_similar_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        seed_user_list_ids: List[str],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a similar audiences user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            seed_user_list_ids: List of user list IDs to base similarity on
            description: Optional description

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            user_list.membership_status = (
                UserListMembershipStatusEnum.UserListMembershipStatus.OPEN
            )

            # Create similar user list info
            similar_user_list = SimilarUserListInfo()
            for seed_list_id in seed_user_list_ids:
                seed_resource = f"customers/{customer_id}/userLists/{seed_list_id}"
                similar_user_list.seed_user_list = seed_resource

            user_list.similar_user_list = similar_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created similar user list '{name}' based on {len(seed_user_list_ids)} seed lists",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create similar user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_logical_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        rules: List[Dict[str, Any]],
        rule_operator: str = "ALL",
        description: Optional[str] = None,
        membership_life_span: int = 30,
    ) -> Dict[str, Any]:
        """Create a logical (combined) user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            rules: List of rule dictionaries with user_list_ids and operator
            rule_operator: ALL, ANY, or NONE
            description: Optional description
            membership_life_span: How long users remain in the list (days)

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            user_list.membership_status = (
                UserListMembershipStatusEnum.UserListMembershipStatus.OPEN
            )
            user_list.membership_life_span = membership_life_span

            # Create logical user list info
            logical_user_list = LogicalUserListInfo()

            # Create user list logical rule info
            for rule in rules:
                user_list_logical_rule_info = UserListLogicalRuleInfo()
                user_list_logical_rule_info.operator = getattr(
                    UserListLogicalRuleOperatorEnum.UserListLogicalRuleOperator,
                    rule.get("operator", "ALL"),
                )

                # Add user lists to the rule
                for user_list_id in rule.get("user_list_ids", []):
                    user_list_resource = (
                        f"customers/{customer_id}/userLists/{user_list_id}"
                    )
                    operand = LogicalUserListOperandInfo()
                    operand.user_list = user_list_resource
                    user_list_logical_rule_info.rule_operands.append(operand)

                logical_user_list.rules.append(user_list_logical_rule_info)

            user_list.logical_user_list = logical_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created logical user list '{name}' with {len(rules)} rules",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create logical user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_user_list(
        self,
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        membership_status: Optional[str] = None,
        membership_life_span: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_id: The user list ID to update
            name: New name (optional)
            description: New description (optional)
            membership_status: New status - OPEN or CLOSED (optional)
            membership_life_span: New membership life span in days (optional)

        Returns:
            Updated user list details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/userLists/{user_list_id}"

            # Create user list with resource name
            user_list = UserList()
            user_list.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                user_list.name = name
                update_mask_fields.append("name")

            if description is not None:
                user_list.description = description
                update_mask_fields.append("description")

            if membership_status is not None:
                user_list.membership_status = getattr(
                    UserListMembershipStatusEnum.UserListMembershipStatus,
                    membership_status,
                )
                update_mask_fields.append("membership_status")

            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span
                update_mask_fields.append("membership_life_span")

            # Create the operation
            operation = UserListOperation()
            operation.update = user_list
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_user_lists(request=request)

            await ctx.log(
                level="info",
                message=f"Updated user list {user_list_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_user_list_tools(
    service: UserListService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the user list service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_basic_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: int = 30,
        membership_status: str = "OPEN",
    ) -> Dict[str, Any]:
        """Create a basic remarketing user list.

        Args:
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days, 0-540)
            membership_status: OPEN (can add users) or CLOSED

        Returns:
            Created user list details including resource_name and user_list_id
        """
        return await service.create_basic_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            membership_life_span=membership_life_span,
            membership_status=membership_status,
        )

    async def create_crm_based_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: int = 30,
        upload_key_type: str = "CONTACT_INFO",
        data_source_type: str = "FIRST_PARTY",
    ) -> Dict[str, Any]:
        """Create a CRM-based user list for customer match.

        Args:
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days, 0-540)
            upload_key_type: Type of data - CONTACT_INFO, CRM_ID, or MOBILE_ADVERTISING_ID
            data_source_type: FIRST_PARTY or THIRD_PARTY

        Returns:
            Created user list details including resource_name and user_list_id
        """
        return await service.create_crm_based_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            membership_life_span=membership_life_span,
            upload_key_type=upload_key_type,
            data_source_type=data_source_type,
        )

    async def create_similar_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        seed_user_list_ids: List[str],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a similar audiences user list.

        Args:
            customer_id: The customer ID
            name: User list name
            seed_user_list_ids: List of user list IDs to base similarity on
            description: Optional description

        Returns:
            Created user list details including resource_name and user_list_id
        """
        return await service.create_similar_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            seed_user_list_ids=seed_user_list_ids,
            description=description,
        )

    async def create_logical_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        rules: List[Dict[str, Any]],
        rule_operator: str = "ALL",
        description: Optional[str] = None,
        membership_life_span: int = 30,
    ) -> Dict[str, Any]:
        """Create a logical (combined) user list.

        Args:
            customer_id: The customer ID
            name: User list name
            rules: List of rule dictionaries, each with:
                - user_list_ids: List of user list IDs
                - operator: ALL, ANY, or NONE
            rule_operator: Top-level operator - ALL, ANY, or NONE
            description: Optional description
            membership_life_span: How long users remain in the list (days, 0-540)

        Example:
            rules=[
                {"user_list_ids": ["123", "456"], "operator": "ALL"},
                {"user_list_ids": ["789"], "operator": "NONE"}
            ]
            This creates: (Users in both 123 AND 456) AND (NOT in 789)

        Returns:
            Created user list details including resource_name and user_list_id
        """
        return await service.create_logical_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            rules=rules,
            rule_operator=rule_operator,
            description=description,
            membership_life_span=membership_life_span,
        )

    async def update_user_list(
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        membership_status: Optional[str] = None,
        membership_life_span: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing user list.

        Args:
            customer_id: The customer ID
            user_list_id: The user list ID to update
            name: New name (optional)
            description: New description (optional)
            membership_status: New status - OPEN or CLOSED (optional)
            membership_life_span: New membership life span in days (optional)

        Returns:
            Updated user list details with updated_fields list
        """
        return await service.update_user_list(
            ctx=ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            name=name,
            description=description,
            membership_status=membership_status,
            membership_life_span=membership_life_span,
        )

    tools.extend(
        [
            create_basic_user_list,
            create_crm_based_user_list,
            create_similar_user_list,
            create_logical_user_list,
            update_user_list,
        ]
    )
    return tools


def register_user_list_tools(mcp: FastMCP[Any]) -> UserListService:
    """Register user list tools with the MCP server.

    Returns the UserListService instance for testing purposes.
    """
    service = UserListService()
    tools = create_user_list_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
