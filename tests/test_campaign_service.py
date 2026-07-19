"""Tests for CampaignService."""

from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v23.enums.types.campaign_experiment_type import (
    CampaignExperimentTypeEnum,
)
from google.ads.googleads.v23.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v23.enums.types.eu_political_advertising_status import (
    EuPoliticalAdvertisingStatusEnum,
)
from google.ads.googleads.v23.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_service import (
    MutateCampaignsResponse,
)

from src.services.campaign.campaign_service import (
    CampaignService,
    create_campaign_tools,
    register_campaign_tools,
)


@pytest.fixture
def campaign_service(mock_sdk_client: Any) -> CampaignService:
    """Create a CampaignService instance with mocked dependencies."""
    mock_campaign_client = Mock(spec=CampaignServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_client  # type: ignore

    with patch(
        "src.services.campaign.campaign_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignService()
        _ = service.client
        return service


def _mock_mutate(campaign_service: CampaignService) -> tuple[Mock, dict[str, Any]]:
    """Set up mock response for mutate_campaigns."""
    mock_response = Mock(spec=MutateCampaignsResponse)
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/campaigns/111222333"
    mock_response.results = [mock_result]

    mock_client = cast(Mock, campaign_service.client)
    mock_client.mutate_campaigns.return_value = mock_response  # type: ignore

    expected = {
        "results": [{"resource_name": "customers/1234567890/campaigns/111222333"}]
    }
    return mock_client, expected


# ---------------------------------------------------------------------------
# create_campaign
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a default Search campaign with ManualCPC."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Test Search Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type=AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH,
            status=CampaignStatusEnum.CampaignStatus.PAUSED,
        )

    assert result == expected
    mock_client.mutate_campaigns.assert_called_once()  # type: ignore

    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.name == "Test Search Campaign"
    assert (
        op.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    )
    assert op.create.status == CampaignStatusEnum.CampaignStatus.PAUSED
    assert (
        op.create.experiment_type
        == CampaignExperimentTypeEnum.CampaignExperimentType.BASE
    )
    assert (
        op.create.contains_eu_political_advertising
        == EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    # Default bidding is ManualCPC
    assert op.create.manual_cpc is not None
    # Network settings should be set for Search
    assert op.create.network_settings.target_google_search is True


@pytest.mark.asyncio
async def test_create_campaign_with_dates(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign with start and end dates."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Limited Time Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type=AdvertisingChannelTypeEnum.AdvertisingChannelType.DISPLAY,
            status=CampaignStatusEnum.CampaignStatus.ENABLED,
            start_date="2024-03-01",
            end_date="2024-03-31",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.start_date_time == "2024-03-01 00:00:00"
    assert op.create.end_date_time == "2024-03-31 23:59:59"


@pytest.mark.asyncio
async def test_create_pmax_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Performance Max campaign with MaximizeConversions."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="PMax Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type=AdvertisingChannelTypeEnum.AdvertisingChannelType.PERFORMANCE_MAX,
            bidding_strategy_type="MAXIMIZE_CONVERSIONS",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert (
        op.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.PERFORMANCE_MAX
    )
    assert op.create.maximize_conversions is not None
    # PMax should NOT have network settings
    assert op.create.network_settings.target_google_search is False


@pytest.mark.asyncio
async def test_create_campaign_maximize_conversion_value(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a PMax campaign with MaximizeConversionValue + target ROAS."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="PMax Revenue Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type=AdvertisingChannelTypeEnum.AdvertisingChannelType.PERFORMANCE_MAX,
            bidding_strategy_type="MAXIMIZE_CONVERSION_VALUE",
            max_conversion_value_target_roas=4.0,
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.maximize_conversion_value is not None
    assert op.create.maximize_conversion_value.target_roas == 4.0


@pytest.mark.asyncio
async def test_create_campaign_target_cpa(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign with Target CPA bidding."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Target CPA Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            bidding_strategy_type="TARGET_CPA",
            target_cpa_micros=5000000,
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.target_cpa is not None
    assert op.create.target_cpa.target_cpa_micros == 5000000


@pytest.mark.asyncio
async def test_create_campaign_portfolio_bidding(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a campaign with a portfolio bidding strategy."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Portfolio Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            bidding_strategy_type="PORTFOLIO",
            bidding_strategy_resource_name="customers/1234567890/biddingStrategies/555",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.create.bidding_strategy == "customers/1234567890/biddingStrategies/555"


@pytest.mark.asyncio
async def test_create_campaign_portfolio_requires_resource_name(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test that PORTFOLIO bidding fails without a resource name."""
    with pytest.raises(Exception, match="bidding_strategy_resource_name is required"):
        await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Bad Portfolio",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            bidding_strategy_type="PORTFOLIO",
        )


# ---------------------------------------------------------------------------
# update_campaign
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign name and status."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
            name="Updated Campaign Name",
            status=CampaignStatusEnum.CampaignStatus.ENABLED,
        )

    assert result == expected
    mock_client.mutate_campaigns.assert_called_once()  # type: ignore
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.update.name == "Updated Campaign Name"
    assert op.update.status == CampaignStatusEnum.CampaignStatus.ENABLED
    assert set(op.update_mask.paths) == {"name", "status"}


@pytest.mark.asyncio
async def test_update_campaign_bidding_strategy(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign's bidding strategy to TARGET_CPA."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
            bidding_strategy_type="TARGET_CPA",
            target_cpa_micros=3000000,
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.update.target_cpa is not None
    assert op.update.target_cpa.target_cpa_micros == 3000000
    assert "target_cpa" in op.update_mask.paths


@pytest.mark.asyncio
async def test_update_campaign_dates_only(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only campaign dates."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
            start_date="2024-04-01",
            end_date="2024-04-30",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.update.start_date_time == "2024-04-01 00:00:00"
    assert op.update.end_date_time == "2024-04-30 23:59:59"
    assert set(op.update_mask.paths) == {"start_date_time", "end_date_time"}


@pytest.mark.asyncio
async def test_update_campaign_no_changes(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating campaign with no changes."""
    mock_client, expected = _mock_mutate(campaign_service)

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert len(op.update_mask.paths) == 0


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_error_handling_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating campaign fails."""
    mock_client = campaign_service.client  # type: ignore
    mock_client.mutate_campaigns.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await campaign_service.create_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Test Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
        )

    assert "Failed to create campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_error_handling_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating campaign fails."""
    mock_client = campaign_service.client  # type: ignore
    mock_client.mutate_campaigns.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await campaign_service.update_campaign(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
            name="Updated Name",
        )

    assert "Failed to update campaign" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Tool wrappers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tool_wrapper_create_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper for create_campaign converts string enums."""
    mock_client, expected = _mock_mutate(campaign_service)

    tools = create_campaign_tools(campaign_service)
    create_campaign_tool = tools[0]

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await create_campaign_tool(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Test Campaign",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type="SEARCH",
            status="PAUSED",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert (
        op.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    )
    assert op.create.status == CampaignStatusEnum.CampaignStatus.PAUSED


@pytest.mark.asyncio
async def test_tool_wrapper_create_pmax_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test tool wrapper for creating a PMax campaign."""
    mock_client, expected = _mock_mutate(campaign_service)

    tools = create_campaign_tools(campaign_service)
    create_campaign_tool = tools[0]

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await create_campaign_tool(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="PMax via Tool",
            budget_resource_name="customers/1234567890/campaignBudgets/987654321",
            advertising_channel_type="PERFORMANCE_MAX",
            bidding_strategy_type="MAXIMIZE_CONVERSION_VALUE",
            max_conversion_value_target_roas=3.5,
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert (
        op.create.advertising_channel_type
        == AdvertisingChannelTypeEnum.AdvertisingChannelType.PERFORMANCE_MAX
    )
    assert op.create.maximize_conversion_value is not None
    assert op.create.maximize_conversion_value.target_roas == 3.5


@pytest.mark.asyncio
async def test_tool_wrapper_update_campaign(
    campaign_service: CampaignService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test the tool wrapper for update_campaign with string enum conversion."""
    mock_client, expected = _mock_mutate(campaign_service)

    tools = create_campaign_tools(campaign_service)
    update_campaign_tool = tools[1]

    with patch(
        "src.services.campaign.campaign_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await update_campaign_tool(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_id="111222333",
            status="ENABLED",
        )

    assert result == expected
    request = mock_client.mutate_campaigns.call_args[1]["request"]  # type: ignore
    op = request.operations[0]
    assert op.update.status == CampaignStatusEnum.CampaignStatus.ENABLED


def test_register_campaign_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    service = register_campaign_tools(mock_mcp)

    assert isinstance(service, CampaignService)
    assert mock_mcp.tool.call_count == 2  # type: ignore

    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]
    assert set(tool_names) == {"create_campaign", "update_campaign"}
