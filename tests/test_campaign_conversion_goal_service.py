"""Tests for Campaign Conversion Goal service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.enums.types.conversion_action_category import (
    ConversionActionCategoryEnum,
)
from google.ads.googleads.v20.enums.types.conversion_origin import (
    ConversionOriginEnum,
)
from google.ads.googleads.v20.resources.types.campaign_conversion_goal import (
    CampaignConversionGoal,
)
from google.ads.googleads.v20.services.types.campaign_conversion_goal_service import (
    CampaignConversionGoalOperation,
    MutateCampaignConversionGoalsResponse,
    MutateCampaignConversionGoalResult,
)

from src.sdk_services.campaign.campaign_conversion_goal_service import (
    CampaignConversionGoalService,
    create_campaign_conversion_goal_tools,
)


@pytest.fixture
def campaign_conversion_goal_service():
    """Create a Campaign Conversion Goal service instance."""
    return CampaignConversionGoalService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Campaign Conversion Goal service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestCampaignConversionGoalService:
    """Test cases for CampaignConversionGoalService."""

    async def test_update_campaign_conversion_goal_success(
        self, campaign_conversion_goal_service, mock_context, mock_client
    ):
        """Test successful update of a campaign conversion goal."""
        # Mock the client
        campaign_conversion_goal_service._client = mock_client

        # Create mock response
        mock_result = MutateCampaignConversionGoalResult()
        mock_result.resource_name = (
            "customers/1234567890/campaignConversionGoals/9876543210~PURCHASE~WEBSITE"
        )

        mock_response = MutateCampaignConversionGoalsResponse()
        mock_response.results.append(mock_result)

        mock_client.mutate_campaign_conversion_goals.return_value = mock_response

        # Execute
        result = await campaign_conversion_goal_service.update_campaign_conversion_goal(
            ctx=mock_context,
            customer_id="123-456-7890",
            campaign_id="9876543210",
            category=ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE,
            origin=ConversionOriginEnum.ConversionOrigin.WEBSITE,
            biddable=True,
        )

        # Verify request
        request = mock_client.mutate_campaign_conversion_goals.call_args[1]["request"]
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.validate_only is False

        operation = request.operations[0]
        assert operation.update.resource_name == (
            "customers/1234567890/campaignConversionGoals/9876543210~PURCHASE~WEBSITE"
        )
        assert operation.update.campaign == "customers/1234567890/campaigns/9876543210"
        assert (
            operation.update.category
            == ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE
        )
        assert operation.update.origin == ConversionOriginEnum.ConversionOrigin.WEBSITE
        assert operation.update.biddable is True
        assert list(operation.update_mask.paths) == ["biddable"]

        # Verify logging
        mock_context.log.assert_called_with(
            level="info",
            message="Updated conversion goal for campaign 9876543210: PURCHASE/WEBSITE biddable=True",
        )

    async def test_update_different_categories_and_origins(
        self, campaign_conversion_goal_service, mock_context, mock_client
    ):
        """Test updating conversion goals with different categories and origins."""
        campaign_conversion_goal_service._client = mock_client

        mock_response = MutateCampaignConversionGoalsResponse()
        mock_response.results.append(MutateCampaignConversionGoalResult())
        mock_client.mutate_campaign_conversion_goals.return_value = mock_response

        # Test with LEAD category and APP origin
        await campaign_conversion_goal_service.update_campaign_conversion_goal(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="1111111111",
            category=ConversionActionCategoryEnum.ConversionActionCategory.LEAD,
            origin=ConversionOriginEnum.ConversionOrigin.APP,
            biddable=False,
        )

        request = mock_client.mutate_campaign_conversion_goals.call_args[1]["request"]
        operation = request.operations[0]
        assert operation.update.resource_name == (
            "customers/1234567890/campaignConversionGoals/1111111111~LEAD~APP"
        )
        assert (
            operation.update.category
            == ConversionActionCategoryEnum.ConversionActionCategory.LEAD
        )
        assert operation.update.origin == ConversionOriginEnum.ConversionOrigin.APP
        assert operation.update.biddable is False

    async def test_update_with_validate_only(
        self, campaign_conversion_goal_service, mock_context, mock_client
    ):
        """Test update with validate_only flag."""
        campaign_conversion_goal_service._client = mock_client

        mock_response = MutateCampaignConversionGoalsResponse()
        mock_client.mutate_campaign_conversion_goals.return_value = mock_response

        await campaign_conversion_goal_service.update_campaign_conversion_goal(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="2222222222",
            category=ConversionActionCategoryEnum.ConversionActionCategory.SIGNUP,
            origin=ConversionOriginEnum.ConversionOrigin.UPLOAD,
            biddable=True,
            validate_only=True,
        )

        request = mock_client.mutate_campaign_conversion_goals.call_args[1]["request"]
        assert request.validate_only is True

    async def test_update_api_error(
        self, campaign_conversion_goal_service, mock_context, mock_client
    ):
        """Test update with API error."""
        campaign_conversion_goal_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()
        error.failure.__str__ = Mock(return_value="Invalid campaign ID")
        mock_client.mutate_campaign_conversion_goals.side_effect = error

        with pytest.raises(Exception) as exc_info:
            await campaign_conversion_goal_service.update_campaign_conversion_goal(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="invalid",
                category=ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE,
                origin=ConversionOriginEnum.ConversionOrigin.WEBSITE,
                biddable=True,
            )

        assert "Google Ads API error: Invalid campaign ID" in str(exc_info.value)

    async def test_update_general_error(
        self, campaign_conversion_goal_service, mock_context, mock_client
    ):
        """Test update with general error."""
        campaign_conversion_goal_service._client = mock_client
        mock_client.mutate_campaign_conversion_goals.side_effect = Exception(
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            await campaign_conversion_goal_service.update_campaign_conversion_goal(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="3333333333",
                category=ConversionActionCategoryEnum.ConversionActionCategory.DOWNLOAD,
                origin=ConversionOriginEnum.ConversionOrigin.STORE,
                biddable=False,
            )

        assert "Failed to update campaign conversion goal: Network error" in str(
            exc_info.value
        )


@pytest.mark.asyncio
class TestCampaignConversionGoalTools:
    """Test cases for Campaign Conversion Goal tool functions."""

    async def test_update_campaign_conversion_goal_tool(self, mock_context):
        """Test update_campaign_conversion_goal tool function."""
        service = CampaignConversionGoalService()
        tools = create_campaign_conversion_goal_tools(service)
        update_tool = tools[0]  # Only one tool in this service

        # Mock the service method
        with patch.object(service, "update_campaign_conversion_goal") as mock_update:
            mock_update.return_value = {
                "results": [
                    {
                        "resource_name": "customers/123/campaignConversionGoals/456~PURCHASE~WEBSITE"
                    }
                ]
            }

            await update_tool(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                category="PURCHASE",
                origin="WEBSITE",
                biddable=True,
            )

            mock_update.assert_called_once_with(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                category=ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE,
                origin=ConversionOriginEnum.ConversionOrigin.WEBSITE,
                biddable=True,
                validate_only=False,
            )

    async def test_update_tool_with_different_enums(self, mock_context):
        """Test tool with different category and origin combinations."""
        service = CampaignConversionGoalService()
        tools = create_campaign_conversion_goal_tools(service)
        update_tool = tools[0]

        with patch.object(service, "update_campaign_conversion_goal") as mock_update:
            mock_update.return_value = {"results": [{"resource_name": "test"}]}

            # Test with LEAD/APP
            await update_tool(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="1111111111",
                category="LEAD",
                origin="APP",
                biddable=False,
                validate_only=True,
            )

            mock_update.assert_called_with(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="1111111111",
                category=ConversionActionCategoryEnum.ConversionActionCategory.LEAD,
                origin=ConversionOriginEnum.ConversionOrigin.APP,
                biddable=False,
                validate_only=True,
            )
