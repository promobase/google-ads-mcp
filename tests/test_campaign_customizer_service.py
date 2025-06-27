"""Tests for Campaign Customizer service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.common.types.customizer_value import CustomizerValue
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.resources.types.campaign_customizer import (
    CampaignCustomizer,
)
from google.ads.googleads.v20.services.types.campaign_customizer_service import (
    CampaignCustomizerOperation,
    MutateCampaignCustomizersResponse,
    MutateCampaignCustomizerResult,
)
from google.rpc import status_pb2

from src.sdk_services.campaign.campaign_customizer_service import (
    CampaignCustomizerService,
    create_campaign_customizer_tools,
)


@pytest.fixture
def campaign_customizer_service():
    """Create a Campaign Customizer service instance."""
    return CampaignCustomizerService()


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = AsyncMock()
    ctx.log = AsyncMock()
    return ctx


@pytest.fixture
def mock_client():
    """Create a mock Campaign Customizer service client."""
    return MagicMock()


@pytest.mark.asyncio
class TestCampaignCustomizerService:
    """Test cases for CampaignCustomizerService."""

    async def test_create_campaign_customizer_text_success(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful creation of a text campaign customizer."""
        # Mock the client
        campaign_customizer_service._client = mock_client

        # Create mock response
        mock_result = MutateCampaignCustomizerResult()
        mock_result.resource_name = (
            "customers/1234567890/campaignCustomizers/9876543210~1111111111"
        )

        # The response includes campaign_customizer field
        mock_result.campaign_customizer.resource_name = mock_result.resource_name  # type: ignore

        mock_response = MutateCampaignCustomizersResponse()
        mock_response.results.append(mock_result)  # type: ignore

        mock_client.mutate_campaign_customizers.return_value = mock_response  # type: ignore

        # Execute
        result = await campaign_customizer_service.create_campaign_customizer(
            ctx=mock_context,
            customer_id="123-456-7890",
            campaign_id="9876543210",
            customizer_attribute_id="1111111111",
            value="Summer Sale",
            attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
        )

        # Verify request
        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        assert request.customer_id == "1234567890"
        assert len(request.operations) == 1
        assert request.partial_failure is False
        assert request.validate_only is False
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

        operation = request.operations[0]
        assert operation.create.campaign == "customers/1234567890/campaigns/9876543210"
        assert (
            operation.create.customizer_attribute
            == "customers/1234567890/customizerAttributes/1111111111"
        )
        assert (
            operation.create.value.type_
            == CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        )
        assert operation.create.value.string_value == "Summer Sale"

        # Verify logging
        mock_context.log.assert_called_with(  # type: ignore
            level="info",
            message="Created campaign customizer: campaign 9876543210, attribute 1111111111, value 'Summer Sale'",
        )

    async def test_create_campaign_customizer_different_types(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test creating customizers with different attribute types."""
        campaign_customizer_service._client = mock_client

        mock_response = MutateCampaignCustomizersResponse()
        mock_response.results.append(MutateCampaignCustomizerResult())  # type: ignore
        mock_client.mutate_campaign_customizers.return_value = mock_response  # type: ignore

        # Test with NUMBER type
        await campaign_customizer_service.create_campaign_customizer(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="2222222222",
            customizer_attribute_id="3333333333",
            value="99",
            attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.NUMBER,
        )

        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert (
            operation.create.value.type_
            == CustomizerAttributeTypeEnum.CustomizerAttributeType.NUMBER
        )
        assert operation.create.value.string_value == "99"

        # Test with PRICE type
        await campaign_customizer_service.create_campaign_customizer(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="4444444444",
            customizer_attribute_id="5555555555",
            value="19.99 USD",
            attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PRICE,
        )

        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert (
            operation.create.value.type_
            == CustomizerAttributeTypeEnum.CustomizerAttributeType.PRICE
        )
        assert operation.create.value.string_value == "19.99 USD"

        # Test with PERCENT type
        await campaign_customizer_service.create_campaign_customizer(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="6666666666",
            customizer_attribute_id="7777777777",
            value="25",
            attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT,
        )

        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]
        assert (
            operation.create.value.type_
            == CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT
        )
        assert operation.create.value.string_value == "25"

    async def test_remove_campaign_customizer_success(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test successful removal of a campaign customizer."""
        campaign_customizer_service._client = mock_client

        mock_response = MutateCampaignCustomizersResponse()
        mock_response.results.append(MutateCampaignCustomizerResult())  # type: ignore
        mock_client.mutate_campaign_customizers.return_value = mock_response  # type: ignore

        # Execute
        result = await campaign_customizer_service.remove_campaign_customizer(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="9876543210",
            customizer_attribute_id="1111111111",
        )

        # Verify request
        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        operation = request.operations[0]

        # Check resource name format with ~ delimiter
        assert operation.remove == (
            "customers/1234567890/campaignCustomizers/9876543210~1111111111"
        )

        # Verify logging
        mock_context.log.assert_called_with(  # type: ignore
            level="info",
            message="Removed campaign customizer: campaign 9876543210, attribute 1111111111",
        )

    async def test_create_with_partial_failure(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test create with partial failure mode."""
        campaign_customizer_service._client = mock_client

        # Create response with partial failure error
        mock_response = MutateCampaignCustomizersResponse()
        mock_response.results.append(MutateCampaignCustomizerResult())  # type: ignore

        partial_error = status_pb2.Status()
        partial_error.code = 3  # INVALID_ARGUMENT
        partial_error.message = "Partial failure occurred"
        mock_response.partial_failure_error.CopyFrom(partial_error)  # type: ignore

        mock_client.mutate_campaign_customizers.return_value = mock_response  # type: ignore

        result = await campaign_customizer_service.create_campaign_customizer(
            ctx=mock_context,
            customer_id="1234567890",
            campaign_id="9876543210",
            customizer_attribute_id="1111111111",
            value="Test Value",
            attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            partial_failure=True,
        )

        request = mock_client.mutate_campaign_customizers.call_args[1]["request"]  # type: ignore
        assert request.partial_failure is True

    async def test_create_api_error(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test create with API error."""
        campaign_customizer_service._client = mock_client

        # Mock API error
        error = GoogleAdsException(None, None, None, None)
        error.failure = Mock()
        error.failure.__str__ = Mock(return_value="Invalid customizer attribute")
        mock_client.mutate_campaign_customizers.side_effect = error  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await campaign_customizer_service.create_campaign_customizer(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="invalid",
                value="Test",
                attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            )

        assert "Google Ads API error: Invalid customizer attribute" in str(
            exc_info.value
        )

    async def test_remove_general_error(
        self, campaign_customizer_service: Any, mock_context: Any, mock_client: Any
    ):
        """Test remove with general error."""
        campaign_customizer_service._client = mock_client
        mock_client.mutate_campaign_customizers.side_effect = Exception("Network error")  # type: ignore

        with pytest.raises(Exception) as exc_info:
            await campaign_customizer_service.remove_campaign_customizer(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
            )

        assert "Failed to remove campaign customizer: Network error" in str(
            exc_info.value
        )


@pytest.mark.asyncio
class TestCampaignCustomizerTools:
    """Test cases for Campaign Customizer tool functions."""

    async def test_create_campaign_customizer_tool(self, mock_context: Any):
        """Test create_campaign_customizer tool function."""
        service = CampaignCustomizerService()
        tools = create_campaign_customizer_tools(service)
        create_tool = tools[0]  # First tool is create_campaign_customizer

        # Mock the service method
        with patch.object(service, "create_campaign_customizer") as mock_create:
            mock_create.return_value = {  # type: ignore
                "results": [
                    {"resource_name": "customers/123/campaignCustomizers/456~789"}
                ]
            }

            await create_tool(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
                value="25",
                attribute_type="PERCENT",
            )

            mock_create.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
                value="25",
                attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT,
                partial_failure=False,
                validate_only=False,
            )

    async def test_create_tool_with_different_types(self, mock_context: Any):
        """Test create tool with different attribute types."""
        service = CampaignCustomizerService()
        tools = create_campaign_customizer_tools(service)
        create_tool = tools[0]

        with patch.object(service, "create_campaign_customizer") as mock_create:
            mock_create.return_value = {"results": [{"resource_name": "test"}]}  # type: ignore

            # Test TEXT type
            await create_tool(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="1111111111",
                customizer_attribute_id="2222222222",
                value="Summer Sale",
                attribute_type="TEXT",
            )

            mock_create.assert_called_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="1111111111",
                customizer_attribute_id="2222222222",
                value="Summer Sale",
                attribute_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
                partial_failure=False,
                validate_only=False,
            )

    async def test_remove_campaign_customizer_tool(self, mock_context: Any):
        """Test remove_campaign_customizer tool function."""
        service = CampaignCustomizerService()
        tools = create_campaign_customizer_tools(service)
        remove_tool = tools[1]  # Second tool is remove_campaign_customizer

        with patch.object(service, "remove_campaign_customizer") as mock_remove:
            mock_remove.return_value = {"results": [{"resource_name": "test"}]}  # type: ignore

            await remove_tool(
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
                validate_only=True,
            )

            mock_remove.assert_called_once_with(  # type: ignore
                ctx=mock_context,
                customer_id="1234567890",
                campaign_id="9876543210",
                customizer_attribute_id="1111111111",
                partial_failure=False,
                validate_only=True,
            )
