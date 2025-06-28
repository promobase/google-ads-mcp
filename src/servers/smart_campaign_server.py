"""Smart campaign server using SDK implementation."""

from fastmcp import FastMCP

from src.services.campaign.smart_campaign_service import (
    register_smart_campaign_tools,
)

# Create the smart campaign server
smart_campaign_server = FastMCP(
    name="smart_campaign",
    instructions="""This server provides tools for smart campaign suggestions.

    Available tools:
    - suggest_budget_options: Get budget recommendations
    - suggest_keyword_themes: Get keyword theme suggestions
    - suggest_ad_content: Get ad headline and description suggestions

    Smart campaigns are simplified campaigns that:
    - Use machine learning for optimization
    - Require minimal setup and management
    - Focus on local businesses and services
    - Automatically create ads based on your business

    Budget suggestions provide:
    - Low, recommended, and high daily budget options
    - Tailored to your business location and goals

    Keyword themes help you:
    - Target relevant searches
    - Reach customers looking for your products/services
    - Can be based on your business name, website, or seed keywords

    Ad content suggestions:
    - Generate headlines and descriptions automatically
    - Based on your business information and landing page
    - Optimized for performance

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
smart_campaign_service = register_smart_campaign_tools(smart_campaign_server)
