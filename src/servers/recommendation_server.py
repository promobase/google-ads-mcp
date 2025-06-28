"""Recommendation server using SDK implementation."""

from fastmcp import FastMCP

from src.services.planning.recommendation_service import (
    register_recommendation_tools,
)

# Create the recommendation server
recommendation_server = FastMCP(
    name="recommendation",
    instructions="""This server provides tools for managing Google Ads optimization recommendations.

    Available tools:
    - get_recommendations: Get optimization recommendations for the account
    - apply_recommendation: Apply a specific recommendation
    - dismiss_recommendation: Dismiss one or more recommendations

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
recommendation_service = register_recommendation_tools(recommendation_server)
