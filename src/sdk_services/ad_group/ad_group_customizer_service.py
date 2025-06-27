"""Ad Group Customizer Service for Google Ads API v20.

This service manages customizer values at the ad group level, allowing dynamic
content insertion in ads based on ad group-specific data.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
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

from src.sdk_client import get_sdk_client


class AdGroupCustomizerService:
    """Service for managing ad group customizers in Google Ads.

    Ad group customizers allow you to insert dynamic content into ads based on
    ad group-specific customizer values.
    """

    def __init__(self) -> None:
        """Initialize the ad group customizer service."""
        self._client: Optional[AdGroupCustomizerServiceClient] = None

    @property
    def client(self) -> AdGroupCustomizerServiceClient:
        """Get the ad group customizer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupCustomizerService")
        assert self._client is not None
        return self._client

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
            return self.client.mutate_ad_group_customizers(request=request)
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


def register_ad_group_customizer_tools(mcp: FastMCP[Any]) -> None:
    """Register ad group customizer tools with the MCP server."""

    @mcp.tool
    async def mutate_ad_group_customizers(
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> dict[str, Any]:
        """Create or remove ad group customizers.

        Args:
            customer_id: The customer ID
            operations: List of ad group customizer operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        service = AdGroupCustomizerService()

        # Convert response content type string to enum
        response_content_type_enum = getattr(
            ResponseContentTypeEnum.ResponseContentType, response_content_type
        )

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                # Convert value type string to enum
                value_type = getattr(
                    CustomizerAttributeTypeEnum.CustomizerAttributeType,
                    op_data["value_type"],
                )

                operation = service.create_ad_group_customizer_operation(
                    ad_group=op_data["ad_group"],
                    customizer_attribute=op_data["customizer_attribute"],
                    value_type=value_type,
                    string_value=op_data["string_value"],
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_ad_group_customizers(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type_enum,
        )

        # Format response
        results = []
        for result in response.results:
            result_data = {
                "resource_name": result.resource_name,
            }
            if result.ad_group_customizer:
                result_data["ad_group_customizer"] = {
                    "resource_name": result.ad_group_customizer.resource_name,
                    "ad_group": result.ad_group_customizer.ad_group,
                    "customizer_attribute": result.ad_group_customizer.customizer_attribute,
                    "status": result.ad_group_customizer.status.name
                    if result.ad_group_customizer.status
                    else None,
                    "value": {
                        "type": result.ad_group_customizer.value.type_.name
                        if result.ad_group_customizer.value.type_
                        else None,
                        "string_value": result.ad_group_customizer.value.string_value,
                    }
                    if result.ad_group_customizer.value
                    else None,
                }
            results.append(result_data)

        return {
            "results": results,
            "partial_failure_error": str(response.partial_failure_error)
            if response.partial_failure_error
            else None,
        }

    @mcp.tool
    async def create_ad_group_customizer(
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        value_type: str,
        string_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create an ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            value_type: Type of customizer value (TEXT, NUMBER, PRICE, PERCENT)
            string_value: String representation of the value
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        service = AdGroupCustomizerService()

        # Convert value type string to enum
        value_type_enum = getattr(
            CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type
        )

        response = service.create_ad_group_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type_enum,
            string_value=string_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_customizer",
            "ad_group": ad_group,
            "customizer_attribute": customizer_attribute,
            "value_type": value_type,
            "string_value": string_value,
        }

    @mcp.tool
    async def create_text_customizer(
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a text ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            text_value: The text value
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        service = AdGroupCustomizerService()

        response = service.create_text_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            text_value=text_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_text_customizer",
            "ad_group": ad_group,
            "customizer_attribute": customizer_attribute,
            "text_value": text_value,
        }

    @mcp.tool
    async def create_number_customizer(
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a number ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            number_value: The number value as a string
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        service = AdGroupCustomizerService()

        response = service.create_number_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            number_value=number_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_number_customizer",
            "ad_group": ad_group,
            "customizer_attribute": customizer_attribute,
            "number_value": number_value,
        }

    @mcp.tool
    async def create_price_customizer(
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a price ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            price_value: The price value as a string (e.g., '19.99')
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        service = AdGroupCustomizerService()

        response = service.create_price_customizer(
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            price_value=price_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_price_customizer",
            "ad_group": ad_group,
            "customizer_attribute": customizer_attribute,
            "price_value": price_value,
        }

    @mcp.tool
    async def remove_ad_group_customizer(
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Remove an ad group customizer.

        Args:
            customer_id: The customer ID
            resource_name: The ad group customizer resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        service = AdGroupCustomizerService()

        response = service.remove_ad_group_customizer(
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "remove",
            "removed_resource_name": resource_name,
        }
