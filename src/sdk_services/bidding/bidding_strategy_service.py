"""Bidding strategy service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.bidding import (
    MaximizeConversions,
    TargetCpa,
    TargetImpressionShare,
    TargetRoas,
)
from google.ads.googleads.v20.enums.types.bidding_strategy_status import (
    BiddingStrategyStatusEnum,
)
from google.ads.googleads.v20.enums.types.bidding_strategy_type import (
    BiddingStrategyTypeEnum,
)
from google.ads.googleads.v20.enums.types.target_impression_share_location import (
    TargetImpressionShareLocationEnum,
)
from google.ads.googleads.v20.resources.types.bidding_strategy import BiddingStrategy
from google.ads.googleads.v20.services.services.bidding_strategy_service import (
    BiddingStrategyServiceClient,
)
from google.ads.googleads.v20.services.types.bidding_strategy_service import (
    BiddingStrategyOperation,
    MutateBiddingStrategiesRequest,
    MutateBiddingStrategiesResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BiddingStrategyService:
    """Bidding strategy service for managing Google Ads automated bidding strategies."""

    def __init__(self) -> None:
        """Initialize the bidding strategy service."""
        self._client: Optional[BiddingStrategyServiceClient] = None

    @property
    def client(self) -> BiddingStrategyServiceClient:
        """Get the bidding strategy service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BiddingStrategyService")
        assert self._client is not None
        return self._client

    async def create_target_cpa_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: int,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target CPA bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Target cost per acquisition in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = BiddingStrategyStatusEnum.BiddingStrategyStatus[
                status
            ]
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_CPA
            )

            # Configure Target CPA
            target_cpa = TargetCpa()
            target_cpa.target_cpa_micros = target_cpa_micros
            bidding_strategy.target_cpa = target_cpa

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target CPA strategy '{name}' with target {target_cpa_micros} micros",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target CPA strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_target_roas_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: float,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target ROAS (Return on Ad Spend) bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_roas: Target return on ad spend (e.g., 4.0 for 400% ROAS)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = BiddingStrategyStatusEnum.BiddingStrategyStatus[
                status
            ]
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_ROAS
            )

            # Configure Target ROAS
            target_roas_strategy = TargetRoas()
            target_roas_strategy.target_roas = target_roas
            bidding_strategy.target_roas = target_roas_strategy

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target ROAS strategy '{name}' with target {target_roas}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target ROAS strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_maximize_conversions_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: Optional[int] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Maximize Conversions bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Optional target CPA constraint
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = BiddingStrategyStatusEnum.BiddingStrategyStatus[
                status
            ]
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.MAXIMIZE_CONVERSIONS
            )

            # Configure Maximize Conversions
            maximize_conversions = MaximizeConversions()
            if target_cpa_micros is not None:
                maximize_conversions.target_cpa_micros = target_cpa_micros
            bidding_strategy.maximize_conversions = maximize_conversions

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Maximize Conversions strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Maximize Conversions strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_target_impression_share_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        location: str,
        location_fraction_micros: int,
        max_cpc_bid_ceiling_micros: Optional[int] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target Impression Share bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            location: Where to show ads (ABSOLUTE_TOP_OF_PAGE, TOP_OF_PAGE, ANYWHERE_ON_PAGE)
            location_fraction_micros: Target impression share (e.g., 650000 for 65%)
            max_cpc_bid_ceiling_micros: Optional max CPC bid limit
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = BiddingStrategyStatusEnum.BiddingStrategyStatus[
                status
            ]
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_IMPRESSION_SHARE
            )

            # Configure Target Impression Share
            target_impression_share = TargetImpressionShare()
            target_impression_share.location = (
                TargetImpressionShareLocationEnum.TargetImpressionShareLocation[
                    location
                ]
            )
            target_impression_share.location_fraction_micros = location_fraction_micros

            if max_cpc_bid_ceiling_micros is not None:
                target_impression_share.cpc_bid_ceiling_micros = (
                    max_cpc_bid_ceiling_micros
                )

            bidding_strategy.target_impression_share = target_impression_share

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target Impression Share strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target Impression Share strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_bidding_strategy_tools(
    service: BiddingStrategyService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the bidding strategy service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_target_cpa_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: int,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target CPA bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Target cost per acquisition in micros (1 million micros = 1 unit)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_cpa_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
        )

    async def create_target_roas_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: float,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target ROAS (Return on Ad Spend) bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_roas: Target return on ad spend (e.g., 4.0 for 400% ROAS)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_roas_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_roas=target_roas,
            status=status,
        )

    async def create_maximize_conversions_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: Optional[int] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Maximize Conversions bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Optional target CPA constraint in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_maximize_conversions_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
        )

    async def create_target_impression_share_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        location: str,
        location_fraction_micros: int,
        max_cpc_bid_ceiling_micros: Optional[int] = None,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a Target Impression Share bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            location: Where to show ads - ABSOLUTE_TOP_OF_PAGE, TOP_OF_PAGE, ANYWHERE_ON_PAGE
            location_fraction_micros: Target impression share in micros (e.g., 650000 for 65%)
            max_cpc_bid_ceiling_micros: Optional max CPC bid limit in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_impression_share_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            location=location,
            location_fraction_micros=location_fraction_micros,
            max_cpc_bid_ceiling_micros=max_cpc_bid_ceiling_micros,
            status=status,
        )

    tools.extend(
        [
            create_target_cpa_strategy,
            create_target_roas_strategy,
            create_maximize_conversions_strategy,
            create_target_impression_share_strategy,
        ]
    )
    return tools


def register_bidding_strategy_tools(mcp: FastMCP[Any]) -> BiddingStrategyService:
    """Register bidding strategy tools with the MCP server.

    Returns the BiddingStrategyService instance for testing purposes.
    """
    service = BiddingStrategyService()
    tools = create_bidding_strategy_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
