"""Tests for Google Ads Experiment Arm Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from google.ads.googleads.v20.resources.types.experiment_arm import ExperimentArm
from google.ads.googleads.v20.services.types.experiment_arm_service import (
    ExperimentArmOperation,
    MutateExperimentArmsRequest,
    MutateExperimentArmsResponse,
    MutateExperimentArmResult,
)

from src.sdk_services.campaign.experiment_arm_service import ExperimentArmService


class TestExperimentArmService:
    """Test cases for ExperimentArmService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service  # type: ignore
        return client

    @pytest.fixture
    def experiment_arm_service(self, mock_client):
        """Create ExperimentArmService instance with mock client"""
        return ExperimentArmService(mock_client)

    def test_mutate_experiment_arms(
        self, experiment_arm_service: Any, mock_client: Any
    ):
        """Test mutating experiment arms"""
        # Setup
        customer_id = "1234567890"
        operations = [ExperimentArmOperation()]

        mock_response = MutateExperimentArmsResponse(
            results=[
                MutateExperimentArmResult(
                    resource_name="customers/1234567890/experimentArms/123~456"
                )
            ]
        )
        mock_client.get_service.return_value.mutate_experiment_arms.return_value = (  # type: ignore
            mock_response
        )

        # Execute
        response = experiment_arm_service.mutate_experiment_arms(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("ExperimentArmService")  # type: ignore

        # Verify request
        call_args = (
            mock_client.get_service.return_value.mutate_experiment_arms.call_args  # type: ignore
        )
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure == True
        assert request.validate_only == False

    def test_create_experiment_arm_operation(self, experiment_arm_service: Any):
        """Test creating experiment arm operation for creation"""
        # Setup
        experiment = "customers/1234567890/experiments/123"
        name = "Test Experiment Arm"
        control = True
        traffic_split = 50
        campaigns = ["customers/1234567890/campaigns/456"]

        # Execute
        operation = experiment_arm_service.create_experiment_arm_operation(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        # Verify
        assert isinstance(operation, ExperimentArmOperation)
        assert operation.create.experiment == experiment
        assert operation.create.name == name
        assert operation.create.control == control
        assert operation.create.traffic_split == traffic_split
        assert operation.create.campaigns == campaigns

    def test_create_experiment_arm_operation_without_campaigns(
        self, experiment_arm_service: Any
    ):
        """Test creating experiment arm operation without campaigns"""
        # Setup
        experiment = "customers/1234567890/experiments/123"
        name = "Test Experiment Arm"
        control = False
        traffic_split = 50

        # Execute
        operation = experiment_arm_service.create_experiment_arm_operation(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
        )

        # Verify
        assert isinstance(operation, ExperimentArmOperation)
        assert operation.create.experiment == experiment
        assert operation.create.name == name
        assert operation.create.control == control
        assert operation.create.traffic_split == traffic_split
        assert operation.create.campaigns == []

    def test_update_experiment_arm_operation(self, experiment_arm_service: Any):
        """Test creating experiment arm operation for update"""
        # Setup
        resource_name = "customers/1234567890/experimentArms/123~456"
        name = "Updated Experiment Arm"
        traffic_split = 60
        campaigns = ["customers/1234567890/campaigns/789"]

        # Execute
        operation = experiment_arm_service.update_experiment_arm_operation(
            resource_name=resource_name,
            name=name,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        # Verify
        assert isinstance(operation, ExperimentArmOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update.traffic_split == traffic_split
        assert operation.update.campaigns == campaigns
        assert set(operation.update_mask.paths) == {
            "name",
            "traffic_split",
            "campaigns",
        }

    def test_update_experiment_arm_operation_partial(self, experiment_arm_service: Any):
        """Test creating experiment arm operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/experimentArms/123~456"
        name = "Updated Experiment Arm"

        # Execute
        operation = experiment_arm_service.update_experiment_arm_operation(
            resource_name=resource_name, name=name
        )

        # Verify
        assert isinstance(operation, ExperimentArmOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update_mask.paths == ["name"]

    def test_remove_experiment_arm_operation(self, experiment_arm_service: Any):
        """Test creating experiment arm operation for removal"""
        # Setup
        resource_name = "customers/1234567890/experimentArms/123~456"

        # Execute
        operation = experiment_arm_service.remove_experiment_arm_operation(
            resource_name
        )

        # Verify
        assert isinstance(operation, ExperimentArmOperation)
        assert operation.remove == resource_name
