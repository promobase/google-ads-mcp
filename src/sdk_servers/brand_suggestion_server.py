"""MCP Server for Google Ads Brand Suggestion Service

This server provides MCP tools for getting brand suggestions in Google Ads.
Brand suggestions help advertisers find relevant brands for their campaigns.
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..sdk_services.planning.brand_suggestion_service import BrandSuggestionService
from ..utils import ensure_client, handle_googleads_exception


def create_brand_suggestion_server() -> Server:
    """Create and configure the brand suggestion MCP server."""
    server = Server("brand-suggestion-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available brand suggestion tools."""
        return [
            Tool(
                name="suggest_brands",
                description="Get brand suggestions based on a brand prefix",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "brand_prefix": {
                            "type": "string",
                            "description": "The prefix of a brand name to search for",
                        },
                        "selected_brands": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of brand IDs to exclude from results",
                            "default": [],
                        },
                    },
                    "required": ["customer_id", "brand_prefix"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for brand suggestion operations."""
        try:
            client = ensure_client()
            service = BrandSuggestionService(client)

            if name == "suggest_brands":
                customer_id = arguments["customer_id"]
                brand_prefix = arguments["brand_prefix"]
                selected_brands = arguments.get("selected_brands", [])

                response = service.suggest_brands(
                    customer_id=customer_id,
                    brand_prefix=brand_prefix,
                    selected_brands=selected_brands,
                )

                # Format the response
                suggestions = []
                for suggestion in response.brands:
                    brand_info = {
                        "id": suggestion.id,
                        "name": suggestion.name,
                        "urls": list(suggestion.urls),
                        "state": str(suggestion.state).split(".")[-1]
                        if suggestion.state
                        else "UNKNOWN",
                    }
                    suggestions.append(brand_info)

                result_text = f"Found {len(suggestions)} brand suggestions for prefix '{brand_prefix}':\n\n"
                for i, brand in enumerate(suggestions, 1):
                    result_text += f"{i}. {brand['name']} (ID: {brand['id']})\n"
                    result_text += f"   State: {brand['state']}\n"
                    if brand["urls"]:
                        result_text += f"   URLs: {', '.join(brand['urls'])}\n"
                    result_text += "\n"

                return [TextContent(type="text", text=result_text)]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
