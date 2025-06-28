"""Smart campaign service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.criteria import LocationInfo
from google.ads.googleads.v20.services.services.smart_campaign_suggest_service import (
    SmartCampaignSuggestServiceClient,
)
from google.ads.googleads.v20.services.types.smart_campaign_suggest_service import (
    SuggestKeywordThemesRequest,
    SuggestKeywordThemesResponse,
    SuggestSmartCampaignAdRequest,
    SuggestSmartCampaignAdResponse,
    SuggestSmartCampaignBudgetOptionsRequest,
    SuggestSmartCampaignBudgetOptionsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class SmartCampaignService:
    """Smart campaign service for simplified campaign management."""

    def __init__(self) -> None:
        """Initialize the smart campaign service."""
        self._client: Optional[SmartCampaignSuggestServiceClient] = None

    @property
    def client(self) -> SmartCampaignSuggestServiceClient:
        """Get the smart campaign suggest service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("SmartCampaignSuggestService")
        assert self._client is not None
        return self._client

    async def suggest_budget_options(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        country_code: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get budget suggestions for a smart campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Existing campaign ID (optional)
            country_code: Country code for new campaigns (e.g., "US")
            language_code: Language code for new campaigns (e.g., "en")

        Returns:
            Budget suggestions with low, recommended, and high options
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = SuggestSmartCampaignBudgetOptionsRequest()
            request.customer_id = customer_id

            if campaign_id:
                request.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
            else:
                # For new campaigns, provide targeting info
                if country_code:
                    location_info = LocationInfo()
                    # Map country code to geo target constant
                    # US = 2840, GB = 2826, etc.
                    country_map = {"US": "2840", "GB": "2826", "CA": "2124"}
                    location_id = country_map.get(country_code, "2840")
                    location_info.geo_target_constant = (
                        f"geoTargetConstants/{location_id}"
                    )
                    request.location_info = location_info

                if language_code:
                    # Map language code to language constant
                    # en = 1000, es = 1003, etc.
                    language_map = {"en": "1000", "es": "1003", "fr": "1002"}
                    language_id = language_map.get(language_code, "1000")
                    request.language_code = f"languageConstants/{language_id}"

            # Make the API call
            response: SuggestSmartCampaignBudgetOptionsResponse = (
                self.client.suggest_smart_campaign_budget_options(request=request)
            )

            # Process results
            options = []
            if response.low:
                options.append(
                    {
                        "level": "LOW",
                        "daily_amount_micros": response.low.daily_amount_micros,
                    }
                )
            if response.recommended:
                options.append(
                    {
                        "level": "RECOMMENDED",
                        "daily_amount_micros": response.recommended.daily_amount_micros,
                    }
                )
            if response.high:
                options.append(
                    {
                        "level": "HIGH",
                        "daily_amount_micros": response.high.daily_amount_micros,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Generated {len(options)} budget suggestions",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get budget suggestions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def suggest_keyword_themes(
        self,
        ctx: Context,
        customer_id: str,
        keyword_text: Optional[str] = None,
        business_name: Optional[str] = None,
        final_url: Optional[str] = None,
        location_id: Optional[str] = None,
        language_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get keyword theme suggestions for a smart campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keyword_text: Seed keyword text
            business_name: Business name for suggestions
            final_url: Landing page URL
            location_id: Geo target location ID
            language_id: Language ID

        Returns:
            List of keyword theme suggestions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = SuggestKeywordThemesRequest()
            request.customer_id = customer_id

            # Set business info
            if business_name:
                request.suggestion_info.business_info.business_name = business_name

            if final_url:
                request.suggestion_info.final_url = final_url

            if keyword_text:
                request.suggestion_info.keyword_seed = keyword_text

            # Set location and language
            if location_id:
                location_info = LocationInfo()
                location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
                request.suggestion_info.location_list.locations.append(location_info)
            else:
                # Default to US
                location_info = LocationInfo()
                location_info.geo_target_constant = "geoTargetConstants/2840"
                request.suggestion_info.location_list.locations.append(location_info)

            request.suggestion_info.language_code = (
                f"languageConstants/{language_id or '1000'}"  # Default to English
            )

            # Make the API call
            response: SuggestKeywordThemesResponse = self.client.suggest_keyword_themes(
                request=request
            )

            # Process results
            themes = []
            for theme in response.keyword_themes:
                theme_dict = {
                    "display_name": theme.display_name,
                    "keyword_theme_constant": theme.keyword_theme_constant,
                }

                # Add free-form keyword if present
                if theme.HasField("free_form_keyword_theme"):
                    theme_dict["free_form_text"] = theme.free_form_keyword_theme
                    theme_dict["type"] = "FREE_FORM"
                else:
                    theme_dict["type"] = "CONSTANT"

                themes.append(theme_dict)

            await ctx.log(
                level="info",
                message=f"Generated {len(themes)} keyword theme suggestions",
            )

            return themes

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get keyword theme suggestions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def suggest_ad_content(
        self,
        ctx: Context,
        customer_id: str,
        business_name: str,
        final_url: str,
        language_id: Optional[str] = None,
        keyword_themes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get ad content suggestions for a smart campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            business_name: Business name
            final_url: Landing page URL
            language_id: Language ID
            keyword_themes: List of keyword themes

        Returns:
            Suggested ad content with headlines and descriptions
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create request
            request = SuggestSmartCampaignAdRequest()
            request.customer_id = customer_id

            # Set business info
            request.suggestion_info.business_info.business_name = business_name
            request.suggestion_info.final_url = final_url
            request.suggestion_info.language_code = (
                f"languageConstants/{language_id or '1000'}"
            )

            # Add keyword themes if provided
            if keyword_themes:
                from google.ads.googleads.v20.common.types.criteria import (
                    KeywordThemeInfo,
                )

                for theme in keyword_themes:
                    theme_info = KeywordThemeInfo()
                    if theme.startswith("keywordThemeConstants/"):
                        theme_info.keyword_theme_constant = theme
                    else:
                        theme_info.free_form_keyword_theme = theme
                    request.suggestion_info.keyword_themes.append(theme_info)

            # Make the API call
            response: SuggestSmartCampaignAdResponse = (
                self.client.suggest_smart_campaign_ad(request=request)
            )

            # Process results
            ad_info = response.ad_info
            result = {
                "headlines": [],
                "descriptions": [],
            }

            if ad_info:
                for headline in ad_info.headlines:
                    result["headlines"].append(headline.text)

                for description in ad_info.descriptions:
                    result["descriptions"].append(description.text)

            await ctx.log(
                level="info",
                message=f"Generated {len(result['headlines'])} headlines and {len(result['descriptions'])} descriptions",
            )

            return result

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get ad content suggestions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_smart_campaign_tools(
    service: SmartCampaignService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the smart campaign service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def suggest_budget_options(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        country_code: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get budget suggestions for a smart campaign.

        Args:
            customer_id: The customer ID
            campaign_id: Existing campaign ID to get suggestions for (optional)
            country_code: Country code for new campaigns (e.g., "US", "GB", "CA")
            language_code: Language code for new campaigns (e.g., "en", "es", "fr")

        Returns:
            Budget suggestions with:
            - options: List of budget levels (LOW, RECOMMENDED, HIGH)
            - Each option includes daily_amount_micros
        """
        return await service.suggest_budget_options(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            country_code=country_code,
            language_code=language_code,
        )

    async def suggest_keyword_themes(
        ctx: Context,
        customer_id: str,
        keyword_text: Optional[str] = None,
        business_name: Optional[str] = None,
        final_url: Optional[str] = None,
        location_id: Optional[str] = None,
        language_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get keyword theme suggestions for a smart campaign.

        Args:
            customer_id: The customer ID
            keyword_text: Seed keyword text to base suggestions on
            business_name: Business name for generating suggestions
            final_url: Landing page URL to analyze
            location_id: Geo target location ID (e.g., "2840" for US)
            language_id: Language ID (e.g., "1000" for English)

        Returns:
            List of keyword themes, each with:
            - display_name: Human-readable theme name
            - type: CONSTANT or FREE_FORM
            - keyword_theme_constant: Resource name for constant themes
            - free_form_text: Text for free-form themes
        """
        return await service.suggest_keyword_themes(
            ctx=ctx,
            customer_id=customer_id,
            keyword_text=keyword_text,
            business_name=business_name,
            final_url=final_url,
            location_id=location_id,
            language_id=language_id,
        )

    async def suggest_ad_content(
        ctx: Context,
        customer_id: str,
        business_name: str,
        final_url: str,
        language_id: Optional[str] = None,
        keyword_themes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get ad content suggestions for a smart campaign.

        Args:
            customer_id: The customer ID
            business_name: Business name to feature in ads
            final_url: Landing page URL
            language_id: Language ID (e.g., "1000" for English)
            keyword_themes: List of keyword theme resource names

        Returns:
            Suggested ad content with:
            - headlines: List of suggested headlines
            - descriptions: List of suggested descriptions
        """
        return await service.suggest_ad_content(
            ctx=ctx,
            customer_id=customer_id,
            business_name=business_name,
            final_url=final_url,
            language_id=language_id,
            keyword_themes=keyword_themes,
        )

    tools.extend([suggest_budget_options, suggest_keyword_themes, suggest_ad_content])
    return tools


def register_smart_campaign_tools(mcp: FastMCP[Any]) -> SmartCampaignService:
    """Register smart campaign tools with the MCP server.

    Returns the SmartCampaignService instance for testing purposes.
    """
    service = SmartCampaignService()
    tools = create_smart_campaign_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
