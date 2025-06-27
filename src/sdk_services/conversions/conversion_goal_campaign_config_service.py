"""Google Ads Conversion Goal Campaign Config Service

This module provides functionality for managing conversion goal campaign configurations in Google Ads.
Conversion goal campaign configs define how campaigns use conversion goals for optimization.
"""

from typing import List, Optional

from google.ads.googleads.v20.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v20.enums.types.response_content_type import ResponseContentTypeEnum
from google.ads.googleads.v20.resources.types.conversion_goal_campaign_config import ConversionGoalCampaignConfig
from google.ads.googleads.v20.services.services.conversion_goal_campaign_config_service import ConversionGoalCampaignConfigServiceClient
from google.ads.googleads.v20.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsRequest,
    MutateConversionGoalCampaignConfigsResponse,
)


class ConversionGoalCampaignConfigService:
    """Service for managing Google Ads conversion goal campaign configurations."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("ConversionGoalCampaignConfigService")

    def mutate_conversion_goal_campaign_configs(
        self,
        customer_id: str,
        operations: List[ConversionGoalCampaignConfigOperation],
        validate_only: bool = False,
        response_content_type: Optional[ResponseContentTypeEnum.ResponseContentType] = None,
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
            
        return self.service.mutate_conversion_goal_campaign_configs(request=request)

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
        conversion_goal_campaign_config = ConversionGoalCampaignConfig(resource_name=resource_name)

        update_mask = []
        if goal_config_level is not None:
            conversion_goal_campaign_config.goal_config_level = goal_config_level
            update_mask.append("goal_config_level")
        if custom_conversion_goal is not None:
            conversion_goal_campaign_config.custom_conversion_goal = custom_conversion_goal
            update_mask.append("custom_conversion_goal")

        return ConversionGoalCampaignConfigOperation(
            update=conversion_goal_campaign_config,
            update_mask={"paths": update_mask},
        )