"""Keyword plan service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.keyword_plan_forecast_interval import (
    KeywordPlanForecastIntervalEnum,
)
from google.ads.googleads.v20.resources.types.keyword_plan import KeywordPlan
from google.ads.googleads.v20.services.services.keyword_plan_service import (
    KeywordPlanServiceClient,
)
from google.ads.googleads.v20.services.services.keyword_plan_idea_service import (
    KeywordPlanIdeaServiceClient,
)
from google.ads.googleads.v20.services.services.keyword_plan_campaign_service import (
    KeywordPlanCampaignServiceClient,
)
from google.ads.googleads.v20.services.services.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordServiceClient,
)
from google.ads.googleads.v20.services.types.keyword_plan_service import (
    KeywordPlanOperation,
    MutateKeywordPlansRequest,
    MutateKeywordPlansResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class KeywordPlanService:
    """Keyword plan service for keyword research and planning."""

    def __init__(self) -> None:
        """Initialize the keyword plan service."""
        self._client: Optional[KeywordPlanServiceClient] = None

    @property
    def client(self) -> KeywordPlanServiceClient:
        """Get the keyword plan service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordPlanService")
        assert self._client is not None
        return self._client

    async def create_keyword_plan(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        forecast_period_days: int = 30,
    ) -> Dict[str, Any]:
        """Create a new keyword plan for keyword research.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The keyword plan name
            forecast_period_days: Forecast period in days (default 30)

        Returns:
            Created keyword plan details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create keyword plan
            keyword_plan = KeywordPlan()
            keyword_plan.name = name

            # Set forecast period
            if forecast_period_days <= 30:
                keyword_plan.forecast_period.date_interval = KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval.NEXT_MONTH
            elif forecast_period_days <= 90:
                keyword_plan.forecast_period.date_interval = KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval.NEXT_QUARTER
            else:
                # For custom periods, use date range (would need start/end dates)
                keyword_plan.forecast_period.date_interval = KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval.NEXT_MONTH

            # Create operation
            operation = KeywordPlanOperation()
            operation.create = keyword_plan

            # Create request
            request = MutateKeywordPlansRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: MutateKeywordPlansResponse = self.client.mutate_keyword_plans(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created keyword plan '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create keyword plan: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_keyword_ideas(
        self,
        ctx: Context,
        customer_id: str,
        keywords: Optional[List[str]] = None,
        url: Optional[str] = None,
        location_ids: Optional[List[str]] = None,
        language_id: Optional[str] = None,
        include_adult_keywords: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get keyword ideas based on seed keywords or URL.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: Seed keywords (optional)
            url: Seed URL (optional)
            location_ids: Geo target location IDs (optional)
            language_id: Language ID (optional)
            include_adult_keywords: Include adult keywords
            limit: Maximum number of results

        Returns:
            List of keyword ideas with metrics
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use KeywordPlanIdeaService
            sdk_client = get_sdk_client()
            idea_service: KeywordPlanIdeaServiceClient = sdk_client.client.get_service(
                "KeywordPlanIdeaService"
            )

            from google.ads.googleads.v20.services.types.keyword_plan_idea_service import (
                GenerateKeywordIdeasRequest,
            )

            # Create request
            request = GenerateKeywordIdeasRequest()
            request.customer_id = customer_id
            request.include_adult_keywords = include_adult_keywords

            # Set language (default to English if not specified)
            request.language = f"languageConstants/{language_id or '1000'}"

            # Set locations (default to US if not specified)
            if location_ids:
                request.geo_target_constants.extend(
                    [f"geoTargetConstants/{loc_id}" for loc_id in location_ids]
                )
            else:
                request.geo_target_constants.append("geoTargetConstants/2840")  # US

            # Set seed keywords or URL
            if keywords:
                request.keyword_seed.keywords.extend(keywords)
            elif url:
                request.url_seed.url = url
            else:
                raise ValueError("Either keywords or url must be provided")

            # Make the API call
            response = idea_service.generate_keyword_ideas(request=request)

            # Process results
            ideas = []
            count = 0
            for idea in response:
                if count >= limit:
                    break
                ideas.append(serialize_proto_message(idea))
                count += 1

            await ctx.log(
                level="info",
                message=f"Generated {len(ideas)} keyword ideas",
            )

            return ideas

        except Exception as e:
            error_msg = f"Failed to get keyword ideas: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_keyword_plan_campaign(
        self,
        ctx: Context,
        customer_id: str,
        keyword_plan_id: str,
        name: str,
        cpc_bid_micros: int,
        location_ids: Optional[List[str]] = None,
        language_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a campaign within a keyword plan.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keyword_plan_id: The keyword plan ID
            name: Campaign name
            cpc_bid_micros: CPC bid in micros
            location_ids: Geo target location IDs
            language_id: Language ID

        Returns:
            Created campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use KeywordPlanCampaignService
            sdk_client = get_sdk_client()
            campaign_service: KeywordPlanCampaignServiceClient = (
                sdk_client.client.get_service("KeywordPlanCampaignService")
            )

            from google.ads.googleads.v20.resources.types.keyword_plan_campaign import (
                KeywordPlanCampaign,
                KeywordPlanGeoTarget,
            )
            from google.ads.googleads.v20.services.types.keyword_plan_campaign_service import (
                KeywordPlanCampaignOperation,
                MutateKeywordPlanCampaignsRequest,
            )

            # Create campaign
            campaign = KeywordPlanCampaign()
            campaign.name = name
            campaign.keyword_plan = (
                f"customers/{customer_id}/keywordPlans/{keyword_plan_id}"
            )
            campaign.cpc_bid_micros = cpc_bid_micros

            # Set language
            campaign.language_constants.append(
                f"languageConstants/{language_id or '1000'}"  # Default to English
            )

            # Set locations
            if location_ids:
                for loc_id in location_ids:
                    geo_target = KeywordPlanGeoTarget()
                    geo_target.geo_target_constant = f"geoTargetConstants/{loc_id}"
                    campaign.geo_targets.append(geo_target)
            else:
                # Default to US
                geo_target = KeywordPlanGeoTarget()
                geo_target.geo_target_constant = "geoTargetConstants/2840"
                campaign.geo_targets.append(geo_target)

            # Create operation
            operation = KeywordPlanCampaignOperation()
            operation.create = campaign

            # Create request
            request = MutateKeywordPlanCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response = campaign_service.mutate_keyword_plan_campaigns(request=request)

            await ctx.log(
                level="info",
                message=f"Created keyword plan campaign '{name}'",
            )

            return serialize_proto_message(response)

        except Exception as e:
            error_msg = f"Failed to create keyword plan campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_keywords_to_plan(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Add keywords to a keyword plan ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The keyword plan ad group ID
            keywords: List of keywords with text, match_type, and optional cpc_bid_micros

        Returns:
            List of created keyword details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use KeywordPlanAdGroupKeywordService
            sdk_client = get_sdk_client()
            keyword_service: KeywordPlanAdGroupKeywordServiceClient = (
                sdk_client.client.get_service("KeywordPlanAdGroupKeywordService")
            )

            from google.ads.googleads.v20.enums.types.keyword_match_type import (
                KeywordMatchTypeEnum,
            )
            from google.ads.googleads.v20.resources.types.keyword_plan_ad_group_keyword import (
                KeywordPlanAdGroupKeyword,
            )
            from google.ads.googleads.v20.services.types.keyword_plan_ad_group_keyword_service import (
                KeywordPlanAdGroupKeywordOperation,
                MutateKeywordPlanAdGroupKeywordsRequest,
            )

            # Create operations
            operations = []
            for kw in keywords:
                keyword = KeywordPlanAdGroupKeyword()
                keyword.text = kw["text"]
                keyword.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, kw.get("match_type", "BROAD")
                )
                keyword.keyword_plan_ad_group = (
                    f"customers/{customer_id}/keywordPlanAdGroups/{ad_group_id}"
                )

                if "cpc_bid_micros" in kw:
                    keyword.cpc_bid_micros = kw["cpc_bid_micros"]

                operation = KeywordPlanAdGroupKeywordOperation()
                operation.create = keyword
                operations.append(operation)

            # Create request
            request = MutateKeywordPlanAdGroupKeywordsRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response = keyword_service.mutate_keyword_plan_ad_group_keywords(
                request=request
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                results.append(
                    {
                        "resource_name": result.resource_name,
                        "text": keywords[i]["text"],
                        "match_type": keywords[i].get("match_type", "BROAD"),
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} keywords to plan",
            )

            return results

        except Exception as e:
            error_msg = f"Failed to add keywords to plan: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_keyword_plan_tools(
    service: KeywordPlanService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the keyword plan service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_keyword_plan(
        ctx: Context,
        customer_id: str,
        name: str,
        forecast_period_days: int = 30,
    ) -> Dict[str, Any]:
        """Create a new keyword plan for keyword research.

        Args:
            customer_id: The customer ID
            name: The keyword plan name
            forecast_period_days: Forecast period in days (default 30)

        Returns:
            Created keyword plan details with resource_name and keyword_plan_id
        """
        return await service.create_keyword_plan(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            forecast_period_days=forecast_period_days,
        )

    async def get_keyword_ideas(
        ctx: Context,
        customer_id: str,
        keywords: Optional[List[str]] = None,
        url: Optional[str] = None,
        location_ids: Optional[List[str]] = None,
        language_id: Optional[str] = None,
        include_adult_keywords: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get keyword ideas based on seed keywords or URL.

        Args:
            customer_id: The customer ID
            keywords: Seed keywords to generate ideas from
            url: Seed URL to extract keyword ideas from
            location_ids: Geo target location IDs (e.g., ["2840"] for US)
            language_id: Language ID (e.g., "1000" for English)
            include_adult_keywords: Include adult keywords in results
            limit: Maximum number of results (default 100)

        Returns:
            List of keyword ideas with:
            - text: The keyword text
            - avg_monthly_searches: Average monthly search volume
            - competition: Competition level (LOW, MEDIUM, HIGH)
            - competition_index: Competition index (0-100)
            - low_top_of_page_bid_micros: Low top of page bid estimate
            - high_top_of_page_bid_micros: High top of page bid estimate
        """
        return await service.get_keyword_ideas(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            url=url,
            location_ids=location_ids,
            language_id=language_id,
            include_adult_keywords=include_adult_keywords,
            limit=limit,
        )

    async def create_keyword_plan_campaign(
        ctx: Context,
        customer_id: str,
        keyword_plan_id: str,
        name: str,
        cpc_bid_micros: int,
        location_ids: Optional[List[str]] = None,
        language_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a campaign within a keyword plan.

        Args:
            customer_id: The customer ID
            keyword_plan_id: The keyword plan ID
            name: Campaign name
            cpc_bid_micros: Default CPC bid in micros (e.g., 1000000 for $1.00)
            location_ids: Geo target location IDs (default: US)
            language_id: Language ID (default: English)

        Returns:
            Created campaign details with resource_name and campaign_id
        """
        return await service.create_keyword_plan_campaign(
            ctx=ctx,
            customer_id=customer_id,
            keyword_plan_id=keyword_plan_id,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
            location_ids=location_ids,
            language_id=language_id,
        )

    async def add_keywords_to_plan(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Add keywords to a keyword plan ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The keyword plan ad group ID
            keywords: List of keywords, each with:
                - text: Keyword text (required)
                - match_type: BROAD, PHRASE, or EXACT (default: BROAD)
                - cpc_bid_micros: CPC bid override (optional)

        Returns:
            List of created keyword details
        """
        return await service.add_keywords_to_plan(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
        )

    tools.extend(
        [
            create_keyword_plan,
            get_keyword_ideas,
            create_keyword_plan_campaign,
            add_keywords_to_plan,
        ]
    )
    return tools


def register_keyword_plan_tools(mcp: FastMCP[Any]) -> KeywordPlanService:
    """Register keyword plan tools with the MCP server.

    Returns the KeywordPlanService instance for testing purposes.
    """
    service = KeywordPlanService()
    tools = create_keyword_plan_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
