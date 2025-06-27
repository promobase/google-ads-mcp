"""MCP Server for Google Ads Customer Asset Service.

This server provides MCP tools for managing customer-level asset associations.
"""

import json
from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.customer_asset_service import (
    CustomerAssetServiceClient,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_field_type import (
    AssetFieldTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_link_status import (
    AssetLinkStatusEnum,
)

from ..sdk_services.assets.customer_asset_service import CustomerAssetService
from ..core.client_manager import get_client


def create_customer_asset_server() -> Server:
    """Create and configure the Customer Asset MCP server."""
    server = Server("customer-asset-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Customer Asset tools."""
        return [
            Tool(
                name="mutate_customer_assets",
                description="Create, update, or remove customer assets",
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
                                        "enum": ["create", "update", "remove"],
                                        "description": "Type of operation",
                                    },
                                    "asset": {
                                        "type": "string",
                                        "description": "Asset resource name (for create operations)",
                                    },
                                    "field_type": {
                                        "type": "string",
                                        "description": "Asset field type (for create operations)",
                                    },
                                    "status": {
                                        "type": "string",
                                        "enum": ["ENABLED", "PAUSED", "REMOVED"],
                                        "description": "Asset link status",
                                    },
                                    "resource_name": {
                                        "type": "string",
                                        "description": "Resource name (for update/remove operations)",
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
                name="create_customer_asset",
                description="Create a customer asset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "asset": {
                            "type": "string",
                            "description": "The asset resource name",
                        },
                        "field_type": {
                            "type": "string",
                            "description": "The asset field type (e.g., LOGO, HEADLINE, etc.)",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ENABLED", "PAUSED", "REMOVED"],
                            "description": "The asset link status",
                            "default": "ENABLED",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "asset", "field_type"],
                },
            ),
            Tool(
                name="update_customer_asset_status",
                description="Update the status of a customer asset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The customer asset resource name",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ENABLED", "PAUSED", "REMOVED"],
                            "description": "The new status",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "resource_name", "status"],
                },
            ),
            Tool(
                name="remove_customer_asset",
                description="Remove a customer asset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The customer asset resource name to remove",
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
        """Handle tool calls for Customer Asset operations."""
        try:
            client = get_client(CustomerAssetServiceClient)
            service = CustomerAssetService(client)

            if name == "mutate_customer_assets":
                return await _handle_mutate_customer_assets(service, arguments)
            elif name == "create_customer_asset":
                return await _handle_create_customer_asset(service, arguments)
            elif name == "update_customer_asset_status":
                return await _handle_update_customer_asset_status(service, arguments)
            elif name == "remove_customer_asset":
                return await _handle_remove_customer_asset(service, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_customer_assets(
    service: CustomerAssetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate customer assets request."""
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
            asset = op_data["asset"]
            field_type_str = op_data["field_type"]
            status_str = op_data.get("status", "ENABLED")

            # Convert strings to enums
            field_type = getattr(AssetFieldTypeEnum.AssetFieldType, field_type_str)
            status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status_str)

            operation = service.create_customer_asset_operation(
                asset=asset,
                field_type=field_type,
                status=status,
            )

        elif operation_type == "update":
            resource_name = op_data["resource_name"]
            status_str = op_data.get("status")

            status = None
            if status_str:
                status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status_str)

            operation = service.create_update_operation(
                resource_name=resource_name,
                status=status,
            )

        elif operation_type == "remove":
            resource_name = op_data["resource_name"]
            operation = service.create_remove_operation(resource_name=resource_name)
        else:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        operations.append(operation)

    response = service.mutate_customer_assets(
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
        if result.customer_asset:
            result_data["customer_asset"] = {
                "resource_name": result.customer_asset.resource_name,
                "asset": result.customer_asset.asset,
                "field_type": result.customer_asset.field_type.name
                if result.customer_asset.field_type
                else None,
                "status": result.customer_asset.status.name
                if result.customer_asset.status
                else None,
                "source": result.customer_asset.source.name
                if result.customer_asset.source
                else None,
                "primary_status": result.customer_asset.primary_status.name
                if result.customer_asset.primary_status
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


async def _handle_create_customer_asset(
    service: CustomerAssetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle create customer asset request."""
    customer_id = arguments["customer_id"]
    asset = arguments["asset"]
    field_type_str = arguments["field_type"]
    status_str = arguments.get("status", "ENABLED")
    validate_only = arguments.get("validate_only", False)

    # Convert strings to enums
    field_type = getattr(AssetFieldTypeEnum.AssetFieldType, field_type_str)
    status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status_str)

    response = service.create_customer_asset(
        customer_id=customer_id,
        asset=asset,
        field_type=field_type,
        status=status,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "create",
        "asset": asset,
        "field_type": field_type_str,
        "status": status_str,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_update_customer_asset_status(
    service: CustomerAssetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle update customer asset status request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    status_str = arguments["status"]
    validate_only = arguments.get("validate_only", False)

    # Convert string to enum
    status = getattr(AssetLinkStatusEnum.AssetLinkStatus, status_str)

    response = service.update_customer_asset_status(
        customer_id=customer_id,
        resource_name=resource_name,
        status=status,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "update_status",
        "new_status": status_str,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_remove_customer_asset(
    service: CustomerAssetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle remove customer asset request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    response = service.remove_customer_asset(
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


def register_customer_asset_server(mcp: FastMCP) -> None:
    """Register Customer Asset service with FastMCP."""
    server = create_customer_asset_server()
    mcp.mount(server, prefix="customer_asset")
