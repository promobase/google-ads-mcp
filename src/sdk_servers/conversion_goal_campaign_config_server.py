"""MCP Server for Google Ads Conversion Goal Campaign Config Service

This server provides MCP tools for managing conversion goal campaign configurations in Google Ads.
Conversion goal campaign configs define how campaigns use conversion goals for optimization.
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.enums.types.goal_config_level import GoalConfigLevelEnum

from ..sdk_services.conversions.conversion_goal_campaign_config_service import ConversionGoalCampaignConfigService
from ..utils import ensure_client, handle_googleads_exception


def create_conversion_goal_campaign_config_server() -> Server:
    """Create and configure the conversion goal campaign config MCP server."""
    server = Server("conversion-goal-campaign-config-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available conversion goal campaign config tools."""
        return [
            Tool(
                name="mutate_conversion_goal_campaign_configs",
                description="Update conversion goal campaign configurations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID"
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of conversion goal campaign config operations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "resource_name": {
                                        "type": "string",
                                        "description": "The conversion goal campaign config resource name"
                                    },
                                    "goal_config_level": {
                                        "type": "string",
                                        "enum": ["CUSTOMER", "CAMPAIGN"],
                                        "description": "The level of goal config the campaign is using"
                                    },
                                    "custom_conversion_goal": {
                                        "type": "string",
                                        "description": "The custom conversion goal resource name"
                                    }
                                },
                                "required": ["resource_name"]
                            }
                        },

                        "validate_only": {
                            "type": "boolean",
                            "description": "Only validate the request",
                            "default": False
                        }
                    },
                    "required": ["customer_id", "operations"]
                }
            ),
            Tool(
                name="update_conversion_goal_campaign_config",
                description="Update a conversion goal campaign configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer ID"
                        },
                        "resource_name": {
                            "type": "string",
                            "description": "The conversion goal campaign config resource name"
                        },
                        "goal_config_level": {
                            "type": "string",
                            "enum": ["CUSTOMER", "CAMPAIGN"],
                            "description": "The level of goal config the campaign is using"
                        },
                        "custom_conversion_goal": {
                            "type": "string",
                            "description": "The custom conversion goal resource name"
                        }
                    },
                    "required": ["customer_id", "resource_name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for conversion goal campaign config operations."""
        try:
            client = ensure_client()
            service = ConversionGoalCampaignConfigService(client)

            def _get_goal_config_level_enum(level_str: str) -> GoalConfigLevelEnum.GoalConfigLevel:
                """Convert string to goal config level enum."""
                if level_str == "CUSTOMER":
                    return GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER
                elif level_str == "CAMPAIGN":
                    return GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
                else:
                    raise ValueError(f"Invalid goal config level: {level_str}")

            if name == "mutate_conversion_goal_campaign_configs":
                customer_id = arguments["customer_id"]
                operations_data = arguments["operations"]
                validate_only = arguments.get("validate_only", False)

                operations = []
                for op_data in operations_data:
                    goal_config_level = None
                    if "goal_config_level" in op_data:
                        goal_config_level = _get_goal_config_level_enum(op_data["goal_config_level"])
                    
                    operation = service.update_conversion_goal_campaign_config_operation(
                        resource_name=op_data["resource_name"],
                        goal_config_level=goal_config_level,
                        custom_conversion_goal=op_data.get("custom_conversion_goal")
                    )
                    operations.append(operation)

                response = service.mutate_conversion_goal_campaign_configs(
                    customer_id=customer_id,
                    operations=operations,
                    validate_only=validate_only
                )

                return [TextContent(
                    type="text",
                    text=f"Successfully processed {len(response.results)} conversion goal campaign config operations"
                )]

            elif name == "update_conversion_goal_campaign_config":
                customer_id = arguments["customer_id"]
                
                goal_config_level = None
                if "goal_config_level" in arguments:
                    goal_config_level = _get_goal_config_level_enum(arguments["goal_config_level"])
                
                operation = service.update_conversion_goal_campaign_config_operation(
                    resource_name=arguments["resource_name"],
                    goal_config_level=goal_config_level,
                    custom_conversion_goal=arguments.get("custom_conversion_goal")
                )

                response = service.mutate_conversion_goal_campaign_configs(
                    customer_id=customer_id,
                    operations=[operation]
                )

                result = response.results[0]
                return [TextContent(
                    type="text",
                    text=f"Updated conversion goal campaign config: {result.resource_name}"
                )]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server