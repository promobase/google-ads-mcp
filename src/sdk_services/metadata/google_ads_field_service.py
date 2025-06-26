"""Google Ads field service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.google_ads_field_service import (
    GoogleAdsFieldServiceClient,
)
from google.ads.googleads.v20.services.types.google_ads_field_service import (
    GetGoogleAdsFieldRequest,
    SearchGoogleAdsFieldsRequest,
)
from google.ads.googleads.v20.resources.types.google_ads_field import GoogleAdsField
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import get_logger

logger = get_logger(__name__)


class GoogleAdsFieldService:
    """Google Ads field service for discovering field metadata."""

    def __init__(self) -> None:
        """Initialize the Google Ads field service."""
        self._client: Optional[GoogleAdsFieldServiceClient] = None

    @property
    def client(self) -> GoogleAdsFieldServiceClient:
        """Get the Google Ads field service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("GoogleAdsFieldService")
        assert self._client is not None
        return self._client

    async def get_field_metadata(
        self,
        ctx: Context,
        field_name: str,
    ) -> Dict[str, Any]:
        """Get metadata for a specific field.

        Args:
            ctx: FastMCP context
            field_name: The field name (e.g., "campaign.name")

        Returns:
            Field metadata including type, category, and attributes
        """
        try:
            # Create request
            request = GetGoogleAdsFieldRequest()
            request.resource_name = f"googleAdsFields/{field_name}"

            # Make the API call
            field: GoogleAdsField = self.client.get_google_ads_field(request=request)

            # Process result
            field_dict = {
                "name": field.name,
                "category": field.category.name if field.category else "UNKNOWN",
                "data_type": field.data_type.name if field.data_type else "UNKNOWN",
                "is_repeated": field.is_repeated,
                "selectable": field.selectable,
                "filterable": field.filterable,
                "sortable": field.sortable,
                "attribute_resources": list(field.attribute_resources),
                "metrics": list(field.metrics),
                "segments": list(field.segments),
                "selectable_with": list(field.selectable_with),
                "type_url": field.type_url,
                "enum_values": list(field.enum_values),
            }

            await ctx.log(
                level="info",
                message=f"Retrieved metadata for field: {field_name}",
            )

            return field_dict

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get field metadata: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_fields(
        self,
        ctx: Context,
        query: Optional[str] = None,
        category_filter: Optional[str] = None,
        selectable_only: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for Google Ads fields based on criteria.

        Args:
            ctx: FastMCP context
            query: Optional search query (e.g., "name LIKE '%campaign%'")
            category_filter: Optional category filter (RESOURCE, ATTRIBUTE, SEGMENT, METRIC)
            selectable_only: Only return selectable fields
            limit: Maximum number of results

        Returns:
            List of field metadata
        """
        try:
            # Build query
            conditions = []

            if query:
                conditions.append(f"({query})")

            if category_filter:
                conditions.append(f"category = '{category_filter}'")

            if selectable_only:
                conditions.append("selectable = true")

            # Construct final query
            search_query = " AND ".join(conditions) if conditions else "name != ''"
            search_query += f" LIMIT {limit}"

            # Create request
            request = SearchGoogleAdsFieldsRequest()
            request.query = search_query

            # Make the API call - returns a pager
            pager = self.client.search_google_ads_fields(request=request)

            # Process results
            fields = []
            for field in pager:
                fields.append(
                    {
                        "name": field.name,
                        "category": field.category.name
                        if field.category
                        else "UNKNOWN",
                        "data_type": field.data_type.name
                        if field.data_type
                        else "UNKNOWN",
                        "is_repeated": field.is_repeated,
                        "selectable": field.selectable,
                        "filterable": field.filterable,
                        "sortable": field.sortable,
                        "type_url": field.type_url,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Found {len(fields)} fields matching criteria",
            )

            return fields

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to search fields: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_resource_fields(
        self,
        ctx: Context,
        resource_name: str,
        include_metrics: bool = True,
        include_segments: bool = True,
    ) -> Dict[str, Any]:
        """Get all available fields for a specific resource.

        Args:
            ctx: FastMCP context
            resource_name: The resource name (e.g., "campaign", "ad_group")
            include_metrics: Include metric fields
            include_segments: Include segment fields

        Returns:
            Dictionary with categorized fields for the resource
        """
        try:
            # Get resource fields
            resource_query = f"name LIKE '{resource_name}.%' AND category = 'ATTRIBUTE'"
            resource_fields = await self.search_fields(
                ctx=ctx, query=resource_query, limit=500
            )

            result = {
                "resource": resource_name,
                "attributes": resource_fields,
            }

            # Get metrics if requested
            if include_metrics:
                metric_query = f"name LIKE 'metrics.%' AND category = 'METRIC'"
                metric_fields = await self.search_fields(
                    ctx=ctx, query=metric_query, limit=200
                )
                result["metrics"] = metric_fields

            # Get segments if requested
            if include_segments:
                segment_query = f"name LIKE 'segments.%' AND category = 'SEGMENT'"
                segment_fields = await self.search_fields(
                    ctx=ctx, query=segment_query, limit=100
                )
                result["segments"] = segment_fields

            await ctx.log(
                level="info",
                message=f"Retrieved field information for resource: {resource_name}",
            )

            return result

        except Exception as e:
            error_msg = f"Failed to get resource fields: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def validate_query_fields(
        self,
        ctx: Context,
        resource_name: str,
        field_names: List[str],
    ) -> Dict[str, Any]:
        """Validate if fields can be selected together in a query.

        Args:
            ctx: FastMCP context
            resource_name: The main resource (e.g., "campaign")
            field_names: List of field names to validate

        Returns:
            Validation result with compatibility information
        """
        try:
            validation_result: Dict[str, Any] = {
                "resource": resource_name,
                "fields": {},
                "all_compatible": True,
                "issues": [],
            }

            # Check each field
            for field_name in field_names:
                try:
                    field_metadata = await self.get_field_metadata(ctx, field_name)
                    validation_result["fields"][field_name] = {
                        "valid": True,
                        "selectable": field_metadata["selectable"],
                        "data_type": field_metadata["data_type"],
                        "category": field_metadata["category"],
                    }

                    if not field_metadata["selectable"]:
                        validation_result["all_compatible"] = False
                        validation_result["issues"].append(
                            f"Field '{field_name}' is not selectable"
                        )

                except Exception:
                    validation_result["fields"][field_name] = {
                        "valid": False,
                        "error": f"Field '{field_name}' not found",
                    }
                    validation_result["all_compatible"] = False
                    validation_result["issues"].append(
                        f"Field '{field_name}' is not a valid field"
                    )

            await ctx.log(
                level="info",
                message=f"Validated {len(field_names)} fields for resource: {resource_name}",
            )

            return validation_result

        except Exception as e:
            error_msg = f"Failed to validate query fields: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_google_ads_field_tools(
    service: GoogleAdsFieldService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the Google Ads field service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def get_field_metadata(
        ctx: Context,
        field_name: str,
    ) -> Dict[str, Any]:
        """Get metadata for a specific Google Ads field.

        Args:
            field_name: The field name (e.g., "campaign.name", "metrics.clicks")

        Returns:
            Field metadata including:
            - category: RESOURCE, ATTRIBUTE, SEGMENT, or METRIC
            - data_type: STRING, INT64, DOUBLE, BOOLEAN, etc.
            - selectable: Whether the field can be selected in queries
            - filterable: Whether the field can be used in WHERE clauses
            - sortable: Whether the field can be used in ORDER BY
        """
        return await service.get_field_metadata(
            ctx=ctx,
            field_name=field_name,
        )

    async def search_fields(
        ctx: Context,
        query: Optional[str] = None,
        category_filter: Optional[str] = None,
        selectable_only: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for Google Ads fields based on criteria.

        Args:
            query: Optional search query using field query syntax
                Examples:
                - "name LIKE '%campaign%'"
                - "category = 'METRIC' AND selectable = true"
            category_filter: Filter by category - RESOURCE, ATTRIBUTE, SEGMENT, or METRIC
            selectable_only: Only return fields that can be selected in queries
            limit: Maximum number of results

        Returns:
            List of field metadata matching the criteria
        """
        return await service.search_fields(
            ctx=ctx,
            query=query,
            category_filter=category_filter,
            selectable_only=selectable_only,
            limit=limit,
        )

    async def get_resource_fields(
        ctx: Context,
        resource_name: str,
        include_metrics: bool = True,
        include_segments: bool = True,
    ) -> Dict[str, Any]:
        """Get all available fields for a specific resource.

        Args:
            resource_name: The resource name (e.g., "campaign", "ad_group", "keyword_view")
            include_metrics: Include available metrics for this resource
            include_segments: Include available segments for this resource

        Returns:
            Dictionary with categorized fields:
            - attributes: Resource-specific fields
            - metrics: Available metrics (if requested)
            - segments: Available segments (if requested)
        """
        return await service.get_resource_fields(
            ctx=ctx,
            resource_name=resource_name,
            include_metrics=include_metrics,
            include_segments=include_segments,
        )

    async def validate_query_fields(
        ctx: Context,
        resource_name: str,
        field_names: List[str],
    ) -> Dict[str, Any]:
        """Validate if fields can be selected together in a query.

        Args:
            resource_name: The main resource for the query (e.g., "campaign")
            field_names: List of field names to validate

        Returns:
            Validation result with:
            - all_compatible: Whether all fields can be selected together
            - fields: Individual field validation results
            - issues: List of compatibility issues found
        """
        return await service.validate_query_fields(
            ctx=ctx,
            resource_name=resource_name,
            field_names=field_names,
        )

    tools.extend(
        [get_field_metadata, search_fields, get_resource_fields, validate_query_fields]
    )
    return tools


def register_google_ads_field_tools(mcp: FastMCP[Any]) -> GoogleAdsFieldService:
    """Register Google Ads field tools with the MCP server.

    Returns the GoogleAdsFieldService instance for testing purposes.
    """
    service = GoogleAdsFieldService()
    tools = create_google_ads_field_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
