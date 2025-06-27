"""Tests for SmartCampaignService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v20.services.services.smart_campaign_suggest_service import (
    SmartCampaignSuggestServiceClient,
)
from google.ads.googleads.v20.services.types.smart_campaign_suggest_service import (
    SuggestKeywordThemesResponse,
    SuggestSmartCampaignAdResponse,
    SuggestSmartCampaignBudgetOptionsResponse,
)

from src.sdk_services.campaign.smart_campaign_service import (
    SmartCampaignService,
    register_smart_campaign_tools,
)


@pytest.fixture
def smart_campaign_service(mock_sdk_client: Any) -> SmartCampaignService:
    """Create a SmartCampaignService instance with mocked dependencies."""
    # Mock SmartCampaignSuggestService client
    mock_smart_campaign_client = Mock(spec=SmartCampaignSuggestServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_smart_campaign_client  # type: ignore

    with patch(
        "src.sdk_services.campaign.smart_campaign_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = SmartCampaignService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_suggest_budget_options_existing_campaign(
    smart_campaign_service: SmartCampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting budget options for an existing campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Create mock response
    mock_response = Mock(spec=SuggestSmartCampaignBudgetOptionsResponse)

    # Mock budget options
    mock_response.low = Mock()
    mock_response.low.daily_amount_micros = 10000000  # $10  # type: ignore

    mock_response.recommended = Mock()
    mock_response.recommended.daily_amount_micros = 25000000  # $25  # type: ignore

    mock_response.high = Mock()
    mock_response.high.daily_amount_micros = 50000000  # $50  # type: ignore

    # Get the mocked smart campaign suggest service client
    mock_smart_campaign_client = smart_campaign_service.client  # type: ignore
    mock_smart_campaign_client.suggest_smart_campaign_budget_options.return_value = (  # type: ignore
        mock_response  # type: ignore
    )

    # Mock serialize_proto_message to return expected structure
    expected_result = {
        "low": {
            "daily_amount_micros": 10000000,
        },
        "recommended": {
            "daily_amount_micros": 25000000,
        },
        "high": {
            "daily_amount_micros": 50000000,
        },
    }

    with patch(
        "src.sdk_services.campaign.smart_campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await smart_campaign_service.suggest_budget_options(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_smart_campaign_client.suggest_smart_campaign_budget_options.assert_called_once()  # type: ignore
    call_args = (
        mock_smart_campaign_client.suggest_smart_campaign_budget_options.call_args  # type: ignore
    )  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 3 budget suggestions",
    )


@pytest.mark.asyncio
async def test_suggest_keyword_themes(
    smart_campaign_service: SmartCampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting keyword themes."""
    # Arrange
    customer_id = "1234567890"
    final_url = "https://example.com"
    business_name = "Example Business"

    # Create mock response
    mock_response = Mock(spec=SuggestKeywordThemesResponse)

    # Mock keyword themes
    mock_themes = []
    theme1 = Mock()
    theme1.display_name = "online shopping"
    theme1.keyword_theme_constant = "keywordThemeConstants/123"
    theme1.HasField.return_value = False  # Not a free-form theme  # type: ignore
    mock_themes.append(theme1)

    theme2 = Mock()
    theme2.display_name = "Example Business products"
    theme2.keyword_theme_constant = ""
    theme2.free_form_keyword_theme = "Example Business products"
    theme2.HasField.return_value = True  # Is a free-form theme  # type: ignore
    mock_themes.append(theme2)

    mock_response.keyword_themes = mock_themes

    # Get the mocked smart campaign suggest service client
    mock_smart_campaign_client = smart_campaign_service.client  # type: ignore
    mock_smart_campaign_client.suggest_keyword_themes.return_value = mock_response  # type: ignore

    # Act
    result = await smart_campaign_service.suggest_keyword_themes(
        ctx=mock_ctx,
        customer_id=customer_id,
        final_url=final_url,
        business_name=business_name,
    )

    # Assert
    assert len(result) == 2
    assert result[0]["display_name"] == "online shopping"
    assert result[0]["type"] == "CONSTANT"
    assert result[1]["display_name"] == "Example Business products"
    assert result[1]["type"] == "FREE_FORM"
    assert result[1]["free_form_text"] == "Example Business products"

    # Verify the API call
    mock_smart_campaign_client.suggest_keyword_themes.assert_called_once()  # type: ignore
    call_args = mock_smart_campaign_client.suggest_keyword_themes.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.suggestion_info.final_url == final_url
    assert request.suggestion_info.business_info.business_name == business_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 2 keyword theme suggestions",
    )


@pytest.mark.asyncio
async def test_suggest_ad_content(
    smart_campaign_service: SmartCampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting ad content."""
    # Arrange
    customer_id = "1234567890"
    final_url = "https://example.com"
    business_name = "Example Business"

    # Create mock response
    mock_response = Mock(spec=SuggestSmartCampaignAdResponse)

    # Mock ad info
    mock_response.ad_info = Mock()

    # Headlines
    mock_headlines = []
    headline_texts = ["Great Deals Online", "Shop Now & Save"]
    for text in headline_texts:
        headline = Mock()
        headline.text = text
        mock_headlines.append(headline)
    mock_response.ad_info.headlines = mock_headlines  # type: ignore

    # Descriptions
    mock_descriptions = []
    description_texts = ["Find amazing products at great prices"]
    for text in description_texts:
        desc = Mock()
        desc.text = text
        mock_descriptions.append(desc)
    mock_response.ad_info.descriptions = mock_descriptions  # type: ignore

    # Get the mocked smart campaign suggest service client
    mock_smart_campaign_client = smart_campaign_service.client  # type: ignore
    mock_smart_campaign_client.suggest_smart_campaign_ad.return_value = mock_response  # type: ignore

    # Act
    result = await smart_campaign_service.suggest_ad_content(
        ctx=mock_ctx,
        customer_id=customer_id,
        business_name=business_name,
        final_url=final_url,
    )

    # Assert
    assert len(result["headlines"]) == 2
    assert result["headlines"][0] == "Great Deals Online"
    assert result["headlines"][1] == "Shop Now & Save"
    assert len(result["descriptions"]) == 1
    assert result["descriptions"][0] == "Find amazing products at great prices"

    # Verify the API call
    mock_smart_campaign_client.suggest_smart_campaign_ad.assert_called_once()  # type: ignore
    call_args = mock_smart_campaign_client.suggest_smart_campaign_ad.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert request.suggestion_info.business_info.business_name == business_name
    assert request.suggestion_info.final_url == final_url

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Generated 2 headlines and 1 descriptions",
    )


@pytest.mark.asyncio
async def test_error_handling_suggest_budget_options(
    smart_campaign_service: SmartCampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when suggesting budget options fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "111222333"

    # Get the mocked smart campaign suggest service client and make it raise exception
    mock_smart_campaign_client = smart_campaign_service.client  # type: ignore
    mock_smart_campaign_client.suggest_smart_campaign_budget_options.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await smart_campaign_service.suggest_budget_options(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
        )

    assert "Failed to get budget suggestions" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to get budget suggestions: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_suggest_ad_content(
    smart_campaign_service: SmartCampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when suggesting ad content fails."""
    # Arrange
    customer_id = "1234567890"
    business_name = "Example Business"
    final_url = "https://example.com"

    # Get the mocked smart campaign suggest service client and make it raise exception
    mock_smart_campaign_client = smart_campaign_service.client  # type: ignore
    mock_smart_campaign_client.suggest_smart_campaign_ad.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await smart_campaign_service.suggest_ad_content(
            ctx=mock_ctx,
            customer_id=customer_id,
            business_name=business_name,
            final_url=final_url,
        )

    assert "Failed to get ad content suggestions" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to get ad content suggestions: Test Google Ads Exception",
    )


def test_register_smart_campaign_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_smart_campaign_tools(mock_mcp)

    # Assert
    assert isinstance(service, SmartCampaignService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 3  # 3 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "suggest_budget_options",
        "suggest_keyword_themes",
        "suggest_ad_content",
    ]

    assert set(tool_names) == set(expected_tools)
