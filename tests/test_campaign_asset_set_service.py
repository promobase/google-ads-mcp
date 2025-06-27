"""Tests for Campaign Asset Set Service."""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from google.ads.googleads.v20.services.services.campaign_asset_set_service import (
    CampaignAssetSetServiceClient,
)
from google.ads.googleads.v20.services.types.campaign_asset_set_service import (
    CampaignAssetSetOperation,
    MutateCampaignAssetSetsRequest,
    MutateCampaignAssetSetsResponse,
    MutateCampaignAssetSetResult,
)
from google.ads.googleads.v20.resources.types.campaign_asset_set import CampaignAssetSet
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)

from src.sdk_services.campaign.campaign_asset_set_service import CampaignAssetSetService


class TestCampaignAssetSetService:
    """Test cases for CampaignAssetSetService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock CampaignAssetSetServiceClient."""
        return Mock(spec=CampaignAssetSetServiceClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create a CampaignAssetSetService instance with mock client."""
        return CampaignAssetSetService(mock_client)

    def test_mutate_campaign_asset_sets_success(self, service: Any, mock_client: Any):
        """Test successful campaign asset sets mutation."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CampaignAssetSetOperation)]
        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                )
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=operations,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateCampaignAssetSetsRequest)
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure is False
        assert request.validate_only is False

    def test_mutate_campaign_asset_sets_with_options(
        self, service: Any, mock_client: Any
    ):
        """Test campaign asset sets mutation with all options."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CampaignAssetSetOperation)]
        expected_response = MutateCampaignAssetSetsResponse()
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_campaign_asset_sets(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        # Assert
        assert response == expected_response
        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    def test_mutate_campaign_asset_sets_failure(self, service: Any, mock_client: Any):
        """Test campaign asset sets mutation failure."""
        # Arrange
        customer_id = "1234567890"
        operations = [Mock(spec=CampaignAssetSetOperation)]
        mock_client.mutate_campaign_asset_sets.side_effect = Exception("API Error")  # type: ignore

        # Act & Assert
        with pytest.raises(Exception, match="Failed to mutate campaign asset sets"):
            service.mutate_campaign_asset_sets(
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_campaign_asset_set_operation(self, service: Any):
        """Test creating campaign asset set operation."""
        # Arrange
        campaign = "customers/1234567890/campaigns/123"
        asset_set = "customers/1234567890/assetSets/456"

        # Act
        operation = service.create_campaign_asset_set_operation(
            campaign=campaign,
            asset_set=asset_set,
        )

        # Assert
        assert isinstance(operation, CampaignAssetSetOperation)
        assert operation.create.campaign == campaign
        assert operation.create.asset_set == asset_set

    def test_create_remove_operation(self, service: Any):
        """Test creating remove operation."""
        # Arrange
        resource_name = "customers/1234567890/campaignAssetSets/123~456"

        # Act
        operation = service.create_remove_operation(resource_name=resource_name)

        # Assert
        assert isinstance(operation, CampaignAssetSetOperation)
        assert operation.remove == resource_name
        assert not operation.create

    def test_link_asset_set_to_campaign(self, service: Any, mock_client: Any):
        """Test linking an asset set to a campaign."""
        # Arrange
        customer_id = "1234567890"
        campaign = "customers/1234567890/campaigns/123"
        asset_set = "customers/1234567890/assetSets/456"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                )
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.link_asset_set_to_campaign(
            customer_id=customer_id,
            campaign=campaign,
            asset_set=asset_set,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

    def test_unlink_asset_set_from_campaign(self, service: Any, mock_client: Any):
        """Test unlinking an asset set from a campaign."""
        # Arrange
        customer_id = "1234567890"
        resource_name = "customers/1234567890/campaignAssetSets/123~456"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[MutateCampaignAssetSetResult(resource_name=resource_name)]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.unlink_asset_set_from_campaign(
            customer_id=customer_id,
            resource_name=resource_name,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

    def test_link_multiple_asset_sets_to_campaign(self, service: Any, mock_client: Any):
        """Test linking multiple asset sets to a campaign."""
        # Arrange
        customer_id = "1234567890"
        campaign = "customers/1234567890/campaigns/123"
        asset_sets = [
            "customers/1234567890/assetSets/456",
            "customers/1234567890/assetSets/789",
        ]

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                ),
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~789"
                ),
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.link_multiple_asset_sets_to_campaign(
            customer_id=customer_id,
            campaign=campaign,
            asset_sets=asset_sets,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

        # Verify that two operations were created
        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    def test_link_asset_set_to_multiple_campaigns(self, service: Any, mock_client: Any):
        """Test linking an asset set to multiple campaigns."""
        # Arrange
        customer_id = "1234567890"
        campaigns = [
            "customers/1234567890/campaigns/123",
            "customers/1234567890/campaigns/456",
        ]
        asset_set = "customers/1234567890/assetSets/789"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~789"
                ),
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/456~789"
                ),
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        # Act
        response = service.link_asset_set_to_multiple_campaigns(
            customer_id=customer_id,
            campaigns=campaigns,
            asset_set=asset_set,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

        # Verify that two operations were created
        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2


@pytest.mark.asyncio
class TestCampaignAssetSetMCPServer:
    """Test cases for Campaign Asset Set MCP server."""

    @patch("src.sdk_servers.campaign_asset_set_server.get_client")
    async def test_link_asset_set_to_campaign_tool(self, mock_get_client: Any):
        """Test link asset set to campaign MCP tool."""
        # Arrange
        from src.sdk_servers.campaign_asset_set_server import (
            create_campaign_asset_set_server,
        )

        mock_client = Mock(spec=CampaignAssetSetServiceClient)
        mock_get_client.return_value = mock_client  # type: ignore

        mock_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                )
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = mock_response  # type: ignore

        server = create_campaign_asset_set_server()

        # Act
        response = await server.call_tool()(
            name="link_asset_set_to_campaign",
            arguments={
                "customer_id": "1234567890",
                "campaign": "customers/1234567890/campaigns/123",
                "asset_set": "customers/1234567890/assetSets/456",
            },
        )

        # Assert
        assert len(response) == 1
        assert "customers/1234567890/campaignAssetSets/123~456" in response[0].text
        assert "link_asset_set" in response[0].text

    @patch("src.sdk_servers.campaign_asset_set_server.get_client")
    async def test_link_multiple_asset_sets_to_campaign_tool(
        self, mock_get_client: Any
    ):
        """Test link multiple asset sets to campaign MCP tool."""
        # Arrange
        from src.sdk_servers.campaign_asset_set_server import (
            create_campaign_asset_set_server,
        )

        mock_client = Mock(spec=CampaignAssetSetServiceClient)
        mock_get_client.return_value = mock_client  # type: ignore

        mock_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                ),
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~789"
                ),
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = mock_response  # type: ignore

        server = create_campaign_asset_set_server()

        # Act
        response = await server.call_tool()(
            name="link_multiple_asset_sets_to_campaign",
            arguments={
                "customer_id": "1234567890",
                "campaign": "customers/1234567890/campaigns/123",
                "asset_sets": [
                    "customers/1234567890/assetSets/456",
                    "customers/1234567890/assetSets/789",
                ],
            },
        )

        # Assert
        assert len(response) == 1
        assert "link_multiple_asset_sets" in response[0].text
        assert "customers/1234567890/campaignAssetSets/123~456" in response[0].text
        assert "customers/1234567890/campaignAssetSets/123~789" in response[0].text
