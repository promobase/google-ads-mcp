"""Ad Group Criterion Label Service for Google Ads API v20.

This service manages label assignments to ad group criteria, allowing for better
organization and management of targeting criteria.
"""

from typing import List

from google.ads.googleads.v20.services.services.ad_group_criterion_label_service import (
    AdGroupCriterionLabelServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_criterion_label_service import (
    AdGroupCriterionLabelOperation,
    MutateAdGroupCriterionLabelsRequest,
    MutateAdGroupCriterionLabelsResponse,
)
from google.ads.googleads.v20.resources.types.ad_group_criterion_label import (
    AdGroupCriterionLabel,
)

# Exception handling


class AdGroupCriterionLabelService:
    """Service for managing ad group criterion labels in Google Ads.

    Ad group criterion labels allow you to organize and categorize targeting criteria
    within ad groups for better management and reporting.
    """

    def __init__(self, client: AdGroupCriterionLabelServiceClient):
        self._client = client

    def mutate_ad_group_criterion_labels(
        self,
        customer_id: str,
        operations: List[AdGroupCriterionLabelOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> MutateAdGroupCriterionLabelsResponse:
        """Create or remove ad group criterion labels.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCriterionLabelsResponse: The response containing results.

        Raises:
            GoogleAdsException: If the request fails.
        """
        try:
            request = MutateAdGroupCriterionLabelsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            return self._client.mutate_ad_group_criterion_labels(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate ad group criterion labels: {e}") from e

    def create_ad_group_criterion_label_operation(
        self,
        ad_group_criterion: str,
        label: str,
    ) -> AdGroupCriterionLabelOperation:
        """Create an ad group criterion label operation for creation.

        Args:
            ad_group_criterion: The ad group criterion resource name.
            label: The label resource name.

        Returns:
            AdGroupCriterionLabelOperation: The operation to create the label assignment.
        """
        ad_group_criterion_label = AdGroupCriterionLabel(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        return AdGroupCriterionLabelOperation(create=ad_group_criterion_label)

    def create_remove_operation(
        self, resource_name: str
    ) -> AdGroupCriterionLabelOperation:
        """Create an ad group criterion label operation for removal.

        Args:
            resource_name: The resource name of the label assignment to remove.
                Format: customers/{customer_id}/adGroupCriterionLabels/{ad_group_id}~{criterion_id}~{label_id}

        Returns:
            AdGroupCriterionLabelOperation: The operation to remove the label assignment.
        """
        return AdGroupCriterionLabelOperation(remove=resource_name)

    def assign_label_to_criterion(
        self,
        customer_id: str,
        ad_group_criterion: str,
        label: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCriterionLabelsResponse:
        """Assign a label to an ad group criterion.

        Args:
            customer_id: The customer ID.
            ad_group_criterion: The ad group criterion resource name.
            label: The label resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCriterionLabelsResponse: The response containing the result.
        """
        operation = self.create_ad_group_criterion_label_operation(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        return self.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def remove_label_from_criterion(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCriterionLabelsResponse:
        """Remove a label assignment from an ad group criterion.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the label assignment to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCriterionLabelsResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def assign_multiple_labels_to_criterion(
        self,
        customer_id: str,
        ad_group_criterion: str,
        labels: List[str],
        validate_only: bool = False,
    ) -> MutateAdGroupCriterionLabelsResponse:
        """Assign multiple labels to an ad group criterion.

        Args:
            customer_id: The customer ID.
            ad_group_criterion: The ad group criterion resource name.
            labels: List of label resource names.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCriterionLabelsResponse: The response containing the results.
        """
        operations = []
        for label in labels:
            operation = self.create_ad_group_criterion_label_operation(
                ad_group_criterion=ad_group_criterion,
                label=label,
            )
            operations.append(operation)

        return self.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

    def assign_label_to_multiple_criteria(
        self,
        customer_id: str,
        ad_group_criteria: List[str],
        label: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCriterionLabelsResponse:
        """Assign a label to multiple ad group criteria.

        Args:
            customer_id: The customer ID.
            ad_group_criteria: List of ad group criterion resource names.
            label: The label resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCriterionLabelsResponse: The response containing the results.
        """
        operations = []
        for ad_group_criterion in ad_group_criteria:
            operation = self.create_ad_group_criterion_label_operation(
                ad_group_criterion=ad_group_criterion,
                label=label,
            )
            operations.append(operation)

        return self.mutate_ad_group_criterion_labels(
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )
