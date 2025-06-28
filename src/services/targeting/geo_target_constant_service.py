"""Geo target constant service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v20.services.services.geo_target_constant_service import (
    GeoTargetConstantServiceClient,
)
from google.ads.googleads.v20.services.types.geo_target_constant_service import (
    SuggestGeoTargetConstantsRequest,
    SuggestGeoTargetConstantsResponse,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import get_logger

logger = get_logger(__name__)


class GeoTargetConstantService:
    """Geo target constant service for location targeting in Google Ads."""

    def __init__(self) -> None:
        """Initialize the geo target constant service."""
        self._client: Optional[GeoTargetConstantServiceClient] = None

    @property
    def client(self) -> GeoTargetConstantServiceClient:
        """Get the geo target constant service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("GeoTargetConstantService")
        assert self._client is not None
        return self._client

    async def suggest_geo_targets_by_location(
        self,
        ctx: Context,
        location_names: List[str],
        locale: str = "en",
        country_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest geo target constants by location names.

        Args:
            ctx: FastMCP context
            location_names: List of location names to search for
            locale: Language locale for results (e.g., "en", "es")
            country_code: Optional country code to filter results

        Returns:
            List of suggested geo target constants
        """
        try:
            # Create request
            request = SuggestGeoTargetConstantsRequest()
            request.locale = locale

            # Set location names
            location_names_obj = request.LocationNames()
            location_names_obj.names.extend(location_names)
            request.location_names = location_names_obj

            if country_code:
                request.country_code = country_code

            # Make the API call
            response: SuggestGeoTargetConstantsResponse = (
                self.client.suggest_geo_target_constants(request=request)
            )

            # Process results
            suggestions = []
            for suggestion in response.geo_target_constant_suggestions:
                geo_target = suggestion.geo_target_constant
                suggestion_dict = {
                    "resource_name": geo_target.resource_name,
                    "id": str(geo_target.id),
                    "name": geo_target.name,
                    "country_code": geo_target.country_code,
                    "target_type": geo_target.target_type,
                    "status": geo_target.status.name
                    if geo_target.status
                    else "UNKNOWN",
                    "canonical_name": geo_target.canonical_name,
                    "parent_geo_target": geo_target.parent_geo_target,
                    "locale": suggestion.locale,
                    "reach": suggestion.reach,
                    "search_term": suggestion.search_term,
                }
                suggestions.append(suggestion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(suggestions)} geo target suggestions for {location_names}",
            )

            return suggestions

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to suggest geo targets by location: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def suggest_geo_targets_by_address(
        self,
        ctx: Context,
        address_text: str,
        locale: str = "en",
        country_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest geo target constants by address.

        Args:
            ctx: FastMCP context
            address_text: Address text to search for
            locale: Language locale for results (e.g., "en", "es")
            country_code: Optional country code to filter results

        Returns:
            List of suggested geo target constants
        """
        try:
            # Create request
            request = SuggestGeoTargetConstantsRequest()
            request.locale = locale

            # Set address
            address_obj = request.GeoTargets()
            address_geo_target = address_obj.GeoTarget()
            address_geo_target.address = address_text
            address_obj.geo_targets.append(address_geo_target)
            request.geo_targets = address_obj

            if country_code:
                request.country_code = country_code

            # Make the API call
            response: SuggestGeoTargetConstantsResponse = (
                self.client.suggest_geo_target_constants(request=request)
            )

            # Process results
            suggestions = []
            for suggestion in response.geo_target_constant_suggestions:
                geo_target = suggestion.geo_target_constant
                suggestion_dict = {
                    "resource_name": geo_target.resource_name,
                    "id": str(geo_target.id),
                    "name": geo_target.name,
                    "country_code": geo_target.country_code,
                    "target_type": geo_target.target_type,
                    "status": geo_target.status.name
                    if geo_target.status
                    else "UNKNOWN",
                    "canonical_name": geo_target.canonical_name,
                    "parent_geo_target": geo_target.parent_geo_target,
                    "locale": suggestion.locale,
                    "reach": suggestion.reach,
                    "search_term": suggestion.search_term,
                }
                suggestions.append(suggestion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(suggestions)} geo target suggestions for address: {address_text}",
            )

            return suggestions

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to suggest geo targets by address: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_geo_targets(
        self,
        ctx: Context,
        query: str,
        locale: str = "en",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for geo target constants using a query.

        Args:
            ctx: FastMCP context
            query: Search query for geo targets
            locale: Language locale for results
            limit: Maximum number of results

        Returns:
            List of geo target constants
        """
        try:
            # Note: Direct GAQL search for geo_target_constant is not straightforward
            # since these are account-independent resources.
            # We'll use the suggest method as an alternative approach.

            await ctx.log(
                level="info",
                message=f"Searching for geo targets matching: {query}",
            )

            # For now, we'll use the suggest method as a search alternative
            return await self.suggest_geo_targets_by_location(
                ctx=ctx,
                location_names=[query],
                locale=locale,
            )

        except Exception as e:
            error_msg = f"Failed to search geo targets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_geo_target_constant_tools(
    service: GeoTargetConstantService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the geo target constant service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def suggest_geo_targets_by_location(
        ctx: Context,
        location_names: List[str],
        locale: str = "en",
        country_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest geo target constants by location names.

        Args:
            location_names: List of location names to search for (e.g., ["New York", "Los Angeles"])
            locale: Language locale for results (e.g., "en", "es", "fr")
            country_code: Optional two-letter country code to filter results (e.g., "US", "GB")

        Returns:
            List of suggested geo target constants with id, name, type, and reach information
        """
        return await service.suggest_geo_targets_by_location(
            ctx=ctx,
            location_names=location_names,
            locale=locale,
            country_code=country_code,
        )

    async def suggest_geo_targets_by_address(
        ctx: Context,
        address_text: str,
        locale: str = "en",
        country_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest geo target constants by address.

        Args:
            address_text: Address text to search for (e.g., "1600 Amphitheatre Parkway, Mountain View, CA")
            locale: Language locale for results (e.g., "en", "es", "fr")
            country_code: Optional two-letter country code to filter results (e.g., "US", "GB")

        Returns:
            List of suggested geo target constants with id, name, type, and reach information
        """
        return await service.suggest_geo_targets_by_address(
            ctx=ctx,
            address_text=address_text,
            locale=locale,
            country_code=country_code,
        )

    async def search_geo_targets(
        ctx: Context,
        query: str,
        locale: str = "en",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for geo target constants using a query.

        Args:
            query: Search query for geo targets (e.g., "California", "London")
            locale: Language locale for results (e.g., "en", "es", "fr")
            limit: Maximum number of results to return

        Returns:
            List of geo target constants matching the query
        """
        return await service.search_geo_targets(
            ctx=ctx,
            query=query,
            locale=locale,
            limit=limit,
        )

    tools.extend(
        [
            suggest_geo_targets_by_location,
            suggest_geo_targets_by_address,
            search_geo_targets,
        ]
    )
    return tools


def register_geo_target_constant_tools(mcp: FastMCP[Any]) -> GeoTargetConstantService:
    """Register geo target constant tools with the MCP server.

    Returns the GeoTargetConstantService instance for testing purposes.
    """
    service = GeoTargetConstantService()
    tools = create_geo_target_constant_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
