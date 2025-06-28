"""Main entry point for Google Ads MCP server."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from types import FrameType
from typing import Any, AsyncGenerator, Optional

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
mcp.mount(customer_service_server, prefix="customer")
mcp.mount(campaign_server, prefix="campaign")
mcp.mount(budget_server, prefix="budget")
mcp.mount(ad_group_server, prefix="ad_group")
mcp.mount(keyword_server, prefix="keyword")
mcp.mount(ad_server, prefix="ad")
mcp.mount(ad_group_ad_server, prefix="ad_group_ad")
mcp.mount(ad_group_asset_server, prefix="ad_group_asset")
mcp.mount(conversion_server, prefix="conversion")
mcp.mount(search_server, prefix="search")
mcp.mount(asset_server, prefix="asset")
mcp.mount(asset_group_server, prefix="asset_group")
mcp.mount(asset_group_asset_server, prefix="asset_group_asset")
mcp.mount(asset_group_signal_server, prefix="asset_group_signal")
mcp.mount(asset_set_server, prefix="asset_set")
mcp.mount(bidding_strategy_server, prefix="bidding_strategy")
# mcp.mount(extension_feed_item_sdk_server, prefix="extension")  # Not available in v20
mcp.mount(user_list_server, prefix="user_list")
mcp.mount(audience_server, prefix="audience")
mcp.mount(geo_target_constant_server, prefix="geo_target")
mcp.mount(recommendation_server, prefix="recommendation")
mcp.mount(campaign_criterion_server, prefix="campaign_criterion")
mcp.mount(ad_group_criterion_server, prefix="ad_group_criterion")
mcp.mount(customer_negative_criterion_server, prefix="customer_negative_criterion")
mcp.mount(shared_set_server, prefix="shared_set")
mcp.mount(shared_criterion_server, prefix="shared_criterion")
mcp.mount(label_server, prefix="label")
mcp.mount(campaign_label_server, prefix="campaign_label")
mcp.mount(campaign_asset_server, prefix="campaign_asset")
mcp.mount(campaign_asset_set_server, prefix="campaign_asset_set")
mcp.mount(ad_group_label_server, prefix="ad_group_label")
mcp.mount(google_ads_field_server, prefix="google_ads_field")
mcp.mount(custom_interest_server, prefix="custom_interest")
mcp.mount(custom_audience_server, prefix="custom_audience")
mcp.mount(keyword_plan_server, prefix="keyword_plan")
mcp.mount(keyword_plan_idea_server, prefix="keyword_plan_idea")
mcp.mount(keyword_plan_ad_group_server, prefix="keyword_plan_ad_group")
mcp.mount(keyword_plan_campaign_server, prefix="keyword_plan_campaign")
mcp.mount(keyword_plan_ad_group_keyword_server, prefix="keyword_plan_ad_group_keyword")
mcp.mount(keyword_plan_campaign_keyword_server, prefix="keyword_plan_campaign_keyword")
mcp.mount(brand_suggestion_server, prefix="brand_suggestion")
mcp.mount(product_link_server, prefix="product_link")
mcp.mount(
    conversion_goal_campaign_config_server, prefix="conversion_goal_campaign_config"
)
mcp.mount(custom_conversion_goal_server, prefix="custom_conversion_goal")
mcp.mount(customer_conversion_goal_server, prefix="customer_conversion_goal")
mcp.mount(experiment_server, prefix="experiment")
mcp.mount(experiment_arm_server, prefix="experiment_arm")
mcp.mount(conversion_upload_server, prefix="conversion_upload")
mcp.mount(smart_campaign_server, prefix="smart_campaign")
mcp.mount(remarketing_action_server, prefix="remarketing_action")
mcp.mount(conversion_adjustment_upload_server, prefix="conversion_adjustment_upload")
mcp.mount(campaign_bid_modifier_server, prefix="campaign_bid_modifier")
mcp.mount(ad_group_bid_modifier_server, prefix="ad_group_bid_modifier")
mcp.mount(campaign_shared_set_server, prefix="campaign_shared_set")
mcp.mount(billing_setup_server, prefix="billing_setup")
mcp.mount(offline_user_data_job_server, prefix="offline_user_data_job")
mcp.mount(conversion_value_rule_server, prefix="conversion_value_rule")
mcp.mount(user_data_server, prefix="user_data")
mcp.mount(customizer_sdk_server, prefix="customizer_attribute")
mcp.mount(customer_user_access_server, prefix="customer_user_access")
mcp.mount(
    customer_user_access_invitation_server, prefix="customer_user_access_invitation"
)
mcp.mount(payments_account_server, prefix="payments_account")
mcp.mount(batch_job_server, prefix="batch_job")
mcp.mount(identity_verification_server, prefix="identity_verification")
mcp.mount(ad_group_ad_label_server, prefix="ad_group_ad_label")
mcp.mount(ad_group_criterion_label_server, prefix="ad_group_criterion_label")
mcp.mount(ad_group_criterion_customizer_server, prefix="ad_group_criterion_customizer")
mcp.mount(ad_parameter_server, prefix="ad_parameter")
mcp.mount(ad_group_customizer_server, prefix="ad_group_customizer")
mcp.mount(ad_group_asset_set_server, prefix="ad_group_asset_set")
mcp.mount(account_link_server, prefix="account_link")
mcp.mount(reach_plan_server, prefix="reach_plan")
mcp.mount(data_link_server, prefix="data_link")
mcp.mount(account_budget_proposal_server, prefix="account_budget_proposal")
mcp.mount(invoice_server, prefix="invoice")
mcp.mount(campaign_draft_server, prefix="campaign_draft")
mcp.mount(bidding_data_exclusion_server, prefix="bidding_data_exclusion")
mcp.mount(
    bidding_seasonality_adjustment_server, prefix="bidding_seasonality_adjustment"
)
mcp.mount(customer_client_link_server, prefix="customer_client_link")
mcp.mount(audience_insights_server, prefix="audience_insights")
mcp.mount(google_ads_server, prefix="google_ads")
mcp.mount(customer_manager_link_server, prefix="customer_manager_link")
mcp.mount(customer_asset_server, prefix="customer_asset")
mcp.mount(customer_customizer_server, prefix="customer_customizer")
mcp.mount(customer_label_server, prefix="customer_label")
mcp.mount(conversion_custom_variable_server, prefix="conversion_custom_variable")
mcp.mount(campaign_conversion_goal_server, prefix="campaign_conversion_goal")
mcp.mount(campaign_customizer_server, prefix="campaign_customizer")


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
