"""MCP Server for Google Ads Experiment Arm Service

This server provides MCP tools for managing experiment arms (variants) in Google Ads.
Experiment arms allow testing different campaign configurations and comparing performance.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..sdk_services.campaign.experiment_arm_service import ExperimentArmService
from ..utils import ensure_client, handle_googleads_exception


def create_experiment_arm_server() -> Server:
    """Create and configure the experiment arm MCP server."""
    server = Server("experiment-arm-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available experiment arm tools."""
        return [
            Tool(
                name="mutate_experiment_arms",
                description="Create, update, or remove experiment arms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of experiment arm operations",
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
                                    "experiment": {
                                        "type": "string",
                                        "description": "Experiment resource name (required for create)",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the experiment arm",
                                    },
                                    "control": {
                                        "type": "boolean",
                                        "description": "Whether this is a control arm (required for create)",
                                    },
                                    "traffic_split": {
                                        "type": "integer",
                                        "description": "Traffic split percentage (1-100)",
                                    },
                                    "campaigns": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of campaign resource names",
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
                name="create_experiment_arm",
                description="Create a new experiment arm",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "experiment": {
                            "type": "string",
                            "description": "The experiment resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the experiment arm",
                        },
                        "control": {
                            "type": "boolean",
                            "description": "Whether this is a control arm",
                        },
                        "traffic_split": {
                            "type": "integer",
                            "description": "Traffic split percentage (1-100)",
                        },
                        "campaigns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of campaign resource names",
                            "default": [],
                        },
                    },
                    "required": [
                        "customer_id",
                        "experiment",
                        "name",
                        "control",
                        "traffic_split",
                    ],
                },
            ),
            Tool(
                name="update_experiment_arm",
                description="Update an existing experiment arm",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The experiment arm resource name",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the experiment arm",
                        },
                        "traffic_split": {
                            "type": "integer",
                            "description": "Traffic split percentage (1-100)",
                        },
                        "campaigns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of campaign resource names",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
            Tool(
                name="remove_experiment_arm",
                description="Remove an experiment arm",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The experiment arm resource name",
                        },
                    },
                    "required": ["customer_id", "resource_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for experiment arm operations."""
        try:
            client = ensure_client()
            service = ExperimentArmService(client)

            if name == "mutate_experiment_arms":
                customer_id = arguments["customer_id"]
                operations_data = arguments["operations"]
                partial_failure = arguments.get("partial_failure", False)
                validate_only = arguments.get("validate_only", False)

                operations = []
                for op_data in operations_data:
                    op_type = op_data["operation_type"]

                    if op_type == "create":
                        operation = service.create_experiment_arm_operation(
                            experiment=op_data["experiment"],
                            name=op_data["name"],
                            control=op_data["control"],
                            traffic_split=op_data["traffic_split"],
                            campaigns=op_data.get("campaigns", []),
                        )
                    elif op_type == "update":
                        operation = service.update_experiment_arm_operation(
                            resource_name=op_data["resource_name"],
                            name=op_data.get("name"),
                            traffic_split=op_data.get("traffic_split"),
                            campaigns=op_data.get("campaigns"),
                        )
                    elif op_type == "remove":
                        operation = service.remove_experiment_arm_operation(
                            resource_name=op_data["resource_name"]
                        )
                    else:
                        raise ValueError(f"Invalid operation type: {op_type}")

                    operations.append(operation)

                response = service.mutate_experiment_arms(
                    customer_id=customer_id,
                    operations=operations,
                    partial_failure=partial_failure,
                    validate_only=validate_only,
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Successfully processed {len(response.results)} experiment arm operations",
                    )
                ]

            elif name == "create_experiment_arm":
                customer_id = arguments["customer_id"]
                operation = service.create_experiment_arm_operation(
                    experiment=arguments["experiment"],
                    name=arguments["name"],
                    control=arguments["control"],
                    traffic_split=arguments["traffic_split"],
                    campaigns=arguments.get("campaigns", []),
                )

                response = service.mutate_experiment_arms(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Created experiment arm: {result.resource_name}",
                    )
                ]

            elif name == "update_experiment_arm":
                customer_id = arguments["customer_id"]
                operation = service.update_experiment_arm_operation(
                    resource_name=arguments["resource_name"],
                    name=arguments.get("name"),
                    traffic_split=arguments.get("traffic_split"),
                    campaigns=arguments.get("campaigns"),
                )

                response = service.mutate_experiment_arms(
                    customer_id=customer_id, operations=[operation]
                )

                result = response.results[0]
                return [
                    TextContent(
                        type="text",
                        text=f"Updated experiment arm: {result.resource_name}",
                    )
                ]

            elif name == "remove_experiment_arm":
                customer_id = arguments["customer_id"]
                operation = service.remove_experiment_arm_operation(
                    resource_name=arguments["resource_name"]
                )

                response = service.mutate_experiment_arms(
                    customer_id=customer_id, operations=[operation]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Removed experiment arm: {arguments['resource_name']}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server
