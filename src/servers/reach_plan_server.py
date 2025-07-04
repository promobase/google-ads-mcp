"""Reach plan server using SDK implementation."""

from fastmcp import FastMCP

from src.services.planning.reach_plan_service import (
    register_reach_plan_tools,
)

# Create the reach plan server
reach_plan_server = FastMCP(name="reach-plan-service")

# Register the tools
register_reach_plan_tools(reach_plan_server)
