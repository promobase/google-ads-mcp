"""Google Ads service implementation with full v20 type safety."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.summary_row_setting import (
    SummaryRowSettingEnum,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.google_ads_service import (
    GoogleAdsRow,
    MutateGoogleAdsRequest,
    MutateGoogleAdsResponse,
    MutateOperation,
    MutateOperationResponse,
    SearchGoogleAdsRequest,
    SearchGoogleAdsStreamRequest,
    SearchGoogleAdsStreamResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class GoogleAdsService:
    """Complete Google Ads service for search and mutate operations."""

    def __init__(self) -> None:
        """Initialize the Google Ads service."""
        self._client: Optional[GoogleAdsServiceClient] = None

    @property
    def client(self) -> GoogleAdsServiceClient:
        """Get the Google Ads service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("GoogleAdsService")
        assert self._client is not None
        return self._client

    async def search(
        self,
        ctx: Context,
        customer_id: str,
        query: str,
        page_size: int = 1000,
        page_token: Optional[str] = None,
        validate_only: bool = False,
        summary_row_setting: SummaryRowSettingEnum.SummaryRowSetting = SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW,
    ) -> Dict[str, Any]:
        """Execute a GAQL query and return paginated results.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            query: The GAQL (Google Ads Query Language) query
            page_size: Number of results per page (max 10000)
            page_token: Token for pagination
            validate_only: If true, only validates the query
            summary_row_setting: Whether to include summary row

        Returns:
            Dictionary containing results and pagination info
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create the request
            request = SearchGoogleAdsRequest()
            request.customer_id = customer_id
            request.query = query
            request.page_size = min(page_size, 10000)  # Max allowed by API
            if page_token:
                request.page_token = page_token
            request.validate_only = validate_only
            request.summary_row_setting = summary_row_setting

            # Execute search
            response = self.client.search(request=request)

            # Process results
            results: List[Dict[str, Any]] = []
            row: GoogleAdsRow
            for row in response.results:
                results.append(serialize_proto_message(row))

            # Include summary row if present
            summary_row = None
            if response.summary_row:
                summary_row = serialize_proto_message(response.summary_row)

            return {
                "results": results,
                "next_page_token": response.next_page_token,
                "total_results_count": response.total_results_count,
                "summary_row": summary_row,
                "field_mask": response.field_mask.paths if response.field_mask else [],
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to execute search: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_stream(
        self,
        ctx: Context,
        customer_id: str,
        query: str,
        summary_row_setting: SummaryRowSettingEnum.SummaryRowSetting = SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW,
    ) -> List[Dict[str, Any]]:
        """Execute a GAQL query and stream all results.

        For large result sets, this is more efficient than paginated search.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            query: The GAQL (Google Ads Query Language) query
            summary_row_setting: Whether to include summary row

        Returns:
            List of all results
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create the request
            request = SearchGoogleAdsStreamRequest()
            request.customer_id = customer_id
            request.query = query
            request.summary_row_setting = summary_row_setting

            # Execute streaming search
            stream = self.client.search_stream(request=request)

            # Process all results
            results: List[Dict[str, Any]] = []
            total_count = 0

            batch: SearchGoogleAdsStreamResponse
            for batch in stream:
                for row in batch.results:
                    results.append(serialize_proto_message(row))
                    total_count += 1

                # Log progress for large result sets
                if total_count % 10000 == 0:
                    await ctx.log(
                        level="info",
                        message=f"Processed {total_count} rows so far...",
                    )

            await ctx.log(
                level="info",
                message=f"Query completed. Total rows: {total_count}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to execute search stream: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def mutate(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[MutateOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
    ) -> Dict[str, Any]:
        """Execute multiple mutate operations across different resource types.

        This is the most flexible mutation method, allowing operations on
        multiple resource types in a single request.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of mutate operations
            partial_failure: If true, valid operations succeed even if others fail
            validate_only: If true, only validates without executing
            response_content_type: What to return in response

        Returns:
            Mutation results
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create the request
            request = MutateGoogleAdsRequest()
            request.customer_id = customer_id
            request.mutate_operations.extend(operations)
            request.partial_failure = partial_failure
            request.validate_only = validate_only
            request.response_content_type = response_content_type

            # Execute mutations
            response: MutateGoogleAdsResponse = self.client.mutate(request=request)

            # Process results
            results: List[Dict[str, Any]] = []
            result: MutateOperationResponse
            for result in response.mutate_operation_responses:
                results.append(serialize_proto_message(result))

            return {
                "results": results,
                "partial_failure_error": (
                    serialize_proto_message(response.partial_failure_error)
                    if response.partial_failure_error
                    else None
                ),
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to execute mutations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_google_ads_tools(
    service: GoogleAdsService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the Google Ads service."""
    tools = []

    async def search_google_ads(
        ctx: Context,
        customer_id: str,
        query: str,
        page_size: int = 1000,
        page_token: Optional[str] = None,
        validate_only: bool = False,
        include_summary_row: bool = False,
    ) -> Dict[str, Any]:
        """Execute a GAQL query with pagination support.

        Args:
            customer_id: The customer ID
            query: The GAQL (Google Ads Query Language) query
            page_size: Number of results per page (max 10000)
            page_token: Token for pagination from previous response
            validate_only: If true, only validates the query
            include_summary_row: If true, includes summary row with totals

        Returns:
            Dictionary with results, next_page_token, and metadata

        Example queries:
            - "SELECT campaign.id, campaign.name FROM campaign WHERE campaign.status = 'ENABLED'"
            - "SELECT metrics.clicks, metrics.impressions FROM campaign WHERE segments.date DURING LAST_7_DAYS"
            - "SELECT ad_group.id, ad_group.name FROM ad_group WHERE ad_group.campaign = 'customers/123/campaigns/456'"
        """
        summary_row_setting = (
            SummaryRowSettingEnum.SummaryRowSetting.SUMMARY_ROW_WITH_RESULTS
            if include_summary_row
            else SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW
        )

        return await service.search(
            ctx=ctx,
            customer_id=customer_id,
            query=query,
            page_size=page_size,
            page_token=page_token,
            validate_only=validate_only,
            summary_row_setting=summary_row_setting,
        )

    async def search_google_ads_stream(
        ctx: Context,
        customer_id: str,
        query: str,
        include_summary_row: bool = False,
    ) -> List[Dict[str, Any]]:
        """Execute a GAQL query and stream all results.

        Use this for large result sets where you need all data at once.
        More efficient than pagination for large queries.

        Args:
            customer_id: The customer ID
            query: The GAQL (Google Ads Query Language) query
            include_summary_row: If true, includes summary row with totals

        Returns:
            List of all query results

        Example:
            results = await search_google_ads_stream(
                customer_id="1234567890",
                query="SELECT campaign.id, metrics.clicks FROM campaign WHERE segments.date DURING LAST_30_DAYS"
            )
        """
        summary_row_setting = (
            SummaryRowSettingEnum.SummaryRowSetting.SUMMARY_ROW_WITH_RESULTS
            if include_summary_row
            else SummaryRowSettingEnum.SummaryRowSetting.NO_SUMMARY_ROW
        )

        return await service.search_stream(
            ctx=ctx,
            customer_id=customer_id,
            query=query,
            summary_row_setting=summary_row_setting,
        )

    tools.extend([search_google_ads, search_google_ads_stream])
    return tools


def register_google_ads_tools(mcp: FastMCP[Any]) -> GoogleAdsService:
    """Register Google Ads tools with the MCP server.

    Returns the GoogleAdsService instance for testing purposes.
    """
    service = GoogleAdsService()
    tools = create_google_ads_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
