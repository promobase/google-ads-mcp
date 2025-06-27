"""Tests for Google Ads Keyword Plan Ad Group Service"""

import pytest
from unittest.mock import Mock, patch

from google.ads.googleads.v20.resources.types.keyword_plan_ad_group import (
    KeywordPlanAdGroup,
)
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupOperation,
    MutateKeywordPlanAdGroupsRequest,
    MutateKeywordPlanAdGroupsResponse,
    MutateKeywordPlanAdGroupResult,
)

from src.sdk_services.planning.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupService,
)


class TestKeywordPlanAdGroupService:
    """Test cases for KeywordPlanAdGroupService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service
        return client

    @pytest.fixture
    def keyword_plan_ad_group_service(self, mock_client):
        """Create KeywordPlanAdGroupService instance with mock client"""
        return KeywordPlanAdGroupService(mock_client)

    def test_mutate_keyword_plan_ad_groups(
        self, keyword_plan_ad_group_service, mock_client
    ):
        """Test mutating keyword plan ad groups"""
        # Setup
        customer_id = "1234567890"
        operations = [KeywordPlanAdGroupOperation()]

        mock_response = MutateKeywordPlanAdGroupsResponse(
            results=[
                MutateKeywordPlanAdGroupResult(
                    resource_name="customers/1234567890/keywordPlanAdGroups/123"
                )
            ]
        )
        mock_client.get_service.return_value.mutate_keyword_plan_ad_groups.return_value = mock_response

        # Execute
        response = keyword_plan_ad_group_service.mutate_keyword_plan_ad_groups(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("KeywordPlanAdGroupService")

        # Verify request
        call_args = (
            mock_client.get_service.return_value.mutate_keyword_plan_ad_groups.call_args
        )
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure == True
        assert request.validate_only == False

    def test_create_keyword_plan_ad_group_operation(
        self, keyword_plan_ad_group_service
    ):
        """Test creating keyword plan ad group operation for creation"""
        # Setup
        keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
        name = "Test Keyword Plan Ad Group"
        cpc_bid_micros = 1000000

        # Execute
        operation = (
            keyword_plan_ad_group_service.create_keyword_plan_ad_group_operation(
                keyword_plan_campaign=keyword_plan_campaign,
                name=name,
                cpc_bid_micros=cpc_bid_micros,
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupOperation)
        assert operation.create.keyword_plan_campaign == keyword_plan_campaign
        assert operation.create.name == name
        assert operation.create.cpc_bid_micros == cpc_bid_micros

    def test_create_keyword_plan_ad_group_operation_without_bid(
        self, keyword_plan_ad_group_service
    ):
        """Test creating keyword plan ad group operation without CPC bid"""
        # Setup
        keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
        name = "Test Keyword Plan Ad Group"

        # Execute
        operation = (
            keyword_plan_ad_group_service.create_keyword_plan_ad_group_operation(
                keyword_plan_campaign=keyword_plan_campaign, name=name
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupOperation)
        assert operation.create.keyword_plan_campaign == keyword_plan_campaign
        assert operation.create.name == name
        # cpc_bid_micros should not be set when not provided

    def test_update_keyword_plan_ad_group_operation(
        self, keyword_plan_ad_group_service
    ):
        """Test creating keyword plan ad group operation for update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroups/123"
        name = "Updated Keyword Plan Ad Group"
        cpc_bid_micros = 2000000

        # Execute
        operation = (
            keyword_plan_ad_group_service.update_keyword_plan_ad_group_operation(
                resource_name=resource_name, name=name, cpc_bid_micros=cpc_bid_micros
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update.cpc_bid_micros == cpc_bid_micros
        assert set(operation.update_mask.paths) == {"name", "cpc_bid_micros"}

    def test_update_keyword_plan_ad_group_operation_partial(
        self, keyword_plan_ad_group_service
    ):
        """Test creating keyword plan ad group operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroups/123"
        name = "Updated Keyword Plan Ad Group"

        # Execute
        operation = (
            keyword_plan_ad_group_service.update_keyword_plan_ad_group_operation(
                resource_name=resource_name, name=name
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.name == name
        assert operation.update_mask.paths == ["name"]

    def test_remove_keyword_plan_ad_group_operation(
        self, keyword_plan_ad_group_service
    ):
        """Test creating keyword plan ad group operation for removal"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroups/123"

        # Execute
        operation = (
            keyword_plan_ad_group_service.remove_keyword_plan_ad_group_operation(
                resource_name
            )
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupOperation)
        assert operation.remove == resource_name
