"""Main entry point for Google Ads MCP server."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from types import FrameType
from typing import Any, AsyncGenerator, Optional

from fastmcp import Context, FastMCP

from src.sdk_client import GoogleAdsSdkClient, get_sdk_client, set_sdk_client
from src.sdk_servers.account_budget_proposal_server import (
    register_account_budget_proposal_server,
)
from src.sdk_servers.account_link_server import register_account_link_server
from src.sdk_servers.ad_group_ad_server import register_ad_group_ad_server
from src.sdk_servers.ad_group_asset_server import register_ad_group_asset_server
from src.sdk_servers.ad_group_bid_modifier_server import (
    register_ad_group_bid_modifier_server,
)
from src.sdk_servers.ad_group_criterion_server import ad_group_criterion_sdk_server
from src.sdk_servers.ad_group_label_server import register_ad_group_label_server
from src.sdk_servers.ad_group_server import ad_group_sdk_server
from src.sdk_servers.ad_server import ad_sdk_server
from src.sdk_servers.asset_group_asset_server import register_asset_group_asset_server
from src.sdk_servers.asset_group_server import register_asset_group_server
from src.sdk_servers.asset_server import asset_sdk_server
from src.sdk_servers.asset_set_server import register_asset_set_server
from src.sdk_servers.audience_insights_server import register_audience_insights_server
from src.sdk_servers.audience_server import register_audience_server
from src.sdk_servers.bidding_data_exclusion_server import (
    register_bidding_data_exclusion_server,
)
from src.sdk_servers.bidding_strategy_server import bidding_strategy_sdk_server
from src.sdk_servers.billing_setup_server import register_billing_setup_server
from src.sdk_servers.budget_server import budget_sdk_server
from src.sdk_servers.campaign_asset_server import register_campaign_asset_server
from src.sdk_servers.campaign_bid_modifier_server import (
    register_campaign_bid_modifier_server,
)
from src.sdk_servers.campaign_conversion_goal_server import (
    register_campaign_conversion_goal_server,
)
from src.sdk_servers.campaign_criterion_server import campaign_criterion_sdk_server
from src.sdk_servers.campaign_customizer_server import (
    register_campaign_customizer_server,
)
from src.sdk_servers.campaign_draft_server import register_campaign_draft_server
from src.sdk_servers.campaign_label_server import register_campaign_label_server
from src.sdk_servers.campaign_server import campaign_sdk_server
from src.sdk_servers.campaign_shared_set_server import (
    register_campaign_shared_set_server,
)
from src.sdk_servers.conversion_adjustment_upload_server import (
    register_conversion_adjustment_upload_server,
)
from src.sdk_servers.conversion_custom_variable_server import (
    register_conversion_custom_variable_server,
)
from src.sdk_servers.conversion_server import conversion_sdk_server
from src.sdk_servers.conversion_upload_server import conversion_upload_sdk_server
from src.sdk_servers.conversion_value_rule_server import (
    register_conversion_value_rule_server,
)
from src.sdk_servers.custom_audience_server import custom_audience_sdk_server
from src.sdk_servers.custom_interest_server import custom_interest_sdk_server
from src.sdk_servers.customer_client_link_server import (
    register_customer_client_link_server,
)
from src.sdk_servers.customer_manager_link_server import (
    register_customer_manager_link_server,
)
from src.sdk_servers.customer_label_server import register_customer_label_server
from src.sdk_servers.customer_negative_criterion_server import (
    customer_negative_criterion_sdk_server,
)
from src.sdk_servers.customer_server import customer_sdk_server
from src.sdk_servers.customer_user_access_server import (
    register_customer_user_access_server,
)
from src.sdk_servers.customizer_attribute_server import (
    register_customizer_attribute_server,
)
from src.sdk_servers.data_link_server import register_data_link_server
from src.sdk_servers.experiment_server import experiment_sdk_server
from src.sdk_servers.geo_target_constant_server import geo_target_constant_sdk_server
from src.sdk_servers.google_ads_field_server import google_ads_field_sdk_server
from src.sdk_servers.google_ads_server import register_google_ads_server
from src.sdk_servers.invoice_server import register_invoice_server
from src.sdk_servers.keyword_plan_idea_server import register_keyword_plan_idea_server
from src.sdk_servers.keyword_plan_server import keyword_plan_sdk_server
from src.sdk_servers.keyword_server import keyword_sdk_server
from src.sdk_servers.label_server import label_sdk_server
from src.sdk_servers.offline_user_data_job_server import (
    register_offline_user_data_job_server,
)
from src.sdk_servers.reach_plan_server import register_reach_plan_server
from src.sdk_servers.recommendation_server import recommendation_sdk_server
from src.sdk_servers.remarketing_action_server import remarketing_action_sdk_server
from src.sdk_servers.search_server import search_sdk_server
from src.sdk_servers.shared_criterion_server import shared_criterion_sdk_server
from src.sdk_servers.shared_set_server import shared_set_sdk_server
from src.sdk_servers.smart_campaign_server import smart_campaign_sdk_server

# from src.sdk_servers.extension_feed_item_server import extension_feed_item_sdk_server  # Not available in v20
from src.sdk_servers.user_data_server import register_user_data_server
from src.sdk_servers.user_list_server import user_list_sdk_server
from src.utils import get_logger, load_dotenv

logger = get_logger(__name__)

load_dotenv()


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


# Mount the servers
mcp.mount(customer_sdk_server, prefix="customer")
mcp.mount(campaign_sdk_server, prefix="campaign")
mcp.mount(budget_sdk_server, prefix="budget")
mcp.mount(ad_group_sdk_server, prefix="ad_group")
mcp.mount(keyword_sdk_server, prefix="keyword")
mcp.mount(ad_sdk_server, prefix="ad")
register_ad_group_ad_server(mcp)
register_ad_group_asset_server(mcp)
mcp.mount(conversion_sdk_server, prefix="conversion")
mcp.mount(search_sdk_server, prefix="search")
mcp.mount(asset_sdk_server, prefix="asset")
register_asset_group_server(mcp)
register_asset_group_asset_server(mcp)
register_asset_set_server(mcp)
mcp.mount(bidding_strategy_sdk_server, prefix="bidding_strategy")
# mcp.mount(extension_feed_item_sdk_server, prefix="extension")  # Not available in v20
mcp.mount(user_list_sdk_server, prefix="user_list")
register_audience_server(mcp)
mcp.mount(geo_target_constant_sdk_server, prefix="geo_target")
mcp.mount(recommendation_sdk_server, prefix="recommendation")
mcp.mount(campaign_criterion_sdk_server, prefix="campaign_criterion")
mcp.mount(ad_group_criterion_sdk_server, prefix="ad_group_criterion")
mcp.mount(customer_negative_criterion_sdk_server, prefix="customer_negative_criterion")
mcp.mount(shared_set_sdk_server, prefix="shared_set")
mcp.mount(shared_criterion_sdk_server, prefix="shared_criterion")
mcp.mount(label_sdk_server, prefix="label")
register_campaign_label_server(mcp)
register_campaign_asset_server(mcp)
register_ad_group_label_server(mcp)
mcp.mount(google_ads_field_sdk_server, prefix="google_ads_field")
mcp.mount(custom_interest_sdk_server, prefix="custom_interest")
mcp.mount(custom_audience_sdk_server, prefix="custom_audience")
mcp.mount(keyword_plan_sdk_server, prefix="keyword_plan")
register_keyword_plan_idea_server(mcp)
mcp.mount(experiment_sdk_server, prefix="experiment")
mcp.mount(conversion_upload_sdk_server, prefix="conversion_upload")
mcp.mount(smart_campaign_sdk_server, prefix="smart_campaign")
mcp.mount(remarketing_action_sdk_server, prefix="remarketing_action")
register_conversion_adjustment_upload_server(mcp)
register_campaign_bid_modifier_server(mcp)
register_ad_group_bid_modifier_server(mcp)
register_campaign_shared_set_server(mcp)
register_billing_setup_server(mcp)
register_offline_user_data_job_server(mcp)
register_conversion_value_rule_server(mcp)
register_user_data_server(mcp)
register_customizer_attribute_server(mcp)
register_customer_user_access_server(mcp)
register_account_link_server(mcp)
register_reach_plan_server(mcp)
register_data_link_server(mcp)
register_account_budget_proposal_server(mcp)
register_invoice_server(mcp)
register_campaign_draft_server(mcp)
register_bidding_data_exclusion_server(mcp)
register_customer_client_link_server(mcp)
register_audience_insights_server(mcp)
register_google_ads_server(mcp)
register_customer_manager_link_server(mcp)
register_customer_label_server(mcp)
register_conversion_custom_variable_server(mcp)
register_campaign_conversion_goal_server(mcp)
register_campaign_customizer_server(mcp)


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
    logger.info(f"Registered tools: {len(tools)} tools")
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
