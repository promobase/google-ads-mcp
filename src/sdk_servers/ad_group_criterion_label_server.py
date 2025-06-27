"""MCP Server for Google Ads Ad Group Criterion Label Service.

This server provides MCP tools for managing label assignments to ad group criteria.
"""

import json
from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.ad_group_criterion_label_service import (
    AdGroupCriterionLabelServiceClient,
)

from ..sdk_services.ad_group.ad_group_criterion_label_service import (
    AdGroupCriterionLabelService,
)
from ..core.client_manager import get_client


def create_ad_group_criterion_label_server() -> Server:
    """Create and configure the Ad Group Criterion Label MCP server."""
    server = Server("ad-group-criterion-label-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Ad Group Criterion Label tools."""
        return [
            Tool(
                name="mutate_ad_group_criterion_labels",
                description="Create or remove ad group criterion label assignments",
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
                                    "ad_group_criterion": {
                                        "type": "string",
                                        "description": "Ad group criterion resource name (for create operations)",
                                    },
                                    "label": {
                                        "type": "string",
                                        "description": "Label resource name (for create operations)",
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
                    },
                    "required": ["customer_id", "operations"],
                },
            ),
            Tool(
                name="assign_label_to_criterion",
                description="Assign a label to an ad group criterion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group_criterion": {
                            "type": "string",
                            "description": "The ad group criterion resource name",
                        },
                        "label": {
                            "type": "string",
                            "description": "The label resource name",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "ad_group_criterion", "label"],
                },
            ),
            Tool(
                name="remove_label_from_criterion",
                description="Remove a label assignment from an ad group criterion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The ad group criterion label resource name to remove",
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
            Tool(
                name="assign_multiple_labels_to_criterion",
                description="Assign multiple labels to an ad group criterion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group_criterion": {
                            "type": "string",
                            "description": "The ad group criterion resource name",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of label resource names",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "ad_group_criterion", "labels"],
                },
            ),
            Tool(
                name="assign_label_to_multiple_criteria",
                description="Assign a label to multiple ad group criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "ad_group_criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ad group criterion resource names",
                        },
                        "label": {
                            "type": "string",
                            "description": "The label resource name",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "ad_group_criteria", "label"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for Ad Group Criterion Label operations."""
        try:
            client = get_client(AdGroupCriterionLabelServiceClient)
            service = AdGroupCriterionLabelService(client)

            if name == "mutate_ad_group_criterion_labels":
                return await _handle_mutate_ad_group_criterion_labels(
                    service, arguments
                )
            elif name == "assign_label_to_criterion":
                return await _handle_assign_label_to_criterion(service, arguments)
            elif name == "remove_label_from_criterion":
                return await _handle_remove_label_from_criterion(service, arguments)
            elif name == "assign_multiple_labels_to_criterion":
                return await _handle_assign_multiple_labels_to_criterion(
                    service, arguments
                )
            elif name == "assign_label_to_multiple_criteria":
                return await _handle_assign_label_to_multiple_criteria(
                    service, arguments
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_ad_group_criterion_labels(
    service: AdGroupCriterionLabelService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate ad group criterion labels request."""
    customer_id = arguments["customer_id"]
    operations_data = arguments["operations"]
    partial_failure = arguments.get("partial_failure", False)
    validate_only = arguments.get("validate_only", False)

    operations = []
    for op_data in operations_data:
        operation_type = op_data["operation_type"]

        if operation_type == "create":
            ad_group_criterion = op_data["ad_group_criterion"]
            label = op_data["label"]
            operation = service.create_ad_group_criterion_label_operation(
                ad_group_criterion=ad_group_criterion,
                label=label,
            )
        elif operation_type == "remove":
            resource_name = op_data["resource_name"]
            operation = service.create_remove_operation(resource_name=resource_name)
        else:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        operations.append(operation)

    response = service.mutate_ad_group_criterion_labels(
        customer_id=customer_id,
        operations=operations,
        partial_failure=partial_failure,
        validate_only=validate_only,
    )

    # Format response
    results = []
    for result in response.results:
        result_data = {
            "resource_name": result.resource_name,
        }
        results.append(result_data)

    response_data = {
        "results": results,
        "partial_failure_error": str(response.partial_failure_error)
        if response.partial_failure_error
        else None,
    }

    return [TextContent(type="text", text=json.dumps(response_data, indent=2))]


async def _handle_assign_label_to_criterion(
    service: AdGroupCriterionLabelService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle assign label to criterion request."""
    customer_id = arguments["customer_id"]
    ad_group_criterion = arguments["ad_group_criterion"]
    label = arguments["label"]
    validate_only = arguments.get("validate_only", False)

    response = service.assign_label_to_criterion(
        customer_id=customer_id,
        ad_group_criterion=ad_group_criterion,
        label=label,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "assign_label",
        "ad_group_criterion": ad_group_criterion,
        "label": label,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_remove_label_from_criterion(
    service: AdGroupCriterionLabelService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle remove label from criterion request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    response = service.remove_label_from_criterion(
        customer_id=customer_id,
        resource_name=resource_name,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "remove_label",
        "removed_resource_name": resource_name,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_assign_multiple_labels_to_criterion(
    service: AdGroupCriterionLabelService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle assign multiple labels to criterion request."""
    customer_id = arguments["customer_id"]
    ad_group_criterion = arguments["ad_group_criterion"]
    labels = arguments["labels"]
    validate_only = arguments.get("validate_only", False)

    response = service.assign_multiple_labels_to_criterion(
        customer_id=customer_id,
        ad_group_criterion=ad_group_criterion,
        labels=labels,
        validate_only=validate_only,
    )

    result_data = {
        "operation": "assign_multiple_labels",
        "ad_group_criterion": ad_group_criterion,
        "labels": labels,
        "results": [result.resource_name for result in response.results],
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_assign_label_to_multiple_criteria(
    service: AdGroupCriterionLabelService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle assign label to multiple criteria request."""
    customer_id = arguments["customer_id"]
    ad_group_criteria = arguments["ad_group_criteria"]
    label = arguments["label"]
    validate_only = arguments.get("validate_only", False)

    response = service.assign_label_to_multiple_criteria(
        customer_id=customer_id,
        ad_group_criteria=ad_group_criteria,
        label=label,
        validate_only=validate_only,
    )

    result_data = {
        "operation": "assign_label_to_multiple",
        "ad_group_criteria": ad_group_criteria,
        "label": label,
        "results": [result.resource_name for result in response.results],
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


def register_ad_group_criterion_label_server(mcp: FastMCP) -> None:
    """Register Ad Group Criterion Label service with FastMCP."""
    server = create_ad_group_criterion_label_server()
    mcp.mount(server, prefix="ad_group_criterion_label")
