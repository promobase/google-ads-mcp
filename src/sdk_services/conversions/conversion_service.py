"""Conversion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.attribution_model import (
    AttributionModelEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_category import (
    ConversionActionCategoryEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_counting_type import (
    ConversionActionCountingTypeEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_status import (
    ConversionActionStatusEnum,
)
from google.ads.googleads.v20.enums.types.conversion_action_type import (
    ConversionActionTypeEnum,
)
from google.ads.googleads.v20.enums.types.data_driven_model_status import (
    DataDrivenModelStatusEnum,
)
from google.ads.googleads.v20.resources.types.conversion_action import (
    ConversionAction,
)
from google.ads.googleads.v20.services.services.conversion_action_service import (
    ConversionActionServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_action_service import (
    ConversionActionOperation,
    MutateConversionActionsRequest,
    MutateConversionActionsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ConversionService:
    """Conversion service for managing Google Ads conversion actions."""

    def __init__(self) -> None:
        """Initialize the conversion service."""
        self._client: Optional[ConversionActionServiceClient] = None

    @property
    def client(self) -> ConversionActionServiceClient:
        """Get the conversion action service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ConversionActionService")
        assert self._client is not None
        return self._client

    async def create_conversion_action(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        category: str = "PURCHASE",
        type: str = "WEBPAGE",
        status: str = "ENABLED",
        value_settings: Optional[Dict[str, Any]] = None,
        counting_type: str = "ONE_PER_CLICK",
        attribution_model: str = "DATA_DRIVEN",
        click_through_lookback_window_days: int = 30,
        view_through_lookback_window_days: int = 1,
    ) -> Dict[str, Any]:
        """Create a new conversion action.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Conversion action name
            category: Category (PURCHASE, LEAD, SIGNUP, PAGE_VIEW, etc.)
            type: Type (WEBPAGE, APP, PHONE_CALLS, IMPORT)
            status: Status (ENABLED, REMOVED, HIDDEN)
            value_settings: Optional dict with default_value and always_use_default_value
            counting_type: ONE_PER_CLICK or MANY_PER_CLICK
            attribution_model: Attribution model (DATA_DRIVEN, LAST_CLICK, etc.)
            click_through_lookback_window_days: Click lookback window (1-90)
            view_through_lookback_window_days: View lookback window (1-30)

        Returns:
            Created conversion action details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create conversion action
            conversion_action = ConversionAction()
            conversion_action.name = name

            # Set enums
            conversion_action.status = getattr(
                ConversionActionStatusEnum.ConversionActionStatus, status
            )
            conversion_action.type_ = getattr(
                ConversionActionTypeEnum.ConversionActionType, type
            )
            conversion_action.category = getattr(
                ConversionActionCategoryEnum.ConversionActionCategory, category
            )

            # Set counting type
            conversion_action.counting_type = getattr(
                ConversionActionCountingTypeEnum.ConversionActionCountingType,
                counting_type,
            )

            # Set value settings
            if value_settings:
                value_settings_obj = ConversionAction.ValueSettings()
                if "default_value" in value_settings:
                    value_settings_obj.default_value = value_settings["default_value"]
                if "always_use_default_value" in value_settings:
                    value_settings_obj.always_use_default_value = value_settings[
                        "always_use_default_value"
                    ]
                conversion_action.value_settings = value_settings_obj
            else:
                # Default value settings
                value_settings_obj = ConversionAction.ValueSettings()
                value_settings_obj.default_value = 0
                value_settings_obj.always_use_default_value = False
                conversion_action.value_settings = value_settings_obj

            # Set attribution model
            attribution_settings = ConversionAction.AttributionModelSettings()
            attribution_settings.attribution_model = getattr(
                AttributionModelEnum.AttributionModel, attribution_model
            )
            attribution_settings.data_driven_model_status = (
                DataDrivenModelStatusEnum.DataDrivenModelStatus.AVAILABLE
            )
            conversion_action.attribution_model_settings = attribution_settings

            # Set lookback windows
            conversion_action.click_through_lookback_window_days = (
                click_through_lookback_window_days
            )
            conversion_action.view_through_lookback_window_days = (
                view_through_lookback_window_days
            )

            # Create operation
            operation = ConversionActionOperation()
            operation.create = conversion_action

            # Create request
            request = MutateConversionActionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateConversionActionsResponse = (
                self.client.mutate_conversion_actions(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create conversion action: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_conversion_action(
        self,
        ctx: Context,
        customer_id: str,
        conversion_action_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        default_value: Optional[float] = None,
        always_use_default_value: Optional[bool] = None,
        counting_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing conversion action.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_action_id: The conversion action ID to update
            name: New name (optional)
            status: New status (optional)
            default_value: New default value (optional)
            always_use_default_value: Whether to always use default value (optional)
            counting_type: New counting type (optional)

        Returns:
            Updated conversion action details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            )

            # Create conversion action with resource name
            conversion_action = ConversionAction()
            conversion_action.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                conversion_action.name = name
                update_mask_fields.append("name")

            if status is not None:
                conversion_action.status = getattr(
                    ConversionActionStatusEnum.ConversionActionStatus, status
                )
                update_mask_fields.append("status")

            if counting_type is not None:
                conversion_action.counting_type = getattr(
                    ConversionActionCountingTypeEnum.ConversionActionCountingType,
                    counting_type,
                )
                update_mask_fields.append("counting_type")

            # Update value settings if any value-related field is provided
            if default_value is not None or always_use_default_value is not None:
                value_settings = ConversionAction.ValueSettings()
                if default_value is not None:
                    value_settings.default_value = default_value
                    update_mask_fields.append("value_settings.default_value")
                if always_use_default_value is not None:
                    value_settings.always_use_default_value = always_use_default_value
                    update_mask_fields.append("value_settings.always_use_default_value")
                conversion_action.value_settings = value_settings

            # Create the operation
            operation = ConversionActionOperation()
            operation.update = conversion_action
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateConversionActionsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = self.client.mutate_conversion_actions(request=request)

            await ctx.log(
                level="info",
                message=f"Updated conversion action {conversion_action_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update conversion action: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_tools(
    service: ConversionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_conversion_action(
        ctx: Context,
        customer_id: str,
        name: str,
        category: str = "PURCHASE",
        type: str = "WEBPAGE",
        status: str = "ENABLED",
        value_settings: Optional[Dict[str, Any]] = None,
        counting_type: str = "ONE_PER_CLICK",
        attribution_model: str = "DATA_DRIVEN",
        click_through_lookback_window_days: int = 30,
        view_through_lookback_window_days: int = 1,
    ) -> Dict[str, Any]:
        """Create a new conversion action.

        Args:
            customer_id: The customer ID
            name: Conversion action name
            category: Category - PURCHASE, LEAD, SIGNUP, PAGE_VIEW, DOWNLOAD, etc.
            type: Type - WEBPAGE, APP, PHONE_CALLS, IMPORT
            status: Status - ENABLED, REMOVED, HIDDEN
            value_settings: Optional dict with:
                - default_value: Default conversion value
                - always_use_default_value: Whether to always use default value
            counting_type: ONE_PER_CLICK or MANY_PER_CLICK
            attribution_model: Attribution model - DATA_DRIVEN, LAST_CLICK, FIRST_CLICK, LINEAR, TIME_DECAY, POSITION_BASED
            click_through_lookback_window_days: Click lookback window (1-90 days)
            view_through_lookback_window_days: View lookback window (1-30 days)

        Returns:
            Created conversion action details
        """
        return await service.create_conversion_action(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            category=category,
            type=type,
            status=status,
            value_settings=value_settings,
            counting_type=counting_type,
            attribution_model=attribution_model,
            click_through_lookback_window_days=click_through_lookback_window_days,
            view_through_lookback_window_days=view_through_lookback_window_days,
        )

    async def update_conversion_action(
        ctx: Context,
        customer_id: str,
        conversion_action_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        default_value: Optional[float] = None,
        always_use_default_value: Optional[bool] = None,
        counting_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing conversion action.

        Args:
            customer_id: The customer ID
            conversion_action_id: The conversion action ID to update
            name: New name (optional)
            status: New status - ENABLED, REMOVED, HIDDEN (optional)
            default_value: New default value (optional)
            always_use_default_value: Whether to always use default value (optional)
            counting_type: New counting type - ONE_PER_CLICK or MANY_PER_CLICK (optional)

        Returns:
            Updated conversion action details
        """
        return await service.update_conversion_action(
            ctx=ctx,
            customer_id=customer_id,
            conversion_action_id=conversion_action_id,
            name=name,
            status=status,
            default_value=default_value,
            always_use_default_value=always_use_default_value,
            counting_type=counting_type,
        )

    tools.extend([create_conversion_action, update_conversion_action])
    return tools


def register_conversion_tools(mcp: FastMCP[Any]) -> ConversionService:
    """Register conversion tools with the MCP server.

    Returns the ConversionService instance for testing purposes.
    """
    service = ConversionService()
    tools = create_conversion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
