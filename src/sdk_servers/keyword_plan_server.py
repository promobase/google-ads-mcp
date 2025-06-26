"""Keyword plan server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.planning.keyword_plan_service import register_keyword_plan_tools

# Create the keyword plan server
keyword_plan_sdk_server = FastMCP(
    name="keyword_plan",
    instructions="""This server provides tools for keyword research and planning.

    Available tools:
    - create_keyword_plan: Create a new keyword plan for research
    - get_keyword_ideas: Get keyword suggestions based on seed keywords or URL
    - create_keyword_plan_campaign: Create a campaign within a keyword plan
    - add_keywords_to_plan: Add keywords to a keyword plan ad group

    Keyword plans help you:
    - Research new keyword opportunities
    - Get search volume and competition data
    - Estimate bid prices
    - Plan campaign structure before creation

    The get_keyword_ideas tool provides:
    - Average monthly searches
    - Competition level (LOW, MEDIUM, HIGH)
    - Bid estimates for top of page placement

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
keyword_plan_service = register_keyword_plan_tools(keyword_plan_sdk_server)
