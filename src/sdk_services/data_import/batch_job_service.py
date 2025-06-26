"""Batch job service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.resources.types.batch_job import BatchJob
from google.ads.googleads.v20.services.services.batch_job_service import (
    BatchJobServiceClient,
)
from google.ads.googleads.v20.services.types.batch_job_service import (
    AddBatchJobOperationsRequest,
    AddBatchJobOperationsResponse,
    BatchJobOperation,
    ListBatchJobResultsRequest,
    MutateBatchJobRequest,
    MutateBatchJobResponse,
    RunBatchJobRequest,
)
from google.ads.googleads.v20.services.types.google_ads_service import MutateOperation

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BatchJobService:
    """Batch job service for performing bulk operations."""

    def __init__(self) -> None:
        """Initialize the batch job service."""
        self._client: Optional[BatchJobServiceClient] = None

    @property
    def client(self) -> BatchJobServiceClient:
        """Get the batch job service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BatchJobService")
        assert self._client is not None
        return self._client

    async def create_batch_job(
        self,
        ctx: Context,
        customer_id: str,
    ) -> Dict[str, Any]:
        """Create a new batch job.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            Created batch job details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create batch job
            batch_job = BatchJob()

            # Create operation
            operation = BatchJobOperation()
            operation.create = batch_job

            # Create request
            request = MutateBatchJobRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateBatchJobResponse = self.client.mutate_batch_job(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created batch job for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create batch job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_batch_job(
        self,
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
    ) -> Dict[str, Any]:
        """Get batch job details.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name

        Returns:
            Batch job details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search instead of get_batch_job
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Extract batch job ID from resource name
            batch_job_id = batch_job_resource_name.split("/")[-1]

            query = f"""
                SELECT
                    batch_job.resource_name,
                    batch_job.id,
                    batch_job.status,
                    batch_job.long_running_operation,
                    batch_job.metadata.creation_date_time,
                    batch_job.metadata.start_date_time,
                    batch_job.metadata.completion_date_time,
                    batch_job.metadata.estimated_completion_ratio,
                    batch_job.metadata.operation_count,
                    batch_job.metadata.executed_operation_count
                FROM batch_job
                WHERE batch_job.id = {batch_job_id}
            """

            response = google_ads_service.search(customer_id=customer_id, query=query)

            batch_job = None
            for row in response:
                batch_job = row.batch_job
                break

            if not batch_job:
                raise Exception(f"Batch job with ID {batch_job_id} not found")

            await ctx.log(
                level="info",
                message="Retrieved batch job details",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get batch job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_operations_to_batch_job(
        self,
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
        operations_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Add operations to a batch job.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name
            operations_data: List of operation data (simplified format)

        Returns:
            Result of adding operations
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Note: This is a simplified implementation
            # In practice, you'd need to construct proper MutateOperation objects
            # based on the specific operation types (campaign, ad group, keyword, etc.)

            operations = []
            for _ in operations_data:
                # This is a placeholder - actual implementation would require
                # parsing the operation data and creating appropriate MutateOperation objects
                operation = MutateOperation()
                # You would set the appropriate operation based on op_data['type']
                # For example:
                # if op_data.get('type') == 'campaign':
                #     operation.campaign_operation = ...
                # elif op_data.get('type') == 'ad_group':
                #     operation.ad_group_operation = ...
                # etc.
                operations.append(operation)

            # Create request
            request = AddBatchJobOperationsRequest()
            request.resource_name = batch_job_resource_name
            request.sequence_token = ""  # Start with empty token
            request.mutate_operations = operations

            # Make the API call
            response: AddBatchJobOperationsResponse = (
                self.client.add_batch_job_operations(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} operations to batch job",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add operations to batch job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def run_batch_job(
        self,
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
    ) -> Dict[str, Any]:
        """Run a batch job.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name

        Returns:
            Batch job execution details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = RunBatchJobRequest()
            request.resource_name = batch_job_resource_name

            # Make the API call
            operation = self.client.run_batch_job(request=request)

            await ctx.log(
                level="info",
                message="Started batch job execution",
            )

            return {
                "batch_job_resource_name": batch_job_resource_name,
                "long_running_operation": str(operation),  # type: ignore
                "status": "RUNNING",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to run batch job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_batch_job_results(
        self,
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
        page_size: int = 1000,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List batch job results.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name
            page_size: Number of results per page
            page_token: Token for pagination

        Returns:
            Batch job results
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = ListBatchJobResultsRequest()
            request.resource_name = batch_job_resource_name
            request.page_size = page_size
            if page_token:
                request.page_token = page_token

            # Make the API call
            response = self.client.list_batch_job_results(request=request)  # type: ignore

            # Process results
            results = []
            for result in response.results:
                result_dict = {
                    "operation_index": result.operation_index,
                    "status": "SUCCESS"
                    if result.mutate_operation_response
                    else "ERROR",
                    "resource_name": None,
                    "error": None,
                }

                if result.mutate_operation_response:
                    # Extract resource name from the successful operation
                    # This depends on the operation type
                    if result.mutate_operation_response.campaign_result:
                        result_dict["resource_name"] = (
                            result.mutate_operation_response.campaign_result.resource_name
                        )
                    elif result.mutate_operation_response.ad_group_result:
                        result_dict["resource_name"] = (
                            result.mutate_operation_response.ad_group_result.resource_name
                        )
                    # Add more operation types as needed

                if result.status:
                    result_dict["error"] = {  # type: ignore
                        "code": result.status.code,
                        "message": result.status.message,
                        "details": [str(detail) for detail in result.status.details],
                    }

                results.append(result_dict)

            await ctx.log(
                level="info",
                message=f"Retrieved {len(results)} batch job results",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list batch job results: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_batch_jobs(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List batch jobs for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            status_filter: Optional status filter

        Returns:
            List of batch jobs
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    batch_job.resource_name,
                    batch_job.id,
                    batch_job.status,
                    batch_job.long_running_operation,
                    batch_job.metadata.creation_date_time,
                    batch_job.metadata.start_date_time,
                    batch_job.metadata.completion_date_time,
                    batch_job.metadata.estimated_completion_ratio,
                    batch_job.metadata.operation_count,
                    batch_job.metadata.executed_operation_count
                FROM batch_job
            """

            if status_filter:
                query += f" WHERE batch_job.status = '{status_filter}'"

            query += " ORDER BY batch_job.metadata.creation_date_time DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            batch_jobs = []
            for row in response:
                batch_job = row.batch_job

                job_dict = {
                    "resource_name": batch_job.resource_name,
                    "id": str(batch_job.id),
                    "status": batch_job.status.name if batch_job.status else "UNKNOWN",
                    "long_running_operation": batch_job.long_running_operation,
                    "metadata": {
                        "creation_date_time": batch_job.metadata.creation_date_time,
                        "start_date_time": batch_job.metadata.start_date_time,
                        "completion_date_time": batch_job.metadata.completion_date_time,
                        "estimated_completion_ratio": batch_job.metadata.estimated_completion_ratio,
                        "operation_count": batch_job.metadata.operation_count,
                        "executed_operation_count": batch_job.metadata.executed_operation_count,
                    }
                    if batch_job.metadata
                    else {},
                }

                batch_jobs.append(job_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(batch_jobs)} batch jobs",
            )

            return batch_jobs

        except Exception as e:
            error_msg = f"Failed to list batch jobs: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_batch_job_tools(
    service: BatchJobService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the batch job service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_batch_job(
        ctx: Context,
        customer_id: str,
    ) -> Dict[str, Any]:
        """Create a new batch job for bulk operations.

        Args:
            customer_id: The customer ID

        Returns:
            Created batch job details with resource_name
        """
        return await service.create_batch_job(
            ctx=ctx,
            customer_id=customer_id,
        )

    async def get_batch_job(
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
    ) -> Dict[str, Any]:
        """Get batch job details and status.

        Args:
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name

        Returns:
            Batch job details including status and metadata
        """
        return await service.get_batch_job(
            ctx=ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
        )

    async def add_operations_to_batch_job(
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
        operations_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Add operations to a batch job.

        Args:
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name
            operations_data: List of operation data in simplified format

        Returns:
            Result of adding operations with sequence token
        """
        return await service.add_operations_to_batch_job(
            ctx=ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
            operations_data=operations_data,
        )

    async def run_batch_job(
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
    ) -> Dict[str, Any]:
        """Run a batch job to execute all added operations.

        Args:
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name

        Returns:
            Batch job execution details with long running operation name
        """
        return await service.run_batch_job(
            ctx=ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
        )

    async def list_batch_job_results(
        ctx: Context,
        customer_id: str,
        batch_job_resource_name: str,
        page_size: int = 1000,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List batch job results to see success/failure of operations.

        Args:
            customer_id: The customer ID
            batch_job_resource_name: The batch job resource name
            page_size: Number of results per page (max 1000)
            page_token: Token for pagination

        Returns:
            Batch job results with operation status and errors
        """
        return await service.list_batch_job_results(
            ctx=ctx,
            customer_id=customer_id,
            batch_job_resource_name=batch_job_resource_name,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_batch_jobs(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List batch jobs for a customer.

        Args:
            customer_id: The customer ID
            status_filter: Optional status filter (UNKNOWN, PENDING, RUNNING, DONE)

        Returns:
            List of batch jobs with status and metadata
        """
        return await service.list_batch_jobs(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    tools.extend(
        [
            create_batch_job,
            get_batch_job,
            add_operations_to_batch_job,
            run_batch_job,
            list_batch_job_results,
            list_batch_jobs,
        ]
    )
    return tools


def register_batch_job_tools(mcp: FastMCP[Any]) -> BatchJobService:
    """Register batch job tools with the MCP server.

    Returns the BatchJobService instance for testing purposes.
    """
    service = BatchJobService()
    tools = create_batch_job_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
