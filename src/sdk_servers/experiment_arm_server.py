"""Experiment arm server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.experiment_arm_service import (
    register_experiment_arm_tools,
)


def register_experiment_arm_server(mcp: FastMCP[Any]) -> None:
    """Register experiment arm server tools with the MCP server."""
    register_experiment_arm_tools(mcp)
