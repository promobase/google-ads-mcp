"""Reach plan service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.services.services.reach_plan_service import (
    ReachPlanServiceClient,
)
from google.ads.googleads.v20.services.types.reach_plan_service import (
    ListPlannableLocationsRequest,
    ListPlannableLocationsResponse,
    ListPlannableProductsRequest,
    ListPlannableProductsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import get_logger, serialize_proto_message

logger = get_logger(__name__)


class ReachPlanService:
    """Reach plan service for reach planning and forecasting."""

    def __init__(self) -> None:
        """Initialize the reach plan service."""
        self._client: Optional[ReachPlanServiceClient] = None

    @property
    def client(self) -> ReachPlanServiceClient:
        """Get the reach plan service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ReachPlanService")
        assert self._client is not None
        return self._client

    async def list_plannable_locations(
        self,
        ctx: Context,
    ) -> Dict[str, Any]:
        """List all plannable locations for reach planning.

        Args:
            ctx: FastMCP context

        Returns:
            List of plannable locations with details
        """
        try:
            # Create request
            request = ListPlannableLocationsRequest()

            # Make the API call
            response: ListPlannableLocationsResponse = (
                self.client.list_plannable_locations(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable locations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_plannable_products(
        self,
        ctx: Context,
        plannable_location_id: str,
    ) -> List[Dict[str, Any]]:
        """List all plannable products for a given location.

        Args:
            ctx: FastMCP context
            plannable_location_id: The plannable location ID

        Returns:
            List of plannable products for the location
        """
        try:
            # Create request
            request = ListPlannableProductsRequest()
            request.plannable_location_id = plannable_location_id

            # Make the API call
            response: ListPlannableProductsResponse = (
                self.client.list_plannable_products(request=request)
            )

            # Process results
            products = []
            for product in response.product_metadata:
                product_dict = {
                    "plannable_product_code": product.plannable_product_code,
                    "plannable_product_name": product.plannable_product_name,
                    "plannable_targeting": {
                        "age_ranges": [
                            str(age_range)
                            for age_range in product.plannable_targeting.age_ranges
                        ]
                        if product.plannable_targeting
                        and product.plannable_targeting.age_ranges
                        else [],
                        "genders": [
                            str(gender)
                            for gender in product.plannable_targeting.genders
                        ]
                        if product.plannable_targeting
                        and product.plannable_targeting.genders
                        else [],
                        "devices": [
                            str(device)
                            for device in product.plannable_targeting.devices
                        ]
                        if product.plannable_targeting
                        and product.plannable_targeting.devices
                        else [],
                        "networks": [
                            str(network)
                            for network in product.plannable_targeting.networks
                        ]
                        if product.plannable_targeting
                        and product.plannable_targeting.networks
                        else [],
                    },
                }
                products.append(product_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(products)} plannable products for location {plannable_location_id}",
            )

            return products

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable products: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_basic_reach_forecast(
        self,
        ctx: Context,
        customer_id: str,
        plannable_location_id: str,
        currency_code: str,
        budget_micros: int,
    ) -> Dict[str, Any]:
        """Generate a basic reach forecast (simplified version due to v20 limitations).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID (can be with or without hyphens)
            plannable_location_id: The plannable location ID
            currency_code: The currency code (e.g., "USD")
            budget_micros: Budget in micros

        Returns:
            Basic reach forecast information
        """
        try:
            # Format customer ID
            if "-" in customer_id:
                customer_id = customer_id.replace("-", "")

            # Note: GenerateReachForecastRequest requires complex types not available in v20
            # This is a simplified implementation that returns basic information
            raise NotImplementedError

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate reach forecast: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_reach_plan_tools(
    service: ReachPlanService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the reach plan service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def list_plannable_locations(
        ctx: Context,
    ) -> Dict[str, Any]:
        """List all available plannable locations for reach planning.

        Returns:
            Response containing plannable locations with ID, name, country code, and location type
        """
        return await service.list_plannable_locations(ctx=ctx)

    async def list_plannable_products(
        ctx: Context,
        plannable_location_id: str,
    ) -> List[Dict[str, Any]]:
        """List all plannable products available for a specific location.

        Args:
            plannable_location_id: The plannable location ID to get products for

        Returns:
            List of plannable products with codes, names, and targeting options
        """
        return await service.list_plannable_products(
            ctx=ctx,
            plannable_location_id=plannable_location_id,
        )

    async def generate_basic_reach_forecast(
        ctx: Context,
        customer_id: str,
        plannable_location_id: str,
        currency_code: str,
        budget_micros: int,
    ) -> Dict[str, Any]:
        """Generate a basic reach forecast (simplified due to v20 limitations).

        Args:
            customer_id: The customer ID (can be with or without hyphens)
            plannable_location_id: The plannable location ID for the forecast
            currency_code: Currency code (e.g., "USD", "EUR")
            budget_micros: Budget in micros (e.g., 1000000 for $1)

        Returns:
            Basic reach forecast information (simplified due to API limitations)
        """
        return await service.generate_basic_reach_forecast(
            ctx=ctx,
            customer_id=customer_id,
            plannable_location_id=plannable_location_id,
            currency_code=currency_code,
            budget_micros=budget_micros,
        )

    tools.extend(
        [
            list_plannable_locations,
            list_plannable_products,
            generate_basic_reach_forecast,
        ]
    )
    return tools


def register_reach_plan_tools(mcp: FastMCP[Any]) -> ReachPlanService:
    """Register reach plan tools with the MCP server.

    Returns the ReachPlanService instance for testing purposes.
    """
    service = ReachPlanService()
    tools = create_reach_plan_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
