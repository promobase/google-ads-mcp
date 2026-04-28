"""Campaign service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.bidding import (
    ManualCpc,
    MaximizeConversions,
    MaximizeConversionValue,
    TargetCpa,
    TargetImpressionShare,
    TargetRoas,
    TargetSpend,
)
from google.ads.googleads.v20.enums.types.advertising_channel_sub_type import (
    AdvertisingChannelSubTypeEnum,
)
from google.ads.googleads.v20.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_experiment_type import (
    CampaignExperimentTypeEnum,
)
from google.ads.googleads.v20.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v20.enums.types.eu_political_advertising_status import (
    EuPoliticalAdvertisingStatusEnum,
)
from google.ads.googleads.v20.resources.types.campaign import Campaign
from google.ads.googleads.v20.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_service import (
    CampaignOperation,
    MutateCampaignsRequest,
    MutateCampaignsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    resolve_enum,
    format_ads_error,
    format_customer_id,
    get_logger,
    serialize_proto_message,
)

logger = get_logger(__name__)

_PMAX = AdvertisingChannelTypeEnum.AdvertisingChannelType.PERFORMANCE_MAX


def _apply_bidding_strategy(
    campaign: Campaign,
    bidding_strategy_type: str,
    bidding_strategy_resource_name: Optional[str] = None,
    target_cpa_micros: Optional[int] = None,
    target_roas: Optional[float] = None,
    max_conversion_value_target_roas: Optional[float] = None,
    target_spend_cpc_bid_ceiling_micros: Optional[int] = None,
) -> None:
    """Set the bidding strategy on a Campaign proto based on type string."""
    bst = bidding_strategy_type.upper()

    if bst == "PORTFOLIO":
        if not bidding_strategy_resource_name:
            raise ValueError(
                "bidding_strategy_resource_name is required for PORTFOLIO bidding"
            )
        campaign.bidding_strategy = bidding_strategy_resource_name
        return

    if bst == "MANUAL_CPC":
        campaign.manual_cpc = ManualCpc()
    elif bst == "TARGET_CPA":
        tc = TargetCpa()
        if target_cpa_micros is not None:
            tc.target_cpa_micros = target_cpa_micros
        campaign.target_cpa = tc
    elif bst == "TARGET_ROAS":
        tr = TargetRoas()
        if target_roas is not None:
            tr.target_roas = target_roas
        campaign.target_roas = tr
    elif bst == "MAXIMIZE_CONVERSIONS":
        mc = MaximizeConversions()
        if target_cpa_micros is not None:
            mc.target_cpa_micros = target_cpa_micros
        campaign.maximize_conversions = mc
    elif bst == "MAXIMIZE_CONVERSION_VALUE":
        mcv = MaximizeConversionValue()
        if max_conversion_value_target_roas is not None:
            mcv.target_roas = max_conversion_value_target_roas
        campaign.maximize_conversion_value = mcv
    elif bst == "TARGET_SPEND":
        ts = TargetSpend()
        if target_spend_cpc_bid_ceiling_micros is not None:
            ts.cpc_bid_ceiling_micros = target_spend_cpc_bid_ceiling_micros
        campaign.target_spend = ts
    elif bst == "TARGET_IMPRESSION_SHARE":
        campaign.target_impression_share = TargetImpressionShare()
    else:
        raise ValueError(f"Unsupported bidding_strategy_type: {bidding_strategy_type}")


class CampaignService:
    """Campaign service for managing Google Ads campaigns."""

    def __init__(self) -> None:
        """Initialize the campaign service."""
        self._client: Optional[CampaignServiceClient] = None

    @property
    def client(self) -> CampaignServiceClient:
        """Get the campaign service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CampaignService", version="v20"
            )
        assert self._client is not None
        return self._client

    async def create_campaign(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: AdvertisingChannelTypeEnum.AdvertisingChannelType = AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH,
        advertising_channel_sub_type: Optional[
            AdvertisingChannelSubTypeEnum.AdvertisingChannelSubType
        ] = None,
        status: CampaignStatusEnum.CampaignStatus = CampaignStatusEnum.CampaignStatus.PAUSED,
        bidding_strategy_type: str = "MANUAL_CPC",
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        max_conversion_value_target_roas: Optional[float] = None,
        target_spend_cpc_bid_ceiling_micros: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget
            advertising_channel_type: Channel type (SEARCH, DISPLAY, SHOPPING, VIDEO, PERFORMANCE_MAX, etc.)
            advertising_channel_sub_type: Optional sub-type refinement
            status: Campaign status (ENABLED, PAUSED, REMOVED)
            bidding_strategy_type: One of MANUAL_CPC, TARGET_CPA, TARGET_ROAS,
                MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, TARGET_SPEND,
                TARGET_IMPRESSION_SHARE, or PORTFOLIO
            bidding_strategy_resource_name: Required when bidding_strategy_type is PORTFOLIO
            target_cpa_micros: Target CPA in micros (for TARGET_CPA or MAXIMIZE_CONVERSIONS)
            target_roas: Target ROAS value (for TARGET_ROAS)
            max_conversion_value_target_roas: Target ROAS (for MAXIMIZE_CONVERSION_VALUE)
            target_spend_cpc_bid_ceiling_micros: CPC ceiling (for TARGET_SPEND)
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)

            campaign = Campaign()
            campaign.name = name
            campaign.campaign_budget = budget_resource_name
            campaign.advertising_channel_type = advertising_channel_type
            campaign.status = status

            if advertising_channel_sub_type is not None:
                campaign.advertising_channel_sub_type = advertising_channel_sub_type

            campaign.contains_eu_political_advertising = EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
            campaign.experiment_type = (
                CampaignExperimentTypeEnum.CampaignExperimentType.BASE
            )

            # Network settings only apply to non-PMax campaigns
            if advertising_channel_type != _PMAX:
                campaign.network_settings.target_google_search = True
                campaign.network_settings.target_search_network = True
                campaign.network_settings.target_content_network = (
                    advertising_channel_type
                    != AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
                )
                campaign.network_settings.target_partner_search_network = False

            _apply_bidding_strategy(
                campaign,
                bidding_strategy_type=bidding_strategy_type,
                bidding_strategy_resource_name=bidding_strategy_resource_name,
                target_cpa_micros=target_cpa_micros,
                target_roas=target_roas,
                max_conversion_value_target_roas=max_conversion_value_target_roas,
                target_spend_cpc_bid_ceiling_micros=target_spend_cpc_bid_ceiling_micros,
            )

            if start_date:
                campaign.start_date = start_date.replace("-", "")
            if end_date:
                campaign.end_date = end_date.replace("-", "")

            operation = CampaignOperation()
            operation.create = campaign

            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateCampaignsResponse = self.client.mutate_campaigns(
                request=request
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[CampaignStatusEnum.CampaignStatus] = None,
        bidding_strategy_type: Optional[str] = None,
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        max_conversion_value_target_roas: Optional[float] = None,
        target_spend_cpc_bid_ceiling_micros: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name
            status: New campaign status
            bidding_strategy_type: New bidding strategy type (MANUAL_CPC, TARGET_CPA, etc.)
            bidding_strategy_resource_name: Portfolio strategy resource name
            target_cpa_micros: Target CPA in micros
            target_roas: Target ROAS value
            max_conversion_value_target_roas: Target ROAS for MaxConvValue
            target_spend_cpc_bid_ceiling_micros: CPC ceiling for TARGET_SPEND
            start_date: New start date (YYYY-MM-DD)
            end_date: New end date (YYYY-MM-DD)

        Returns:
            Updated campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign = Campaign()
            campaign.resource_name = resource_name

            update_mask_fields: list[str] = []

            if name is not None:
                campaign.name = name
                update_mask_fields.append("name")

            if status is not None:
                campaign.status = status
                update_mask_fields.append("status")

            if start_date is not None:
                campaign.start_date = start_date.replace("-", "")
                update_mask_fields.append("start_date")

            if end_date is not None:
                campaign.end_date = end_date.replace("-", "")
                update_mask_fields.append("end_date")

            if bidding_strategy_type is not None:
                bst = bidding_strategy_type.upper()
                _apply_bidding_strategy(
                    campaign,
                    bidding_strategy_type=bst,
                    bidding_strategy_resource_name=bidding_strategy_resource_name,
                    target_cpa_micros=target_cpa_micros,
                    target_roas=target_roas,
                    max_conversion_value_target_roas=max_conversion_value_target_roas,
                    target_spend_cpc_bid_ceiling_micros=target_spend_cpc_bid_ceiling_micros,
                )
                _BIDDING_FIELD_MAP: Dict[str, str] = {
                    "MANUAL_CPC": "manual_cpc",
                    "TARGET_CPA": "target_cpa",
                    "TARGET_ROAS": "target_roas",
                    "MAXIMIZE_CONVERSIONS": "maximize_conversions",
                    "MAXIMIZE_CONVERSION_VALUE": "maximize_conversion_value",
                    "TARGET_SPEND": "target_spend",
                    "TARGET_IMPRESSION_SHARE": "target_impression_share",
                    "PORTFOLIO": "bidding_strategy",
                }
                field = _BIDDING_FIELD_MAP.get(bst)
                if field:
                    update_mask_fields.append(field)

            operation = CampaignOperation()
            operation.update = campaign
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response = self.client.mutate_campaigns(request=request)

            await ctx.log(
                level="info",
                message=f"Updated campaign {campaign_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = format_ads_error(e)
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_tools(
    service: CampaignService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools: list[Callable[..., Awaitable[Any]]] = []

    async def create_campaign(
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: str = "SEARCH",
        advertising_channel_sub_type: Optional[str] = None,
        status: str = "PAUSED",
        bidding_strategy_type: str = "MANUAL_CPC",
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        max_conversion_value_target_roas: Optional[float] = None,
        target_spend_cpc_bid_ceiling_micros: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign. Supports Search, Display, Shopping, Video, and Performance Max.

        Args:
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget (e.g., customers/123/campaignBudgets/456)
            advertising_channel_type: Channel type - SEARCH, DISPLAY, SHOPPING, VIDEO, PERFORMANCE_MAX
            advertising_channel_sub_type: Optional sub-type (e.g., SHOPPING_SMART_ADS, VIDEO_ACTION)
            status: Campaign status - ENABLED, PAUSED, REMOVED
            bidding_strategy_type: Bidding strategy - MANUAL_CPC, TARGET_CPA, TARGET_ROAS,
                MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, TARGET_SPEND,
                TARGET_IMPRESSION_SHARE, or PORTFOLIO.
                PMax campaigns require MAXIMIZE_CONVERSIONS or MAXIMIZE_CONVERSION_VALUE.
            bidding_strategy_resource_name: Portfolio bidding strategy resource name (required when bidding_strategy_type is PORTFOLIO)
            target_cpa_micros: Target CPA in micros (for TARGET_CPA or MAXIMIZE_CONVERSIONS)
            target_roas: Target ROAS as float (for TARGET_ROAS, e.g. 4.0 = 400%)
            max_conversion_value_target_roas: Target ROAS for MAXIMIZE_CONVERSION_VALUE
            target_spend_cpc_bid_ceiling_micros: Max CPC ceiling in micros (for TARGET_SPEND)
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details with resource_name and campaign_id
        """
        channel_type_enum = resolve_enum(
            AdvertisingChannelTypeEnum.AdvertisingChannelType,
            advertising_channel_type,
            "advertising_channel_type",
        )
        status_enum = resolve_enum(CampaignStatusEnum.CampaignStatus, status, "status")
        sub_type_enum = (
            getattr(
                AdvertisingChannelSubTypeEnum.AdvertisingChannelSubType,
                advertising_channel_sub_type,
            )
            if advertising_channel_sub_type
            else None
        )

        return await service.create_campaign(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
            advertising_channel_type=channel_type_enum,
            advertising_channel_sub_type=sub_type_enum,
            status=status_enum,
            bidding_strategy_type=bidding_strategy_type,
            bidding_strategy_resource_name=bidding_strategy_resource_name,
            target_cpa_micros=target_cpa_micros,
            target_roas=target_roas,
            max_conversion_value_target_roas=max_conversion_value_target_roas,
            target_spend_cpc_bid_ceiling_micros=target_spend_cpc_bid_ceiling_micros,
            start_date=start_date,
            end_date=end_date,
        )

    async def update_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        bidding_strategy_type: Optional[str] = None,
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        max_conversion_value_target_roas: Optional[float] = None,
        target_spend_cpc_bid_ceiling_micros: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name
            status: New campaign status - ENABLED, PAUSED, REMOVED
            bidding_strategy_type: New bidding strategy - MANUAL_CPC, TARGET_CPA, TARGET_ROAS,
                MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, TARGET_SPEND,
                TARGET_IMPRESSION_SHARE, or PORTFOLIO
            bidding_strategy_resource_name: Portfolio bidding strategy resource name
            target_cpa_micros: Target CPA in micros
            target_roas: Target ROAS as float
            max_conversion_value_target_roas: Target ROAS for MAXIMIZE_CONVERSION_VALUE
            target_spend_cpc_bid_ceiling_micros: Max CPC ceiling in micros
            start_date: New start date (YYYY-MM-DD)
            end_date: New end date (YYYY-MM-DD)

        Returns:
            Updated campaign details
        """
        status_enum = (
            resolve_enum(CampaignStatusEnum.CampaignStatus, status, "status")
            if status
            else None
        )

        return await service.update_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=status_enum,
            bidding_strategy_type=bidding_strategy_type,
            bidding_strategy_resource_name=bidding_strategy_resource_name,
            target_cpa_micros=target_cpa_micros,
            target_roas=target_roas,
            max_conversion_value_target_roas=max_conversion_value_target_roas,
            target_spend_cpc_bid_ceiling_micros=target_spend_cpc_bid_ceiling_micros,
            start_date=start_date,
            end_date=end_date,
        )

    tools.extend([create_campaign, update_campaign])
    return tools


def register_campaign_tools(mcp: FastMCP[Any]) -> CampaignService:
    """Register campaign tools with the MCP server.

    Returns the CampaignService instance for testing purposes.
    """
    service = CampaignService()
    tools = create_campaign_tools(service)

    for tool in tools:
        mcp.tool(tool)

    return service
