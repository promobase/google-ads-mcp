"""Tests for Google Ads Keyword Plan Ad Group Keyword Service"""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v20.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v20.services.types.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordOperation,
    MutateKeywordPlanAdGroupKeywordsResponse,
    MutateKeywordPlanAdGroupKeywordResult,
)

from src.sdk_services.planning.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordService,
)


class TestKeywordPlanAdGroupKeywordService:
    """Test cases for KeywordPlanAdGroupKeywordService"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Google Ads client"""
        client = Mock()
        service = Mock()
        client.get_service.return_value = service  # type: ignore
        return client

    @pytest.fixture
    def keyword_plan_ad_group_keyword_service(self, mock_client: Any) -> Any:
        """Create KeywordPlanAdGroupKeywordService instance with mock client"""
        service = KeywordPlanAdGroupKeywordService()
        service._client = mock_client  # type: ignore # Need to set private attribute for testing
        return service

    def test_mutate_keyword_plan_ad_group_keywords(
        self, keyword_plan_ad_group_keyword_service: Any, mock_client: Any
    ):
        """Test mutating keyword plan ad group keywords"""
        # Setup
        customer_id = "1234567890"
        operations = [KeywordPlanAdGroupKeywordOperation()]

        mock_response = MutateKeywordPlanAdGroupKeywordsResponse(
            results=[
                MutateKeywordPlanAdGroupKeywordResult(
                    resource_name="customers/1234567890/keywordPlanAdGroupKeywords/123"
                )
            ]
        )
        mock_client.get_service.return_value.mutate_keyword_plan_ad_group_keywords.return_value = mock_response  # type: ignore

        # Execute
        response = (
            keyword_plan_ad_group_keyword_service.mutate_keyword_plan_ad_group_keywords(
                customer_id=customer_id,
                operations=operations,
                partial_failure=True,
                validate_only=False,
            )
        )

        # Verify
        assert response == mock_response
        mock_client.get_service.assert_called_with("KeywordPlanAdGroupKeywordService")  # type: ignore

        # Verify request
        call_args = mock_client.get_service.return_value.mutate_keyword_plan_ad_group_keywords.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.operations == operations
        assert request.partial_failure == True
        assert request.validate_only == False

    def test_create_keyword_plan_ad_group_keyword_operation(
        self, keyword_plan_ad_group_keyword_service: Any
    ):
        """Test creating keyword plan ad group keyword operation for creation"""
        # Setup
        keyword_plan_ad_group = "customers/1234567890/keywordPlanAdGroups/123"
        text = "running shoes"
        match_type = KeywordMatchTypeEnum.KeywordMatchType.EXACT
        cpc_bid_micros = 1000000
        negative = False

        # Execute
        operation = keyword_plan_ad_group_keyword_service.create_keyword_plan_ad_group_keyword_operation(
            keyword_plan_ad_group=keyword_plan_ad_group,
            text=text,
            match_type=match_type,
            cpc_bid_micros=cpc_bid_micros,
            negative=negative,
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
        assert operation.create.keyword_plan_ad_group == keyword_plan_ad_group
        assert operation.create.text == text
        assert operation.create.match_type == match_type
        assert operation.create.cpc_bid_micros == cpc_bid_micros
        assert operation.create.negative == negative

    def test_create_keyword_plan_ad_group_keyword_operation_negative(
        self, keyword_plan_ad_group_keyword_service: Any
    ):
        """Test creating negative keyword plan ad group keyword operation"""
        # Setup
        keyword_plan_ad_group = "customers/1234567890/keywordPlanAdGroups/123"
        text = "cheap shoes"
        match_type = KeywordMatchTypeEnum.KeywordMatchType.BROAD
        negative = True

        # Execute
        operation = keyword_plan_ad_group_keyword_service.create_keyword_plan_ad_group_keyword_operation(
            keyword_plan_ad_group=keyword_plan_ad_group,
            text=text,
            match_type=match_type,
            negative=negative,
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
        assert operation.create.keyword_plan_ad_group == keyword_plan_ad_group
        assert operation.create.text == text
        assert operation.create.match_type == match_type
        assert operation.create.negative == negative
        # CPC bid should not be set for negative keywords

    def test_update_keyword_plan_ad_group_keyword_operation(
        self, keyword_plan_ad_group_keyword_service: Any
    ):
        """Test creating keyword plan ad group keyword operation for update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"
        text = "updated running shoes"
        match_type = KeywordMatchTypeEnum.KeywordMatchType.PHRASE
        cpc_bid_micros = 2000000

        # Execute
        operation = keyword_plan_ad_group_keyword_service.update_keyword_plan_ad_group_keyword_operation(
            resource_name=resource_name,
            text=text,
            match_type=match_type,
            cpc_bid_micros=cpc_bid_micros,
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.text == text
        assert operation.update.match_type == match_type
        assert operation.update.cpc_bid_micros == cpc_bid_micros
        assert set(operation.update_mask.paths) == {
            "text",
            "match_type",
            "cpc_bid_micros",
        }

    def test_update_keyword_plan_ad_group_keyword_operation_partial(
        self, keyword_plan_ad_group_keyword_service: Any
    ):
        """Test creating keyword plan ad group keyword operation for partial update"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"
        text = "updated running shoes"

        # Execute
        operation = keyword_plan_ad_group_keyword_service.update_keyword_plan_ad_group_keyword_operation(
            resource_name=resource_name, text=text
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.text == text
        assert operation.update_mask.paths == ["text"]

    def test_remove_keyword_plan_ad_group_keyword_operation(
        self, keyword_plan_ad_group_keyword_service: Any
    ):
        """Test creating keyword plan ad group keyword operation for removal"""
        # Setup
        resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"

        # Execute
        operation = keyword_plan_ad_group_keyword_service.remove_keyword_plan_ad_group_keyword_operation(
            resource_name
        )

        # Verify
        assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
        assert operation.remove == resource_name
