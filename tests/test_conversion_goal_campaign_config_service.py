"""Tests for Google Ads Conversion Goal Campaign Config Service"""

import pytest
from unittest.mock import Mock

from google.ads.googleads.v20.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v20.resources.types.conversion_goal_campaign_config import ConversionGoalCampaignConfig
from google.ads.googleads.v20.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsRequest,
    MutateConversionGoalCampaignConfigsResponse,
    MutateConversionGoalCampaignConfigResult,
)

from src.sdk_services.conversions.conversion_goal_campaign_config_service import ConversionGoalCampaignConfigService


class TestConversionGoalCampaignConfigService:
    """Test cases for ConversionGoalCampaignConfigService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service
        return client

    @pytest.fixture
    def conversion_goal_campaign_config_service(self, mock_client):
        """Create ConversionGoalCampaignConfigService instance with mock client"""
        return ConversionGoalCampaignConfigService(mock_client)

    def test_mutate_conversion_goal_campaign_configs(self, conversion_goal_campaign_config_service, mock_client):
        """Test mutating conversion goal campaign configs"""
        # Setup
        customer_id = "1234567890"
        operations = [ConversionGoalCampaignConfigOperation()]
        
        mock_response = MutateConversionGoalCampaignConfigsResponse(
            results=[MutateConversionGoalCampaignConfigResult(resource_name="customers/1234567890/conversionGoalCampaignConfigs/123")]
        )
        mock_client.get_service.return_value.mutate_conversion_goal_campaign_configs.return_value = mock_response

        # Execute
        response = conversion_goal_campaign_config_service.mutate_conversion_goal_campaign_configs(
            customer_id=customer_id,
            operations=operations,
            validate_only=False
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("ConversionGoalCampaignConfigService")
        
        # Verify request
        call_args = mock_client.get_service.return_value.mutate_conversion_goal_campaign_configs.call_args
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.validate_only == False

    def test_update_conversion_goal_campaign_config_operation(self, conversion_goal_campaign_config_service):
        """Test creating conversion goal campaign config operation for update"""
        # Setup
        resource_name = "customers/1234567890/conversionGoalCampaignConfigs/123"
        goal_config_level = GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
        custom_conversion_goal = "customers/1234567890/customConversionGoals/456"

        # Execute
        operation = conversion_goal_campaign_config_service.update_conversion_goal_campaign_config_operation(
            resource_name=resource_name,
            goal_config_level=goal_config_level,
            custom_conversion_goal=custom_conversion_goal
        )

        # Verify
        assert isinstance(operation, ConversionGoalCampaignConfigOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.goal_config_level == goal_config_level
        assert operation.update.custom_conversion_goal == custom_conversion_goal
        assert set(operation.update_mask.paths) == {"goal_config_level", "custom_conversion_goal"}

    def test_update_conversion_goal_campaign_config_operation_partial(self, conversion_goal_campaign_config_service):
        """Test creating conversion goal campaign config operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/conversionGoalCampaignConfigs/123"
        goal_config_level = GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER

        # Execute
        operation = conversion_goal_campaign_config_service.update_conversion_goal_campaign_config_operation(
            resource_name=resource_name,
            goal_config_level=goal_config_level
        )

        # Verify
        assert isinstance(operation, ConversionGoalCampaignConfigOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.goal_config_level == goal_config_level
        assert operation.update_mask.paths == ["goal_config_level"]