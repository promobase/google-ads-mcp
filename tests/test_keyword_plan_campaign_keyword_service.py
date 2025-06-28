"""Tests for Google Ads Keyword Plan Campaign Keyword Service"""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.services.types.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordOperation,
    MutateKeywordPlanCampaignKeywordsResponse,
    MutateKeywordPlanCampaignKeywordResult,
)

from src.services.planning.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordService,
)


class TestKeywordPlanCampaignKeywordService:
    """Test cases for KeywordPlanCampaignKeywordService"""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service  # type: ignore
        return client

    @pytest.fixture
    def keyword_plan_campaign_keyword_service(self, mock_client: Any) -> Any:
        """Create KeywordPlanCampaignKeywordService instance with mock client"""
        service = KeywordPlanCampaignKeywordService()
        service._client = mock_client  # type: ignore # Need to set private attribute for testing
        return service

    def test_mutate_keyword_plan_campaign_keywords(
        self, keyword_plan_campaign_keyword_service: Any, mock_client: Any
    ):
        """Test mutating keyword plan campaign keywords"""
        # Setup
        customer_id = "1234567890"
        operations = [KeywordPlanCampaignKeywordOperation()]

        mock_response = MutateKeywordPlanCampaignKeywordsResponse(
            results=[
                MutateKeywordPlanCampaignKeywordResult(
                    resource_name="customers/1234567890/keywordPlanCampaignKeywords/123"
                )
            ]
        )
        mock_client.get_service.return_value.mutate_keyword_plan_campaign_keywords.return_value = mock_response  # type: ignore

        # Execute
        response = (
            keyword_plan_campaign_keyword_service.mutate_keyword_plan_campaign_keywords(
                customer_id=customer_id,
                operations=operations,
                partial_failure=True,
                validate_only=False,
            )
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("KeywordPlanCampaignKeywordService")  # type: ignore

        # Verify request
        call_args = mock_client.get_service.return_value.mutate_keyword_plan_campaign_keywords.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure == True
        assert request.validate_only == False

    def test_create_keyword_plan_campaign_keyword_operation(
        self, keyword_plan_campaign_keyword_service: Any
    ):
        """Test creating keyword plan campaign keyword operation for creation"""
        # Setup
        keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
        text = "cheap shoes"
        match_type = KeywordMatchTypeEnum.KeywordMatchType.BROAD

        # Execute
        operation = keyword_plan_campaign_keyword_service.create_keyword_plan_campaign_keyword_operation(
            keyword_plan_campaign=keyword_plan_campaign,
            text=text,
            match_type=match_type,
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
        assert operation.create.keyword_plan_campaign == keyword_plan_campaign
        assert operation.create.text == text
        assert operation.create.match_type == match_type
        assert operation.create.negative == True  # Always true for campaign keywords

    def test_update_keyword_plan_campaign_keyword_operation(
        self, keyword_plan_campaign_keyword_service: Any
    ):
        """Test creating keyword plan campaign keyword operation for update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"
        text = "updated cheap shoes"
        match_type = KeywordMatchTypeEnum.KeywordMatchType.EXACT

        # Execute
        operation = keyword_plan_campaign_keyword_service.update_keyword_plan_campaign_keyword_operation(
            resource_name=resource_name, text=text, match_type=match_type
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.text == text
        assert operation.update.match_type == match_type
        assert set(operation.update_mask.paths) == {"text", "match_type"}

    def test_update_keyword_plan_campaign_keyword_operation_partial(
        self, keyword_plan_campaign_keyword_service: Any
    ):
        """Test creating keyword plan campaign keyword operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"
        text = "updated cheap shoes"

        # Execute
        operation = keyword_plan_campaign_keyword_service.update_keyword_plan_campaign_keyword_operation(
            resource_name=resource_name, text=text
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.text == text
        assert operation.update_mask.paths == ["text"]

    def test_remove_keyword_plan_campaign_keyword_operation(
        self, keyword_plan_campaign_keyword_service: Any
    ):
        """Test creating keyword plan campaign keyword operation for removal"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"

        # Execute
        operation = keyword_plan_campaign_keyword_service.remove_keyword_plan_campaign_keyword_operation(
            resource_name
        )

        # Verify
        assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
        assert operation.remove == resource_name
