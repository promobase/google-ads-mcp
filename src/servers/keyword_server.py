"""Keyword server using SDK implementation."""

from fastmcp import FastMCP

from src.services.ad_group.keyword_service import register_keyword_tools

# Create the keyword server
keyword_server = FastMCP(name="keyword-service")

# Register the tools
register_keyword_tools(keyword_server)
