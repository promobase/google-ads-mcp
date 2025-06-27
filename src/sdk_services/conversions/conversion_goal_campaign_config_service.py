"""Google Ads Conversion Goal Campaign Config Service

This module provides functionality for managing conversion goal campaign configurations in Google Ads.
Conversion goal campaign configs define how campaigns use conversion goals for optimization.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.conversion_goal_campaign_config import (
    ConversionGoalCampaignConfig,
)
from google.ads.googleads.v20.services.services.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigServiceClient,
)
from google.ads.googleads.v20.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsRequest,
    MutateConversionGoalCampaignConfigsResponse,
)

from src.sdk_client import get_sdk_client


class ConversionGoalCampaignConfigService:
    """Service for managing Google Ads conversion goal campaign configurations."""

    def __init__(self) -> None:
        """Initialize the conversion goal campaign config service."""
        self._client: Optional[ConversionGoalCampaignConfigServiceClient] = None

    @property
    def client(self) -> ConversionGoalCampaignConfigServiceClient:
        """Get the conversion goal campaign config service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ConversionGoalCampaignConfigService"
            )
        assert self._client is not None
        return self._client

    def mutate_conversion_goal_campaign_configs(
        self,
        customer_id: str,
        operations: List[ConversionGoalCampaignConfigOperation],
        validate_only: bool = False,
        response_content_type: Optional[
            ResponseContentTypeEnum.ResponseContentType
        ] = None,
    ) -> MutateConversionGoalCampaignConfigsResponse:
        """Mutate conversion goal campaign configurations.

        Args:
            customer_id: The customer ID
            operations: List of conversion goal campaign config operations
            validate_only: Whether to only validate the request
            response_content_type: The response content type setting

        Returns:
            MutateConversionGoalCampaignConfigsResponse: The response containing results
        """
        request = MutateConversionGoalCampaignConfigsRequest(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

        if response_content_type is not None:
            request.response_content_type = response_content_type

        return self.client.mutate_conversion_goal_campaign_configs(request=request)

    def update_conversion_goal_campaign_config_operation(
        self,
        resource_name: str,
        goal_config_level: Optional[GoalConfigLevelEnum.GoalConfigLevel] = None,
        custom_conversion_goal: Optional[str] = None,
    ) -> ConversionGoalCampaignConfigOperation:
        """Create a conversion goal campaign config operation for update.

        Args:
            resource_name: The conversion goal campaign config resource name
            goal_config_level: The level of goal config the campaign is using
            custom_conversion_goal: The custom conversion goal resource name

        Returns:
            ConversionGoalCampaignConfigOperation: The operation to update the conversion goal campaign config
        """
        conversion_goal_campaign_config = ConversionGoalCampaignConfig(
            resource_name=resource_name
        )

        update_mask = []
        if goal_config_level is not None:
            conversion_goal_campaign_config.goal_config_level = goal_config_level
            update_mask.append("goal_config_level")
        if custom_conversion_goal is not None:
            conversion_goal_campaign_config.custom_conversion_goal = (
                custom_conversion_goal
            )
            update_mask.append("custom_conversion_goal")

        return ConversionGoalCampaignConfigOperation(
            update=conversion_goal_campaign_config,
            update_mask={"paths": update_mask},
        )


def register_conversion_goal_campaign_config_tools(mcp: FastMCP[Any]) -> None:
    """Register conversion goal campaign config tools with the MCP server."""

    @mcp.tool
    async def mutate_conversion_goal_campaign_configs(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        validate_only: bool = False,
    ) -> str:
        """Create or update conversion goal campaign configurations.

        Args:
            customer_id: The customer ID
            operations: List of conversion goal campaign config operations
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = ConversionGoalCampaignConfigService()

        def _get_goal_config_level_enum(
            level_str: str,
        ) -> GoalConfigLevelEnum.GoalConfigLevel:
            """Convert string to goal config level enum."""
            if level_str == "CUSTOMER":
                return GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER
            elif level_str == "CAMPAIGN":
                return GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
            else:
                raise ValueError(f"Invalid goal config level: {level_str}")

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "update":
                goal_config_level = None
                if "goal_config_level" in op_data:
                    goal_config_level = _get_goal_config_level_enum(
                        op_data["goal_config_level"]
                    )

                operation = service.update_conversion_goal_campaign_config_operation(
                    resource_name=op_data["resource_name"],
                    goal_config_level=goal_config_level,
                    custom_conversion_goal=op_data.get("custom_conversion_goal"),
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_conversion_goal_campaign_configs(
            customer_id=customer_id,
            operations=ops,
            validate_only=validate_only,
        )

        return f"Successfully processed {len(response.results)} conversion goal campaign config operations"

    @mcp.tool
    async def update_conversion_goal_campaign_config(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        goal_config_level: Optional[str] = None,
        custom_conversion_goal: Optional[str] = None,
    ) -> str:
        """Update a conversion goal campaign configuration.

        Args:
            customer_id: The customer ID
            resource_name: The conversion goal campaign config resource name
            goal_config_level: The level of goal config (CUSTOMER or CAMPAIGN)
            custom_conversion_goal: The custom conversion goal resource name

        Returns:
            The updated conversion goal campaign config resource name
        """
        service = ConversionGoalCampaignConfigService()

        def _get_goal_config_level_enum(
            level_str: str,
        ) -> GoalConfigLevelEnum.GoalConfigLevel:
            """Convert string to goal config level enum."""
            if level_str == "CUSTOMER":
                return GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER
            elif level_str == "CAMPAIGN":
                return GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
            else:
                raise ValueError(f"Invalid goal config level: {level_str}")

        goal_config_level_enum = None
        if goal_config_level is not None:
            goal_config_level_enum = _get_goal_config_level_enum(goal_config_level)

        operation = service.update_conversion_goal_campaign_config_operation(
            resource_name=resource_name,
            goal_config_level=goal_config_level_enum,
            custom_conversion_goal=custom_conversion_goal,
        )

        response = service.mutate_conversion_goal_campaign_configs(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated conversion goal campaign config: {result.resource_name}"
