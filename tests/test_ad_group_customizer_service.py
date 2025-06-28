"""Tests for Ad Group Customizer Service."""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v20.services.services.ad_group_customizer_service import (
    AdGroupCustomizerServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_customizer_service import (
    AdGroupCustomizerOperation,
    MutateAdGroupCustomizersRequest,
    MutateAdGroupCustomizersResponse,
    MutateAdGroupCustomizerResult,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)

from src.sdk_services.ad_group.ad_group_customizer_service import (
    AdGroupCustomizerService,
)


class TestAdGroupCustomizerService:
    """Test cases for AdGroupCustomizerService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AdGroupCustomizerServiceClient."""
        return Mock(spec=AdGroupCustomizerServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any):
        """Create an AdGroupCustomizerService instance with mock client."""
        service = AdGroupCustomizerService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    def test_mutate_ad_group_customizers_success(self, service: Any, mock_client: Any):
        """Test successful ad group customizers mutation."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operation.create.customizer_attribute = (
            "customers/1234567890/customizerAttributes/456"
        )
        operation.create.value.type_ = (
            CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        )
        operation.create.value.string_value = "Test Value"
        operations = [operation]

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_ad_group_customizers(
            customer_id=customer_id,
            operations=operations,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_ad_group_customizers.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAdGroupCustomizersRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1
        assert (
            request.operations[0].create.ad_group == "customers/1234567890/adGroups/123"
        )
        assert (
            request.operations[0].create.customizer_attribute
            == "customers/1234567890/customizerAttributes/456"
        )
        assert (
            request.operations[0].create.value.type_
            == CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        )
        assert request.operations[0].create.value.string_value == "Test Value"
        assert request.partial_failure is False
        assert request.validate_only is False

    def test_mutate_ad_group_customizers_with_options(
        self, service: Any, mock_client: Any
    ):
        """Test ad group customizers mutation with all options."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operation.create.customizer_attribute = (
            "customers/1234567890/customizerAttributes/456"
        )
        operation.create.value.type_ = (
            CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        )
        operation.create.value.string_value = "Test Value"
        operations = [operation]

        expected_response = MutateAdGroupCustomizersResponse()
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_ad_group_customizers(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        # Assert
        assert response == expected_response
        call_args = mock_client.mutate_ad_group_customizers.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    def test_mutate_ad_group_customizers_failure(self, service: Any, mock_client: Any):
        """Test ad group customizers mutation failure."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operation.create.customizer_attribute = (
            "customers/1234567890/customizerAttributes/456"
        )
        operations = [operation]

        mock_client.mutate_ad_group_customizers.side_effect = Exception("API Error")  # type: ignore

        # Act & Assert
        with pytest.raises(Exception, match="Failed to mutate ad group customizers"):
            service.mutate_ad_group_customizers(
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_ad_group_customizer_operation(self, service: Any):
        """Test creating ad group customizer operation."""
        # Arrange
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        value_type = CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        string_value = "Test Value"

        # Act
        operation = service.create_ad_group_customizer_operation(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        # Assert
        assert isinstance(operation, AdGroupCustomizerOperation)
        assert operation.create.ad_group == ad_group
        assert operation.create.customizer_attribute == customizer_attribute
        assert operation.create.value.type_ == value_type
        assert operation.create.value.string_value == string_value

    def test_create_remove_operation(self, service: Any):
        """Test creating remove operation."""
        # Arrange
        resource_name = "customers/1234567890/adGroupCustomizers/123~456"

        # Act
        operation = service.create_remove_operation(resource_name=resource_name)

        # Assert
        assert isinstance(operation, AdGroupCustomizerOperation)
        assert operation.remove == resource_name
        assert not operation.create

    def test_create_ad_group_customizer(self, service: Any, mock_client: Any):
        """Test creating a single ad group customizer."""
        # Arrange
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        value_type = CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        string_value = "Test Value"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_remove_ad_group_customizer(self, service: Any, mock_client: Any):
        """Test removing an ad group customizer."""
        # Arrange
        customer_id = "1234567890"
        resource_name = "customers/1234567890/adGroupCustomizers/123~456"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[MutateAdGroupCustomizerResult(resource_name=resource_name)]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.remove_ad_group_customizer(
            customer_id=customer_id,
            resource_name=resource_name,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_create_text_customizer(self, service: Any, mock_client: Any):
        """Test creating a text customizer."""
        # Arrange
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        text_value = "Test Text"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.create_text_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            text_value=text_value,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_create_number_customizer(self, service: Any, mock_client: Any):
        """Test creating a number customizer."""
        # Arrange
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        number_value = "42"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.create_number_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            number_value=number_value,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_create_price_customizer(self, service: Any, mock_client: Any):
        """Test creating a price customizer."""
        # Arrange
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        price_value = "19.99"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.create_price_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            price_value=price_value,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_create_percent_customizer(self, service: Any, mock_client: Any):
        """Test creating a percent customizer."""
        # Arrange
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        percent_value = "25"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        # Act
        response = service.create_percent_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            percent_value=percent_value,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore


# Server tests removed - server architecture has changed
