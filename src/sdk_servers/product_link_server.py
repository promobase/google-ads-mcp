"""MCP Server for Google Ads Product Link Service

This server provides MCP tools for managing product links in Google Ads.
Product links connect Google Ads accounts with other Google products like Merchant Center.
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..sdk_services.product_integration.product_link_service import ProductLinkService
from ..utils import ensure_client, handle_googleads_exception


def create_product_link_server() -> Server:
    """Create and configure the product link MCP server."""
    server = Server("product-link-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available product link tools."""
        return [
            Tool(
                name="create_merchant_center_link",
                description="Create a link to a Google Merchant Center account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "merchant_center_id": {
                            "type": "integer",
                            "description": "The Merchant Center account ID",
                        },
                    },
                    "required": ["customer_id", "merchant_center_id"],
                },
            ),
            Tool(
                name="create_google_ads_link",
                description="Create a link to another Google Ads account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "linked_customer_id": {
                            "type": "integer",
                            "description": "The linked Google Ads customer ID",
                        },
                    },
                    "required": ["customer_id", "linked_customer_id"],
                },
            ),
            Tool(
                name="create_data_partner_link",
                description="Create a link to a data partner",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "data_partner_id": {
                            "type": "integer",
                            "description": "The data partner ID",
                        },
                    },
                    "required": ["customer_id", "data_partner_id"],
                },
            ),
            Tool(
                name="remove_product_link",
                description="Remove a product link",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The product link resource name to remove",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for product link operations."""
        try:
            client = ensure_client()
            service = ProductLinkService(client)

            if name == "create_merchant_center_link":
                customer_id = arguments["customer_id"]
                merchant_center_id = arguments["merchant_center_id"]

                response = service.create_merchant_center_link(
                    customer_id=customer_id, merchant_center_id=merchant_center_id
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Created Merchant Center link: {response.resource_name}",
                    )
                ]

            elif name == "create_google_ads_link":
                customer_id = arguments["customer_id"]
                linked_customer_id = arguments["linked_customer_id"]

                response = service.create_google_ads_link(
                    customer_id=customer_id, linked_customer_id=linked_customer_id
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Created Google Ads link: {response.resource_name}",
                    )
                ]

            elif name == "create_data_partner_link":
                customer_id = arguments["customer_id"]
                data_partner_id = arguments["data_partner_id"]

                response = service.create_data_partner_link(
                    customer_id=customer_id, data_partner_id=data_partner_id
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Created data partner link: {response.resource_name}",
                    )
                ]

            elif name == "remove_product_link":
                customer_id = arguments["customer_id"]
                resource_name = arguments["resource_name"]

                response = service.remove_product_link(
                    customer_id=customer_id, resource_name=resource_name
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Removed product link: {response.resource_name}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
