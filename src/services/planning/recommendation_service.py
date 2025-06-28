"""Recommendation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.services.services.recommendation_service import (
    RecommendationServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.recommendation_service import (
    ApplyRecommendationOperation,
    ApplyRecommendationRequest,
    ApplyRecommendationResponse,
    DismissRecommendationRequest,
    DismissRecommendationResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class RecommendationService:
    """Recommendation service for Google Ads optimization suggestions."""

    def __init__(self) -> None:
        """Initialize the recommendation service."""
        self._client: Optional[RecommendationServiceClient] = None

    @property
    def client(self) -> RecommendationServiceClient:
        """Get the recommendation service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("RecommendationService")
        assert self._client is not None
        return self._client

    async def get_recommendations(
        self,
        ctx: Context,
        customer_id: str,
        types: Optional[List[str]] = None,
        campaign_ids: Optional[List[str]] = None,
        dismissed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get recommendations for the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            types: Optional list of recommendation types to filter
            campaign_ids: Optional list of campaign IDs to filter
            dismissed: Whether to include dismissed recommendations
            limit: Maximum number of results

        Returns:
            List of recommendations
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
                    recommendation.type,
                    recommendation.impact,
                    recommendation.campaign,
                    recommendation.ad_group,
                    recommendation.resource_name,
                    recommendation.dismissed,
                    recommendation.campaign_budget_recommendation,
                    recommendation.keyword_recommendation,
                    recommendation.text_ad_recommendation,
                    recommendation.target_cpa_opt_in_recommendation,
                    recommendation.responsive_search_ad_recommendation,
                    recommendation.sitelink_extension_recommendation
                FROM recommendation
            """

            # Add filters
            conditions = []
            if not dismissed:
                conditions.append("recommendation.dismissed = FALSE")

            if types:
                type_conditions = [f"recommendation.type = '{t}'" for t in types]
                conditions.append(f"({' OR '.join(type_conditions)})")

            if campaign_ids:
                campaign_conditions = [
                    f"recommendation.campaign = 'customers/{customer_id}/campaigns/{cid}'"
                    for cid in campaign_ids
                ]
                conditions.append(f"({' OR '.join(campaign_conditions)})")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY recommendation.impact.base_metrics.clicks DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            recommendations = []
            for row in response:
                rec = row.recommendation
                rec_dict = {
                    "resource_name": rec.resource_name,
                    "type": rec.type.name if rec.type else "UNKNOWN",
                    "dismissed": rec.dismissed,
                }

                # Add impact if available
                if rec.impact:
                    impact = rec.impact
                    rec_dict["impact"] = {"base_metrics": {}, "potential_metrics": {}}

                    if impact.base_metrics:
                        base = impact.base_metrics
                        rec_dict["impact"]["base_metrics"] = {
                            "impressions": base.impressions,
                            "clicks": base.clicks,
                            "cost_micros": base.cost_micros,
                            "conversions": base.conversions,
                            "conversions_value": base.conversions_value,
                        }

                    if impact.potential_metrics:
                        potential = impact.potential_metrics
                        rec_dict["impact"]["potential_metrics"] = {
                            "impressions": potential.impressions,
                            "clicks": potential.clicks,
                            "cost_micros": potential.cost_micros,
                            "conversions": potential.conversions,
                            "conversions_value": potential.conversions_value,
                        }

                # Add campaign and ad group info
                if rec.campaign:
                    rec_dict["campaign"] = rec.campaign
                if rec.ad_group:
                    rec_dict["ad_group"] = rec.ad_group

                # Add type-specific details
                if rec.campaign_budget_recommendation:
                    budget_rec = rec.campaign_budget_recommendation
                    rec_dict["campaign_budget_recommendation"] = {
                        "current_budget_amount_micros": budget_rec.current_budget_amount_micros,
                        "recommended_budget_amount_micros": budget_rec.recommended_budget_amount_micros,
                        "budget_options": [
                            {
                                "budget_amount_micros": opt.budget_amount_micros,
                                "impact": {
                                    "impressions": opt.impact.impressions,
                                    "clicks": opt.impact.clicks,
                                    "cost_micros": opt.impact.cost_micros,
                                    "conversions": opt.impact.conversions,
                                },
                            }
                            for opt in budget_rec.budget_options
                        ],
                    }

                if rec.keyword_recommendation:
                    kw_rec = rec.keyword_recommendation
                    rec_dict["keyword_recommendation"] = {
                        "keyword_text": kw_rec.keyword.text,
                        "match_type": kw_rec.keyword.match_type.name,
                        "recommended_cpc_bid_micros": kw_rec.recommended_cpc_bid_micros,
                    }

                if rec.text_ad_recommendation:
                    ad_rec = rec.text_ad_recommendation
                    rec_dict["text_ad_recommendation"] = {
                        "ad": {
                            "headlines": [h.text for h in ad_rec.ad.headlines],
                            "descriptions": [d.text for d in ad_rec.ad.descriptions],
                            "final_urls": list(ad_rec.ad.final_urls),
                        }
                    }

                recommendations.append(rec_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(recommendations)} recommendations",
            )

            return recommendations

        except Exception as e:
            error_msg = f"Failed to get recommendations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_recommendation(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_resource_name: str,
    ) -> Dict[str, Any]:
        """Apply a recommendation.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_resource_name: The recommendation resource name to apply

        Returns:
            Applied recommendation details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = ApplyRecommendationOperation()
            operation.resource_name = recommendation_resource_name

            # Create request
            request = ApplyRecommendationRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            # Make the API call
            response: ApplyRecommendationResponse = self.client.apply_recommendation(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Applied recommendation: {recommendation_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply recommendation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def dismiss_recommendation(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_resource_names: List[str],
    ) -> Dict[str, Any]:
        """Dismiss one or more recommendations.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_resource_names: List of recommendation resource names to dismiss

        Returns:
            Dismissal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for resource_name in recommendation_resource_names:
                operation = (
                    DismissRecommendationRequest.DismissRecommendationOperation()
                )
                operation.resource_name = resource_name
                operations.append(operation)

            # Create request
            request = DismissRecommendationRequest()
            request.customer_id = customer_id
            request.operations = operations

            # Make the API call
            response: DismissRecommendationResponse = (
                self.client.dismiss_recommendation(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Dismissed {len(recommendation_resource_names)} recommendations",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to dismiss recommendations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_recommendation_tools(
    service: RecommendationService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the recommendation service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def get_recommendations(
        ctx: Context,
        customer_id: str,
        types: Optional[List[str]] = None,
        campaign_ids: Optional[List[str]] = None,
        dismissed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations for the account.

        Args:
            customer_id: The customer ID
            types: Optional list of recommendation types to filter:
                - CAMPAIGN_BUDGET
                - KEYWORD
                - TEXT_AD
                - TARGET_CPA_OPT_IN
                - RESPONSIVE_SEARCH_AD
                - SITELINK_EXTENSION
                - CALL_EXTENSION
                - KEYWORD_MATCH_TYPE
                - etc.
            campaign_ids: Optional list of campaign IDs to filter recommendations
            dismissed: Whether to include dismissed recommendations
            limit: Maximum number of results

        Returns:
            List of recommendations with type, impact, and specific details
        """
        return await service.get_recommendations(
            ctx=ctx,
            customer_id=customer_id,
            types=types,
            campaign_ids=campaign_ids,
            dismissed=dismissed,
            limit=limit,
        )

    async def apply_recommendation(
        ctx: Context,
        customer_id: str,
        recommendation_resource_name: str,
    ) -> Dict[str, Any]:
        """Apply a specific recommendation.

        Args:
            customer_id: The customer ID
            recommendation_resource_name: The full resource name of the recommendation to apply

        Returns:
            Applied recommendation details
        """
        return await service.apply_recommendation(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_resource_name=recommendation_resource_name,
        )

    async def dismiss_recommendation(
        ctx: Context,
        customer_id: str,
        recommendation_resource_names: List[str],
    ) -> Dict[str, Any]:
        """Dismiss one or more recommendations.

        Args:
            customer_id: The customer ID
            recommendation_resource_names: List of recommendation resource names to dismiss

        Returns:
            Dismissal result with count and status
        """
        return await service.dismiss_recommendation(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_resource_names=recommendation_resource_names,
        )

    tools.extend([get_recommendations, apply_recommendation, dismiss_recommendation])
    return tools


def register_recommendation_tools(mcp: FastMCP[Any]) -> RecommendationService:
    """Register recommendation tools with the MCP server.

    Returns the RecommendationService instance for testing purposes.
    """
    service = RecommendationService()
    tools = create_recommendation_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
