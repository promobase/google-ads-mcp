"""Google Ads Custom Conversion Goal Service

This module provides functionality for managing custom conversion goals in Google Ads.
Custom conversion goals allow making arbitrary conversion actions biddable.
"""

from typing import List, Optional

from google.ads.googleads.v20.enums.types.custom_conversion_goal_status import CustomConversionGoalStatusEnum
from google.ads.googleads.v20.enums.types.response_content_type import ResponseContentTypeEnum
from google.ads.googleads.v20.resources.types.custom_conversion_goal import CustomConversionGoal
from google.ads.googleads.v20.services.services.custom_conversion_goal_service import CustomConversionGoalServiceClient
from google.ads.googleads.v20.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
    MutateCustomConversionGoalsRequest,
    MutateCustomConversionGoalsResponse,
)


class CustomConversionGoalService:
    """Service for managing Google Ads custom conversion goals."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("CustomConversionGoalService")

    def mutate_custom_conversion_goals(
        self,
        customer_id: str,
        operations: List[CustomConversionGoalOperation],
        validate_only: bool = False,
        response_content_type: Optional[ResponseContentTypeEnum.ResponseContentType] = None,
    ) -> MutateCustomConversionGoalsResponse:
        """Mutate custom conversion goals.

        Args:
            customer_id: The customer ID
            operations: List of custom conversion goal operations
            validate_only: Whether to only validate the request
            response_content_type: The response content type setting

        Returns:
            MutateCustomConversionGoalsResponse: The response containing results
        """
        request = MutateCustomConversionGoalsRequest(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )
        
        if response_content_type is not None:
            request.response_content_type = response_content_type
            
        return self.service.mutate_custom_conversion_goals(request=request)

    def create_custom_conversion_goal_operation(
        self,
        name: str,
        conversion_actions: List[str],
        status: CustomConversionGoalStatusEnum.CustomConversionGoalStatus = CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for creation.

        Args:
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to create the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(
            name=name,
            conversion_actions=conversion_actions,
            status=status,
        )

        return CustomConversionGoalOperation(create=custom_conversion_goal)

    def update_custom_conversion_goal_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        conversion_actions: Optional[List[str]] = None,
        status: Optional[CustomConversionGoalStatusEnum.CustomConversionGoalStatus] = None,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for update.

        Args:
            resource_name: The custom conversion goal resource name
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to update the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(resource_name=resource_name)

        update_mask = []
        if name is not None:
            custom_conversion_goal.name = name
            update_mask.append("name")
        if conversion_actions is not None:
            custom_conversion_goal.conversion_actions = conversion_actions
            update_mask.append("conversion_actions")
        if status is not None:
            custom_conversion_goal.status = status
            update_mask.append("status")

        return CustomConversionGoalOperation(
            update=custom_conversion_goal,
            update_mask={"paths": update_mask},
        )

    def remove_custom_conversion_goal_operation(self, resource_name: str) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for removal.

        Args:
            resource_name: The custom conversion goal resource name

        Returns:
            CustomConversionGoalOperation: The operation to remove the custom conversion goal
        """
        return CustomConversionGoalOperation(remove=resource_name)