"""MCP Server for Google Ads Keyword Plan Ad Group Service

This server provides MCP tools for managing keyword plan ad groups in Google Ads.
Keyword plan ad groups organize keywords within keyword plan campaigns for planning purposes.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..sdk_services.planning.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupService,
)
from ..utils import ensure_client, handle_googleads_exception


def create_keyword_plan_ad_group_server() -> Server:
    """Create and configure the keyword plan ad group MCP server."""
    server = Server("keyword-plan-ad-group-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available keyword plan ad group tools."""
        return [
            Tool(
                name="mutate_keyword_plan_ad_groups",
                description="Create, update, or remove keyword plan ad groups",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of keyword plan ad group operations",
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
                                    "keyword_plan_campaign": {
                                        "type": "string",
                                        "description": "Keyword plan campaign resource name (required for create)",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the keyword plan ad group",
                                    },
                                    "cpc_bid_micros": {
                                        "type": "integer",
                                        "description": "Default CPC bid in micros",
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
                name="create_keyword_plan_ad_group",
                description="Create a new keyword plan ad group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "keyword_plan_campaign": {
                            "type": "string",
                            "description": "The keyword plan campaign resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the keyword plan ad group",
                        },
                        "cpc_bid_micros": {
                            "type": "integer",
                            "description": "Default CPC bid in micros",
                        },
                    },
                    "required": ["customer_id", "keyword_plan_campaign", "name"],
                },
            ),
            Tool(
                name="update_keyword_plan_ad_group",
                description="Update an existing keyword plan ad group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan ad group resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the keyword plan ad group",
                        },
                        "cpc_bid_micros": {
                            "type": "integer",
                            "description": "Default CPC bid in micros",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
            Tool(
                name="remove_keyword_plan_ad_group",
                description="Remove a keyword plan ad group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan ad group resource name",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for keyword plan ad group operations."""
        try:
            client = ensure_client()
            service = KeywordPlanAdGroupService(client)

            if name == "mutate_keyword_plan_ad_groups":
                customer_id = arguments["customer_id"]
                operations_data = arguments["operations"]
                partial_failure = arguments.get("partial_failure", False)
                validate_only = arguments.get("validate_only", False)

                operations = []
                for op_data in operations_data:
                    op_type = op_data["operation_type"]

                    if op_type == "create":
                        operation = service.create_keyword_plan_ad_group_operation(
                            keyword_plan_campaign=op_data["keyword_plan_campaign"],
                            name=op_data["name"],
                            cpc_bid_micros=op_data.get("cpc_bid_micros"),
                        )
                    elif op_type == "update":
                        operation = service.update_keyword_plan_ad_group_operation(
                            resource_name=op_data["resource_name"],
                            name=op_data.get("name"),
                            cpc_bid_micros=op_data.get("cpc_bid_micros"),
                        )
                    elif op_type == "remove":
                        operation = service.remove_keyword_plan_ad_group_operation(
                            resource_name=op_data["resource_name"]
                        )
                    else:
                        raise ValueError(f"Invalid operation type: {op_type}")

                    operations.append(operation)

                response = service.mutate_keyword_plan_ad_groups(
                    customer_id=customer_id,
                    operations=operations,
                    partial_failure=partial_failure,
                    validate_only=validate_only,
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Successfully processed {len(response.results)} keyword plan ad group operations",
                    )
                ]

            elif name == "create_keyword_plan_ad_group":
                customer_id = arguments["customer_id"]
                operation = service.create_keyword_plan_ad_group_operation(
                    keyword_plan_campaign=arguments["keyword_plan_campaign"],
                    name=arguments["name"],
                    cpc_bid_micros=arguments.get("cpc_bid_micros"),
                )

                response = service.mutate_keyword_plan_ad_groups(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Created keyword plan ad group: {result.resource_name}",
                    )
                ]

            elif name == "update_keyword_plan_ad_group":
                customer_id = arguments["customer_id"]
                operation = service.update_keyword_plan_ad_group_operation(
                    resource_name=arguments["resource_name"],
                    name=arguments.get("name"),
                    cpc_bid_micros=arguments.get("cpc_bid_micros"),
                )

                response = service.mutate_keyword_plan_ad_groups(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Updated keyword plan ad group: {result.resource_name}",
                    )
                ]

            elif name == "remove_keyword_plan_ad_group":
                customer_id = arguments["customer_id"]
                operation = service.remove_keyword_plan_ad_group_operation(
                    resource_name=arguments["resource_name"]
                )

                response = service.mutate_keyword_plan_ad_groups(
                    customer_id=customer_id, operations=[operation]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Removed keyword plan ad group: {arguments['resource_name']}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
