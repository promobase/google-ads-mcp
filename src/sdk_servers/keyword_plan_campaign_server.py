"""MCP Server for Google Ads Keyword Plan Campaign Service

This server provides MCP tools for managing keyword plan campaigns in Google Ads.
Keyword plan campaigns define the targeting and settings for keyword planning.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)

from ..sdk_services.planning.keyword_plan_campaign_service import (
    KeywordPlanCampaignService,
)
from ..utils import ensure_client, handle_googleads_exception


def create_keyword_plan_campaign_server() -> Server:
    """Create and configure the keyword plan campaign MCP server."""
    server = Server("keyword-plan-campaign-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available keyword plan campaign tools."""
        return [
            Tool(
                name="mutate_keyword_plan_campaigns",
                description="Create, update, or remove keyword plan campaigns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of keyword plan campaign operations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "operation_type": {
                                        "type": "string",
                                        "enum": ["create", "update", "remove"],
                                        "description": "Type of operation",
                                    },
                                    "resource_name": {
                                        "type": "string",
                                        "description": "Resource name (required for update/remove)",
                                    },
                                    "keyword_plan": {
                                        "type": "string",
                                        "description": "Keyword plan resource name (required for create)",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the keyword plan campaign",
                                    },
                                    "keyword_plan_network": {
                                        "type": "string",
                                        "enum": [
                                            "GOOGLE_SEARCH",
                                            "GOOGLE_SEARCH_AND_PARTNERS",
                                        ],
                                        "description": "Targeting network (required for create)",
                                    },
                                    "cpc_bid_micros": {
                                        "type": "integer",
                                        "description": "Default CPC bid in micros (required for create)",
                                    },
                                    "language_constants": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of language constant resource names",
                                    },
                                    "geo_target_constants": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of geo target constant resource names",
                                    },
                                },
                                "required": ["operation_type"],
                            },
                        },
                        "partial_failure": {
                            "type": "boolean",
                            "description": "Enable partial failure",
                            "default": False,
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "Only validate the request",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "operations"],
                },
            ),
            Tool(
                name="create_keyword_plan_campaign",
                description="Create a new keyword plan campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "keyword_plan": {
                            "type": "string",
                            "description": "The keyword plan resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the keyword plan campaign",
                        },
                        "keyword_plan_network": {
                            "type": "string",
                            "enum": ["GOOGLE_SEARCH", "GOOGLE_SEARCH_AND_PARTNERS"],
                            "description": "Targeting network",
                        },
                        "cpc_bid_micros": {
                            "type": "integer",
                            "description": "Default CPC bid in micros",
                        },
                        "language_constants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of language constant resource names",
                            "default": [],
                        },
                        "geo_target_constants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of geo target constant resource names",
                            "default": [],
                        },
                    },
                    "required": [
                        "customer_id",
                        "keyword_plan",
                        "name",
                        "keyword_plan_network",
                        "cpc_bid_micros",
                    ],
                },
            ),
            Tool(
                name="update_keyword_plan_campaign",
                description="Update an existing keyword plan campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan campaign resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the keyword plan campaign",
                        },
                        "keyword_plan_network": {
                            "type": "string",
                            "enum": ["GOOGLE_SEARCH", "GOOGLE_SEARCH_AND_PARTNERS"],
                            "description": "Targeting network",
                        },
                        "cpc_bid_micros": {
                            "type": "integer",
                            "description": "Default CPC bid in micros",
                        },
                        "language_constants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of language constant resource names",
                        },
                        "geo_target_constants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of geo target constant resource names",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
            Tool(
                name="remove_keyword_plan_campaign",
                description="Remove a keyword plan campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan campaign resource name",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for keyword plan campaign operations."""
        try:
            client = ensure_client()
            service = KeywordPlanCampaignService(client)

            def _get_network_enum(
                network_str: str,
            ) -> KeywordPlanNetworkEnum.KeywordPlanNetwork:
                """Convert string to network enum."""
                if network_str == "GOOGLE_SEARCH":
                    return KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
                elif network_str == "GOOGLE_SEARCH_AND_PARTNERS":
                    return KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
                else:
                    raise ValueError(f"Invalid network: {network_str}")

            if name == "mutate_keyword_plan_campaigns":
                customer_id = arguments["customer_id"]
                operations_data = arguments["operations"]
                partial_failure = arguments.get("partial_failure", False)
                validate_only = arguments.get("validate_only", False)

                operations = []
                for op_data in operations_data:
                    op_type = op_data["operation_type"]

                    if op_type == "create":
                        operation = service.create_keyword_plan_campaign_operation(
                            keyword_plan=op_data["keyword_plan"],
                            name=op_data["name"],
                            keyword_plan_network=_get_network_enum(
                                op_data["keyword_plan_network"]
                            ),
                            cpc_bid_micros=op_data["cpc_bid_micros"],
                            language_constants=op_data.get("language_constants"),
                            geo_target_constants=op_data.get("geo_target_constants"),
                        )
                    elif op_type == "update":
                        network = None
                        if "keyword_plan_network" in op_data:
                            network = _get_network_enum(op_data["keyword_plan_network"])

                        operation = service.update_keyword_plan_campaign_operation(
                            resource_name=op_data["resource_name"],
                            name=op_data.get("name"),
                            keyword_plan_network=network,
                            cpc_bid_micros=op_data.get("cpc_bid_micros"),
                            language_constants=op_data.get("language_constants"),
                            geo_target_constants=op_data.get("geo_target_constants"),
                        )
                    elif op_type == "remove":
                        operation = service.remove_keyword_plan_campaign_operation(
                            resource_name=op_data["resource_name"]
                        )
                    else:
                        raise ValueError(f"Invalid operation type: {op_type}")

                    operations.append(operation)

                response = service.mutate_keyword_plan_campaigns(
                    customer_id=customer_id,
                    operations=operations,
                    partial_failure=partial_failure,
                    validate_only=validate_only,
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Successfully processed {len(response.results)} keyword plan campaign operations",
                    )
                ]

            elif name == "create_keyword_plan_campaign":
                customer_id = arguments["customer_id"]
                operation = service.create_keyword_plan_campaign_operation(
                    keyword_plan=arguments["keyword_plan"],
                    name=arguments["name"],
                    keyword_plan_network=_get_network_enum(
                        arguments["keyword_plan_network"]
                    ),
                    cpc_bid_micros=arguments["cpc_bid_micros"],
                    language_constants=arguments.get("language_constants", []),
                    geo_target_constants=arguments.get("geo_target_constants", []),
                )

                response = service.mutate_keyword_plan_campaigns(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Created keyword plan campaign: {result.resource_name}",
                    )
                ]

            elif name == "update_keyword_plan_campaign":
                customer_id = arguments["customer_id"]

                network = None
                if "keyword_plan_network" in arguments:
                    network = _get_network_enum(arguments["keyword_plan_network"])

                operation = service.update_keyword_plan_campaign_operation(
                    resource_name=arguments["resource_name"],
                    name=arguments.get("name"),
                    keyword_plan_network=network,
                    cpc_bid_micros=arguments.get("cpc_bid_micros"),
                    language_constants=arguments.get("language_constants"),
                    geo_target_constants=arguments.get("geo_target_constants"),
                )

                response = service.mutate_keyword_plan_campaigns(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Updated keyword plan campaign: {result.resource_name}",
                    )
                ]

            elif name == "remove_keyword_plan_campaign":
                customer_id = arguments["customer_id"]
                operation = service.remove_keyword_plan_campaign_operation(
                    resource_name=arguments["resource_name"]
                )

                response = service.mutate_keyword_plan_campaigns(
                    customer_id=customer_id, operations=[operation]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Removed keyword plan campaign: {arguments['resource_name']}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
