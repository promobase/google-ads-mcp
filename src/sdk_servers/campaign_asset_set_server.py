"""MCP Server for Google Ads Campaign Asset Set Service.

This server provides MCP tools for managing asset set associations with campaigns.
"""

import json
from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.services.services.campaign_asset_set_service import (
    CampaignAssetSetServiceClient,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)

from ..sdk_services.campaign.campaign_asset_set_service import CampaignAssetSetService
from ..core.client_manager import get_client


def create_campaign_asset_set_server() -> Server:
    """Create and configure the Campaign Asset Set MCP server."""
    server = Server("campaign-asset-set-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available Campaign Asset Set tools."""
        return [
            Tool(
                name="mutate_campaign_asset_sets",
                description="Create or remove campaign asset set associations",
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
                                    "campaign": {
                                        "type": "string",
                                        "description": "Campaign resource name (for create operations)",
                                    },
                                    "asset_set": {
                                        "type": "string",
                                        "description": "Asset set resource name (for create operations)",
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
                name="link_asset_set_to_campaign",
                description="Link an asset set to a campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "campaign": {
                            "type": "string",
                            "description": "The campaign resource name",
                        },
                        "asset_set": {
                            "type": "string",
                            "description": "The asset set resource name",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "campaign", "asset_set"],
                },
            ),
            Tool(
                name="unlink_asset_set_from_campaign",
                description="Unlink an asset set from a campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The campaign asset set resource name to remove",
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
                name="link_multiple_asset_sets_to_campaign",
                description="Link multiple asset sets to a campaign",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "campaign": {
                            "type": "string",
                            "description": "The campaign resource name",
                        },
                        "asset_sets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of asset set resource names",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "campaign", "asset_sets"],
                },
            ),
            Tool(
                name="link_asset_set_to_multiple_campaigns",
                description="Link an asset set to multiple campaigns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID",
                        },
                        "campaigns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of campaign resource names",
                        },
                        "asset_set": {
                            "type": "string",
                            "description": "The asset set resource name",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "description": "If true, the request is validated but not executed",
                            "default": False,
                        },
                    },
                    "required": ["customer_id", "campaigns", "asset_set"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for Campaign Asset Set operations."""
        try:
            client = get_client(CampaignAssetSetServiceClient)
            service = CampaignAssetSetService(client)

            if name == "mutate_campaign_asset_sets":
                return await _handle_mutate_campaign_asset_sets(service, arguments)
            elif name == "link_asset_set_to_campaign":
                return await _handle_link_asset_set_to_campaign(service, arguments)
            elif name == "unlink_asset_set_from_campaign":
                return await _handle_unlink_asset_set_from_campaign(service, arguments)
            elif name == "link_multiple_asset_sets_to_campaign":
                return await _handle_link_multiple_asset_sets_to_campaign(
                    service, arguments
                )
            elif name == "link_asset_set_to_multiple_campaigns":
                return await _handle_link_asset_set_to_multiple_campaigns(
                    service, arguments
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _handle_mutate_campaign_asset_sets(
    service: CampaignAssetSetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle mutate campaign asset sets request."""
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
            campaign = op_data["campaign"]
            asset_set = op_data["asset_set"]
            operation = service.create_campaign_asset_set_operation(
                campaign=campaign,
                asset_set=asset_set,
            )
        elif operation_type == "remove":
            resource_name = op_data["resource_name"]
            operation = service.create_remove_operation(resource_name=resource_name)
        else:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        operations.append(operation)

    response = service.mutate_campaign_asset_sets(
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
        if result.campaign_asset_set:
            result_data["campaign_asset_set"] = {
                "resource_name": result.campaign_asset_set.resource_name,
                "campaign": result.campaign_asset_set.campaign,
                "asset_set": result.campaign_asset_set.asset_set,
                "status": result.campaign_asset_set.status.name
                if result.campaign_asset_set.status
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


async def _handle_link_asset_set_to_campaign(
    service: CampaignAssetSetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle link asset set to campaign request."""
    customer_id = arguments["customer_id"]
    campaign = arguments["campaign"]
    asset_set = arguments["asset_set"]
    validate_only = arguments.get("validate_only", False)

    response = service.link_asset_set_to_campaign(
        customer_id=customer_id,
        campaign=campaign,
        asset_set=asset_set,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "link_asset_set",
        "campaign": campaign,
        "asset_set": asset_set,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_unlink_asset_set_from_campaign(
    service: CampaignAssetSetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle unlink asset set from campaign request."""
    customer_id = arguments["customer_id"]
    resource_name = arguments["resource_name"]
    validate_only = arguments.get("validate_only", False)

    response = service.unlink_asset_set_from_campaign(
        customer_id=customer_id,
        resource_name=resource_name,
        validate_only=validate_only,
    )

    result_data = {
        "resource_name": response.results[0].resource_name
        if response.results
        else None,
        "operation": "unlink_asset_set",
        "removed_resource_name": resource_name,
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_link_multiple_asset_sets_to_campaign(
    service: CampaignAssetSetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle link multiple asset sets to campaign request."""
    customer_id = arguments["customer_id"]
    campaign = arguments["campaign"]
    asset_sets = arguments["asset_sets"]
    validate_only = arguments.get("validate_only", False)

    response = service.link_multiple_asset_sets_to_campaign(
        customer_id=customer_id,
        campaign=campaign,
        asset_sets=asset_sets,
        validate_only=validate_only,
    )

    result_data = {
        "operation": "link_multiple_asset_sets",
        "campaign": campaign,
        "asset_sets": asset_sets,
        "results": [result.resource_name for result in response.results],
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


async def _handle_link_asset_set_to_multiple_campaigns(
    service: CampaignAssetSetService, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle link asset set to multiple campaigns request."""
    customer_id = arguments["customer_id"]
    campaigns = arguments["campaigns"]
    asset_set = arguments["asset_set"]
    validate_only = arguments.get("validate_only", False)

    response = service.link_asset_set_to_multiple_campaigns(
        customer_id=customer_id,
        campaigns=campaigns,
        asset_set=asset_set,
        validate_only=validate_only,
    )

    result_data = {
        "operation": "link_asset_set_to_multiple",
        "campaigns": campaigns,
        "asset_set": asset_set,
        "results": [result.resource_name for result in response.results],
    }

    return [TextContent(type="text", text=json.dumps(result_data, indent=2))]


def register_campaign_asset_set_server(mcp: FastMCP) -> None:
    """Register Campaign Asset Set service with FastMCP."""
    server = create_campaign_asset_set_server()
    mcp.mount(server, prefix="campaign_asset_set")
