"""Google Ads Experiment Arm Service

This module provides functionality for managing experiment arms (variants) in Google Ads.
Experiment arms allow you to test different campaign configurations and compare performance.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.resources.types.experiment_arm import ExperimentArm
from google.ads.googleads.v20.services.services.experiment_arm_service import (
    ExperimentArmServiceClient,
)
from google.ads.googleads.v20.services.types.experiment_arm_service import (
    ExperimentArmOperation,
    MutateExperimentArmsRequest,
    MutateExperimentArmsResponse,
)

from src.sdk_client import get_sdk_client


class ExperimentArmService:
    """Service for managing Google Ads experiment arms."""

    def __init__(self) -> None:
        """Initialize the experiment arm service."""
        self._client: Optional[ExperimentArmServiceClient] = None

    @property
    def client(self) -> ExperimentArmServiceClient:
        """Get the experiment arm service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ExperimentArmService")
        assert self._client is not None
        return self._client

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
        return self.client.mutate_experiment_arms(request=request)

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


def register_experiment_arm_tools(mcp: FastMCP[Any]) -> None:
    """Register experiment arm tools with the MCP server."""

    @mcp.tool
    async def mutate_experiment_arms(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> str:
        """Create, update, or remove experiment arms.

        Args:
            customer_id: The customer ID
            operations: List of experiment arm operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Success message with operation count
        """
        service = ExperimentArmService()

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_experiment_arm_operation(
                    experiment=op_data["experiment"],
                    name=op_data["name"],
                    control=op_data["control"],
                    traffic_split=op_data["traffic_split"],
                    campaigns=op_data.get("campaigns", []),
                )
            elif op_type == "update":
                operation = service.update_experiment_arm_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    traffic_split=op_data.get("traffic_split"),
                    campaigns=op_data.get("campaigns"),
                )
            elif op_type == "remove":
                operation = service.remove_experiment_arm_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_experiment_arms(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

        return (
            f"Successfully processed {len(response.results)} experiment arm operations"
        )

    @mcp.tool
    async def create_experiment_arm(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        experiment: str,
        name: str,
        control: bool,
        traffic_split: int,
        campaigns: list[str] = [],
    ) -> str:
        """Create a new experiment arm.

        Args:
            customer_id: The customer ID
            experiment: The experiment resource name
            name: Name of the experiment arm
            control: Whether this is a control arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            The created experiment arm resource name
        """
        service = ExperimentArmService()

        operation = service.create_experiment_arm_operation(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        response = service.mutate_experiment_arms(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Created experiment arm: {result.resource_name}"

    @mcp.tool
    async def update_experiment_arm(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        traffic_split: Optional[int] = None,
        campaigns: Optional[list[str]] = None,
    ) -> str:
        """Update an existing experiment arm.

        Args:
            customer_id: The customer ID
            resource_name: The experiment arm resource name
            name: Name of the experiment arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            The updated experiment arm resource name
        """
        service = ExperimentArmService()

        operation = service.update_experiment_arm_operation(
            resource_name=resource_name,
            name=name,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        response = service.mutate_experiment_arms(
            customer_id=customer_id, operations=[operation]
        )

        result = response.results[0]
        return f"Updated experiment arm: {result.resource_name}"

    @mcp.tool
    async def remove_experiment_arm(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
    ) -> str:
        """Remove an experiment arm.

        Args:
            customer_id: The customer ID
            resource_name: The experiment arm resource name

        Returns:
            Success message
        """
        service = ExperimentArmService()

        operation = service.remove_experiment_arm_operation(resource_name=resource_name)

        service.mutate_experiment_arms(customer_id=customer_id, operations=[operation])

        return f"Removed experiment arm: {resource_name}"
