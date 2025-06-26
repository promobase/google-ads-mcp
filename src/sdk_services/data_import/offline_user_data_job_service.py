"""Offline user data job service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.offline_user_data import (
    OfflineUserAddressInfo,
    UserData,
    UserIdentifier,
)
from google.ads.googleads.v20.enums.types.offline_user_data_job_type import (
    OfflineUserDataJobTypeEnum,
)
from google.ads.googleads.v20.resources.types.offline_user_data_job import (
    OfflineUserDataJob,
)
from google.ads.googleads.v20.services.services.offline_user_data_job_service import (
    OfflineUserDataJobServiceClient,
)
from google.ads.googleads.v20.services.types.offline_user_data_job_service import (
    AddOfflineUserDataJobOperationsRequest,
    AddOfflineUserDataJobOperationsResponse,
    CreateOfflineUserDataJobRequest,
    CreateOfflineUserDataJobResponse,
    OfflineUserDataJobOperation,
    RunOfflineUserDataJobRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class OfflineUserDataJobService:
    """Offline user data job service for customer match and enhanced conversions."""

    def __init__(self) -> None:
        """Initialize the offline user data job service."""
        self._client: Optional[OfflineUserDataJobServiceClient] = None

    @property
    def client(self) -> OfflineUserDataJobServiceClient:
        """Get the offline user data job service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("OfflineUserDataJobService")
        assert self._client is not None
        return self._client

    async def create_customer_match_job(
        self,
        ctx: Context,
        customer_id: str,
        job_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a customer match job for uploading user data.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_name: Optional name for the job

        Returns:
            Created job details with resource_name
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create offline user data job
            job = OfflineUserDataJob()
            job.type_ = OfflineUserDataJobTypeEnum.OfflineUserDataJobType.CUSTOMER_MATCH_USER_LIST
            if job_name:
                job.customer_match_user_list_metadata.user_list = job_name

            # Create request
            request = CreateOfflineUserDataJobRequest()
            request.customer_id = customer_id
            request.job = job

            # Make the API call
            response: CreateOfflineUserDataJobResponse = (
                self.client.create_offline_user_data_job(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created customer match job for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer match job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_user_data_operations(
        self,
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
        user_data_list: List[Dict[str, Any]],
        enable_partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Add user data operations to an offline user data job.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name
            user_data_list: List of user data to upload
            enable_partial_failure: Whether to enable partial failure

        Returns:
            Result of adding operations
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for user_data_dict in user_data_list:
                operation = OfflineUserDataJobOperation()

                # Create user data
                user_data = UserData()

                # Process user identifiers
                if "user_identifiers" in user_data_dict:
                    for identifier_dict in user_data_dict["user_identifiers"]:
                        identifier = UserIdentifier()

                        # Set identifier based on type
                        if "hashed_email" in identifier_dict:
                            identifier.hashed_email = identifier_dict["hashed_email"]
                        elif "hashed_phone_number" in identifier_dict:
                            identifier.hashed_phone_number = identifier_dict[
                                "hashed_phone_number"
                            ]
                        elif "mobile_id" in identifier_dict:
                            identifier.mobile_id = identifier_dict["mobile_id"]
                        elif "third_party_user_id" in identifier_dict:
                            identifier.third_party_user_id = identifier_dict[
                                "third_party_user_id"
                            ]
                        elif "address_info" in identifier_dict:
                            address_info = OfflineUserAddressInfo()
                            addr = identifier_dict["address_info"]

                            if "hashed_first_name" in addr:
                                address_info.hashed_first_name = addr[
                                    "hashed_first_name"
                                ]
                            if "hashed_last_name" in addr:
                                address_info.hashed_last_name = addr["hashed_last_name"]
                            if "country_code" in addr:
                                address_info.country_code = addr["country_code"]
                            if "postal_code" in addr:
                                address_info.postal_code = addr["postal_code"]
                            if "hashed_street_address" in addr:
                                address_info.hashed_street_address = addr[
                                    "hashed_street_address"
                                ]

                            identifier.address_info = address_info

                        user_data.user_identifiers.append(identifier)

                # Set transaction attributes if provided
                if "transaction_attribute" in user_data_dict:
                    trans_attr = user_data_dict["transaction_attribute"]
                    user_data.transaction_attribute.conversion_action = trans_attr.get(
                        "conversion_action"
                    )
                    user_data.transaction_attribute.currency_code = trans_attr.get(
                        "currency_code"
                    )
                    user_data.transaction_attribute.transaction_amount_micros = (
                        trans_attr.get("transaction_amount_micros")
                    )
                    user_data.transaction_attribute.transaction_date_time = (
                        trans_attr.get("transaction_date_time")
                    )

                # Note: OfflineUserData not available in v20 - simplified implementation
                # operation.create = user_data  # Simplified approach
                operation.create = user_data
                operations.append(operation)

            # Create request
            request = AddOfflineUserDataJobOperationsRequest()
            request.resource_name = job_resource_name
            request.enable_partial_failure = enable_partial_failure
            request.operations = operations

            # Make the API call
            response: AddOfflineUserDataJobOperationsResponse = (
                self.client.add_offline_user_data_job_operations(request=request)
            )

            # Process results
            result = {
                "job_resource_name": job_resource_name,
                "operations_added": len(operations),
                "partial_failure_error": str(response.partial_failure_error)
                if response.partial_failure_error
                else None,
            }

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} user data operations to job",
            )

            return result

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add user data operations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def run_offline_user_data_job(
        self,
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
    ) -> Dict[str, Any]:
        """Run an offline user data job.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name

        Returns:
            Job execution details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = RunOfflineUserDataJobRequest()
            request.resource_name = job_resource_name

            # Make the API call
            operation = self.client.run_offline_user_data_job(request=request)

            await ctx.log(
                level="info",
                message="Started offline user data job execution",
            )

            return {
                "job_resource_name": job_resource_name,
                "long_running_operation": str(operation),  # type: ignore
                "status": "RUNNING",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to run offline user data job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_offline_user_data_job(
        self,
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
    ) -> Dict[str, Any]:
        """Get offline user data job details.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name

        Returns:
            Job details including status and match rate
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService to search for the job
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Extract job ID from resource name
            job_id = job_resource_name.split("/")[-1]

            query = f"""
                SELECT
                    offline_user_data_job.resource_name,
                    offline_user_data_job.id,
                    offline_user_data_job.type,
                    offline_user_data_job.status,
                    offline_user_data_job.failure_reason,
                    offline_user_data_job.operation_metadata.match_rate_range
                FROM offline_user_data_job
                WHERE offline_user_data_job.id = {job_id}
            """

            response = google_ads_service.search(customer_id=customer_id, query=query)

            job = None
            for row in response:
                job = row.offline_user_data_job
                break

            if not job:
                raise Exception(f"Offline user data job with ID {job_id} not found")

            await ctx.log(
                level="info",
                message="Retrieved offline user data job details",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get offline user data job: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_offline_user_data_jobs(
        self,
        ctx: Context,
        customer_id: str,
        job_type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List offline user data jobs for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_type_filter: Optional job type filter

        Returns:
            List of offline user data jobs
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    offline_user_data_job.resource_name,
                    offline_user_data_job.id,
                    offline_user_data_job.type,
                    offline_user_data_job.status,
                    offline_user_data_job.failure_reason,
                    offline_user_data_job.operation_metadata.match_rate_range
                FROM offline_user_data_job
            """

            if job_type_filter:
                query += f" WHERE offline_user_data_job.type = '{job_type_filter}'"

            query += " ORDER BY offline_user_data_job.id DESC"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            jobs = []
            for row in response:
                job = row.offline_user_data_job

                job_dict = {
                    "resource_name": job.resource_name,
                    "id": str(job.id),
                    "type": job.type_.name if job.type_ else "UNKNOWN",
                    "status": job.status.name if job.status else "UNKNOWN",
                    "failure_reason": job.failure_reason.name
                    if job.failure_reason
                    else None,
                    "match_rate_range": job.operation_metadata.match_rate_range.name
                    if job.operation_metadata
                    and job.operation_metadata.match_rate_range
                    else None,
                }

                jobs.append(job_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(jobs)} offline user data jobs",
            )

            return jobs

        except Exception as e:
            error_msg = f"Failed to list offline user data jobs: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_offline_user_data_job_tools(
    service: OfflineUserDataJobService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the offline user data job service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customer_match_job(
        ctx: Context,
        customer_id: str,
        job_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a customer match job for uploading user data.

        Args:
            customer_id: The customer ID
            job_name: Optional name for the job

        Returns:
            Created job details with resource_name and status
        """
        return await service.create_customer_match_job(
            ctx=ctx,
            customer_id=customer_id,
            job_name=job_name,
        )

    async def add_user_data_operations(
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
        user_data_list: List[Dict[str, Any]],
        enable_partial_failure: bool = True,
    ) -> Dict[str, Any]:
        """Add user data operations to an offline user data job.

        Args:
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name
            user_data_list: List of user data to upload. Each item should contain:
                - user_identifiers: List of identifiers, each with one of:
                    - hashed_email: SHA256 hashed email address
                    - hashed_phone_number: SHA256 hashed phone number (E.164 format)
                    - mobile_id: Mobile advertising ID
                    - third_party_user_id: Third-party user ID
                    - address_info: Address information with hashed fields
                - transaction_attribute: Optional transaction data for enhanced conversions
            enable_partial_failure: Whether to enable partial failure

        Returns:
            Result of adding operations with success/failure details
        """
        return await service.add_user_data_operations(
            ctx=ctx,
            customer_id=customer_id,
            job_resource_name=job_resource_name,
            user_data_list=user_data_list,
            enable_partial_failure=enable_partial_failure,
        )

    async def run_offline_user_data_job(
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
    ) -> Dict[str, Any]:
        """Run an offline user data job to process uploaded data.

        Args:
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name

        Returns:
            Job execution details with long running operation name
        """
        return await service.run_offline_user_data_job(
            ctx=ctx,
            customer_id=customer_id,
            job_resource_name=job_resource_name,
        )

    async def get_offline_user_data_job(
        ctx: Context,
        customer_id: str,
        job_resource_name: str,
    ) -> Dict[str, Any]:
        """Get offline user data job details including status and match rate.

        Args:
            customer_id: The customer ID
            job_resource_name: The offline user data job resource name

        Returns:
            Job details including status, match rate, and failure reason if any
        """
        return await service.get_offline_user_data_job(
            ctx=ctx,
            customer_id=customer_id,
            job_resource_name=job_resource_name,
        )

    async def list_offline_user_data_jobs(
        ctx: Context,
        customer_id: str,
        job_type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List offline user data jobs for a customer.

        Args:
            customer_id: The customer ID
            job_type_filter: Optional job type filter (CUSTOMER_MATCH_USER_LIST, STORE_SALES_DIRECT_UPLOAD)

        Returns:
            List of offline user data jobs with status and details
        """
        return await service.list_offline_user_data_jobs(
            ctx=ctx,
            customer_id=customer_id,
            job_type_filter=job_type_filter,
        )

    tools.extend(
        [
            create_customer_match_job,
            add_user_data_operations,
            run_offline_user_data_job,
            get_offline_user_data_job,
            list_offline_user_data_jobs,
        ]
    )
    return tools


def register_offline_user_data_job_tools(
    mcp: FastMCP[Any],
) -> OfflineUserDataJobService:
    """Register offline user data job tools with the MCP server.

    Returns the OfflineUserDataJobService instance for testing purposes.
    """
    service = OfflineUserDataJobService()
    tools = create_offline_user_data_job_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
