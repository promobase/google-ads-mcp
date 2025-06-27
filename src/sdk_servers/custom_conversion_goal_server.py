"""MCP Server for Google Ads Custom Conversion Goal Service

This server provides MCP tools for managing custom conversion goals in Google Ads.
Custom conversion goals allow making arbitrary conversion actions biddable.
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from google.ads.googleads.v20.enums.types.custom_conversion_goal_status import CustomConversionGoalStatusEnum

from ..sdk_services.conversions.custom_conversion_goal_service import CustomConversionGoalService
from ..utils import ensure_client, handle_googleads_exception


def create_custom_conversion_goal_server() -> Server:
    """Create and configure the custom conversion goal MCP server."""
    server = Server("custom-conversion-goal-service")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available custom conversion goal tools."""
        return [
            Tool(
                name="create_custom_conversion_goal",
                description="Create a new custom conversion goal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer ID"},
                        "name": {"type": "string", "description": "The name for this custom conversion goal"},
                        "conversion_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of conversion action resource names"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ENABLED", "REMOVED"],
                            "description": "The status of the custom conversion goal",
                            "default": "ENABLED"
                        }
                    },
                    "required": ["customer_id", "name", "conversion_actions"]
                }
            ),
            Tool(
                name="update_custom_conversion_goal",
                description="Update an existing custom conversion goal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer ID"},
                        "resource_name": {"type": "string", "description": "The custom conversion goal resource name"},
                        "name": {"type": "string", "description": "The name for this custom conversion goal"},
                        "conversion_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of conversion action resource names"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ENABLED", "REMOVED"],
                            "description": "The status of the custom conversion goal"
                        }
                    },
                    "required": ["customer_id", "resource_name"]
                }
            ),
            Tool(
                name="remove_custom_conversion_goal",
                description="Remove a custom conversion goal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer ID"},
                        "resource_name": {"type": "string", "description": "The custom conversion goal resource name"}
                    },
                    "required": ["customer_id", "resource_name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls for custom conversion goal operations."""
        try:
            client = ensure_client()
            service = CustomConversionGoalService(client)

            def _get_status_enum(status_str: str) -> CustomConversionGoalStatusEnum.CustomConversionGoalStatus:
                """Convert string to status enum."""
                if status_str == "ENABLED":
                    return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
                elif status_str == "REMOVED":
                    return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.REMOVED
                else:
                    raise ValueError(f"Invalid status: {status_str}")

            if name == "create_custom_conversion_goal":
                customer_id = arguments["customer_id"]
                status = _get_status_enum(arguments.get("status", "ENABLED"))
                
                operation = service.create_custom_conversion_goal_operation(
                    name=arguments["name"],
                    conversion_actions=arguments["conversion_actions"],
                    status=status
                )

                response = service.mutate_custom_conversion_goals(
                    customer_id=customer_id,
                    operations=[operation]
                )

                result = response.results[0]
                return [TextContent(
                    type="text",
                    text=f"Created custom conversion goal: {result.resource_name}"
                )]

            elif name == "update_custom_conversion_goal":
                customer_id = arguments["customer_id"]
                
                status = None
                if "status" in arguments:
                    status = _get_status_enum(arguments["status"])
                
                operation = service.update_custom_conversion_goal_operation(
                    resource_name=arguments["resource_name"],
                    name=arguments.get("name"),
                    conversion_actions=arguments.get("conversion_actions"),
                    status=status
                )

                response = service.mutate_custom_conversion_goals(
                    customer_id=customer_id,
                    operations=[operation]
                )

                result = response.results[0]
                return [TextContent(
                    type="text",
                    text=f"Updated custom conversion goal: {result.resource_name}"
                )]

            elif name == "remove_custom_conversion_goal":
                customer_id = arguments["customer_id"]
                operation = service.remove_custom_conversion_goal_operation(
                    resource_name=arguments["resource_name"]
                )

                response = service.mutate_custom_conversion_goals(
                    customer_id=customer_id,
                    operations=[operation]
                )

                return [TextContent(
                    type="text",
                    text=f"Removed custom conversion goal: {arguments['resource_name']}"
                )]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = handle_googleads_exception(e)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    return server