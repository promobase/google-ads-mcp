"""MCP Server for Google Ads Asset Group Signal Service.

This server provides MCP tools for managing audience and search theme signals
for Performance Max asset groups.
"""

import json
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.asset_group_signal_service import (
    AssetGroupSignalServiceClient,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)

from ..sdk_services.assets.asset_group_signal_service import AssetGroupSignalService
from ..core.client_manager import get_client


def create_asset_group_signal_server() -> Server:
    """Create and configure the Asset Group Signal MCP server."""
    server = Server("asset-group-signal-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Asset Group Signal tools."""
        return [
            Tool(
                name="mutate_asset_group_signals",
                description="Create or remove asset group signals for Performance Max campaigns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of operations to perform",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "operation_type": {
                                        "type": "string",
                                        "enum": ["create", "remove"],
                                        "description": "Type of operation",
                                    },
                                    "asset_group": {
                                        "type": "string",
                                        "description": "Asset group resource name (for create operations)",
                                    },
                                    "signal_type": {
                                        "type": "string",
                                        "enum": ["audience", "search_theme"],
                                        "description": "Type of signal (for create operations)",
                                    },
                                    "audience_resource_name": {
                                        "type": "string",
                                        "description": "Audience resource name (for audience signals)",
                                    },
                                    "search_theme_text": {
                                        "type": "string",
                                        "description": "Search theme text (for search theme signals)",
                                    },
                                    "resource_name": {
                                        "type": "string",
                                        "description": "Resource name to remove (for remove operations)",
                                    },
                                },
                                "required": ["operation_type"],
                            },
                        },
                        "partial_failure": {
                            "type": "boolean",
                            "description": "If true, successful operations will be carried out and invalid operations will return errors",
                            "default": False,
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                        "response_content_type": {
                            "type": "string",
                            "enum": ["RESOURCE_NAME_ONLY", "MUTABLE_RESOURCE"],
                            "description": "The response content type setting",
                            "default": "RESOURCE_NAME_ONLY",
                        },
                    },
                    "required": ["customer_id", "operations"],
                },
            ),
            Tool(
                name="create_audience_signal",
                description="Create an audience signal for a Performance Max asset group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "asset_group": {
                            "type": "string",
                            "description": "The asset group resource name",
                        },
                        "audience_resource_name": {
                            "type": "string",
                            "description": "The audience resource name",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": [
                        "customer_id",
                        "asset_group",
                        "audience_resource_name",
                    ],
                },
            ),
            Tool(
                name="create_search_theme_signal",
                description="Create a search theme signal for a Performance Max asset group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "asset_group": {
                            "type": "string",
                            "description": "The asset group resource name",
                        },
                        "search_theme_text": {
                            "type": "string",
                            "description": "The search theme text",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "asset_group", "search_theme_text"],
                },
            ),
            Tool(
                name="remove_asset_group_signal",
                description="Remove an asset group signal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The resource name of the signal to remove",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for Asset Group Signal operations."""
        try:
            client = get_client(AssetGroupSignalServiceClient)
            service = AssetGroupSignalService(client)

            if name == "mutate_asset_group_signals":
                return await _handle_mutate_asset_group_signals(service, arguments)
            elif name == "create_audience_signal":
                return await _handle_create_audience_signal(service, arguments)
            elif name == "create_search_theme_signal":
                return await _handle_create_search_theme_signal(service, arguments)
            elif name == "remove_asset_group_signal":
                return await _handle_remove_asset_group_signal(service, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_asset_group_signals(
    service: AssetGroupSignalService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate asset group signals request."""
    customer_id = arguments["customer_id"]
    operations_data = arguments["operations"]
    partial_failure = arguments.get("partial_failure", False)
    validate_only = arguments.get("validate_only", False)
    response_content_type_str = arguments.get(
        "response_content_type", "RESOURCE_NAME_ONLY"
    )

    # Convert string to enum
    response_content_type = getattr(
        ResponseContentTypeEnum.ResponseContentType, response_content_type_str
    )

    operations = []
    for op_data in operations_data:
        operation_type = op_data["operation_type"]

        if operation_type == "create":
            asset_group = op_data["asset_group"]
            signal_type = op_data["signal_type"]

            if signal_type == "audience":
                audience_resource_name = op_data["audience_resource_name"]
                operation = service.create_audience_signal(
                    asset_group=asset_group,
                    audience_resource_name=audience_resource_name,
                )
            elif signal_type == "search_theme":
                search_theme_text = op_data["search_theme_text"]
                operation = service.create_search_theme_signal(
                    asset_group=asset_group, search_theme=search_theme_text
                )
            else:
                raise ValueError(f"Invalid signal_type: {signal_type}")

        elif operation_type == "remove":
            resource_name = op_data["resource_name"]
            operation = service.create_remove_operation(resource_name=resource_name)
        else:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        operations.append(operation)

    response = service.mutate_asset_group_signals(
        customer_id=customer_id,
        operations=operations,
        partial_failure=partial_failure,
        validate_only=validate_only,
        response_content_type=response_content_type,
    )

    # Format response
    results = []
    for result in response.results:
        result_data = {
            "resource_name": result.resource_name,
        }
        if result.asset_group_signal:
            result_data["asset_group_signal"] = {
                "resource_name": result.asset_group_signal.resource_name,
                "asset_group": result.asset_group_signal.asset_group,
                "approval_status": result.asset_group_signal.approval_status.name
                if result.asset_group_signal.approval_status
                else None,
                "disapproval_reasons": list(
                    result.asset_group_signal.disapproval_reasons
                ),
            }

            # Add signal type specific data
            if result.asset_group_signal.audience:
                result_data["asset_group_signal"]["signal_type"] = "audience"
                result_data["asset_group_signal"]["audience"] = (
                    result.asset_group_signal.audience.audience
                )
            elif result.asset_group_signal.search_theme:
                result_data["asset_group_signal"]["signal_type"] = "search_theme"
                result_data["asset_group_signal"]["search_theme"] = (
                    result.asset_group_signal.search_theme.text
                )

        results.append(result_data)

    response_data = {
        "results": results,
        "partial_failure_error": str(response.partial_failure_error)
        if response.partial_failure_error
        else None,
    }

    return [TextContent(type="text", text=json.dumps(response_data, indent=2))]


async def _handle_create_audience_signal(
    service: AssetGroupSignalService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create audience signal request."""
    customer_id = arguments["customer_id"]
    asset_group = arguments["asset_group"]
    audience_resource_name = arguments["audience_resource_name"]
    validate_only = arguments.get("validate_only", False)

    operation = service.create_audience_signal(
        asset_group=asset_group, audience_resource_name=audience_resource_name
    )

    response = service.mutate_asset_group_signals(
        customer_id=customer_id,
        operations=[operation],
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_audience_signal",
        "asset_group": asset_group,
        "audience_resource_name": audience_resource_name,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_search_theme_signal(
    service: AssetGroupSignalService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create search theme signal request."""
    customer_id = arguments["customer_id"]
    asset_group = arguments["asset_group"]
    search_theme_text = arguments["search_theme_text"]
    validate_only = arguments.get("validate_only", False)

    operation = service.create_search_theme_signal(
        asset_group=asset_group, search_theme=search_theme_text
    )

    response = service.mutate_asset_group_signals(
        customer_id=customer_id,
        operations=[operation],
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_search_theme_signal",
        "asset_group": asset_group,
        "search_theme_text": search_theme_text,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_remove_asset_group_signal(
    service: AssetGroupSignalService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle remove asset group signal request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    operation = service.create_remove_operation(resource_name=resource_name)

    response = service.mutate_asset_group_signals(
        customer_id=customer_id,
        operations=[operation],
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "remove",
        "removed_resource_name": resource_name,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


def register_asset_group_signal_server(mcp: FastMCP) -> None:
    """Register Asset Group Signal service with FastMCP."""
    server = create_asset_group_signal_server()
    mcp.mount(server, prefix="asset_group_signal")
