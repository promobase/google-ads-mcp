"""Tests for Ad Group Criterion Label Service."""

import pytest
from typing import Any
from unittest.mock import Mock

from google.ads.googleads.v20.services.services.ad_group_criterion_label_service import (
    AdGroupCriterionLabelServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_label_service import (
    AdGroupCriterionLabelOperation,
    MutateAdGroupCriterionLabelsRequest,
    MutateAdGroupCriterionLabelsResponse,
    MutateAdGroupCriterionLabelResult,
)

from src.services.ad_group.ad_group_criterion_label_service import (
    AdGroupCriterionLabelService,
)


class TestAdGroupCriterionLabelService:
    """Test cases for AdGroupCriterionLabelService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AdGroupCriterionLabelServiceClient."""
        return Mock(spec=AdGroupCriterionLabelServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any):
        """Create an AdGroupCriterionLabelService instance with mock client."""
        service = AdGroupCriterionLabelService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    def test_mutate_ad_group_criterion_labels_success(
        self, service: Any, mock_client: Any
    ):
        """Test successful ad group criterion labels mutation."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                )
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=operations,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAdGroupCriterionLabelsRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1
        assert (
            request.operations[0].create.ad_group_criterion
            == "customers/1234567890/adGroupCriteria/123~456"
        )
        assert request.operations[0].create.label == "customers/1234567890/labels/789"
        assert request.partial_failure is False
        assert request.validate_only is False

    def test_mutate_ad_group_criterion_labels_with_options(
        self, service: Any, mock_client: Any
    ):
        """Test ad group criterion labels mutation with all options."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        expected_response = MutateAdGroupCriterionLabelsResponse()
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
        )

        # Assert
        assert response == expected_response
        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True

    def test_mutate_ad_group_criterion_labels_failure(
        self, service: Any, mock_client: Any
    ):
        """Test ad group criterion labels mutation failure."""
        # Arrange
        customer_id = "1234567890"

        # Create a real operation object
        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        mock_client.mutate_ad_group_criterion_labels.side_effect = Exception(  # type: ignore
            "API Error"
        )

        # Act & Assert
        with pytest.raises(
            Exception, match="Failed to mutate ad group criterion labels"
        ):
            service.mutate_ad_group_criterion_labels(
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_ad_group_criterion_label_operation(self, service: Any):
        """Test creating ad group criterion label operation."""
        # Arrange
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        label = "customers/1234567890/labels/789"

        # Act
        operation = service.create_ad_group_criterion_label_operation(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        # Assert
        assert isinstance(operation, AdGroupCriterionLabelOperation)
        assert operation.create.ad_group_criterion == ad_group_criterion
        assert operation.create.label == label

    def test_create_remove_operation(self, service: Any):
        """Test creating remove operation."""
        # Arrange
        resource_name = "customers/1234567890/adGroupCriterionLabels/123~456~789"

        # Act
        operation = service.create_remove_operation(resource_name=resource_name)

        # Assert
        assert isinstance(operation, AdGroupCriterionLabelOperation)
        assert operation.remove == resource_name
        assert not operation.create

    def test_assign_label_to_criterion(self, service: Any, mock_client: Any):
        """Test assigning a label to a criterion."""
        # Arrange
        customer_id = "1234567890"
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        label = "customers/1234567890/labels/789"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                )
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.assign_label_to_criterion(
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

    def test_remove_label_from_criterion(self, service: Any, mock_client: Any):
        """Test removing a label from a criterion."""
        # Arrange
        customer_id = "1234567890"
        resource_name = "customers/1234567890/adGroupCriterionLabels/123~456~789"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[MutateAdGroupCriterionLabelResult(resource_name=resource_name)]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.remove_label_from_criterion(
            customer_id=customer_id,
            resource_name=resource_name,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

    def test_assign_multiple_labels_to_criterion(self, service: Any, mock_client: Any):
        """Test assigning multiple labels to a criterion."""
        # Arrange
        customer_id = "1234567890"
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        labels = [
            "customers/1234567890/labels/789",
            "customers/1234567890/labels/101112",
        ]

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                ),
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~101112"
                ),
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.assign_multiple_labels_to_criterion(
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            labels=labels,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

        # Verify that two operations were created
        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    def test_assign_label_to_multiple_criteria(self, service: Any, mock_client: Any):
        """Test assigning a label to multiple criteria."""
        # Arrange
        customer_id = "1234567890"
        ad_group_criteria = [
            "customers/1234567890/adGroupCriteria/123~456",
            "customers/1234567890/adGroupCriteria/123~789",
        ]
        label = "customers/1234567890/labels/101112"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~101112"
                ),
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~789~101112"
                ),
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        # Act
        response = service.assign_label_to_multiple_criteria(
            customer_id=customer_id,
            ad_group_criteria=ad_group_criteria,
            label=label,
        )

        # Assert
        assert response == expected_response
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

        # Verify that two operations were created
        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2


# Server tests removed - server architecture has changed
