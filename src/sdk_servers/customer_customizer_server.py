"""MCP Server for Google Ads Customer Customizer Service.

This server provides MCP tools for managing customizer values at the customer level.
"""

import json
from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.customer_customizer_service import (
    CustomerCustomizerServiceClient,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)

from ..sdk_services.account.customer_customizer_service import CustomerCustomizerService
from ..core.client_manager import get_client


def create_customer_customizer_server() -> Server:
    """Create and configure the Customer Customizer MCP server."""
    server = Server("customer-customizer-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Customer Customizer tools."""
        return [
            Tool(
                name="mutate_customer_customizers",
                description="Create or remove customer customizers",
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
                name="create_customer_customizer",
                description="Create a customer customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
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
                        "customizer_attribute",
                        "value_type",
                        "string_value",
                    ],
                },
            ),
            Tool(
                name="create_text_customizer",
                description="Create a text customer customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
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
                    "required": ["customer_id", "customizer_attribute", "text_value"],
                },
            ),
            Tool(
                name="create_number_customizer",
                description="Create a number customer customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
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
                    "required": ["customer_id", "customizer_attribute", "number_value"],
                },
            ),
            Tool(
                name="create_price_customizer",
                description="Create a price customer customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
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
                    "required": ["customer_id", "customizer_attribute", "price_value"],
                },
            ),
            Tool(
                name="remove_customer_customizer",
                description="Remove a customer customizer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The customer customizer resource name to remove",
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
        """Handle tool calls for Customer Customizer operations."""
        try:
            client = get_client(CustomerCustomizerServiceClient)
            service = CustomerCustomizerService(client)

            if name == "mutate_customer_customizers":
                return await _handle_mutate_customer_customizers(service, arguments)
            elif name == "create_customer_customizer":
                return await _handle_create_customer_customizer(service, arguments)
            elif name == "create_text_customizer":
                return await _handle_create_text_customizer(service, arguments)
            elif name == "create_number_customizer":
                return await _handle_create_number_customizer(service, arguments)
            elif name == "create_price_customizer":
                return await _handle_create_price_customizer(service, arguments)
            elif name == "remove_customer_customizer":
                return await _handle_remove_customer_customizer(service, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_customer_customizers(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate customer customizers request."""
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
            customizer_attribute = op_data["customizer_attribute"]
            value_type_str = op_data["value_type"]
            string_value = op_data["string_value"]

            # Convert string to enum
            value_type = getattr(
                CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type_str
            )

            operation = service.create_customer_customizer_operation(
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

    response = service.mutate_customer_customizers(
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
        if result.customer_customizer:
            result_data["customer_customizer"] = {
                "resource_name": result.customer_customizer.resource_name,
                "customizer_attribute": result.customer_customizer.customizer_attribute,
                "status": result.customer_customizer.status.name
                if result.customer_customizer.status
                else None,
                "value": {
                    "type": result.customer_customizer.value.type_.name
                    if result.customer_customizer.value.type_
                    else None,
                    "string_value": result.customer_customizer.value.string_value,
                }
                if result.customer_customizer.value
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


async def _handle_create_customer_customizer(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create customer customizer request."""
    customer_id = arguments["customer_id"]
    customizer_attribute = arguments["customizer_attribute"]
    value_type_str = arguments["value_type"]
    string_value = arguments["string_value"]
    validate_only = arguments.get("validate_only", False)

    # Convert string to enum
    value_type = getattr(
        CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type_str
    )

    response = service.create_customer_customizer(
        customer_id=customer_id,
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
        "customizer_attribute": customizer_attribute,
        "value_type": value_type_str,
        "string_value": string_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_text_customizer(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create text customizer request."""
    customer_id = arguments["customer_id"]
    customizer_attribute = arguments["customizer_attribute"]
    text_value = arguments["text_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_text_customizer(
        customer_id=customer_id,
        customizer_attribute=customizer_attribute,
        text_value=text_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_text_customizer",
        "customizer_attribute": customizer_attribute,
        "text_value": text_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_number_customizer(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create number customizer request."""
    customer_id = arguments["customer_id"]
    customizer_attribute = arguments["customizer_attribute"]
    number_value = arguments["number_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_number_customizer(
        customer_id=customer_id,
        customizer_attribute=customizer_attribute,
        number_value=number_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_number_customizer",
        "customizer_attribute": customizer_attribute,
        "number_value": number_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_create_price_customizer(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create price customizer request."""
    customer_id = arguments["customer_id"]
    customizer_attribute = arguments["customizer_attribute"]
    price_value = arguments["price_value"]
    validate_only = arguments.get("validate_only", False)

    response = service.create_price_customizer(
        customer_id=customer_id,
        customizer_attribute=customizer_attribute,
        price_value=price_value,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create_price_customizer",
        "customizer_attribute": customizer_attribute,
        "price_value": price_value,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_remove_customer_customizer(
    service: CustomerCustomizerService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle remove customer customizer request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    response = service.remove_customer_customizer(
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


def register_customer_customizer_server(mcp: FastMCP) -> None:
    """Register Customer Customizer service with FastMCP."""
    server = create_customer_customizer_server()
    mcp.mount(server, prefix="customer_customizer")
