"""MCP Server for Google Ads Ad Group Customizer Service.

This server provides MCP tools for managing customizer values at the ad group level.
"""

import json
from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.ad_group_customizer_service import (
    AdGroupCustomizerServiceClient,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)

from ..sdk_services.ad_group.ad_group_customizer_service import AdGroupCustomizerService
from ..core.client_manager import get_client


def create_ad_group_customizer_server() -> Server:
    """Create and configure the Ad Group Customizer MCP server."""
    server = Server("ad-group-customizer-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Ad Group Customizer tools."""
        return [
            Tool(
                name="mutate_ad_group_customizers",
                description="Create or remove ad group customizers",
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
                                    "ad_group": {
                                        "type": "string",
                                        "description": "Ad group resource name (for create operations)",
                                    },
                                    "customizer_attribute": {
                                        "type": "string",
                                        "description": "Customizer attribute resource name (for create operations)",
                                    },
                                    "value_type": {
                                        "type": "string",
                                        "enum": ["TEXT", "NUMBER", "PRICE", "PERCENT"],
                                        "description": "Type of customizer value (for create operations)",
                                    },
                                    "string_value": {
                                        "type": "string",
                                        "description": "String representation of the value (for create operations)",
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
                name="create_ad_group_customizer",
                description="Create an ad group customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group": {
                            "type": "string",
                            "description": "The ad group resource name",
                        },
                        "customizer_attribute": {
                            "type": "string",
                            "description": "The customizer attribute resource name",
                        },
                        "value_type": {
                            "type": "string",
                            "enum": ["TEXT", "NUMBER", "PRICE", "PERCENT"],
                            "description": "The type of customizer value",
                        },
                        "string_value": {
                            "type": "string",
                            "description": "The string representation of the value",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": [
                        "customer_id",
                        "ad_group",
                        "customizer_attribute",
                        "value_type",
                        "string_value",
                    ],
                },
            ),
            Tool(
                name="create_text_customizer",
                description="Create a text ad group customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group": {
                            "type": "string",
                            "description": "The ad group resource name",
                        },
                        "customizer_attribute": {
                            "type": "string",
                            "description": "The customizer attribute resource name",
                        },
                        "text_value": {
                            "type": "string",
                            "description": "The text value",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": [
                        "customer_id",
                        "ad_group",
                        "customizer_attribute",
                        "text_value",
                    ],
                },
            ),
            Tool(
                name="create_number_customizer",
                description="Create a number ad group customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group": {
                            "type": "string",
                            "description": "The ad group resource name",
                        },
                        "customizer_attribute": {
                            "type": "string",
                            "description": "The customizer attribute resource name",
                        },
                        "number_value": {
                            "type": "string",
                            "description": "The number value as a string",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": [
                        "customer_id",
                        "ad_group",
                        "customizer_attribute",
                        "number_value",
                    ],
                },
            ),
            Tool(
                name="create_price_customizer",
                description="Create a price ad group customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group": {
                            "type": "string",
                            "description": "The ad group resource name",
                        },
                        "customizer_attribute": {
                            "type": "string",
                            "description": "The customizer attribute resource name",
                        },
                        "price_value": {
                            "type": "string",
                            "description": "The price value as a string (e.g., '19.99')",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": [
                        "customer_id",
                        "ad_group",
                        "customizer_attribute",
                        "price_value",
                    ],
                },
            ),
            Tool(
                name="remove_ad_group_customizer",
                description="Remove an ad group customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The ad group customizer resource name to remove",
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
        """Handle tool calls for Ad Group Customizer operations."""
        try:
            client = get_client(AdGroupCustomizerServiceClient)
            service = AdGroupCustomizerService(client)

            if name == "mutate_ad_group_customizers":
                return await _handle_mutate_ad_group_customizers(service, arguments)
            elif name == "create_ad_group_customizer":
                return await _handle_create_ad_group_customizer(service, arguments)
            elif name == "create_text_customizer":
                return await _handle_create_text_customizer(service, arguments)
            elif name == "create_number_customizer":
                return await _handle_create_number_customizer(service, arguments)
            elif name == "create_price_customizer":
                return await _handle_create_price_customizer(service, arguments)
            elif name == "remove_ad_group_customizer":
                return await _handle_remove_ad_group_customizer(service, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_ad_group_customizers(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate ad group customizers request."""
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
            ad_group = op_data["ad_group"]
            customizer_attribute = op_data["customizer_attribute"]
            value_type_str = op_data["value_type"]
            string_value = op_data["string_value"]

            # Convert string to enum
            value_type = getattr(
                CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type_str
            )

            operation = service.create_ad_group_customizer_operation(
                ad_group=ad_group,
                customizer_attribute=customizer_attribute,
                value_type=value_type,
                string_value=string_value,
            )
        elif operation_type == "remove":
            resource_name = op_data["resource_name"]
            operation = service.create_remove_operation(resource_name=resource_name)
        else:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        operations.append(operation)

    response = service.mutate_ad_group_customizers(
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
        if result.ad_group_customizer:
            result_data["ad_group_customizer"] = {
                "resource_name": result.ad_group_customizer.resource_name,
                "ad_group": result.ad_group_customizer.ad_group,
                "customizer_attribute": result.ad_group_customizer.customizer_attribute,
                "status": result.ad_group_customizer.status.name
                if result.ad_group_customizer.status
                else None,
                "value": {
                    "type": result.ad_group_customizer.value.type_.name
                    if result.ad_group_customizer.value.type_
                    else None,
                    "string_value": result.ad_group_customizer.value.string_value,
                }
                if result.ad_group_customizer.value
                else None,
            }
        results.append(result_data)

    response_data = {
        "results": results,
        "partial_failure_error": str(response.partial_failure_error)
        if response.partial_failure_error
        else None,
    }

    return [TextContent(type="text", text=json.dumps(response_data, indent=2))]


async def _handle_create_ad_group_customizer(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create ad group customizer request."""
    customer_id = arguments["customer_id"]
    ad_group = arguments["ad_group"]
    customizer_attribute = arguments["customizer_attribute"]
    value_type_str = arguments["value_type"]
    string_value = arguments["string_value"]
    validate_only = arguments.get("validate_only", False)

    # Convert string to enum
    value_type = getattr(
        CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type_str
    )

    response = service.create_ad_group_customizer(
        customer_id=customer_id,
        ad_group=ad_group,
        customizer_attribute=customizer_attribute,
        value_type=value_type,
        string_value=string_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_customizer",
        "ad_group": ad_group,
        "customizer_attribute": customizer_attribute,
        "value_type": value_type_str,
        "string_value": string_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_text_customizer(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create text customizer request."""
    customer_id = arguments["customer_id"]
    ad_group = arguments["ad_group"]
    customizer_attribute = arguments["customizer_attribute"]
    text_value = arguments["text_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_text_customizer(
        customer_id=customer_id,
        ad_group=ad_group,
        customizer_attribute=customizer_attribute,
        text_value=text_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_text_customizer",
        "ad_group": ad_group,
        "customizer_attribute": customizer_attribute,
        "text_value": text_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_number_customizer(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create number customizer request."""
    customer_id = arguments["customer_id"]
    ad_group = arguments["ad_group"]
    customizer_attribute = arguments["customizer_attribute"]
    number_value = arguments["number_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_number_customizer(
        customer_id=customer_id,
        ad_group=ad_group,
        customizer_attribute=customizer_attribute,
        number_value=number_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_number_customizer",
        "ad_group": ad_group,
        "customizer_attribute": customizer_attribute,
        "number_value": number_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_price_customizer(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create price customizer request."""
    customer_id = arguments["customer_id"]
    ad_group = arguments["ad_group"]
    customizer_attribute = arguments["customizer_attribute"]
    price_value = arguments["price_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_price_customizer(
        customer_id=customer_id,
        ad_group=ad_group,
        customizer_attribute=customizer_attribute,
        price_value=price_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_price_customizer",
        "ad_group": ad_group,
        "customizer_attribute": customizer_attribute,
        "price_value": price_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_remove_ad_group_customizer(
    service: AdGroupCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle remove ad group customizer request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    response = service.remove_ad_group_customizer(
        customer_id=customer_id,
        resource_name=resource_name,
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


def register_ad_group_customizer_server(mcp: FastMCP) -> None:
    """Register Ad Group Customizer service with FastMCP."""
    server = create_ad_group_customizer_server()
    mcp.mount(server, prefix="ad_group_customizer")
