"""Experiment service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.experiment_status import ExperimentStatusEnum
from google.ads.googleads.v20.enums.types.experiment_type import ExperimentTypeEnum
from google.ads.googleads.v20.resources.types.experiment import Experiment
from google.ads.googleads.v20.services.services.experiment_service import (
    ExperimentServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.experiment_service import (
    EndExperimentRequest,
    ExperimentOperation,
    MutateExperimentsRequest,
    MutateExperimentsResponse,
    PromoteExperimentRequest,
    ScheduleExperimentRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ExperimentService:
    """Experiment service for A/B testing campaigns."""

    def __init__(self) -> None:
        """Initialize the experiment service."""
        self._client: Optional[ExperimentServiceClient] = None

    @property
    def client(self) -> ExperimentServiceClient:
        """Get the experiment service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ExperimentService")
        assert self._client is not None
        return self._client

    async def create_experiment(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        base_campaign_id: str,
        description: Optional[str] = None,
        traffic_split_percent: int = 50,
        experiment_type: str = "SEARCH_CUSTOM",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new experiment for A/B testing.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The experiment name
            base_campaign_id: The base campaign to experiment on
            description: Optional description
            traffic_split_percent: Traffic split percentage (0-100)
            experiment_type: Type of experiment (SEARCH_CUSTOM, DISPLAY_CUSTOM, etc.)
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Created experiment details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create experiment
            experiment = Experiment()
            experiment.name = name
            experiment.campaigns.append(
                f"customers/{customer_id}/campaigns/{base_campaign_id}"
            )
            experiment.traffic_split_percent = traffic_split_percent
            experiment.type_ = getattr(
                ExperimentTypeEnum.ExperimentType, experiment_type
            )
            experiment.status = getattr(ExperimentStatusEnum.ExperimentStatus, "SETUP")

            if description:
                experiment.description = description

            # Set dates if provided
            if start_date:
                experiment.start_date = start_date
            if end_date:
                experiment.end_date = end_date

            # Create operation
            operation = ExperimentOperation()
            operation.create = experiment

            # Create request
            request = MutateExperimentsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateExperimentsResponse = self.client.mutate_experiments(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created experiment '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def schedule_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Schedule an experiment to start running.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to schedule
            validate_only: Only validate without scheduling

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = ScheduleExperimentRequest()
            request.resource_name = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.schedule_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated' if validate_only else 'Scheduled'} experiment {experiment_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to schedule experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def end_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """End a running experiment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to end
            validate_only: Only validate without ending

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = EndExperimentRequest()
            request.resource_name = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.end_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated ending' if validate_only else 'Ended'} experiment {experiment_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to end experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def promote_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Promote experiment changes to the base campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to promote
            validate_only: Only validate without promoting

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = PromoteExperimentRequest()
            request.resource_name = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.promote_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated promoting' if validate_only else 'Promoted'} experiment {experiment_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to promote experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_experiments(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all experiments in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional filter by campaign
            status_filter: Optional filter by status

        Returns:
            List of experiments
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    experiment.id,
                    experiment.name,
                    experiment.description,
                    experiment.status,
                    experiment.type,
                    experiment.traffic_split_percent,
                    experiment.campaigns,
                    experiment.start_date,
                    experiment.end_date,
                    experiment.resource_name
                FROM experiment
            """

            conditions = []
            if campaign_id:
                conditions.append(
                    f"experiment.campaigns CONTAINS 'customers/{customer_id}/campaigns/{campaign_id}'"
                )
            if status_filter:
                conditions.append(f"experiment.status = '{status_filter}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY experiment.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            experiments = []
            for row in response:
                experiments.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(experiments)} experiments",
            )

            return experiments

        except Exception as e:
            error_msg = f"Failed to list experiments: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_experiment_tools(
    service: ExperimentService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the experiment service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_experiment(
        ctx: Context,
        customer_id: str,
        name: str,
        base_campaign_id: str,
        description: Optional[str] = None,
        traffic_split_percent: int = 50,
        experiment_type: str = "SEARCH_CUSTOM",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new experiment for A/B testing campaigns.

        Args:
            customer_id: The customer ID
            name: The experiment name
            base_campaign_id: The campaign ID to run the experiment on
            description: Optional description of the experiment
            traffic_split_percent: Percentage of traffic for experiment (0-100, default 50)
            experiment_type: Type of experiment:
                - SEARCH_CUSTOM: For search campaigns
                - DISPLAY_CUSTOM: For display campaigns
                - VIDEO_CUSTOM: For video campaigns
                - SHOPPING_COMPARISON_LISTING_ADS: For shopping campaigns
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Created experiment details with resource_name and experiment_id
        """
        return await service.create_experiment(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            base_campaign_id=base_campaign_id,
            description=description,
            traffic_split_percent=traffic_split_percent,
            experiment_type=experiment_type,
            start_date=start_date,
            end_date=end_date,
        )

    async def schedule_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Schedule an experiment to start running.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to schedule
            validate_only: Only validate without actually scheduling

        Returns:
            Operation status with experiment_id and status
        """
        return await service.schedule_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def end_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """End a running experiment.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to end
            validate_only: Only validate without actually ending

        Returns:
            Operation status with experiment_id and status
        """
        return await service.end_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def promote_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Promote experiment changes to the base campaign.

        This applies the experiment's changes permanently to the base campaign.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to promote
            validate_only: Only validate without actually promoting

        Returns:
            Operation status with experiment_id and status
        """
        return await service.promote_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def list_experiments(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all experiments in the account.

        Args:
            customer_id: The customer ID
            campaign_id: Optional filter by campaign ID
            status_filter: Optional filter by status:
                - SETUP: Not yet started
                - INITIATED: Starting
                - RUNNING: Currently active
                - GRADUATED: Successfully completed
                - HALTED: Stopped early
                - PROMOTED: Changes applied to base campaign

        Returns:
            List of experiments with details
        """
        return await service.list_experiments(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            status_filter=status_filter,
        )

    tools.extend(
        [
            create_experiment,
            schedule_experiment,
            end_experiment,
            promote_experiment,
            list_experiments,
        ]
    )
    return tools


def register_experiment_tools(mcp: FastMCP[Any]) -> ExperimentService:
    """Register experiment tools with the MCP server.

    Returns the ExperimentService instance for testing purposes.
    """
    service = ExperimentService()
    tools = create_experiment_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
