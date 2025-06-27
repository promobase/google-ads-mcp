"""Ad Group Customizer Service for Google Ads API v20.

This service manages customizer values at the ad group level, allowing dynamic
content insertion in ads based on ad group-specific data.
"""

from typing import List

from google.ads.googleads.v20.services.services.ad_group_customizer_service import (
    AdGroupCustomizerServiceClient,
)
from google.ads.googleads.v20.services.types.ad_group_customizer_service import (
    AdGroupCustomizerOperation,
    MutateAdGroupCustomizersRequest,
    MutateAdGroupCustomizersResponse,
)
from google.ads.googleads.v20.resources.types.ad_group_customizer import (
    AdGroupCustomizer,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.common.types.customizer_value import CustomizerValue


class AdGroupCustomizerService:
    """Service for managing ad group customizers in Google Ads.

    Ad group customizers allow you to insert dynamic content into ads based on
    ad group-specific customizer values.
    """

    def __init__(self, client: AdGroupCustomizerServiceClient):
        self._client = client

    def mutate_ad_group_customizers(
        self,
        customer_id: str,
        operations: List[AdGroupCustomizerOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateAdGroupCustomizersResponse:
        """Create or remove ad group customizers.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing results.

        Raises:
            Exception: If the request fails.
        """
        try:
            request = MutateAdGroupCustomizersRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self._client.mutate_ad_group_customizers(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate ad group customizers: {e}") from e

    def create_ad_group_customizer_operation(
        self,
        ad_group: str,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
    ) -> AdGroupCustomizerOperation:
        """Create an ad group customizer operation for creation.

        Args:
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.

        Returns:
            AdGroupCustomizerOperation: The operation to create the ad group customizer.
        """
        customizer_value = CustomizerValue(
            type_=value_type,
            string_value=string_value,
        )

        ad_group_customizer = AdGroupCustomizer(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value=customizer_value,
        )

        return AdGroupCustomizerOperation(create=ad_group_customizer)

    def create_remove_operation(self, resource_name: str) -> AdGroupCustomizerOperation:
        """Create an ad group customizer operation for removal.

        Args:
            resource_name: The resource name of the ad group customizer to remove.
                Format: customers/{customer_id}/adGroupCustomizers/{ad_group_id}~{customizer_attribute_id}

        Returns:
            AdGroupCustomizerOperation: The operation to remove the ad group customizer.
        """
        return AdGroupCustomizerOperation(remove=resource_name)

    def create_ad_group_customizer(
        self,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Create a single ad group customizer.

        Args:
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        operation = self.create_ad_group_customizer_operation(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        return self.mutate_ad_group_customizers(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def remove_ad_group_customizer(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Remove an ad group customizer.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the ad group customizer to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_ad_group_customizers(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def create_text_customizer(
        self,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Create a text ad group customizer.

        Args:
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            text_value: The text value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        return self.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            string_value=text_value,
            validate_only=validate_only,
        )

    def create_number_customizer(
        self,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Create a number ad group customizer.

        Args:
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            number_value: The number value as a string.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        return self.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.NUMBER,
            string_value=number_value,
            validate_only=validate_only,
        )

    def create_price_customizer(
        self,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Create a price ad group customizer.

        Args:
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            price_value: The price value as a string (e.g., "19.99").
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        return self.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PRICE,
            string_value=price_value,
            validate_only=validate_only,
        )

    def create_percent_customizer(
        self,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        percent_value: str,
        validate_only: bool = False,
    ) -> MutateAdGroupCustomizersResponse:
        """Create a percent ad group customizer.

        Args:
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            percent_value: The percent value as a string (e.g., "25").
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateAdGroupCustomizersResponse: The response containing the result.
        """
        return self.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT,
            string_value=percent_value,
            validate_only=validate_only,
        )
