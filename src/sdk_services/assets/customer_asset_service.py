"""Customer Asset Service for Google Ads API v20.

This service manages customer-level asset associations, allowing assets to be linked
to customers for use across campaigns.
"""

from typing import Any, List, Optional

from fastmcp import FastMCP
from google.ads.googleads.v20.services.services.customer_asset_service import (
    CustomerAssetServiceClient,
)
from google.ads.googleads.v20.services.types.customer_asset_service import (
    CustomerAssetOperation,
    MutateCustomerAssetsRequest,
    MutateCustomerAssetsResponse,
)
from google.ads.googleads.v20.resources.types.customer_asset import CustomerAsset
from google.ads.googleads.v20.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_field_type import (
    AssetFieldTypeEnum,
)
from google.ads.googleads.v20.enums.types.asset_link_status import (
    AssetLinkStatusEnum,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client


class CustomerAssetService:
    """Service for managing customer assets in Google Ads.

    Customer assets are assets linked at the customer level that can be used
    across multiple campaigns.
    """

    def __init__(self) -> None:
        """Initialize the customer asset service."""
        self._client: Optional[CustomerAssetServiceClient] = None

    @property
    def client(self) -> CustomerAssetServiceClient:
        """Get the customer asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerAssetService")
        assert self._client is not None
        return self._client

    def mutate_customer_assets(
        self,
        customer_id: str,
        operations: List[CustomerAssetOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: ResponseContentTypeEnum.ResponseContentType = ResponseContentTypeEnum.ResponseContentType.RESOURCE_NAME_ONLY,
    ) -> MutateCustomerAssetsResponse:
        """Create, update, or remove customer assets.

        Args:
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            MutateCustomerAssetsResponse: The response containing results.

        Raises:
            GoogleAdsException: If the request fails.
        """
        try:
            request = MutateCustomerAssetsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            return self.client.mutate_customer_assets(request=request)
        except Exception as e:
            raise Exception(f"Failed to mutate customer assets: {e}") from e

    def create_customer_asset_operation(
        self,
        asset: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        status: AssetLinkStatusEnum.AssetLinkStatus = AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
    ) -> CustomerAssetOperation:
        """Create a customer asset operation for creation.

        Args:
            asset: The asset resource name.
            field_type: The asset field type (role of the asset).
            status: The status of the asset link.

        Returns:
            CustomerAssetOperation: The operation to create the customer asset.
        """
        customer_asset = CustomerAsset(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        return CustomerAssetOperation(create=customer_asset)

    def create_update_operation(
        self,
        resource_name: str,
        status: Optional[AssetLinkStatusEnum.AssetLinkStatus] = None,
        update_mask: Optional[field_mask_pb2.FieldMask] = None,
    ) -> CustomerAssetOperation:
        """Create a customer asset operation for update.

        Args:
            resource_name: The resource name of the customer asset to update.
            status: The new status of the asset link.
            update_mask: The field mask specifying which fields to update.

        Returns:
            CustomerAssetOperation: The operation to update the customer asset.
        """
        customer_asset = CustomerAsset(resource_name=resource_name)

        if status is not None:
            customer_asset.status = status

        # Create update mask if not provided
        if update_mask is None:
            paths = []
            if status is not None:
                paths.append("status")
            update_mask = field_mask_pb2.FieldMask(paths=paths)

        return CustomerAssetOperation(
            update=customer_asset,
            update_mask=update_mask,
        )

    def create_remove_operation(self, resource_name: str) -> CustomerAssetOperation:
        """Create a customer asset operation for removal.

        Args:
            resource_name: The resource name of the customer asset to remove.
                Format: customers/{customer_id}/customerAssets/{asset_id}~{field_type}

        Returns:
            CustomerAssetOperation: The operation to remove the customer asset.
        """
        return CustomerAssetOperation(remove=resource_name)

    def create_customer_asset(
        self,
        customer_id: str,
        asset: str,
        field_type: AssetFieldTypeEnum.AssetFieldType,
        status: AssetLinkStatusEnum.AssetLinkStatus = AssetLinkStatusEnum.AssetLinkStatus.ENABLED,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Create a single customer asset.

        Args:
            customer_id: The customer ID.
            asset: The asset resource name.
            field_type: The asset field type.
            status: The status of the asset link.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_customer_asset_operation(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def update_customer_asset_status(
        self,
        customer_id: str,
        resource_name: str,
        status: AssetLinkStatusEnum.AssetLinkStatus,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Update the status of a customer asset.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the customer asset.
            status: The new status.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_update_operation(
            resource_name=resource_name,
            status=status,
        )

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    def remove_customer_asset(
        self,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> MutateCustomerAssetsResponse:
        """Remove a customer asset.

        Args:
            customer_id: The customer ID.
            resource_name: The resource name of the customer asset to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            MutateCustomerAssetsResponse: The response containing the result.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return self.mutate_customer_assets(
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )


def register_customer_asset_tools(mcp: FastMCP[Any]) -> None:
    """Register customer asset tools with the MCP server."""

    @mcp.tool
    async def mutate_customer_assets(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: str = "RESOURCE_NAME_ONLY",
    ) -> dict[str, Any]:
        """Create, update, or remove customer assets.

        Args:
            customer_id: The customer ID
            operations: List of customer asset operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        service = CustomerAssetService()

        # Convert response content type string to enum
        response_content_type_enum = getattr(
            ResponseContentTypeEnum.ResponseContentType, response_content_type
        )

        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                # Convert strings to enums
                field_type = getattr(
                    AssetFieldTypeEnum.AssetFieldType, op_data["field_type"]
                )
                status = getattr(
                    AssetLinkStatusEnum.AssetLinkStatus,
                    op_data.get("status", "ENABLED"),
                )

                operation = service.create_customer_asset_operation(
                    asset=op_data["asset"],
                    field_type=field_type,
                    status=status,
                )
            elif op_type == "update":
                status = None
                if "status" in op_data:
                    status = getattr(
                        AssetLinkStatusEnum.AssetLinkStatus, op_data["status"]
                    )

                operation = service.create_update_operation(
                    resource_name=op_data["resource_name"],
                    status=status,
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        response = service.mutate_customer_assets(
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
            if result.customer_asset:
                result_data["customer_asset"] = {
                    "resource_name": result.customer_asset.resource_name,
                    "asset": result.customer_asset.asset,
                    "field_type": result.customer_asset.field_type.name
                    if result.customer_asset.field_type
                    else None,
                    "status": result.customer_asset.status.name
                    if result.customer_asset.status
                    else None,
                    "source": result.customer_asset.source.name
                    if result.customer_asset.source
                    else None,
                    "primary_status": result.customer_asset.primary_status.name
                    if result.customer_asset.primary_status
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
    async def create_customer_asset(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        asset: str,
        field_type: str,
        status: str = "ENABLED",
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Create a customer asset.

        Args:
            customer_id: The customer ID
            asset: The asset resource name
            field_type: The asset field type (e.g., LOGO, HEADLINE, etc.)
            status: The asset link status (ENABLED, PAUSED, REMOVED)
            validate_only: Only validate the request

        Returns:
            Created customer asset details
        """
        service = CustomerAssetService()

        # Convert strings to enums
        field_type_enum = getattr(AssetFieldTypeEnum.AssetFieldType, field_type)
        status_enum = getattr(AssetLinkStatusEnum.AssetLinkStatus, status)

        response = service.create_customer_asset(
            customer_id=customer_id,
            asset=asset,
            field_type=field_type_enum,
            status=status_enum,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "create",
            "asset": asset,
            "field_type": field_type,
            "status": status,
        }

    @mcp.tool
    async def update_customer_asset_status(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        status: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Update the status of a customer asset.

        Args:
            customer_id: The customer ID
            resource_name: The customer asset resource name
            status: The new status (ENABLED, PAUSED, REMOVED)
            validate_only: Only validate the request

        Returns:
            Update result details
        """
        service = CustomerAssetService()

        # Convert string to enum
        status_enum = getattr(AssetLinkStatusEnum.AssetLinkStatus, status)

        response = service.update_customer_asset_status(
            customer_id=customer_id,
            resource_name=resource_name,
            status=status_enum,
            validate_only=validate_only,
        )

        result = response.results[0] if response.results else None
        return {
            "resource_name": result.resource_name if result else None,
            "operation": "update_status",
            "new_status": status,
        }

    @mcp.tool
    async def remove_customer_asset(  # pyright: ignore[reportUnusedFunction]
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> dict[str, Any]:
        """Remove a customer asset.

        Args:
            customer_id: The customer ID
            resource_name: The customer asset resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        service = CustomerAssetService()

        response = service.remove_customer_asset(
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
