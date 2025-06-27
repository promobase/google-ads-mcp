"""MCP Server for Google Ads Keyword Plan Campaign Keyword Service

This server provides MCP tools for managing keyword plan campaign keywords in Google Ads.
Note: Only negative keywords are supported for campaign-level keywords in keyword plans.
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum

from ..sdk_services.planning.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordService,
)
from ..utils import ensure_client, handle_googleads_exception


def create_keyword_plan_campaign_keyword_server() -> Server:
    """Create and configure the keyword plan campaign keyword MCP server."""
    server = Server("keyword-plan-campaign-keyword-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available keyword plan campaign keyword tools."""
        return [
            Tool(
                name="mutate_keyword_plan_campaign_keywords",
                description="Create, update, or remove keyword plan campaign keywords (negative keywords only)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of keyword plan campaign keyword operations",
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
                                    "text": {
                                        "type": "string",
                                        "description": "The keyword text",
                                    },
                                    "match_type": {
                                        "type": "string",
                                        "enum": ["EXACT", "PHRASE", "BROAD"],
                                        "description": "The keyword match type (required for create)",
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
                name="create_keyword_plan_campaign_keyword",
                description="Create a new keyword plan campaign keyword (negative keyword only)",
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
                        "text": {"type": "string", "description": "The keyword text"},
                        "match_type": {
                            "type": "string",
                            "enum": ["EXACT", "PHRASE", "BROAD"],
                            "description": "The keyword match type",
                        },
                    },
                    "required": [
                        "customer_id",
                        "keyword_plan_campaign",
                        "text",
                        "match_type",
                    ],
                },
            ),
            Tool(
                name="update_keyword_plan_campaign_keyword",
                description="Update an existing keyword plan campaign keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan campaign keyword resource name",
                        },
                        "text": {"type": "string", "description": "The keyword text"},
                        "match_type": {
                            "type": "string",
                            "enum": ["EXACT", "PHRASE", "BROAD"],
                            "description": "The keyword match type",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
            Tool(
                name="remove_keyword_plan_campaign_keyword",
                description="Remove a keyword plan campaign keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The keyword plan campaign keyword resource name",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for keyword plan campaign keyword operations."""
        try:
            client = ensure_client()
            service = KeywordPlanCampaignKeywordService(client)

            def _get_match_type_enum(
                match_type_str: str,
            ) -> KeywordMatchTypeEnum.KeywordMatchType:
                """Convert string to match type enum."""
                if match_type_str == "EXACT":
                    return KeywordMatchTypeEnum.KeywordMatchType.EXACT
                elif match_type_str == "PHRASE":
                    return KeywordMatchTypeEnum.KeywordMatchType.PHRASE
                elif match_type_str == "BROAD":
                    return KeywordMatchTypeEnum.KeywordMatchType.BROAD
                else:
                    raise ValueError(f"Invalid match type: {match_type_str}")

            if name == "mutate_keyword_plan_campaign_keywords":
                customer_id = arguments["customer_id"]
                operations_data = arguments["operations"]
                partial_failure = arguments.get("partial_failure", False)
                validate_only = arguments.get("validate_only", False)

                operations = []
                for op_data in operations_data:
                    op_type = op_data["operation_type"]

                    if op_type == "create":
                        operation = (
                            service.create_keyword_plan_campaign_keyword_operation(
                                keyword_plan_campaign=op_data["keyword_plan_campaign"],
                                text=op_data["text"],
                                match_type=_get_match_type_enum(op_data["match_type"]),
                            )
                        )
                    elif op_type == "update":
                        match_type = None
                        if "match_type" in op_data:
                            match_type = _get_match_type_enum(op_data["match_type"])

                        operation = (
                            service.update_keyword_plan_campaign_keyword_operation(
                                resource_name=op_data["resource_name"],
                                text=op_data.get("text"),
                                match_type=match_type,
                            )
                        )
                    elif op_type == "remove":
                        operation = (
                            service.remove_keyword_plan_campaign_keyword_operation(
                                resource_name=op_data["resource_name"]
                            )
                        )
                    else:
                        raise ValueError(f"Invalid operation type: {op_type}")

                    operations.append(operation)

                response = service.mutate_keyword_plan_campaign_keywords(
                    customer_id=customer_id,
                    operations=operations,
                    partial_failure=partial_failure,
                    validate_only=validate_only,
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Successfully processed {len(response.results)} keyword plan campaign keyword operations",
                    )
                ]

            elif name == "create_keyword_plan_campaign_keyword":
                customer_id = arguments["customer_id"]
                operation = service.create_keyword_plan_campaign_keyword_operation(
                    keyword_plan_campaign=arguments["keyword_plan_campaign"],
                    text=arguments["text"],
                    match_type=_get_match_type_enum(arguments["match_type"]),
                )

                response = service.mutate_keyword_plan_campaign_keywords(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Created keyword plan campaign keyword (negative): {result.resource_name}",
                    )
                ]

            elif name == "update_keyword_plan_campaign_keyword":
                customer_id = arguments["customer_id"]

                match_type = None
                if "match_type" in arguments:
                    match_type = _get_match_type_enum(arguments["match_type"])

                operation = service.update_keyword_plan_campaign_keyword_operation(
                    resource_name=arguments["resource_name"],
                    text=arguments.get("text"),
                    match_type=match_type,
                )

                response = service.mutate_keyword_plan_campaign_keywords(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Updated keyword plan campaign keyword: {result.resource_name}",
                    )
                ]

            elif name == "remove_keyword_plan_campaign_keyword":
                customer_id = arguments["customer_id"]
                operation = service.remove_keyword_plan_campaign_keyword_operation(
                    resource_name=arguments["resource_name"]
                )

                response = service.mutate_keyword_plan_campaign_keywords(
                    customer_id=customer_id, operations=[operation]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Removed keyword plan campaign keyword: {arguments['resource_name']}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
