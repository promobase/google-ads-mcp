"""Google Ads Experiment Arm Service

This module provides functionality for managing experiment arms (variants) in Google Ads.
Experiment arms allow you to test different campaign configurations and compare performance.
"""

from typing import List, Optional

from google.ads.googleads.v20.resources.types.experiment_arm import ExperimentArm
from google.ads.googleads.v20.services.services.experiment_arm_service import (
    ExperimentArmServiceClient,
)
from google.ads.googleads.v20.services.types.experiment_arm_service import (
    ExperimentArmOperation,
    MutateExperimentArmsRequest,
    MutateExperimentArmsResponse,
)


class ExperimentArmService:
    """Service for managing Google Ads experiment arms."""

    def __init__(self, client):
        self.client = client
        self.service = self.client.get_service("ExperimentArmService")

    def mutate_experiment_arms(
        self,
        customer_id: str,
        operations: List[ExperimentArmOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateExperimentArmsResponse:
        """Mutate experiment arms.

        Args:
            customer_id: The customer ID
            operations: List of experiment arm operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            MutateExperimentArmsResponse: The response containing results
        """
        request = MutateExperimentArmsRequest(
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )
        return self.service.mutate_experiment_arms(request=request)

    def create_experiment_arm_operation(
        self,
        experiment: str,
        name: str,
        control: bool,
        traffic_split: int,
        campaigns: Optional[List[str]] = None,
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for creation.

        Args:
            experiment: The experiment resource name
            name: The name of the experiment arm
            control: Whether this is a control arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            ExperimentArmOperation: The operation to create the experiment arm
        """
        experiment_arm = ExperimentArm(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
            campaigns=campaigns or [],
        )

        return ExperimentArmOperation(create=experiment_arm)

    def update_experiment_arm_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        traffic_split: Optional[int] = None,
        campaigns: Optional[List[str]] = None,
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for update.

        Args:
            resource_name: The experiment arm resource name
            name: The name of the experiment arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            ExperimentArmOperation: The operation to update the experiment arm
        """
        experiment_arm = ExperimentArm(resource_name=resource_name)

        update_mask = []
        if name is not None:
            experiment_arm.name = name
            update_mask.append("name")
        if traffic_split is not None:
            experiment_arm.traffic_split = traffic_split
            update_mask.append("traffic_split")
        if campaigns is not None:
            experiment_arm.campaigns = campaigns
            update_mask.append("campaigns")

        return ExperimentArmOperation(
            update=experiment_arm,
            update_mask={"paths": update_mask},
        )

    def remove_experiment_arm_operation(
        self, resource_name: str
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for removal.

        Args:
            resource_name: The experiment arm resource name

        Returns:
            ExperimentArmOperation: The operation to remove the experiment arm
        """
        return ExperimentArmOperation(remove=resource_name)
