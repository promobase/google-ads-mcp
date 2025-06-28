"""Server wrapper for conversion value rule service."""

from fastmcp import FastMCP

from src.services.conversions.conversion_value_rule_service import (
    register_conversion_value_rule_tools,
)

# Create the FastMCP instance
conversion_value_rule_server = FastMCP(name="conversion-value-rule-service")

# Register the tools with the server instance
register_conversion_value_rule_tools(conversion_value_rule_server)
