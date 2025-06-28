"""Experiment server using SDK implementation."""

from fastmcp import FastMCP

from src.services.campaign.experiment_service import register_experiment_tools

# Create the experiment server
experiment_server = FastMCP(
    name="experiment",
    instructions="""This server provides tools for A/B testing campaigns with experiments.

    Available tools:
    - create_experiment: Create a new experiment for A/B testing
    - schedule_experiment: Start running an experiment
    - end_experiment: Stop a running experiment
    - promote_experiment: Apply experiment changes to base campaign
    - list_experiments: List all experiments in the account

    Experiments allow you to:
    - Test changes to campaigns before applying them
    - Split traffic between control and experiment
    - Measure performance differences
    - Promote successful changes

    Experiment lifecycle:
    1. SETUP: Create and configure experiment
    2. INITIATED: Schedule to start
    3. RUNNING: Active and collecting data
    4. GRADUATED/HALTED: Experiment ended
    5. PROMOTED: Changes applied to base campaign

    All tools use the Google Ads Python SDK for type-safe API communication.""",
)

# Register the tools and store the service instance
experiment_service = register_experiment_tools(experiment_server)
