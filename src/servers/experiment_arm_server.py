"""Experiment arm server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.campaign.experiment_arm_service import (
    register_experiment_arm_tools,
)

# Create the FastMCP server instance
experiment_arm_server = FastMCP[Any](name="experiment_arm_sdk_server")

# Register the tools with the server instance
register_experiment_arm_tools(experiment_arm_server)
