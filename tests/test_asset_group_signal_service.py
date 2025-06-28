"""Tests for Asset Group Signal Service."""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v20.services.services.asset_group_signal_service import (
    AssetGroupSignalServiceClient,
)
from google.ads.googleads.v20.services.types.asset_group_signal_service import (
    AssetGroupSignalOperation,
    MutateAssetGroupSignalsRequest,
    MutateAssetGroupSignalsResponse,
    MutateAssetGroupSignalResult,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.common.types.criteria import AudienceInfo, SearchThemeInfo

from src.services.assets.asset_group_signal_service import AssetGroupSignalService


class TestAssetGroupSignalService:
    """Test cases for AssetGroupSignalService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AssetGroupSignalServiceClient."""
        return Mock(spec=AssetGroupSignalServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any):
        """Create an AssetGroupSignalService instance with mock client."""
        service = AssetGroupSignalService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    def test_mutate_asset_group_signals_success(self, service: Any, mock_client: Any):
        """Test successful asset group signals mutation."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operation.create.audience.audience = "customers/1234567890/audiences/456"
        operations = [operation]

        expected_response = MutateAssetGroupSignalsResponse(
            results=[
                MutateAssetGroupSignalResult(
                    resource_name="customers/1234567890/assetGroupSignals/123~456"
                )
            ]
        )
        mock_client.mutate_asset_group_signals.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=operations,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_asset_group_signals.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_asset_group_signals.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAssetGroupSignalsRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1
        assert (
            request.operations[0].create.asset_group
            == "customers/1234567890/assetGroups/123"
        )
        assert (
            request.operations[0].create.audience.audience
            == "customers/1234567890/audiences/456"
        )
        assert request.partial_failure is False
        assert request.validate_only is False

    def test_mutate_asset_group_signals_with_options(
        self, service: Any, mock_client: Any
    ):
        """Test asset group signals mutation with all options."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operation.create.audience.audience = "customers/1234567890/audiences/456"
        operations = [operation]

        expected_response = MutateAssetGroupSignalsResponse()
        mock_client.mutate_asset_group_signals.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_asset_group_signals(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        # Assert
        assert response == expected_response
        call_args = mock_client.mutate_asset_group_signals.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    def test_mutate_asset_group_signals_failure(self, service: Any, mock_client: Any):
        """Test asset group signals mutation failure."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operation.create.audience.audience = "customers/1234567890/audiences/456"
        operations = [operation]

        mock_client.mutate_asset_group_signals.side_effect = Exception("API Error")  # type: ignore

        # Act & Assert
        with pytest.raises(Exception, match="Failed to mutate asset group signals"):
            service.mutate_asset_group_signals(
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_asset_group_signal_operation_with_audience(self, service: Any):
        """Test creating asset group signal operation with audience."""
        # Arrange
        asset_group = "customers/1234567890/assetGroups/123"
        audience_info = AudienceInfo(audience="customers/1234567890/audiences/456")

        # Act
        operation = service.create_asset_group_signal_operation(
            asset_group=asset_group,
            audience_info=audience_info,
        )

        # Assert
        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.audience == audience_info
        assert not operation.create.search_theme

    def test_create_asset_group_signal_operation_with_search_theme(self, service: Any):
        """Test creating asset group signal operation with search theme."""
        # Arrange
        asset_group = "customers/1234567890/assetGroups/123"
        search_theme_info = SearchThemeInfo(text="running shoes")

        # Act
        operation = service.create_asset_group_signal_operation(
            asset_group=asset_group,
            search_theme_info=search_theme_info,
        )

        # Assert
        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.search_theme == search_theme_info
        assert not operation.create.audience

    def test_create_asset_group_signal_operation_invalid_signals(self, service: Any):
        """Test creating asset group signal operation with invalid signal combination."""
        # Arrange
        asset_group = "customers/1234567890/assetGroups/123"
        audience_info = AudienceInfo(audience="customers/1234567890/audiences/456")
        search_theme_info = SearchThemeInfo(text="running shoes")

        # Act & Assert - Both signals provided
        with pytest.raises(
            ValueError,
            match="Exactly one of audience_info or search_theme_info must be provided",
        ):
            service.create_asset_group_signal_operation(
                asset_group=asset_group,
                audience_info=audience_info,
                search_theme_info=search_theme_info,
            )

        # Act & Assert - No signals provided
        with pytest.raises(
            ValueError,
            match="Exactly one of audience_info or search_theme_info must be provided",
        ):
            service.create_asset_group_signal_operation(
                asset_group=asset_group,
            )

    def test_create_remove_operation(self, service: Any):
        """Test creating remove operation."""
        # Arrange
        resource_name = "customers/1234567890/assetGroupSignals/123~456"

        # Act
        operation = service.create_remove_operation(resource_name=resource_name)

        # Assert
        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.remove == resource_name
        assert not operation.create

    def test_create_audience_signal(self, service: Any):
        """Test creating audience signal operation."""
        # Arrange
        asset_group = "customers/1234567890/assetGroups/123"
        audience_resource_name = "customers/1234567890/audiences/456"

        # Act
        operation = service.create_audience_signal(
            asset_group=asset_group,
            audience_resource_name=audience_resource_name,
        )

        # Assert
        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.audience.audience == audience_resource_name
        assert not operation.create.search_theme

    def test_create_search_theme_signal(self, service: Any):
        """Test creating search theme signal operation."""
        # Arrange
        asset_group = "customers/1234567890/assetGroups/123"
        search_theme = "running shoes"

        # Act
        operation = service.create_search_theme_signal(
            asset_group=asset_group,
            search_theme=search_theme,
        )

        # Assert
        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.search_theme.text == search_theme
        assert not operation.create.audience


# Server tests removed - server architecture has changed
