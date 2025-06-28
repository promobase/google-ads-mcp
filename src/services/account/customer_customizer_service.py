"""Customer Customizer Service for Google Ads API v20.

This service manages customizer values at the customer level, allowing dynamic
content insertion in ads based on customer-specific data.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP

from google.ads.googleads.v20.services.services.customer_customizer_service import (
    CustomerCustomizerServiceClient,
)
from google.ads.googleads.v20.services.types.customer_customizer_service import (
    CustomerCustomizerOperation,
    MutateCustomerCustomizersRequest,
    MutateCustomerCustomizersResponse,
)
from google.ads.googleads.v20.resources.types.customer_customizer import (
    CustomerCustomizer,
)
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v20.common.types.customizer_value import CustomizerValue

from src.sdk_client import get_sdk_client


class CustomerCustomizerService:
    """Service for managing customer customizers in Google Ads.

    Customer customizers allow you to insert dynamic content into ads based on
    customer-level customizer values.
    """

    def __init__(self) -> None:
        """Initialize the customer customizer service."""
        self._client: Optional[CustomerCustomizerServiceClient] = None

    @property
    def client(self) -> CustomerCustomizerServiceClient:
        """Get the customer customizer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerCustomizerService")
        assert self._client is not None
        return self._client

    def mutate_customer_customizers(
        self,
        customer_id: str,
        operations: List[CustomerCustomizerOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateCustomerCustomizersResponse:
        """Create or remove customer customizers.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateCustomerCustomizersResponse: The response containing results.

        Raises:
            Exception: If the request fails.
        """
        try:
            request = MutateCustomerCustomizersRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self.client.mutate_customer_customizers(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate customer customizers: {e}") from e

    def create_customer_customizer_operation(
        self,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
    ) -> CustomerCustomizerOperation:
        """Create a customer customizer operation for creation.

        Args:
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.

        Returns:
            CustomerCustomizerOperation: The operation to create the customer customizer.
        """
        customizer_value = CustomizerValue(
            type_=value_type,
            string_value=string_value,
        )

        customer_customizer = CustomerCustomizer(
            customizer_attribute=customizer_attribute,
            value=customizer_value,
        )

        return CustomerCustomizerOperation(create=customer_customizer)

    def create_remove_operation(
        self, resource_name: str
    ) -> CustomerCustomizerOperation:
        """Create a customer customizer operation for removal.

        Args:
            resource_name: The resource name of the customer customizer to remove.
                Format: customers/{customer_id}/customerCustomizers/{customizer_attribute_id}

        Returns:
            CustomerCustomizerOperation: The operation to remove the customer customizer.
        """
        return CustomerCustomizerOperation(remove=resource_name)

    def create_customer_customizer(
        self,
        customer_id: str,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Create a single customer customizer.

        Args:
            customer_id: The customer ID.
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        operation = self.create_customer_customizer_operation(
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        return self.mutate_customer_customizers(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def remove_customer_customizer(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Remove a customer customizer.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the customer customizer to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_customer_customizers(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def create_text_customizer(
        self,
        customer_id: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Create a text customer customizer.

        Args:
            customer_id: The customer ID.
            customizer_attribute: The customizer attribute resource name.
            text_value: The text value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        return self.create_customer_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            string_value=text_value,
            validate_only=validate_only,
        )

    def create_number_customizer(
        self,
        customer_id: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Create a number customer customizer.

        Args:
            customer_id: The customer ID.
            customizer_attribute: The customizer attribute resource name.
            number_value: The number value as a string.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        return self.create_customer_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.NUMBER,
            string_value=number_value,
            validate_only=validate_only,
        )

    def create_price_customizer(
        self,
        customer_id: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Create a price customer customizer.

        Args:
            customer_id: The customer ID.
            customizer_attribute: The customizer attribute resource name.
            price_value: The price value as a string (e.g., "19.99").
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        return self.create_customer_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PRICE,
            string_value=price_value,
            validate_only=validate_only,
        )

    def create_percent_customizer(
        self,
        customer_id: str,
        customizer_attribute: str,
        percent_value: str,
        validate_only: bool = False,
    ) -> MutateCustomerCustomizersResponse:
        """Create a percent customer customizer.

        Args:
            customer_id: The customer ID.
            customizer_attribute: The customizer attribute resource name.
            percent_value: The percent value as a string (e.g., "25").
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerCustomizersResponse: The response containing the result.
        """
        return self.create_customer_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT,
            string_value=percent_value,
            validate_only=validate_only,
        )


def register_customer_customizer_tools(mcp: FastMCP[Any]) -> None:
    """Register customer customizer tools with the MCP server."""

    @mcp.tool
    async def mutate_customer_customizers(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> dict[str, Any]:
        """Create or remove customer customizers.

        Args:
            customer_id: The customer ID
            operations: List of customer customizer operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        service = CustomerCustomizerService()

        # Convert response content type string to enum
        response_content_type_enum = getattr(
            ResponseContentTypeEnum.ResponseContentType, response_content_type
        )

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                # Convert string to enum
                value_type = getattr(
                    CustomizerAttributeTypeEnum.CustomizerAttributeType,
                    op_data["value_type"],
                )

                operation = service.create_customer_customizer_operation(
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

        response = service.mutate_customer_customizers(
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type_enum,
        )

        # Format response
        results = []
        for result in response.results:
            result_data: dict[str, Any] = {
                "resource_name": result.resource_name,
            }
            if result.customer_customizer:
                result_data["customer_customizer"] = {
                    "resource_name": result.customer_customizer.resource_name,
                    "customizer_attribute": result.customer_customizer.customizer_attribute,
                    "status": result.customer_customizer.status.name
                    if result.customer_customizer.status
                    else None,
                    "value": {
                        "type": result.customer_customizer.value.type_.name
                        if result.customer_customizer.value.type_
                        else None,
                        "string_value": result.customer_customizer.value.string_value,
                    }
                    if result.customer_customizer.value
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
    async def create_customer_customizer(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        customizer_attribute: str,
        value_type: str,
        string_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a customer customizer.

        Args:
            customer_id: The customer ID
            customizer_attribute: The customizer attribute resource name
            value_type: The type of customizer value (TEXT, NUMBER, PRICE, PERCENT)
            string_value: The string representation of the value
            validate_only: Only validate the request

        Returns:
            Created customer customizer details
        """
        service = CustomerCustomizerService()

        # Convert string to enum
        value_type_enum = getattr(
            CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type
        )

        response = service.create_customer_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            value_type=value_type_enum,
            string_value=string_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_customizer",
            "customizer_attribute": customizer_attribute,
            "value_type": value_type,
            "string_value": string_value,
        }

    @mcp.tool
    async def create_text_customizer(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a text customer customizer.

        Args:
            customer_id: The customer ID
            customizer_attribute: The customizer attribute resource name
            text_value: The text value
            validate_only: Only validate the request

        Returns:
            Created text customizer details
        """
        service = CustomerCustomizerService()

        response = service.create_text_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            text_value=text_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_text_customizer",
            "customizer_attribute": customizer_attribute,
            "text_value": text_value,
        }

    @mcp.tool
    async def create_number_customizer(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a number customer customizer.

        Args:
            customer_id: The customer ID
            customizer_attribute: The customizer attribute resource name
            number_value: The number value as a string
            validate_only: Only validate the request

        Returns:
            Created number customizer details
        """
        service = CustomerCustomizerService()

        response = service.create_number_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            number_value=number_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_number_customizer",
            "customizer_attribute": customizer_attribute,
            "number_value": number_value,
        }

    @mcp.tool
    async def create_price_customizer(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a price customer customizer.

        Args:
            customer_id: The customer ID
            customizer_attribute: The customizer attribute resource name
            price_value: The price value as a string (e.g., '19.99')
            validate_only: Only validate the request

        Returns:
            Created price customizer details
        """
        service = CustomerCustomizerService()

        response = service.create_price_customizer(
            customer_id=customer_id,
            customizer_attribute=customizer_attribute,
            price_value=price_value,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create_price_customizer",
            "customizer_attribute": customizer_attribute,
            "price_value": price_value,
        }

    @mcp.tool
    async def remove_customer_customizer(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Remove a customer customizer.

        Args:
            customer_id: The customer ID
            resource_name: The customer customizer resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        service = CustomerCustomizerService()

        response = service.remove_customer_customizer(
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
