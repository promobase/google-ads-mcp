"""Main entry point for Google Ads MCP server."""

import argparse
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from types import FrameType
from typing import Any, AsyncGenerator, Optional, Set

from fastmcp import Context, FastMCP

from src.sdk_client import GoogleAdsSdkClient, get_sdk_client, set_sdk_client
from src.servers.account_budget_proposal_server import (
    account_budget_proposal_server,
)
from src.servers.account_link_server import account_link_server
from src.servers.ad_group_ad_label_server import ad_group_ad_label_server
from src.servers.ad_group_ad_server import ad_group_ad_server
from src.servers.ad_group_asset_server import ad_group_asset_server
from src.servers.ad_group_asset_set_server import ad_group_asset_set_server
from src.servers.ad_group_bid_modifier_server import (
    ad_group_bid_modifier_server,
)
from src.servers.ad_group_criterion_customizer_server import (
    ad_group_criterion_customizer_server,
)
from src.servers.ad_group_criterion_label_server import (
    ad_group_criterion_label_server,
)
from src.servers.ad_group_criterion_server import ad_group_criterion_server
from src.servers.ad_group_customizer_server import (
    ad_group_customizer_server,
)
from src.servers.ad_group_label_server import ad_group_label_server
from src.servers.ad_group_server import ad_group_server
from src.servers.ad_parameter_server import (
    ad_parameter_server,
)
from src.servers.ad_server import ad_server
from src.servers.asset_group_asset_server import asset_group_asset_server
from src.servers.asset_group_server import asset_group_server
from src.servers.asset_group_signal_server import asset_group_signal_server
from src.servers.asset_server import asset_server
from src.servers.asset_set_server import asset_set_server
from src.servers.audience_insights_server import audience_insights_server
from src.servers.audience_server import audience_server
from src.servers.batch_job_server import batch_job_server
from src.servers.bidding_data_exclusion_server import (
    bidding_data_exclusion_server,
)
from src.servers.bidding_seasonality_adjustment_server import (
    bidding_seasonality_adjustment_server,
)
from src.servers.bidding_strategy_server import bidding_strategy_server
from src.servers.billing_setup_server import billing_setup_server
from src.servers.brand_suggestion_server import brand_suggestion_server
from src.servers.budget_server import budget_server
from src.servers.campaign_asset_server import campaign_asset_server
from src.servers.campaign_asset_set_server import campaign_asset_set_server
from src.servers.campaign_bid_modifier_server import (
    campaign_bid_modifier_server,
)
from src.servers.campaign_conversion_goal_server import (
    campaign_conversion_goal_server,
)
from src.servers.campaign_criterion_server import campaign_criterion_server
from src.servers.campaign_customizer_server import (
    campaign_customizer_server,
)
from src.servers.campaign_draft_server import campaign_draft_server
from src.servers.campaign_label_server import campaign_label_server
from src.servers.campaign_server import campaign_server
from src.servers.campaign_shared_set_server import (
    campaign_shared_set_server,
)
from src.servers.conversion_adjustment_upload_server import (
    conversion_adjustment_upload_server,
)
from src.servers.conversion_custom_variable_server import (
    conversion_custom_variable_server,
)
from src.servers.conversion_goal_campaign_config_server import (
    conversion_goal_campaign_config_server,
)
from src.servers.conversion_server import conversion_server
from src.servers.conversion_upload_server import conversion_upload_server
from src.servers.conversion_value_rule_server import (
    conversion_value_rule_server,
)
from src.servers.custom_audience_server import custom_audience_server
from src.servers.custom_conversion_goal_server import (
    custom_conversion_goal_server,
)
from src.servers.custom_interest_server import custom_interest_server
from src.servers.customer_asset_server import customer_asset_server
from src.servers.customer_client_link_server import (
    customer_client_link_server,
)
from src.servers.customer_conversion_goal_server import (
    customer_conversion_goal_server,
)
from src.servers.customer_customizer_server import (
    customer_customizer_server,
)
from src.servers.customer_label_server import customer_label_server
from src.servers.customer_manager_link_server import (
    customer_manager_link_server,
)
from src.servers.customer_negative_criterion_server import (
    customer_negative_criterion_server,
)
from src.servers.customer_server import customer_service_server
from src.servers.customer_user_access_invitation_server import (
    customer_user_access_invitation_server,
)
from src.servers.customer_user_access_server import (
    customer_user_access_server,
)
from src.servers.customizer_attribute_server import (
    customizer_sdk_server,
)
from src.servers.data_link_server import data_link_server
from src.servers.experiment_arm_server import experiment_arm_server
from src.servers.experiment_server import experiment_server
from src.servers.geo_target_constant_server import geo_target_constant_server
from src.servers.google_ads_field_server import google_ads_field_server
from src.servers.google_ads_server import google_ads_server
from src.servers.identity_verification_server import (
    identity_verification_server,
)
from src.servers.invoice_server import invoice_server
from src.servers.keyword_plan_ad_group_keyword_server import (
    keyword_plan_ad_group_keyword_server,
)
from src.servers.keyword_plan_ad_group_server import (
    keyword_plan_ad_group_server,
)
from src.servers.keyword_plan_campaign_keyword_server import (
    keyword_plan_campaign_keyword_server,
)
from src.servers.keyword_plan_campaign_server import (
    keyword_plan_campaign_server,
)
from src.servers.keyword_plan_idea_server import keyword_plan_idea_server
from src.servers.keyword_plan_server import keyword_plan_server
from src.servers.keyword_server import keyword_server
from src.servers.label_server import label_server
from src.servers.offline_user_data_job_server import (
    offline_user_data_job_server,
)
from src.servers.payments_account_server import (
    payments_account_server,
)
from src.servers.product_link_server import product_link_server
from src.servers.reach_plan_server import reach_plan_server
from src.servers.recommendation_server import recommendation_server
from src.servers.remarketing_action_server import remarketing_action_server
from src.servers.search_server import search_server
from src.servers.shared_criterion_server import shared_criterion_server
from src.servers.shared_set_server import shared_set_server
from src.servers.smart_campaign_server import smart_campaign_server

# from src.sdk_servers.extension_feed_item_server import extension_feed_item_sdk_server  # Not available in v20
from src.servers.user_data_server import user_data_server
from src.servers.user_list_server import user_list_server
from src.utils import get_logger, load_dotenv

logger = get_logger(__name__)

load_dotenv()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Google Ads MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available server groups:
  core        - Essential services (customer, campaign, budget, ad groups, keywords, ads)
  assets      - Asset management services
  targeting   - Targeting and audience services
  bidding     - Bidding strategies and modifiers
  planning    - Keyword planning and reach planning
  experiments - Campaign experiments and drafts
  reporting   - Reporting and field metadata
  conversion  - Conversion tracking and uploads
  organization - Labels and shared sets
  customizers - Customizer attributes and parameters
  account     - Account management and linking
  other       - Smart campaigns, batch jobs, user data

Examples:
  uv run main.py                    # Mount all servers
  uv run main.py --groups all       # Mount all servers
  uv run main.py --groups core      # Mount only core services
  uv run main.py --groups core,assets,targeting  # Mount specific groups
""",
    )

    parser.add_argument(
        "--groups",
        type=str,
        default="core",
        help="Comma-separated list of server groups to mount (default: core)",
    )

    return parser.parse_args()


@asynccontextmanager
async def lifespan(app: Any) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Manage Google Ads SDK client lifecycle."""
    logger.info("Starting Google Ads SDK API MCP server...")
    client = None
    try:
        client = GoogleAdsSdkClient()
        set_sdk_client(client)
        logger.info("Google Ads SDK client initialized successfully")
        yield
    finally:
        logger.info("Shutting down Google Ads SDK API MCP server...")
        if client:
            client.close()


# Initialize main MCP server with lifespan
mcp = FastMCP(
    name="google-ads-mcp",
    instructions="""This is a Google Ads MCP server that provides API tools for managing Google Ads accounts.

    It includes tools for:
    - Customer management (create customers, list accessible customers)
    - Campaign management (create and update campaigns)
    - Budget management (create and update campaign budgets)
    - Ad group management (create and update ad groups)
    - Keyword management (add, update, and remove keywords)
    - Ad management (create responsive search ads and expanded text ads)
    - Conversion tracking (create and update conversion actions)
    - Search and reporting (search campaigns, ad groups, keywords, and execute GAQL queries)
    - Asset management (create text, image, and video assets)
    - Bidding strategies (create Target CPA, Target ROAS, and other automated bidding strategies)
    - Ad extensions (create sitelinks, callouts, call extensions, and structured snippets)
    - User lists (create remarketing lists, customer match lists, and similar audiences)
    - Geo targeting (search and suggest locations for targeting)
    - Recommendations (get and apply optimization recommendations)
    - Campaign criteria (manage campaign-level targeting and exclusions)
    - Ad group criteria (manage keywords, audiences, and demographics at ad group level)
    - Account-level exclusions (negative keywords, placements, and content labels)
    - Shared sets (create and manage shared negative keyword/placement lists)
    - Labels (organize campaigns, ad groups, and ads with color-coded labels)
    - Field metadata (discover available fields and validate queries)
    - Custom interests (create custom affinity and intent audiences)
    - Custom audiences (create custom segments with keywords, URLs, apps, and places)
    - Keyword planning (research keywords and get search volume data)
    - Experiments (A/B test campaign changes)
    - Offline conversion uploads (track offline sales from clicks and calls)
    - Smart campaigns (simplified campaign management with AI suggestions)
    - Remarketing actions (create and manage remarketing tags)
    - Conversion adjustments (restate or retract conversions)
    - Campaign bid modifiers (adjust bids by device, location, schedule, demographics)
    - Ad group bid modifiers (ad group-level bid adjustments)
    - Campaign shared sets (link campaigns to shared negative lists)
    - Billing setup (configure billing and payments accounts)

    The Google Ads SDK client is initialized automatically when the server starts.
    All customer IDs can be provided with or without hyphens.

    This implementation uses the Google Ads Python SDK for all operations with full type safety.""",
    lifespan=lifespan,
)


# Define server groups
SERVER_GROUPS = {
    "core": [
        ("customer", customer_service_server),
        ("campaign", campaign_server),
        ("budget", budget_server),
        ("ad_group", ad_group_server),
        ("keyword", keyword_server),
        ("ad", ad_server),
        ("ad_group_ad", ad_group_ad_server),
        ("conversion", conversion_server),
        ("google_ads", google_ads_server),
    ],
    "assets": [
        ("asset", asset_server),
        ("asset_group", asset_group_server),
        ("asset_group_asset", asset_group_asset_server),
        ("asset_group_signal", asset_group_signal_server),
        ("asset_set", asset_set_server),
        ("ad_group_asset", ad_group_asset_server),
        ("ad_group_asset_set", ad_group_asset_set_server),
        ("campaign_asset", campaign_asset_server),
        ("campaign_asset_set", campaign_asset_set_server),
        ("customer_asset", customer_asset_server),
    ],
    "targeting": [
        ("campaign_criterion", campaign_criterion_server),
        ("ad_group_criterion", ad_group_criterion_server),
        ("customer_negative_criterion", customer_negative_criterion_server),
        ("geo_target", geo_target_constant_server),
        ("audience", audience_server),
        ("custom_interest", custom_interest_server),
        ("custom_audience", custom_audience_server),
        ("user_list", user_list_server),
    ],
    "bidding": [
        ("bidding_strategy", bidding_strategy_server),
        ("campaign_bid_modifier", campaign_bid_modifier_server),
        ("ad_group_bid_modifier", ad_group_bid_modifier_server),
        ("bidding_data_exclusion", bidding_data_exclusion_server),
        ("bidding_seasonality_adjustment", bidding_seasonality_adjustment_server),
    ],
    "planning": [
        ("keyword_plan", keyword_plan_server),
        ("keyword_plan_idea", keyword_plan_idea_server),
        ("keyword_plan_ad_group", keyword_plan_ad_group_server),
        ("keyword_plan_campaign", keyword_plan_campaign_server),
        ("keyword_plan_ad_group_keyword", keyword_plan_ad_group_keyword_server),
        ("keyword_plan_campaign_keyword", keyword_plan_campaign_keyword_server),
        ("reach_plan", reach_plan_server),
        ("brand_suggestion", brand_suggestion_server),
    ],
    "experiments": [
        ("experiment", experiment_server),
        ("experiment_arm", experiment_arm_server),
        ("campaign_draft", campaign_draft_server),
    ],
    "reporting": [
        ("search", search_server),
        ("google_ads_field", google_ads_field_server),
        ("recommendation", recommendation_server),
        ("invoice", invoice_server),
        ("audience_insights", audience_insights_server),
    ],
    "conversion": [
        ("conversion_upload", conversion_upload_server),
        ("conversion_adjustment_upload", conversion_adjustment_upload_server),
        ("conversion_value_rule", conversion_value_rule_server),
        ("conversion_custom_variable", conversion_custom_variable_server),
        ("conversion_goal_campaign_config", conversion_goal_campaign_config_server),
        ("custom_conversion_goal", custom_conversion_goal_server),
        ("customer_conversion_goal", customer_conversion_goal_server),
        ("campaign_conversion_goal", campaign_conversion_goal_server),
        ("offline_user_data_job", offline_user_data_job_server),
        ("remarketing_action", remarketing_action_server),
    ],
    "organization": [
        ("label", label_server),
        ("campaign_label", campaign_label_server),
        ("ad_group_label", ad_group_label_server),
        ("ad_group_ad_label", ad_group_ad_label_server),
        ("ad_group_criterion_label", ad_group_criterion_label_server),
        ("customer_label", customer_label_server),
        ("shared_set", shared_set_server),
        ("shared_criterion", shared_criterion_server),
        ("campaign_shared_set", campaign_shared_set_server),
    ],
    "customizers": [
        ("customizer_attribute", customizer_sdk_server),
        ("customer_customizer", customer_customizer_server),
        ("campaign_customizer", campaign_customizer_server),
        ("ad_group_customizer", ad_group_customizer_server),
        ("ad_group_criterion_customizer", ad_group_criterion_customizer_server),
        ("ad_parameter", ad_parameter_server),
    ],
    "account": [
        ("customer_user_access", customer_user_access_server),
        ("customer_user_access_invitation", customer_user_access_invitation_server),
        ("customer_client_link", customer_client_link_server),
        ("customer_manager_link", customer_manager_link_server),
        ("account_link", account_link_server),
        ("account_budget_proposal", account_budget_proposal_server),
        ("billing_setup", billing_setup_server),
        ("payments_account", payments_account_server),
        ("identity_verification", identity_verification_server),
        ("product_link", product_link_server),
        ("data_link", data_link_server),
    ],
    "other": [
        ("smart_campaign", smart_campaign_server),
        ("batch_job", batch_job_server),
        ("user_data", user_data_server),
    ],
}


def get_servers_to_mount(groups_arg: str) -> Set[tuple[str, Any]]:
    """Get the set of servers to mount based on the groups argument."""
    if groups_arg == "all":
        # Return all servers from all groups
        all_servers = set()
        for servers in SERVER_GROUPS.values():
            all_servers.update(servers)
        return all_servers

    # Parse requested groups
    requested_groups = [g.strip() for g in groups_arg.split(",")]
    servers_to_mount = set()

    for group in requested_groups:
        if group in SERVER_GROUPS:
            servers_to_mount.update(SERVER_GROUPS[group])
        else:
            logger.warning(f"Unknown server group: {group}")

    return servers_to_mount


# Parse command line arguments
args = parse_arguments()
servers_to_mount = get_servers_to_mount(args.groups)

# Log which groups are being mounted
if args.groups == "all":
    logger.info("Mounting all server groups")
else:
    logger.info(f"Mounting server groups: {args.groups}")

# Mount the selected servers
for prefix, server in servers_to_mount:
    mcp.mount(server, prefix=prefix)


@mcp.tool
async def check_sdk_client_status(ctx: Context) -> str:  # noqa: ARG001
    """Check if the Google Ads SDK client is initialized."""
    try:
        client = get_sdk_client()
        if client:
            return "Google Ads SDK client is initialized and ready"
    except Exception:
        pass
    return "Google Ads SDK client is not initialized"


shutdown_event = asyncio.Event()


def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    # Set the shutdown event instead of sys.exit
    shutdown_event.set()

    # Force exit after a timeout if graceful shutdown fails
    def force_exit():
        logger.warning("Force exiting after timeout...")
        os._exit(0)

    import threading

    threading.Timer(2.0, force_exit).start()


async def run_with_shutdown():
    """Run the MCP server with graceful shutdown support."""
    tools = await mcp.get_tools()
    logger.info(
        f"Registered tools: {len(tools)} tools from {len(servers_to_mount)} servers"
    )
    # Create a task for the server
    server_task = asyncio.create_task(mcp.run_async(transport="stdio"))

    # Wait for either the server to complete or shutdown signal
    shutdown_task = asyncio.create_task(shutdown_event.wait())

    _, pending = await asyncio.wait(
        [server_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel any pending tasks
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logger.info("Server stopped gracefully")


if __name__ == "__main__":
    import os

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(run_with_shutdown())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt during startup")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
