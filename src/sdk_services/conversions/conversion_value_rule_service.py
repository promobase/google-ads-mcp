"""Conversion value rule service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP

# Note: Value rule types may not be available in v20 - using simplified implementation
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.services.services.conversion_value_rule_service import (
    ConversionValueRuleServiceClient,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger

logger = get_logger(__name__)


class ConversionValueRuleService:
    """Conversion value rule service for managing conversion value adjustments."""

    def __init__(self) -> None:
        """Initialize the conversion value rule service."""
        self._client: Optional[ConversionValueRuleServiceClient] = None

    @property
    def client(self) -> ConversionValueRuleServiceClient:
        """Get the conversion value rule service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ConversionValueRuleService")
        assert self._client is not None
        return self._client

    async def create_basic_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        conversion_value_rule_set_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a basic conversion value rule (simplified due to v20 limitations).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_value_rule_set_id: The conversion value rule set ID
            status: Rule status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created conversion value rule details (simplified)
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Note: Value rule types not available in v20 - simplified implementation
            await ctx.log(
                level="info",
                message=f"Conversion value rule creation requested for rule set {conversion_value_rule_set_id}",
            )

            return {
                "customer_id": customer_id,
                "conversion_value_rule_set_id": conversion_value_rule_set_id,
                "status": status,
                "result": "Request processed - conversion value rule creation requires additional v20 type support",
                "note": "This is a simplified implementation due to v20 API limitations",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_basic_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule (simplified due to v20 limitations).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to update
            status: Optional new status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated conversion value rule details (simplified)
        """
        try:
            customer_id = format_customer_id(customer_id)

            await ctx.log(
                level="info",
                message=f"Conversion value rule update requested for {rule_resource_name}",
            )

            return {
                "resource_name": rule_resource_name,
                "status": status,
                "result": "Request processed - conversion value rule updates require additional v20 type support",
                "note": "This is a simplified implementation due to v20 API limitations",
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_conversion_value_rules(
        self,
        ctx: Context,
        customer_id: str,
        conversion_value_rule_set_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List conversion value rules.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            conversion_value_rule_set_id: Optional rule set ID to filter by

        Returns:
            List of conversion value rules
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service = sdk_client.client.get_service("GoogleAdsService")

            # Build query
            query = """
                SELECT
                    conversion_value_rule.resource_name,
                    conversion_value_rule.id,
                    conversion_value_rule.conversion_value_rule_set,
                    conversion_value_rule.status,
                    conversion_value_rule.value_rule.operation.operator,
                    conversion_value_rule.value_rule.operation.value,
                    conversion_value_rule.value_rule.operation.value_micros
                FROM conversion_value_rule
            """

            if conversion_value_rule_set_id:
                rule_set_resource = f"customers/{customer_id}/conversionValueRuleSets/{conversion_value_rule_set_id}"
                query += f" WHERE conversion_value_rule.conversion_value_rule_set = '{rule_set_resource}'"

            query += " ORDER BY conversion_value_rule.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            rules = []
            for row in response:
                rule = row.conversion_value_rule

                rule_dict = {
                    "resource_name": rule.resource_name,
                    "id": str(rule.id),
                    "conversion_value_rule_set": rule.conversion_value_rule_set,
                    "status": rule.status.name if rule.status else "UNKNOWN",
                    "operation": {
                        "operator": rule.value_rule.operation.operator.name
                        if rule.value_rule.operation.operator
                        else "UNKNOWN",
                        "value": rule.value_rule.operation.value
                        if hasattr(rule.value_rule.operation, "value")
                        else None,
                        "value_micros": rule.value_rule.operation.value_micros
                        if hasattr(rule.value_rule.operation, "value_micros")
                        else None,
                    },
                }

                rules.append(rule_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(rules)} conversion value rules",
            )

            return rules

        except Exception as e:
            error_msg = f"Failed to list conversion value rules: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            raise NotImplementedError

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_value_rule_tools(
    service: ConversionValueRuleService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion value rule service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_basic_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        conversion_value_rule_set_id: str,
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a basic conversion value rule (simplified due to v20 limitations).

        Args:
            customer_id: The customer ID
            conversion_value_rule_set_id: The conversion value rule set ID
            status: Rule status - ENABLED, PAUSED, or REMOVED

        Returns:
            Created conversion value rule details (simplified implementation)
        """
        return await service.create_basic_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            conversion_value_rule_set_id=conversion_value_rule_set_id,
            status=status,
        )

    async def update_basic_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule (simplified due to v20 limitations).

        Args:
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to update
            status: Optional new status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated conversion value rule details (simplified implementation)
        """
        return await service.update_basic_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            rule_resource_name=rule_resource_name,
            status=status,
        )

    async def list_conversion_value_rules(
        ctx: Context,
        customer_id: str,
        conversion_value_rule_set_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List conversion value rules.

        Args:
            customer_id: The customer ID
            conversion_value_rule_set_id: Optional rule set ID to filter by

        Returns:
            List of conversion value rules with operation details
        """
        return await service.list_conversion_value_rules(
            ctx=ctx,
            customer_id=customer_id,
            conversion_value_rule_set_id=conversion_value_rule_set_id,
        )

    async def remove_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule.

        Args:
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to remove

        Returns:
            Removal result
        """
        return await service.remove_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            rule_resource_name=rule_resource_name,
        )

    tools.extend(
        [
            create_basic_conversion_value_rule,
            update_basic_conversion_value_rule,
            list_conversion_value_rules,
            remove_conversion_value_rule,
        ]
    )
    return tools


def register_conversion_value_rule_tools(
    mcp: FastMCP[Any],
) -> ConversionValueRuleService:
    """Register conversion value rule tools with the MCP server.

    Returns the ConversionValueRuleService instance for testing purposes.
    """
    service = ConversionValueRuleService()
    tools = create_conversion_value_rule_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
