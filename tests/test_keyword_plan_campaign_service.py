"""Tests for Google Ads Keyword Plan Campaign Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from google.ads.googleads.v20.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)
from google.ads.googleads.v20.resources.types.keyword_plan_campaign import (
    KeywordPlanCampaign,
    KeywordPlanGeoTarget,
)
from google.ads.googleads.v20.services.types.keyword_plan_campaign_service import (
    KeywordPlanCampaignOperation,
    MutateKeywordPlanCampaignsRequest,
    MutateKeywordPlanCampaignsResponse,
    MutateKeywordPlanCampaignResult,
)

from src.sdk_services.planning.keyword_plan_campaign_service import (
    KeywordPlanCampaignService,
)


class TestKeywordPlanCampaignService:
    """Test cases for KeywordPlanCampaignService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service  # type: ignore
        return client

    @pytest.fixture
    def keyword_plan_campaign_service(self, mock_client):
        """Create KeywordPlanCampaignService instance with mock client"""
        return KeywordPlanCampaignService(mock_client)

    def test_mutate_keyword_plan_campaigns(
        self, keyword_plan_campaign_service: Any, mock_client: Any
    ):
        """Test mutating keyword plan campaigns"""
        # Setup
        customer_id = "1234567890"
        operations = [KeywordPlanCampaignOperation()]

        mock_response = MutateKeywordPlanCampaignsResponse(
            results=[
                MutateKeywordPlanCampaignResult(
                    resource_name="customers/1234567890/keywordPlanCampaigns/123"
                )
            ]
        )
        mock_client.get_service.return_value.mutate_keyword_plan_campaigns.return_value = mock_response  # type: ignore

        # Execute
        response = keyword_plan_campaign_service.mutate_keyword_plan_campaigns(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("KeywordPlanCampaignService")  # type: ignore

        # Verify request
        call_args = (
            mock_client.get_service.return_value.mutate_keyword_plan_campaigns.call_args  # type: ignore
        )
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure == True
        assert request.validate_only == False

    def test_create_keyword_plan_campaign_operation(
        self, keyword_plan_campaign_service: Any
    ):
        """Test creating keyword plan campaign operation for creation"""
        # Setup
        keyword_plan = "customers/1234567890/keywordPlans/123"
        name = "Test Keyword Plan Campaign"
        keyword_plan_network = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
        cpc_bid_micros = 1000000
        language_constants = ["languageConstants/1000"]
        geo_target_constants = ["geoTargetConstants/2840"]

        # Execute
        operation = (
            keyword_plan_campaign_service.create_keyword_plan_campaign_operation(
                keyword_plan=keyword_plan,
                name=name,
                keyword_plan_network=keyword_plan_network,
                cpc_bid_micros=cpc_bid_micros,
                language_constants=language_constants,
                geo_target_constants=geo_target_constants,
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignOperation)
        assert operation.create.keyword_plan == keyword_plan
        assert operation.create.name == name
        assert operation.create.keyword_plan_network == keyword_plan_network
        assert operation.create.cpc_bid_micros == cpc_bid_micros
        assert operation.create.language_constants == language_constants
        assert len(operation.create.geo_targets) == 1
        assert (
            operation.create.geo_targets[0].geo_target_constant
            == geo_target_constants[0]
        )

    def test_create_keyword_plan_campaign_operation_minimal(
        self, keyword_plan_campaign_service: Any
    ):
        """Test creating keyword plan campaign operation with minimal fields"""
        # Setup
        keyword_plan = "customers/1234567890/keywordPlans/123"
        name = "Test Keyword Plan Campaign"
        keyword_plan_network = (
            KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
        )
        cpc_bid_micros = 1000000

        # Execute
        operation = (
            keyword_plan_campaign_service.create_keyword_plan_campaign_operation(
                keyword_plan=keyword_plan,
                name=name,
                keyword_plan_network=keyword_plan_network,
                cpc_bid_micros=cpc_bid_micros,
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignOperation)
        assert operation.create.keyword_plan == keyword_plan
        assert operation.create.name == name
        assert operation.create.keyword_plan_network == keyword_plan_network
        assert operation.create.cpc_bid_micros == cpc_bid_micros
        assert operation.create.language_constants == []
        assert operation.create.geo_targets == []

    def test_update_keyword_plan_campaign_operation(
        self, keyword_plan_campaign_service: Any
    ):
        """Test creating keyword plan campaign operation for update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaigns/123"
        name = "Updated Keyword Plan Campaign"
        keyword_plan_network = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
        cpc_bid_micros = 2000000
        language_constants = ["languageConstants/1001"]
        geo_target_constants = ["geoTargetConstants/2841"]

        # Execute
        operation = (
            keyword_plan_campaign_service.update_keyword_plan_campaign_operation(
                resource_name=resource_name,
                name=name,
                keyword_plan_network=keyword_plan_network,
                cpc_bid_micros=cpc_bid_micros,
                language_constants=language_constants,
                geo_target_constants=geo_target_constants,
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update.keyword_plan_network == keyword_plan_network
        assert operation.update.cpc_bid_micros == cpc_bid_micros
        assert operation.update.language_constants == language_constants
        assert len(operation.update.geo_targets) == 1
        assert (
            operation.update.geo_targets[0].geo_target_constant
            == geo_target_constants[0]
        )
        assert set(operation.update_mask.paths) == {
            "name",
            "keyword_plan_network",
            "cpc_bid_micros",
            "language_constants",
            "geo_targets",
        }

    def test_update_keyword_plan_campaign_operation_partial(
        self, keyword_plan_campaign_service: Any
    ):
        """Test creating keyword plan campaign operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaigns/123"
        name = "Updated Keyword Plan Campaign"

        # Execute
        operation = (
            keyword_plan_campaign_service.update_keyword_plan_campaign_operation(
                resource_name=resource_name, name=name
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update_mask.paths == ["name"]

    def test_remove_keyword_plan_campaign_operation(
        self, keyword_plan_campaign_service: Any
    ):
        """Test creating keyword plan campaign operation for removal"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaigns/123"

        # Execute
        operation = (
            keyword_plan_campaign_service.remove_keyword_plan_campaign_operation(
                resource_name
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignOperation)
        assert operation.remove == resource_name
