"""Search server using SDK implementation."""

from fastmcp import FastMCP

from src.sdk_services.metadata.search_service import register_search_tools

# Create the search server
search_sdk_server = FastMCP(name="search-service")

# Register the tools
register_search_tools(search_sdk_server)
